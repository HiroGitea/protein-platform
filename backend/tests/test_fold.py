"""AlphaFold 2 NIM contract and complete job/download flow without a GPU."""

import asyncio
import json
import time

import httpx
import pytest

from app.config import settings
from app.engines.fold import AF2_PATH, fold_engine, predict_af2
from app.nvidia_api import RemoteApiError
from app.schemas import FoldRequest

PDB = (
    "MODEL        1\nATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 90.00           C\nENDMDL\n"
)


@pytest.fixture
def nim(monkeypatch):
    original = httpx.AsyncClient
    monkeypatch.setattr(settings, "af2_local_url", "http://af2.test:8001")
    monkeypatch.setattr(settings, "af2_remote_url", "")
    monkeypatch.setattr(settings, "af2_api_key", "dedicated-token")
    monkeypatch.setattr(settings, "af2_poll_interval_seconds", 0.001)
    monkeypatch.setattr(settings, "fold_provider", "auto")

    def install(handler):
        monkeypatch.setattr(
            httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs)
        )

    return install


def test_sequence_validation(client):
    assert FoldRequest(sequence=" mkta\nyia ").sequence == "MKTAYIA"
    assert len(FoldRequest(sequence="A" * 4096).sequence) == 4096
    for sequence in ("", " \n", "ACDX", ">protein\nACD", "ACD*", "A" * 4097):
        assert client.post("/api/fold/predict", json={"sequence": sequence}).status_code == 422
    assert (
        client.post("/api/fold/predict", json={"sequence": "ACD", "algorithm": "invalid"}).status_code == 422
    )


async def test_polling_and_credentials(nim):
    requests = []

    def handler(request):
        requests.append(request)
        assert request.headers["Authorization"] == "Bearer dedicated-token"
        if request.method == "POST":
            assert str(request.url) == f"https://af2.test/v1{AF2_PATH}"
            assert json.loads(request.content) == {"sequence": "ACD"}
            return httpx.Response(202, headers={"nvcf-reqid": "request-1"})
        assert str(request.url) == "https://af2.test/v1/status/request-1"
        return httpx.Response(202) if len(requests) == 2 else httpx.Response(200, json=[PDB])

    nim(handler)
    assert await predict_af2("https://af2.test/v1/", {"sequence": "ACD"}, api_key="dedicated-token") == [PDB]
    assert len(requests) == 3


@pytest.mark.parametrize(
    "response,match",
    [
        (httpx.Response(202), "nvcf-reqid"),
        (httpx.Response(401, text="denied"), "401"),
        (httpx.Response(503, text="unavailable"), "503"),
        (httpx.Response(200, text="not json"), "invalid JSON"),
        (httpx.Response(200, json=[]), "PDB structures"),
        (httpx.Response(200, json={"pdbs": [PDB]}), "PDB structures"),
        (httpx.Response(200, json=["not a pdb"]), "PDB structures"),
        (httpx.Response(200, json=[PDB, None]), "PDB structures"),
    ],
)
async def test_bad_responses_fail(nim, response, match):
    nim(lambda request: response)
    with pytest.raises(RemoteApiError, match=match):
        await predict_af2("http://af2.test", {"sequence": "ACD"})


async def test_deadline_bounds_polling(nim, monkeypatch):
    monkeypatch.setattr(settings, "af2_timeout_seconds", 0.02)
    nim(lambda request: httpx.Response(202, headers={"nvcf-reqid": "pending"}))
    with pytest.raises(RemoteApiError, match="timed out"):
        await predict_af2("http://af2.test", {"sequence": "ACD"})


async def test_transport_failure(nim):
    def handler(request):
        raise httpx.ConnectError("offline", request=request)

    nim(handler)
    with pytest.raises(RemoteApiError, match="Unable to connect"):
        await predict_af2("http://af2.test", {"sequence": "ACD"})


async def test_cancellation_interrupts_polling(nim):
    accepted = asyncio.Event()

    def handler(request):
        accepted.set()
        return httpx.Response(202, headers={"nvcf-reqid": "pending"})

    nim(handler)
    task = asyncio.create_task(predict_af2("http://af2.test", {"sequence": "ACD"}))
    await accepted.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_provider_configuration(nim, monkeypatch):
    assert fold_engine.pick().kind == "local"
    monkeypatch.setattr(settings, "af2_local_url", "")
    assert not fold_engine.status().available
    monkeypatch.setattr(settings, "af2_remote_url", "https://af2.test")
    assert fold_engine.pick().kind == "remote"
    monkeypatch.setattr(settings, "fold_provider", "local")
    assert not fold_engine.status().available


@pytest.mark.parametrize("provider", ["local", "remote"])
def test_prediction_job_and_downloads(client, nim, monkeypatch, tmp_path, provider):
    monkeypatch.setattr(settings, "storage_dir", tmp_path)
    monkeypatch.setattr(settings, "fold_provider", provider)
    monkeypatch.setattr(settings, "af2_remote_url", "https://af2.test")

    def handler(request):
        assert request.url.path == AF2_PATH
        assert json.loads(request.content) == {
            "sequence": "ACD",
            "algorithm": "mmseqs2",
            "relax_prediction": False,
        }
        if provider == "local":
            assert "Authorization" not in request.headers
        else:
            assert request.headers["Authorization"] == "Bearer dedicated-token"
        return httpx.Response(200, json=[PDB, PDB])

    nim(handler)
    response = client.post(
        "/api/fold/predict", json={"sequence": "ac d", "algorithm": "mmseqs2", "relax_prediction": False}
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    for _ in range(100):
        job = client.get(f"/api/jobs/{job_id}").json()
        if job["status"] in ("succeeded", "failed"):
            break
        time.sleep(0.01)
    assert job["status"] == "succeeded", job
    assert job["result"]["model"] == "alphafold2"
    assert job["result"]["provider"] == provider
    assert job["result"]["sequence_length"] == 3
    assert job["result"]["pdb_files"] == ["predicted.pdb", "predicted_2.pdb"]
    assert client.get(job["result"]["viewer_url"]).text == PDB
    assert len(job["files"]) == 2
    for file in job["files"]:
        assert client.get(file["url"]).text == PDB

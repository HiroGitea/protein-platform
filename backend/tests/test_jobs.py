"""任务流水线：提交 -> 轮询 -> 终态。重点是失败路径要干净。"""

from __future__ import annotations

import time


def _wait(client, job_id, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = client.get(f"/api/jobs/{job_id}").json()
        if job["status"] in ("succeeded", "failed", "cancelled"):
            return job
        time.sleep(0.05)
    raise AssertionError(f"任务 {job_id} 超时未结束")


def test_submit_returns_job_id(client):
    r = client.post("/api/genmol/generate", json={"mode": "denovo", "num_samples": 5})
    assert r.status_code == 200
    assert r.json()["status"] == "queued"


def test_engine_not_ready_fails_job_not_request(client):
    """引擎没装应该让任务失败，而不是让 HTTP 请求 500。"""
    r = client.post("/api/genmol/generate", json={"mode": "denovo", "num_samples": 5})
    assert r.status_code == 200
    job = _wait(client, r.json()["job_id"])
    assert job["status"] == "failed"
    assert "无可用 provider" in job["error"]


def test_error_names_every_provider_that_failed(client):
    """错误信息要同时说明 local 和 remote 各自为什么不能用。"""
    r = client.post("/api/fold/predict", json={"sequence": "MKTAYIAKQRQISFVKSHFS"})
    job = _wait(client, r.json()["job_id"])
    assert job["status"] == "failed"
    assert "local:" in job["error"] and "remote:" in job["error"]


def test_all_tool_endpoints_accept_submissions(client):
    """五个工具的提交入口都要在，且返回 job_id。"""
    submissions = [
        ("/api/genmol/generate", {"num_samples": 3}),
        ("/api/molmim/optimize", {"smiles": "CCO"}),
        ("/api/mmseqs/search", {"sequence": "MKTAYIAKQRQ"}),
        ("/api/fold/predict", {"sequence": "MKTAYIAKQRQ"}),
    ]
    for path, body in submissions:
        r = client.post(path, json=body)
        assert r.status_code == 200, f"{path} -> {r.status_code} {r.text[:200]}"
        assert r.json()["job_id"]


def test_remote_only_engine_without_api_key(client):
    """没配 NVIDIA_API_KEY 时，远程 provider 要明说，不能静默失败。"""
    r = client.post("/api/molmim/optimize", json={"smiles": "CCO"})
    job = _wait(client, r.json()["job_id"])
    assert job["status"] == "failed"
    assert "NVIDIA_API_KEY" in job["error"]


def test_unknown_job_404(client):
    assert client.get("/api/jobs/nonexistent").status_code == 404


def test_param_validation(client):
    # num_samples 上限 1000
    assert client.post("/api/genmol/generate", json={"num_samples": 99999}).status_code == 422
    # temperature 必须为正
    assert client.post("/api/genmol/generate", json={"softmax_temp": 0}).status_code == 422

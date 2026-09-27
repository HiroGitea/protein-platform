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
    assert "未就绪" in job["error"] or "尚未实现" in job["error"]


def test_planned_engine_says_not_implemented(client):
    r = client.post("/api/fold/predict", json={"sequence": "MKTAYIAKQRQISFVKSHFS"})
    job = _wait(client, r.json()["job_id"])
    assert job["status"] == "failed"
    assert "尚未实现" in job["error"]


def test_unknown_job_404(client):
    assert client.get("/api/jobs/nonexistent").status_code == 404


def test_param_validation(client):
    # num_samples 上限 1000
    assert client.post("/api/genmol/generate", json={"num_samples": 99999}).status_code == 422
    # temperature 必须为正
    assert client.post("/api/genmol/generate", json={"softmax_temp": 0}).status_code == 422

"""文件上传与下载的边界。"""

from __future__ import annotations


def test_upload_accepts_known_types(client):
    r = client.post("/api/files", files={"file": ("protein.pdb", b"ATOM      1  N   MET A   1")})
    assert r.status_code == 200
    assert r.json()["filename"] == "protein.pdb"


def test_upload_rejects_unknown_types(client):
    r = client.post("/api/files", files={"file": ("payload.exe", b"MZ\x90\x00")})
    assert r.status_code == 400


def test_download_rejects_path_traversal(client):
    job_id = client.post("/api/genmol/generate", json={"num_samples": 1}).json()["job_id"]
    r = client.get(f"/api/jobs/{job_id}/files/..%2F..%2Fpyproject.toml")
    assert r.status_code == 404

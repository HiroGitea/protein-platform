"""健康检查：即使一个引擎都没装，服务也必须能起来并如实报告状态。"""

from __future__ import annotations


def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert {"genmol", "diffdock", "mmseqs", "fold"} <= {e["name"] for e in body["engines"]}


def test_unavailable_engine_explains_why(client):
    """引擎未就绪时必须说明缺什么，不能只给个 false。"""
    engines = client.get("/api/health").json()["engines"]
    for engine in engines:
        if not engine["available"]:
            assert engine["reason"], f"{engine['name']} 未就绪但没给原因"


def test_gpu_info_present(client):
    gpu = client.get("/api/health").json()["gpu"]
    assert "available" in gpu
    # 没显卡时也要给出原因，不能静默
    assert gpu["available"] or gpu["reason"]

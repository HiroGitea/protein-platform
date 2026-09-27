"""健康检查：即使一个引擎都没装，服务也必须能起来并如实报告状态。"""

from __future__ import annotations

ALL_ENGINES = {"genmol", "molmim", "diffdock", "mmseqs", "fold"}


def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert ALL_ENGINES <= {e["name"] for e in body["engines"]}


def test_unavailable_engine_explains_why(client):
    """引擎未就绪时必须说明缺什么，不能只给个 false。"""
    for engine in client.get("/api/health").json()["engines"]:
        if not engine["available"]:
            assert engine["reason"], f"{engine['name']} 未就绪但没给原因"


def test_every_provider_reports_reason(client):
    """每个 provider 单独报告可用性和原因。"""
    for engine in client.get("/api/health").json()["engines"]:
        assert engine["providers"], f"{engine['name']} 没有任何 provider"
        for p in engine["providers"]:
            assert p["kind"] in ("local", "remote")
            if not p["available"]:
                assert p["reason"], f"{engine['name']}/{p['kind']} 不可用但没给原因"


def test_engines_expose_both_providers(client):
    """除 mmseqs（官方无托管搜索 API）外，都应有 local + remote 两条路。"""
    engines = {e["name"]: e for e in client.get("/api/health").json()["engines"]}
    for name in ALL_ENGINES - {"mmseqs"}:
        kinds = {p["kind"] for p in engines[name]["providers"]}
        assert kinds == {"local", "remote"}, f"{name} 缺 provider: {kinds}"


def test_gpu_info_present(client):
    gpu = client.get("/api/health").json()["gpu"]
    assert "available" in gpu
    # 没显卡时也要给出原因，不能静默
    assert gpu["available"] or gpu["reason"]

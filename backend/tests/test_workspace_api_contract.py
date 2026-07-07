from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_market_overview_contract():
    response = client.get("/api/v1/market/overview")

    assert response.status_code == 200
    data = response.json()
    assert {"score", "status", "turnover", "upCount", "downCount", "summary"}.issubset(data)


def test_market_sectors_contract():
    response = client.get("/api/v1/market/sectors")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert {"name", "change", "score", "leader", "reason"}.issubset(data[0])


def test_research_queue_contract_includes_score_details():
    response = client.get("/api/v1/research/queue")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert {"code", "name", "score", "reason", "scoreDetails"}.issubset(data[0])


def test_cors_allows_local_frontend():
    response = client.options(
        "/api/v1/market/overview",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

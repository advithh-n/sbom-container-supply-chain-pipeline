from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_assets() -> None:
    response = client.get("/api/v1/assets")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_asset_lookup_is_case_insensitive() -> None:
    response = client.get("/api/v1/assets/der-101")
    assert response.status_code == 200
    assert response.json()["asset_type"] == "solar"


def test_missing_asset_returns_404_without_internal_details() -> None:
    response = client.get("/api/v1/assets/DER-999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Asset not found"}


def test_grid_summary() -> None:
    response = client.get("/api/v1/grid/summary")
    body = response.json()
    assert response.status_code == 200
    assert body["assets_total"] == 3
    assert body["assets_online"] == 2
    assert body["generation_mw"] == 201.0


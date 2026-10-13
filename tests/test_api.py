"""FastAPI contract regression tests for the public arithmetic endpoint."""
from fastapi.testclient import TestClient
from agents.api import app


client = TestClient(app)


def test_health_and_browser_root():
    assert client.get("/health").status_code == 200
    html = client.get("/")
    assert html.status_code == 200
    assert "Macronutrient energy calculator" in html.text
    assert client.get("/calculator.js").status_code == 200


def test_macronutrient_api_reconciles_energy():
    response = client.post("/api/macronutrients", json={
        "weight_kg": 70, "energy_kcal": 2000,
        "amino_acids_g": 90, "lipid_20pct_ml": 250
    })
    assert response.status_code == 200
    data = response.json()
    assert data["dextrose_kcal"] == 1140
    assert data["total_calculated_kcal"] == 2000


def test_macronutrient_api_rejects_energy_budget_and_non_finite():
    data = {"weight_kg": 70, "energy_kcal": 100, "amino_acids_g": 90, "lipid_20pct_ml": 250}
    assert client.post("/api/macronutrients", json=data).status_code == 422
    data.update({"energy_kcal": 2000, "weight_kg": 0})
    assert client.post("/api/macronutrients", json=data).status_code == 422


def test_audit_rejects_identifiers_without_leaking_them():
    response = client.post("/api/audit", json={
        "task_id": "MRN-123456", "target_identifier": "SYNTH",
        "primary_metric": 10, "secondary_metric": 0
    })
    assert response.status_code == 400
    assert "MRN-123456" not in response.text

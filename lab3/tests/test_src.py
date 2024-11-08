import random
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.main import app

# global client for non-pred endpoints 
client = TestClient(app)

@pytest.fixture
def test_data_single():
    return {
        "MedInc": 1,
        "HouseAge": 1,
        "AveRooms": 3,
        "AveBedrms": 3,
        "Population": 3,
        "AveOccup": 5,
        "Latitude": 1,
        "Longitude": 1,
    }

@pytest.fixture
def test_data_bulk():
    return {
        "houses": [
            {
                "MedInc": 1,
                "HouseAge": 1,
                "AveRooms": 3,
                "AveBedrms": 3,
                "Population": 3,
                "AveOccup": 5,
                "Latitude": 1,
                "Longitude": 1,
            },
            {
                "MedInc": 2,
                "HouseAge": 2,
                "AveRooms": 4,
                "AveBedrms": 2,
                "Population": 4,
                "AveOccup": 4,
                "Latitude": 2,
                "Longitude": 2,
            }
        ]
    }

# endpoints using global client
def test_health():
    response = client.get("/lab/health")
    assert response.status_code == 200
    assert datetime.fromisoformat(response.json()["time"])


def test_root():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

def test_docs_endpoint():
    response = client.get("/lab/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_openapi_version_correct():
    response = client.get("/lab/openapi.json")
    assert response.status_code == 200
    assert response.json()["openapi"][0:2] == "3."
    assert response.headers["content-type"] == "application/json"

@pytest.mark.parametrize(
    "query_parameter, value",
    [("bob", "name"), ("nam", "name")],
)
def test_hello_endpoint_bad_parameter(query_parameter, value):
    response = client.get(f"/lab/hello?{query_parameter}={value}")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": ["query", "name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


@pytest.mark.parametrize(
    "test_input, expected",
    [("james", "james"), ("bOB", "bOB"), ("BoB", "BoB"), (100, 100)],
)
def test_hello_endpoint(test_input, expected):
    response = client.get(f"/lab/hello?name={test_input}")
    assert response.status_code == 200
    assert response.json()["message"].lower() == f"Hello {expected}".lower()

# lifespanned client pred tests following boilerplate
def test_predict_basic(test_data_single):
    with TestClient(app) as lifespanned_client:
        response = lifespanned_client.post("/lab/predict", json=test_data_single)
        assert response.status_code == 200
        assert isinstance(response.json()["prediction"], float)

def test_bulk_predict_basic(test_data_bulk):
    with TestClient(app) as lifespanned_client:
        response = lifespanned_client.post("/lab/bulk-predict", json=test_data_bulk)
        assert response.status_code == 200
        predictions = response.json()["predictions"]
        assert isinstance(predictions, list)
        assert len(predictions) == len(test_data_bulk["houses"])
        assert all(isinstance(pred, float) for pred in predictions)

def test_predict_with_cache(test_data_single):
    with TestClient(app) as lifespanned_client:
        response1 = lifespanned_client.post("/lab/predict", json=test_data_single)
        response2 = lifespanned_client.post("/lab/predict", json=test_data_single)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["prediction"] == response2.json()["prediction"]

def test_bulk_predict_with_cache(test_data_bulk):
    with TestClient(app) as lifespanned_client:
        response1 = lifespanned_client.post("/lab/bulk-predict", json=test_data_bulk)
        response2 = lifespanned_client.post("/lab/bulk-predict", json=test_data_bulk)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["predictions"] == response2.json()["predictions"]

def test_predict_validation(test_data_single):
    with TestClient(app) as lifespanned_client:
        # Test invalid latitude
        invalid_data = test_data_single.copy()
        invalid_data["Latitude"] = 91
        response = lifespanned_client.post("/lab/predict", json=invalid_data)
        assert response.status_code == 422

        # Test invalid MedInc
        invalid_data = test_data_single.copy()
        invalid_data["MedInc"] = -1
        response = lifespanned_client.post("/lab/predict", json=invalid_data)
        assert response.status_code == 422

def test_bulk_predict_validation(test_data_bulk):
    with TestClient(app) as lifespanned_client:
        
        response = lifespanned_client.post("/lab/bulk-predict", json={"houses": []})
        assert response.status_code == 200
        assert response.json()["predictions"] == []

        invalid_data = test_data_bulk.copy()
        invalid_data["houses"][0]["Latitude"] = 91
        response = lifespanned_client.post("/lab/bulk-predict", json=invalid_data)
        assert response.status_code == 422


@pytest.mark.anyio
async def test_bulk_predict_output_model():
    routes = app.routes
    bulk_predict_route = None
    for route in routes:
        if route.path == "/lab/bulk-predict":
            bulk_predict_route = route
            break
    
    assert bulk_predict_route is not None
    assert bulk_predict_route.response_model is not None
    
    test_data = {
        "houses": [
            {
                "MedInc": 1,
                "HouseAge": 2,
                "AveRooms": 3,
                "AveBedrms": 4,
                "Population": 5,
                "AveOccup": 6,
                "Latitude": 7,
                "Longitude": 8,
            }
        ]
    }

    class MockRequest:
        async def json(self):
            return data.model_dump()
    
    response = await bulk_predict_route.endpoint(data, MockRequest())
    assert isinstance (response, BulkHousePrediction)
    
@pytest.fixture
def anyio_backend():
    return "asyncio"

if __name__ == "__main__":
    pytest.main()
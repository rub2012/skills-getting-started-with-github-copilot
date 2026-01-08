import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "participants" in data["Basketball"]

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/static/index.html"

def test_signup_success():
    # Use a new email
    response = client.post("/activities/Basketball/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Basketball" in data["message"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Tennis%20Club/signup?email=duplicate@example.com")
    # Second signup should fail
    response = client.post("/activities/Tennis%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_remove_participant_success():
    # First add
    client.post("/activities/Art%20Studio/signup?email=remove@example.com")
    # Then remove
    response = client.delete("/activities/Art%20Studio/participants?email=remove@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Removed remove@example.com from Art Studio" in data["message"]

def test_remove_participant_not_signed_up():
    response = client.delete("/activities/Science%20Club/participants?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_remove_participant_activity_not_found():
    response = client.delete("/activities/Nonexistent/participants?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]
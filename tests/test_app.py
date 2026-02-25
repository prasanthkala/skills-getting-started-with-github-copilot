import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
_initial = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore the in-memory activities dictionary before each test
    activities.clear()
    activities.update(copy.deepcopy(_initial))
    yield


def test_root_redirects():
    # Arrange: nothing special, client is ready
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 200
    # FastAPI returns HTML redirect; verify redirect location is to index.html
    assert "/static/index.html" in str(response.url)


def test_get_activities():
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data


def test_signup_success_and_duplicates():
    # Arrange
    email = "try@example.com"

    # Act - first signup
    r1 = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert r1.status_code == 200
    assert email in activities["Chess Club"]["participants"]

    # Act - duplicate signup
    r2 = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert r2.status_code == 400

    # Act - signup to nonexistent activity
    r3 = client.post("/activities/Nope/signup", params={"email": email})
    # Assert
    assert r3.status_code == 404


def test_unregister_success_and_errors():
    # Arrange - michael is initially signed up for Chess Club
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]

    # Act - unregister existing participant
    r1 = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"},
    )
    # Assert
    assert r1.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    # Act - unregister someone not registered
    r2 = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "nobody@nowhere"},
    )
    # Assert
    assert r2.status_code == 400

    # Act - unregister from nonexistent activity
    r3 = client.post(
        "/activities/Nope/unregister",
        params={"email": "foo@bar"},
    )
    # Assert
    assert r3.status_code == 404

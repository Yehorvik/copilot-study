import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Fixture to reset activities before each test
@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = deepcopy(activities)
    yield
    # Restore activities after test completes
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client(reset_activities):
    """FastAPI test client"""
    return TestClient(app)


def test_get_activities_returns_200(client):
    """Test that GET /activities returns 200 and includes 'Chess Club'"""
    # Arrange
    # (no setup needed, client is ready)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data


def test_successful_signup_adds_to_data(client):
    """Test that successful signup of a new email adds to data"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Programming Class"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    """Test that duplicate signup returns 400 with correct detail"""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_to_nonexistent_activity_returns_404(client):
    """Test that signup to non-existent activity returns 404"""
    # Arrange
    email = "test@mergington.edu"
    activity_name = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_removing_participant_succeeds(client):
    """Test that removing a participant succeeds and removes from list"""
    # Arrange
    email = "michael@mergington.edu"  # In Chess Club
    activity_name = "Chess Club"
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participant?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_removing_nonexistent_participant_returns_404(client):
    """Test that removing non-existent participant returns 404"""
    # Arrange
    email = "nonexistent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participant?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"

"""
Test suite for Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in inter-school games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming techniques and participate in competitions",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["sarah@mergington.edu", "alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lily@mergington.edu"]
        },
        "Drama Club": {
            "description": "Develop acting skills and perform in school theatrical productions",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Society": {
            "description": "Enhance critical thinking and public speaking through competitive debates",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for science competitions and conduct experiments",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Reset to original state before each test
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_student(self, client):
        """Test that duplicate signup is prevented"""
        # First signup
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # Try to signup again
        response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post("/activities/Programming%20Class/signup?email=urltest@mergington.edu")
        assert response.status_code == 200
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "urltest@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successful unregistration from an activity"""
        # First, ensure the student is registered
        client.post("/activities/Chess Club/signup?email=remove@mergington.edu")
        
        # Now unregister
        response = client.delete("/activities/Chess Club/unregister?email=remove@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "remove@mergington.edu" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "remove@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # michael@mergington.edu is already in Chess Club
        response = client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_non_registered_student(self, client):
        """Test unregistering a student not registered for the activity"""
        response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        response = client.delete("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestActivityCapacity:
    """Test activity participant capacity constraints"""
    
    def test_activity_max_participants_tracked(self, client):
        """Test that max_participants is properly tracked"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) <= chess_club["max_participants"]


class TestEndToEndWorkflow:
    """Test complete user workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete signup and unregister workflow"""
        email = "workflow@mergington.edu"
        activity = "Drama Club"
        
        # Get initial participants
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify added
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        assert email in after_signup.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify removed
        after_unregister = client.get("/activities")
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
        assert email not in after_unregister.json()[activity]["participants"]
    
    def test_multiple_students_signup(self, client):
        """Test multiple students signing up for the same activity"""
        activity = "Art Studio"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity]["participants"]
        assert len(final_participants) == initial_count + len(emails)
        
        for email in emails:
            assert email in final_participants

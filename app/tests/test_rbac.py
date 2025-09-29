# app/tests/test_rbac.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create a test client instance for the application
client = TestClient(app)

# Helper function to register and get user data
def register_user(email: str, password: str):
    """Registers a user and returns their token and data."""
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password, "role": "User"} 
    )
    if response.status_code != 200:
        # If user already exists, try logging in
        response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
    # Fail test setup if user creation/login failed
    if response.status_code not in (200, 201):
        pytest.fail(f"Setup failed for user {email}: {response.text}")
        
    return response.json()

# --- Global Setup: Register Admin (first user) and Standard User (second user) ---

# Admin setup (executed once)
admin_data = register_user("admin@test.com", "securepassword")
ADMIN_TOKEN = admin_data.get('access_token')

# User setup (executed once)
user_data = register_user("user1@test.com", "userpassword")
USER_TOKEN = user_data.get('access_token')

# Create an event owned by the Admin
admin_event_response = client.post(
    "/api/v1/events/",
    headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
    json={"title": "Admin's Event", "description": "Admin only event", "date": "2026-01-01", "location": "HQ", "status": "Upcoming"}
)
ADMIN_EVENT_ID = admin_event_response.json().get('id')

# Create an event owned by the User
user_event_response = client.post(
    "/api/v1/events/",
    headers={"Authorization": f"Bearer {USER_TOKEN}"},
    json={"title": "User's Event", "description": "User's own event", "date": "2026-02-01", "location": "Field", "status": "Upcoming"}
)
USER_EVENT_ID = user_event_response.json().get('id')


# --- Core RBAC and Ownership Tests ---

def test_user_only_sees_their_own_events():
    """Verify standard user only sees their own events (Ownership enforcement on GET)."""
    response = client.get(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1
    
    titles = [event.get('title') for event in events]
    assert "User's Event" in titles
    assert "Admin's Event" not in titles 

def test_admin_can_view_all_events():
    """Verify Admin sees all events (Admin access on GET)."""
    response = client.get(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    assert response.status_code == 200
    titles = [event.get('title') for event in response.json()]
    assert "User's Event" in titles
    assert "Admin's Event" in titles 

def test_user_cannot_update_others_event():
    """Verify ownership protection on PUT/Update."""
    response = client.put(
        f"/api/v1/events/{ADMIN_EVENT_ID}",
        headers={"Authorization": f"Bearer {USER_TOKEN}"},
        json={"title": "User Attempted Hacked Title", "description": "Attempted takeover", "date": "2026-01-01", "location": "HQ", "status": "Upcoming"}
    )
    assert response.status_code == 403 

def test_admin_can_update_any_event_status():
    """Verify Admin can perform the high-privilege action on a non-owned event (PATCH /status)."""
    response = client.patch(
        f"/api/v1/events/{USER_EVENT_ID}/status",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
        params={"new_status": "Completed"}
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'Completed' 

def test_user_cannot_delete_others_event():
    """Verify ownership protection on DELETE."""
    response = client.delete(
        f"/api/v1/events/{ADMIN_EVENT_ID}",
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    assert response.status_code == 403
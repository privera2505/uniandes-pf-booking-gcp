import pytest

from fastapi.testclient import TestClient

from adapters.memory.booking_repository_memory import InMemoryBookingRepositoryAdapter
from entrypoints.app import app
from entrypoints.routers import repo_dep

@pytest.fixture
def client():
    """Test client por test. Crea una instancia del repositorio para cada test."""
    test_repo = InMemoryBookingRepositoryAdapter()

    def _override_repo():
        return test_repo
    
    app.dependency_overrides[repo_dep] = _override_repo

    c = TestClient(app)
    return c

HEADER = {
    "x-apigateway-api-userinfo": "eyJzdWIiOiIxN2E0ZWQ5ZC1mN2Y5LTQ4NjItODkwYS01ZmY5ZDczNjMzNGYiLCJyb2xlIjoidHJhdmVsZXIiLCJtZmFfdmVyaWZpZWQiOmZhbHNlLCJjb3VudHJ5IjoiQ08iLCJob3RlbF9pZCI6bnVsbCwidHlwZSI6ImFjY2VzcyIsImlzcyI6Imh0dHBzOi8vYXV0aC50cmF2ZWxodWIuYXBwIiwiYXVkIjoidHJhdmVsaHViLWFwaSIsImV4cCI6MTc3NzE0Mzc3OSwiaWF0IjoxNzc3MTQyODc5fQ"
}

def test_booking_room_correct(client: client):
    post = client.post(
            "/api/v1/booking/booking_room",
            headers=HEADER,
            json={
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "checkin": "2026-09-03T10:00:00",
                "checkout": "2026-09-12T10:00:00",
                "numHuespedes": 2
            }
        )
    json = post.json()
    assert post.status_code == 200
    assert "id" in json
    assert "viajeroId" in json
    assert "habitacionId" in json

def test_booking_room_duplicate_booking(client: client):
    post = client.post(
            "/api/v1/booking/booking_room",
            headers=HEADER,
            json={
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "checkin": "2026-09-03T10:00:00",
                "checkout": "2026-09-12T10:00:00",
                "numHuespedes": 2
            }
        )
    post_2 = client.post(
            "/api/v1/booking/booking_room",
            headers=HEADER,
            json={
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "checkin": "2026-09-03T10:00:00",
                "checkout": "2026-09-12T10:00:00",
                "numHuespedes": 2
            }
        )
    assert post_2.status_code == 409

def test_booking_room_invalid_date_Range(client: client):
    post = client.post(
            "/api/v1/booking/booking_room",
            headers=HEADER,
            json={
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "checkin": "2024-09-03T10:00:00",
                "checkout": "2026-09-12T10:00:00",
                "numHuespedes": 2
            }
        )
    assert post.status_code == 400

def test_booking_room_date_validation_exception(client: client):
    post = client.post(
            "/api/v1/booking/booking_room",
            headers=HEADER,
            json={
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "checkin": "2026-09-03T10:00:00",
                "checkout": "2024-09-12T10:00:00",
                "numHuespedes": 2
            }
        )
    assert post.status_code == 400

def test_booking_room_not_exist(client: client):
    post = client.post(
            "/api/v1/booking/booking_room",
            headers=HEADER,
            json={
                "habitacionId": "mock",
                "checkin": "2026-09-03T10:00:00",
                "checkout": "2026-09-12T10:00:00",
                "numHuespedes": 2
            }
        )
    assert post.status_code == 404

def test_booking_user_not_exist(client: client):
    post = client.post(
            "/api/v1/booking/booking_room",
            json={
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "checkin": "2026-09-03T10:00:00",
                "checkout": "2026-09-12T10:00:00",
                "numHuespedes": 2
            }
        )
    assert post.status_code == 404

def test_booking_room_already_booked(client: client):
    post = client.post(
            "/api/v1/booking/booking_room",
            headers=HEADER,
            json={
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "checkin": "2026-09-01T10:00:00",
                "checkout": "2026-09-03T10:00:00",
                "numHuespedes": 2
            }
        )
    assert post.status_code == 409

def test_booking_room_max_persons(client: client):
    post = client.post(
            "/api/v1/booking/booking_room",
            headers=HEADER,
            json={
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "checkin": "2026-09-10T10:00:00",
                "checkout": "2026-09-13T10:00:00",
                "numHuespedes": 400
            }
        )
    assert post.status_code == 422

def test_healthcheck(client: client):
    get = client.get(
        "/api/v1/booking/ping"
    )
    assert get.status_code == 200

def test_reviews_hotel(client: client):
    get = client.get(
        "/api/v1/booking/reviews_hotel?hotelId=11111111-1111-1111-1111-000000000011"
    )
    data = get.json()
    assert isinstance(data, list)
    assert len(data) == 2

def test_reviews_hotel_no_parrams(client: client):
    get = client.get(
        "/api/v1/booking/reviews_hotel"
    )
    assert get.status_code == 422


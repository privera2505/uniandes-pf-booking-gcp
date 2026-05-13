from typing import List
from datetime import date

from adapters.memory.booking_repository_memory import InMemoryBookingRepositoryAdapter
from domain.use_cases.booking_room_use_case import BookingRoomUseCase
from domain.use_cases.reviews_hotel_use_case import ReviewsHotelUseCase
from domain.use_cases.update_booking_status_use_case import UpdateBookingStatusUseCase
from domain.use_cases.get_bookings_use_case import GetBookingsUseCase

def test_booking_use_case():
    repo = InMemoryBookingRepositoryAdapter()
    uc = BookingRoomUseCase(repo)

    habitacion_id = "22222222-2222-2222-2222-000000000001"
    viajero_id = "44444444-4444-4444-4444-000000000001"
    checkin = date(2026, 9, 3)
    checkout = date(2026, 9, 12)
    num_huespedes = 2

    reserva = uc.execute(
        habitacionId=habitacion_id,
        viajeroId=viajero_id,
        checkin=checkin,
        checkout=checkout,
        numHuespedes=num_huespedes
    )

    assert reserva is not None
    assert isinstance(reserva, dict)

    # validar contenido
    assert "id" in reserva
    assert "viajeroId" in reserva
    assert "habitacionId" in reserva
    assert reserva["viajeroId"] == viajero_id
    assert reserva["habitacionId"] == habitacion_id
    assert reserva["numHuespedes"] == num_huespedes

def test_reviews_hotels():
    repo = InMemoryBookingRepositoryAdapter()
    uc = ReviewsHotelUseCase(repo)

    hotel_id = "11111111-1111-1111-1111-000000000011"

    reviews = uc.execute(hotelId=hotel_id)

    assert reviews is not None
    assert isinstance(reviews, list)
    assert len(reviews) == 2

    # validar contenido
    first = reviews[0]
    assert "id" in first
    assert "hotelId" in first
    assert "calificacion" in first
    assert first["hotelId"] == hotel_id

def test_update_booking():
    repo = InMemoryBookingRepositoryAdapter()
    uc = UpdateBookingStatusUseCase(repo)

    bookingId = "33333333-3333-3333-3333-000000000001"
    hotel_id = "11111111-1111-1111-1111-000000000011"
    userId = "123"
    status = "pendiente"

    reserva = uc.execute(bookingId=bookingId, status=status, hotelId=hotel_id, userId= userId)

    assert reserva is not None
    assert isinstance(reserva, dict)
    assert reserva["estado"] == status.upper()

def test_get_bookings():
    repo = InMemoryBookingRepositoryAdapter()
    uc = GetBookingsUseCase(repo)

    hotel_id = "11111111-1111-1111-1111-000000000011"
    moneda = "USD"

    get_bookings = uc.execute(hotel_id, moneda)

    assert get_bookings is not None
    assert isinstance(get_bookings, list)
import pytest

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from adapters.postgres.repository_adapter import (
    InBdBookingRepositoryAdapter
)

from adapters.postgres.models.models import (
    Habitacion,
    Reserva as ReservaSQL,
    Tarifa,
    Hotel,
    Resena as ResenaSQL
)

from domain.models.models import Reserva

from error import (
    ReservationDuplicated,
    RoomAlreadyBooked,
    RoomNotExist,
    RateNotAvailableException,
    MaxGuestsExceededException,
    BookingNotExist,
    NotAuthorized,
    RefundNotAllowed
)

# =========================================================
# FIXTURES
# =========================================================

@pytest.fixture
def mock_session():
    session = MagicMock()
    yield session


@pytest.fixture
def repo(mock_session):

    with patch(
        "adapters.postgres.repository_adapter.db1.get_session",
        return_value=mock_session
    ), patch(
        "adapters.postgres.repository_adapter.db1.get_engine"
    ):
        repo = InBdBookingRepositoryAdapter()
        yield repo


# =========================================================
# HELPERS
# =========================================================

@pytest.fixture
def room():
    return Habitacion(
        id="22222222-2222-2222-2222-000000000001",
        hotelId="11111111-1111-1111-1111-000000000011",
        tipo="Doble",
        categoria="Deluxe",
        capacidadMaxima=2,
        descripcion="Vista ciudad",
        imagenes=["img1.jpg"],
        tipo_habitacion="Deluxe",
        tipo_cama=["king"],
        tamano_habitacion="35m2",
        amenidades=["AC"]
    )


@pytest.fixture
def tarifa(room):
    return Tarifa(
        id="55555555-5555-5555-5555-000000000001",
        habitacionId=room.id,
        precioBase=100.0,
        moneda="EUR",
        fechaInicio=datetime(2024, 1, 1),
        fechaFin=datetime(2028, 1, 1),
        descuento=0.1
    )


@pytest.fixture
def reserva_existente(room):
    return ReservaSQL(
        id="33333333-3333-3333-3333-000000000001",
        codigo="CODE1",
        viajeroId="44444444-4444-4444-4444-000000000001",
        habitacionId=room.id,
        fechaCheckIn=datetime(2026, 9, 1),
        fechaCheckOut=datetime(2026, 9, 3),
        numHuespedes=2,
        estado="CONFIRMADA",
        subtotal=200,
        impuestos=40,
        total=240,
        moneda="EUR"
    )


@pytest.fixture
def hotel():
    return Hotel(
        id="11111111-1111-1111-1111-000000000011",
        nombre="Hotel del canto",
        direccion="Calle 123",
        ciudad="Madrid",
        pais="Spain",
        latitud=50.0755,
        longitud=14.4378,
        estrellas=5,
        pmsProveedor="Opera",
        activo=True,
        distancia="3 km del centro",
        acceso="Metro"
    )


# =========================================================
# TESTS BOOKING ROOM
# =========================================================

def test_booking_room_correct(
    repo,
    mock_session,
    room,
    tarifa
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        None,       # reserva duplicada
        room,       # habitación
        None,       # reserva existente
        tarifa      # tarifa
    ]

    def refresh_side_effect(obj):
        obj.id = "booking-id"

    mock_session.refresh.side_effect = refresh_side_effect

    result = repo.booking_room(
        habitacionId=room.id,
        viajeroId="user-id",
        checkin=datetime(2026, 9, 3),
        checkout=datetime(2026, 9, 12),
        numHuespedes=2
    )

    assert isinstance(result, Reserva)

    assert result.id == "booking-id"
    assert result.habitacionId == room.id
    assert result.estado == "PENDIENTE"

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_booking_room_duplicate_booking(
    repo,
    mock_session,
    reserva_existente
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        reserva_existente
    ]

    with pytest.raises(ReservationDuplicated):
        repo.booking_room(
            habitacionId="room-id",
            viajeroId="user-id",
            checkin=datetime(2026, 9, 3),
            checkout=datetime(2026, 9, 12),
            numHuespedes=2
        )

    mock_session.rollback.assert_called_once()


def test_booking_room_not_exist(
    repo,
    mock_session
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        None,   # reserva duplicada
        None    # habitación inexistente
    ]

    with pytest.raises(RoomNotExist):
        repo.booking_room(
            habitacionId="invalid-room",
            viajeroId="user-id",
            checkin=datetime(2026, 9, 3),
            checkout=datetime(2026, 9, 12),
            numHuespedes=2
        )


def test_booking_room_already_booked(
    repo,
    mock_session,
    room,
    reserva_existente
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        None,               # reserva duplicada
        room,               # habitación
        reserva_existente   # reserva existente
    ]

    with pytest.raises(RoomAlreadyBooked):
        repo.booking_room(
            habitacionId=room.id,
            viajeroId="user-id",
            checkin=datetime(2026, 9, 2),
            checkout=datetime(2026, 9, 5),
            numHuespedes=2
        )


def test_booking_room_max_guests(
    repo,
    mock_session,
    room
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        None,
        room,
        None
    ]

    with pytest.raises(MaxGuestsExceededException):
        repo.booking_room(
            habitacionId=room.id,
            viajeroId="user-id",
            checkin=datetime(2026, 9, 3),
            checkout=datetime(2026, 9, 12),
            numHuespedes=5
        )


def test_booking_room_no_rate(
    repo,
    mock_session,
    room
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        None,
        room,
        None,
        None
    ]

    with pytest.raises(RateNotAvailableException):
        repo.booking_room(
            habitacionId=room.id,
            viajeroId="user-id",
            checkin=datetime(2035, 9, 3),
            checkout=datetime(2035, 9, 12),
            numHuespedes=2
        )


# =========================================================
# TESTS REVIEWS
# =========================================================

def test_reviews_hotel(
    repo,
    mock_session
):

    review = ResenaSQL(
        id="review-id",
        viajeroId="traveler-id",
        hotelId="hotel-id",
        reservaId="booking-id",
        calificacion=5,
        comentario="Excelente",
        fecha=datetime.now(),
        verificada=True
    )

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.all.return_value = [
        review
    ]

    result = repo.reviews_hotel("hotel-id")

    assert len(result) == 1

    assert result[0].comentario == "Excelente"


# =========================================================
# TESTS UPDATE STATUS
# =========================================================

def test_update_booking_status_success(
    repo,
    mock_session,
    room,
    reserva_existente,
    hotel
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        reserva_existente,
        room,
        hotel
    ]

    result = repo.update_booking_status(
        bookingId=reserva_existente.id,
        status="PENDIENTE",
        hotelId=room.hotelId,
        userId="hotel-user"
    )

    assert result["estado"] == "PENDIENTE"

    mock_session.commit.assert_called_once()


def test_update_booking_not_exist(
    repo,
    mock_session
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.return_value = None

    with pytest.raises(BookingNotExist):
        repo.update_booking_status(
            bookingId="invalid-id",
            status="PENDIENTE",
            hotelId="hotel-id",
            userId="user-id"
        )


def test_update_booking_not_authorized(
    repo,
    mock_session,
    room,
    reserva_existente
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        reserva_existente,
        room
    ]

    with pytest.raises(NotAuthorized):
        repo.update_booking_status(
            bookingId=reserva_existente.id,
            status="PENDIENTE",
            hotelId="another-hotel",
            userId="user-id"
        )
# =========================================================
# TESTS GET BOOKINGS
# =========================================================

def test_get_bookings_success(
    repo,
    mock_session,
    reserva_existente,
    room,
    hotel
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.join.return_value = query_mock
    query_mock.outerjoin.return_value = query_mock
    query_mock.filter.return_value = query_mock

    query_mock.all.return_value = [
        (
            reserva_existente,
            room,
            hotel,
            "Pablo",
            "pablo@test.com"
        )
    ]

    result = repo.get_bookings(
        id_filter="44444444-4444-4444-4444-000000000001",
        moneda="USD"
    )

    assert len(result) == 1

    booking = result[0]

    assert booking.id == reserva_existente.id
    assert booking.nombreUser == "Pablo"
    assert booking.nombreHotel == hotel.nombre
    assert booking.moneda == "USD"


def test_get_bookings_empty(
    repo,
    mock_session
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.join.return_value = query_mock
    query_mock.outerjoin.return_value = query_mock
    query_mock.filter.return_value = query_mock

    query_mock.all.return_value = []

    result = repo.get_bookings(
        id_filter="user-id",
        moneda="USD"
    )

    assert result == []


def test_get_bookings_without_user_name(
    repo,
    mock_session,
    reserva_existente,
    room,
    hotel
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.join.return_value = query_mock
    query_mock.outerjoin.return_value = query_mock
    query_mock.filter.return_value = query_mock

    query_mock.all.return_value = [
        (
            reserva_existente,
            room,
            hotel,
            None,
            None
        )
    ]

    result = repo.get_bookings(
        id_filter="user-id",
        moneda="EUR"
    )

    assert len(result) == 1

    assert result[0].nombreUser == "Sin nombre"


# =========================================================
# TESTS UPDATE STATUS EXTRA
# =========================================================

def test_update_booking_room_not_exist(
    repo,
    mock_session,
    reserva_existente
):

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        reserva_existente,
        None
    ]

    with pytest.raises(RoomNotExist):
        repo.update_booking_status(
            bookingId=reserva_existente.id,
            status="PENDIENTE",
            hotelId="hotel-id",
            userId="user-id"
        )


def test_update_booking_cancel_paid_future_booking(
    repo,
    mock_session,
    room,
    hotel
):

    reserva_pagada = ReservaSQL(
        id="booking-id",
        codigo="CODE1",
        viajeroId="traveler-id",
        habitacionId=room.id,
        fechaCheckIn=datetime(2030, 1, 1, tzinfo=timezone.utc),
        fechaCheckOut=datetime(2030, 1, 5, tzinfo=timezone.utc),
        numHuespedes=2,
        estado="PAGADA",
        subtotal=100,
        impuestos=20,
        total=120,
        moneda="EUR"
    )

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        reserva_pagada,
        room,
        hotel
    ]

    result = repo.update_booking_status(
        bookingId="booking-id",
        status="CANCELADA",
        hotelId=None,
        userId="traveler-id"
    )

    assert result["estado"] == "REEMBOLSANDO"


def test_update_booking_confirm_paid_booking(
    repo,
    mock_session,
    room,
    hotel
):

    reserva_pagada = ReservaSQL(
        id="booking-id",
        codigo="CODE1",
        viajeroId="traveler-id",
        habitacionId=room.id,
        fechaCheckIn=datetime(2030, 1, 1),
        fechaCheckOut=datetime(2030, 1, 5),
        numHuespedes=2,
        estado="PAGADA",
        subtotal=100,
        impuestos=20,
        total=120,
        moneda="EUR"
    )

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        reserva_pagada,
        room,
        hotel
    ]

    result = repo.update_booking_status(
        bookingId="booking-id",
        status="CONFIRMADA",
        hotelId=room.hotelId,
        userId="hotel-user"
    )

    assert result["estado"] == "PAGADA"


def test_update_booking_refund_not_allowed(
    repo,
    mock_session,
    room,
    hotel
):

    reserva_pagada = ReservaSQL(
        id="booking-id",
        codigo="CODE1",
        viajeroId="traveler-id",
        habitacionId=room.id,
        fechaCheckIn=datetime(2020, 1, 1, tzinfo=timezone.utc),
        fechaCheckOut=datetime(2020, 1, 5, tzinfo=timezone.utc),
        numHuespedes=2,
        estado="PAGADA",
        subtotal=100,
        impuestos=20,
        total=120,
        moneda="EUR"
    )

    query_mock = MagicMock()

    mock_session.query.return_value = query_mock

    query_mock.filter.return_value.first.side_effect = [
        reserva_pagada,
        room,
        hotel
    ]

    with pytest.raises(RefundNotAllowed):
        repo.update_booking_status(
            bookingId="booking-id",
            status="CANCELADA",
            hotelId=None,
            userId="traveler-id"
        )
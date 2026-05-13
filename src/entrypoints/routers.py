from fastapi import APIRouter, Depends, HTTPException, Request, Query
from datetime import date

from typing import Optional

from domain.models.models import Reserva, BookingRequest, ReviewsRequest, Resena, UpdateBookingStatusRequest, Currency
from domain.ports.booking_repository_port import BookingRepositoryPort

from error import (
    BookingNotExist,
    InvalidDateRangeException,
    BookingDateValidationException,
    MaxGuestsExceededException,
    NotAuthorized,
    RateNotAvailableException,
    RefundNotAllowed,
    ReservationDuplicated,
    RoomAlreadyBooked,
    RoomNotExist,
    UserNotExist
    )

import json

from entrypoints.assembly import build_booking_repository
from utils.currency_check import currency_dep
from utils.decode import get_current_user_id, get_id_filter, get_current_hotel_id
from utils.kakfa_producer import publish_sync_command


def repo_dep() -> BookingRepositoryPort:
    return build_booking_repository()

router = APIRouter()

@router.post("/booking_room", response_model=Reserva, status_code=200)
def book_room(request: BookingRequest, user_id: str = Depends(get_current_user_id), repo: BookingRepositoryPort = Depends(repo_dep)):
    today = date.today()
    try:
        if request.checkin.date()<today:
            raise BookingDateValidationException()
        if request.checkin.date()>=request.checkout.date():
            raise InvalidDateRangeException()
        book_room = repo.booking_room(
            request.habitacionId,
            user_id,
            request.checkin.date(),
            request.checkout.date(),
            request.numHuespedes)
        return book_room
    except InvalidDateRangeException:
        raise HTTPException(400, "the check-in date is later than the check-out date")
    except RateNotAvailableException:
        raise HTTPException(404, "No existe tarifa para la habitación en ese periodo")
    except BookingDateValidationException:
        raise HTTPException(400, "the check-in date is lower than today")
    except RoomNotExist:
        raise HTTPException(404, "El recurso habitación no existe.")
    except UserNotExist:
        raise HTTPException(404, "El recurso usuario no existe.")
    except ReservationDuplicated:
        raise HTTPException(409, "Reserva Duplicada")
    except RoomAlreadyBooked:
        raise HTTPException(409, "La solicitud entra en conflicto con estado actual (ocupada).")
    except MaxGuestsExceededException:
        raise HTTPException(422, "NumGuest supera maxGuest")

@router.get("/reviews_hotel", response_model=list[Resena], status_code=200)
def reviews_hotel(hotelId: str, repo: BookingRepositoryPort = Depends(repo_dep)):
    try:
        query = repo.reviews_hotel(hotelId)
        return query
    except Exception:
        raise HTTPException(500, "Servicio caido")

@router.get("/get_bookings")
def get_bookings(
    id_filter: str = Depends(get_id_filter),
    moneda: Currency = Depends(currency_dep),
    name:  Optional[str] = Query(None),
    bookingId: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    checkin: Optional[date] = Query(None),
    checkout: Optional[date] = Query(None),
    repo: BookingRepositoryPort = Depends(repo_dep)):
    try:
        print(email)
        bookings = repo.get_bookings(id_filter, moneda, name, bookingId, email, status, checkin, checkout)
        return bookings
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Servicio caido: {str(e)}"
        )

@router.get("/ping")
def health_check():
    return "pong"

@router.patch("/update/{booking_id}")
def update_booking(
    booking_id: str,
    status: UpdateBookingStatusRequest,
    hotelId: str = Depends(get_current_hotel_id),
    userId: str = Depends(get_current_user_id),
    repo: BookingRepositoryPort = Depends(repo_dep)
):
    try:
        print(hotelId)
        print(userId)
        reserva: Reserva = repo.update_booking_status(booking_id, status.status, hotelId, userId)
        if reserva["estado"] == "REEMBOLSANDO":
            process_event_and_publish(reserva)
        return reserva
    except BookingNotExist:
        raise HTTPException(
            404,
            "Reserva no encontrada"
        )
    except RoomNotExist:
        raise HTTPException(
            404,
            "Habitacion no encontrada"
        )
    except NotAuthorized:
        raise HTTPException(
            403,
            "No autorizado para modificar esta reserva"
        )
    except RefundNotAllowed:
        raise HTTPException(
            400,
            "No se puede solicitar reembolso el día del check-in ni después"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Servicio caido: {str(e)}"
        )

def process_event_and_publish(reserva: Reserva):
    publish_sync_command(reserva["id"], json.dumps(reserva, default=str))
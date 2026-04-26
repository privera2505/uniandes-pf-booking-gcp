from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import date

from domain.models.models import Reserva, BookingRequest, ReviewsRequest, Resena
from domain.ports.booking_repository_port import BookingRepositoryPort

from error import (
    InvalidDateRangeException,
    BookingDateValidationException,
    MaxGuestsExceededException,
    RateNotAvailableException,
    ReservationDuplicated,
    RoomAlreadyBooked,
    RoomNotExist,
    UserNotExist
    )

from entrypoints.assembly import build_booking_repository
from utils.decode import get_current_user_id


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
    except: 
        pass

@router.get("/ping")
def health_check():
    return "pong"

@router.post("/debug_header")
def debug_header(request: Request):
    return {
        "headers": dict(
            request.headers
        )
    }
from fastapi import APIRouter, Depends, HTTPException
from datetime import date

from domain.models.models import Reserva, BookingRequest, ReviewsRequest, Resena
from domain.ports.booking_repository_port import BookingRepositoryPort

from error import (
    InvalidDateRangeException,
    BookingDateValidationException,
    MaxGuestsExceededException,
    RoomAlreadyBooked,
    RoomNotExist,
    UserNotExist
    )

from entrypoints.assembly import build_booking_repository


def repo_dep() -> BookingRepositoryPort:
    return build_booking_repository()

router = APIRouter()

@router.post("/booking_room", response_model=Reserva, status_code=200)
def book_room(request: BookingRequest, repo: BookingRepositoryPort = Depends(repo_dep)):
    today = date.today()
    try:
        if request.checkin.date()<today:
            raise BookingDateValidationException()
        if request.checkin.date()>=request.checkout.date():
            raise InvalidDateRangeException()
        book_room = repo.booking_room(
            request.habitacionId,
            request.viajeroId,
            request.checkin.date(),
            request.checkout.date(),
            request.numHuespedes)
        return book_room
    except InvalidDateRangeException:
        raise HTTPException(400, "the check-in date is later than the check-out date")
    except BookingDateValidationException:
        raise HTTPException(400, "the check-in date is lower than today")
    except RoomNotExist:
        raise HTTPException(404, "El recurso habitación no existe.")
    except UserNotExist:
        raise HTTPException(404, "El recurso usuario no existe.")
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
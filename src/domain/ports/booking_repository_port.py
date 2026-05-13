from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain.models.models import Reserva, Resena, VerReservas


class BookingRepositoryPort(ABC):
    """Booking repository interface."""

    @abstractmethod
    def booking_room(self, habitacionId: str, viajeroId: str, checkin: date,  checkout: date, numHuespedes: int) -> Reserva:
        """Create a booking for a room."""
        pass

    @abstractmethod
    def reviews_hotel(self, hotelId: str) -> list[Resena]:
        """Return a list of reviews for a hotel."""
        pass

    @abstractmethod
    def get_bookings(self, 
        id_filter: str,
        moneda: str,
        name:  Optional[str] = None,
        bookingId: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        checkin: Optional[date] = None,
        checkout: Optional[date] = None,
        ) -> list[VerReservas]:
        """Return a list of booking"""
        pass

    @abstractmethod
    def update_booking_status(self,
        bookingId: str,
        status: str,
        hotelId: Optional[str],
        userId: Optional[str]
    ) -> Reserva:
        """Update a booking request for the hotel"""
        pass
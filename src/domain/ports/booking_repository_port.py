from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain.models.models import Reserva, Resena


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
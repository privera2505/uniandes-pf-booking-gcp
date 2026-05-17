from domain.ports.booking_repository_port import BookingRepositoryPort
from domain.use_cases.base_use_case import BaseUseCase

from typing import Optional

from datetime import date

from domain.models.models import VerReservas

class GetBookingsUseCase(BaseUseCase):
    """Use case for book a room."""

    def __init__(self, booking_repository: BookingRepositoryPort):
        self.booking_repository = booking_repository
    
    def execute(
            self, 
            id_filter: str,
            moneda: str,
            name:  Optional[str] = None,
            bookingId: Optional[str] = None,
            email: Optional[str] = None,
            status: Optional[str] = None,
            checkin: Optional[date] = None,
            checkout: Optional[date] = None
            ) -> list[VerReservas]:
        return self.booking_repository.get_bookings(id_filter, moneda, name, bookingId, email, status, checkin, checkout)
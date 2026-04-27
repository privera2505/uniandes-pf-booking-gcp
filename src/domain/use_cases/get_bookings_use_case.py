from domain.ports.booking_repository_port import BookingRepositoryPort
from domain.use_cases.base_use_case import BaseUseCase

from datetime import date

from domain.models.models import VerReservas

class GetBookingsUseCase(BaseUseCase):
    """Use case for book a room."""

    def __init__(self, booking_repository: BookingRepositoryPort):
        self.booking_repository = booking_repository
    
    def execute(self, id_filter: str) -> list[VerReservas]:
        return self.booking_repository.get_bookings(id_filter)
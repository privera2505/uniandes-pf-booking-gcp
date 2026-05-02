from domain.ports.booking_repository_port import BookingRepositoryPort
from domain.use_cases.base_use_case import BaseUseCase

from domain.models.models import Reserva

class UpdateBookingStatusUseCase(BaseUseCase):
    """Use case for Reviews for a Hotel"""

    def __init__(self, booking_repository: BookingRepositoryPort):
        self.booking_repository = booking_repository
    
    def execute(
        self,         
        bookingId: str,
        status: str,
        hotelId: str) -> Reserva:
        return self.booking_repository.update_booking_status(bookingId, status, hotelId)
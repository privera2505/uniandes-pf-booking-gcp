from domain.ports.booking_repository_port import BookingRepositoryPort
from domain.use_cases.base_use_case import BaseUseCase

from datetime import date

from domain.models.models import Reserva

class BookingRoomUseCase(BaseUseCase):
    """Use case for book a room."""

    def __init__(self, booking_repository: BookingRepositoryPort):
        self.booking_repository = booking_repository
    
    def execute(self, habitacionId: str, viajeroId: str, checkin: date,  checkout: date, numHuespedes: int) -> Reserva:
        return self.booking_repository.booking_room(habitacionId, viajeroId, checkin, checkout, numHuespedes)
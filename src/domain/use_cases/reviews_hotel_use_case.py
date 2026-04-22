from domain.ports.booking_repository_port import BookingRepositoryPort
from domain.use_cases.base_use_case import BaseUseCase

from domain.models.models import Resena

class ReviewsHotelUseCase(BaseUseCase):
    """Use case for Reviews for a Hotel"""

    def __init__(self, booking_repository: BookingRepositoryPort):
        self.booking_repository = booking_repository
    
    def execute(self, hotelId: str) -> list[Resena]:
        return self.booking_repository.reviews_hotel(hotelId)
# Implementaciones
from adapters.memory.booking_repository_memory import InMemoryBookingRepositoryAdapter
from domain.ports.booking_repository_port import BookingRepositoryPort
from config import REPOSITORY_IMPL


def build_booking_repository() -> BookingRepositoryPort:
    if REPOSITORY_IMPL == "postgres":
        return
    return InMemoryBookingRepositoryAdapter()
# Implementaciones
from adapters.memory.booking_repository_memory import InMemoryBookingRepositoryAdapter
from adapters.postgres.repository_adapter import InBdBookingRepositoryAdapter
from domain.ports.booking_repository_port import BookingRepositoryPort
from config import REPOSITORY_IMPL

_memory_repo = InMemoryBookingRepositoryAdapter()

def build_booking_repository() -> BookingRepositoryPort:
    if REPOSITORY_IMPL == "postgres":
        return InBdBookingRepositoryAdapter()
    return _memory_repo
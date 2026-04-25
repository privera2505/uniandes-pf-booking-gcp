from adapters.postgres.models.models import Base
from adapters.postgres.declarative_base import db1
from domain.ports.booking_repository_port import BookingRepositoryPort
from domain.models.models import Reserva, Resena

from sqlalchemy import func, select, exists

from math import ceil

from adapters.postgres.models.models import Resena, Reserva, Habitacion, Tarifa
from error import RoomNotFound, RoomNotHavefee


class InBdSearchRepositoryAdapter(BookingRepositoryPort):
    "In BD Implementation of BookingRepository"

    def __init__(self):
        Base.metadata.create_all(db1.get_engine())
    
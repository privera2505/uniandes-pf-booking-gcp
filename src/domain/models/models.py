from pydantic import BaseModel

from datetime import datetime

class Reserva(BaseModel):
    id: str | None = None
    codigo: str
    viajeroId: str
    habitacionId: str
    fechaCheckIn: datetime
    fechaCheckOut: datetime
    numHuespedes: int
    estado: str
    subtotal: float
    impuestos: float
    total: float
    moneda: str

class Resena(BaseModel):
    id: str | None = None
    viajeroId: str
    calificacion: int
    comentario: str
    fecha: datetime
    verificada: bool

class Tarifa(BaseModel):
    id: str | None = None
    HabitacionId: str
    precioBase: float
    moneda: str
    fechaInicio: datetime
    fechaFin: datetime
    descuento: float

class Habitacion(BaseModel):
    id: str | None = None
    hotelId: str
    tipo: str
    categoria: str
    capacidadMaxima: int
    descripcion: str
    imagenes: list[str]
    tipo_habitacion: str
    tipo_cama: list[str]
    tamano_habitacion: str
    amenidades: list[str]

class BookingRequest(BaseModel):
    habitacionId: str
    viajeroId: str
    checkin: datetime
    checkout: datetime
    numHuespedes: int

class ReviewsRequest(BaseModel):
    hotelId: str
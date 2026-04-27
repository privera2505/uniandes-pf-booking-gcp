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

class Hotel(BaseModel):
    id: str | None = None
    nombre: str
    direccion: str
    ciudad: str
    pais: str
    latitud: float
    longitud: float
    estrellas: int
    pmsProveedor: str
    activo: bool
    distancia: str
    acceso: str

class VerReservas(BaseModel):
    id: str
    nombreUser:str
    descripcion: str
    numHuespedes: int
    fechaCheckIn: datetime
    fechaCheckOut: datetime
    estado: str
    nombreHotel: str
    direccion: str
    ciudad: str
    pais: str
    latitud: float
    longitud: float
    estrellas: int
    distancia: str
    acceso: str
    tipo: str
    categoria: str    
    imagenes: list[str]
    tipo_habitacion: str
    tipo_cama: list[str]
    tamano_habitacion: str
    amenidades: list[str]
    subtotal: float
    impuestos: float
    total: float

class Users(BaseModel):
    id: str
    nombre: str

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
    checkin: datetime
    checkout: datetime
    numHuespedes: int

class ReviewsRequest(BaseModel):
    hotelId: str
import uuid

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Float, Integer, Boolean, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Reserva(Base):
    __tablename__ = "reserva"
    __mapper_args__ = {"confirm_deleted_rows": False}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo = Column(String, nullable=False, unique=True)
    viajeroId = Column(String, nullable=False)
    habitacionId = Column(String(36), ForeignKey("habitacion.id"), nullable=False)
    fechaCheckIn = Column(DateTime(timezone=True), nullable=False)
    fechaCheckOut = Column(DateTime(timezone=True), nullable=False)
    numHuespedes = Column(Integer, nullable=False)
    estado = Column(String, nullable=False)
    subtotal = Column(Float, nullable=False)
    impuestos = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    moneda = Column(String, nullable=False)
    
    __table_args__ = (
        Index("idx_reserva_habitacion_fechas", "habitacionId", "fechaCheckIn", "fechaCheckOut"),
    )

class Tarifa(Base):
    __tablename__ = "tarifa"
    __mapper_args__ = {"confirm_deleted_rows": False}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    habitacionId = Column(String(36), ForeignKey("habitacion.id"), nullable=False)
    precioBase = Column(Float, nullable=False)
    moneda = Column(String, nullable=False)
    fechaInicio = Column(DateTime(timezone=True), nullable=False)
    fechaFin = Column(DateTime(timezone=True), nullable=False)
    descuento = Column(Float, nullable=False)
    
    __table_args__ = (
        Index("idx_tarifa_habitacion_fecha", "habitacionId", "fechaInicio", "fechaFin"),
    )

class Resena(Base):
    __tablename__ = "resena"
    __mapper_args__ = {"confirm_deleted_rows": False}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    viajeroId = Column(String, nullable=False)
    hotelId = Column(String, nullable=False)
    reservaId = Column(String(36), ForeignKey("reserva.id"), nullable=False)
    calificacion = Column(Integer, nullable=False)
    comentario = Column(String, nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False)
    verificada = Column(Boolean, nullable=False)

    __table_args__ = (
        Index("idx_resena_hotel", "hotelId"),
    )

class Habitacion(Base):
    __tablename__ = "habitacion"
    __mapper_args__ = {"confirm_deleted_rows": False}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hotelId = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    capacidadMaxima = Column(Integer, nullable=False)
    descripcion = Column(String, nullable=False)
    imagenes = Column(JSON, nullable=False)
    tipo_habitacion = Column(String, nullable=False)
    tipo_cama = Column(JSON, nullable=False)
    tamano_habitacion = Column(String, nullable=False)
    amenidades = Column(JSON, nullable=False)

    __table_args__ = (
        Index("idx_habitacion_hotel", "hotelId"),
    )
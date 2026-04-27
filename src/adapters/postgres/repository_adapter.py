from adapters.postgres.models.models import Base
from adapters.postgres.declarative_base import db1
from domain.ports.booking_repository_port import BookingRepositoryPort
from domain.models.models import Reserva, Resena, VerReservas

from sqlalchemy import and_, func, select, exists, or_

from math import ceil

from adapters.postgres.models.models import Habitacion, Reserva as ReservaSQL, Tarifa, Resena as ResenaSQL, Hotel, User
from error import MaxGuestsExceededException, RateNotAvailableException, ReservationDuplicated, RoomAlreadyBooked, RoomNotExist
from utils.to_utc import to_utc
from utils.reservation_code import generate_reservation_code

class InBdBookingRepositoryAdapter(BookingRepositoryPort):
    "In BD Implementation of BookingRepository"

    def __init__(self):
        Base.metadata.create_all(db1.get_engine())
    
    def booking_room(self, habitacionId, viajeroId, checkin, checkout, numHuespedes) -> Reserva:
        db = db1.get_session()
        noches = (checkout-checkin).days
        try:
            #Verifica reserva Duplicada
            codigo = generate_reservation_code(viajeroId, habitacionId, checkin, checkout)
            reserva_duplicada = (
                db.query(ReservaSQL)
                .filter(ReservaSQL.codigo == codigo)
                .first()
            )
            if reserva_duplicada:
                raise ReservationDuplicated()

            #Validación habitacion
            habitacion = (
                db.query(Habitacion)
                .filter(Habitacion.id == habitacionId)
                .first()
            )
            if not habitacion:
                raise RoomNotExist()
            
            #Vaidar reservas en fechas
            reserva_existente = (
                db.query(ReservaSQL)
                .filter(
                    ReservaSQL.habitacionId == habitacionId,
                    ReservaSQL.estado == "CONFIRMADA",
                    and_(
                        checkin < ReservaSQL.fechaCheckOut,
                        checkout > ReservaSQL.fechaCheckIn
                    )
                )
                .first()
            )
            if reserva_existente:
                raise RoomAlreadyBooked()
            
            #Validar número de huespedes
            if numHuespedes > habitacion.capacidadMaxima:
                raise MaxGuestsExceededException()
            
            #Validar tarifa disponible
            tarifa = (
                db.query(Tarifa)
                .filter(
                    Tarifa.habitacionId == habitacionId,
                    Tarifa.fechaInicio <= checkin,
                    Tarifa.fechaFin >= checkout
                )
                .first()
            )

            if not tarifa:
                raise RateNotAvailableException()
            
            #Calculos

            precio_base = tarifa.precioBase
            descuento = tarifa.descuento

            subtotal = precio_base * noches * (1-descuento)
            impuesto = subtotal * 0.2

            #Crear reserva
            nueva_reserva = ReservaSQL(
                codigo=codigo,
                viajeroId=viajeroId,
                habitacionId=habitacionId,
                fechaCheckIn=checkin,
                fechaCheckOut=checkout,
                numHuespedes=numHuespedes,
                estado="PENDIENTE",
                subtotal=subtotal,
                impuestos=impuesto,
                total=subtotal + impuesto,
                moneda=tarifa.moneda
            )

            #Persistir en base de datos
            db.add(nueva_reserva)
            db.commit()
            db.refresh(nueva_reserva)
            return Reserva(
                    id=nueva_reserva.id,
                    codigo=nueva_reserva.codigo,
                    viajeroId=nueva_reserva.viajeroId,
                    habitacionId=nueva_reserva.habitacionId,
                    fechaCheckIn=nueva_reserva.fechaCheckIn,
                    fechaCheckOut=nueva_reserva.fechaCheckOut,
                    numHuespedes=nueva_reserva.numHuespedes,
                    estado=nueva_reserva.estado,
                    subtotal=nueva_reserva.subtotal,
                    impuestos=nueva_reserva.impuestos,
                    total=nueva_reserva.total,
                    moneda=nueva_reserva.moneda
                )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def reviews_hotel(self, hotelId) -> list[Resena]:
        db = db1.get_session()
        try:
            resenas = (
                db.query(ResenaSQL)
                .filter(ResenaSQL.hotelId == hotelId)
                .all()
            )
            return [
                    Resena(
                        id=r.id,
                        viajeroId=r.viajeroId,
                        hotelId=r.hotelId,
                        reservaId=r.reservaId,
                        calificacion=r.calificacion,
                        comentario=r.comentario,
                        fecha=r.fecha,
                        verificada=r.verificada
                    )
                    for r in resenas
                ]
        finally:
            db.close()
    
    def get_bookings(self, id_filter):
        db = db1.get_session()

        try:
            rows = (
                db.query(
                    ReservaSQL,
                    Habitacion,
                    Hotel,
                    User.name.label("nombre_user")
                )
                .join(
                    Habitacion,
                    Habitacion.id == ReservaSQL.habitacionId
                )
                .join(
                    Hotel,
                    Hotel.id == Habitacion.hotelId
                )
                .outerjoin(
                    User,
                    User.id == ReservaSQL.viajeroId
                )
                .filter(
                    or_(
                        ReservaSQL.viajeroId == id_filter,
                        Hotel.id == id_filter
                    )
                )
                .all()
            )

            return [
                VerReservas(
                    id=reserva.id,
                    nombreUser=nombre_user or "Sin nombre",
                    descripcion=habitacion.descripcion,
                    numHuespedes=reserva.numHuespedes,
                    fechaCheckIn=reserva.fechaCheckIn,
                    fechaCheckOut=reserva.fechaCheckOut,
                    estado=reserva.estado,
                    subtotal=reserva.subtotal,
                    impuestos=reserva.impuestos,
                    total=reserva.total,

                    nombreHotel=hotel.nombre,
                    direccion=hotel.direccion,
                    ciudad=hotel.ciudad,
                    pais=hotel.pais,
                    latitud=hotel.latitud,
                    longitud=hotel.longitud,
                    estrellas=hotel.estrellas,
                    distancia=hotel.distancia,
                    acceso=hotel.acceso,

                    tipo=habitacion.tipo,
                    categoria=habitacion.categoria,
                    imagenes=habitacion.imagenes,
                    tipo_habitacion=habitacion.tipo_habitacion,
                    tipo_cama=habitacion.tipo_cama,
                    tamano_habitacion=habitacion.tamano_habitacion,
                    amenidades=habitacion.amenidades
                )
                for reserva, habitacion, hotel, nombre_user in rows
            ]

        finally:
            db.close()
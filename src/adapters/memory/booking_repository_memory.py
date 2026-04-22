from typing import Dict
from datetime import date, datetime
from uuid import uuid4

from domain.models.models import Resena, Tarifa, Reserva, Habitacion
from domain.ports.booking_repository_port import BookingRepositoryPort
from error import RateNotAvailableException, RoomAlreadyBooked, RoomNotExist, UserNotExist, MaxGuestsExceededException


class InMemoryBookingRepositoryAdapter(BookingRepositoryPort):
    def __init__(self) -> None:
        self._reserva: Dict[str, Reserva] = {
            "33333333-3333-3333-3333-000000000001": {
                "id": "33333333-3333-3333-3333-000000000001",
                "codigo": "CODE1",
                "viajeroId": "44444444-4444-4444-4444-000000000001",
                "habitacionId": "22222222-2222-2222-2222-000000000001",
                "fechaCheckIn": datetime(2026, 9, 1, 15, 0),
                "fechaCheckOut": datetime(2026, 9, 3, 10, 0),
                "numHuespedes": 2,
                "estado": "CONFIRMADA",
                "subtotal": 200.0,
                "impuestos": 40.0,
                "total": 240.0,
                "moneda": "EUR"
            },
            "33333333-3333-3333-3333-000000000002": {
                "id": "33333333-3333-3333-3333-000000000002",
                "codigo": "CODE1",
                "viajeroId": "44444444-4444-4444-4444-000000000002",
                "habitacionId": "22222222-2222-2222-2222-000000000003",
                "fechaCheckIn": datetime(2026, 8, 1, 15, 0),
                "fechaCheckOut": datetime(2026, 8, 3, 10, 0),
                "numHuespedes": 2,
                "estado": "CONFIRMADA",
                "subtotal": 200.0,
                "impuestos": 40.0,
                "total": 240.0,
                "moneda": "EUR"
            }
        }
        self._tarifa: Dict[str, Tarifa] = {
            "55555555-5555-5555-5555-000000000001": {
                "id": "55555555-5555-5555-5555-000000000001",
                "HabitacionId": "22222222-2222-2222-2222-000000000001",
                "precioBase": 100.0,
                "moneda": "EUR",
                "fechaInicio": datetime(2024, 4, 1),
                "fechaFin": datetime(2028, 4, 30),
                "descuento": 0.1
            },
            "55555555-5555-5555-5555-000000000003": {
                "id": "55555555-5555-5555-5555-000000000003",
                "HabitacionId": "22222222-2222-2222-2222-000000000003",
                "precioBase": 80.0,
                "moneda": "EUR",
                "fechaInicio": datetime(2024, 4, 1),
                "fechaFin": datetime(2028, 4, 30),
                "descuento": 0.0
            }
        }
        self._resenas: Dict[str, Resena] = {
            "66666666-6666-6666-6666-000000000001": {
                "id": "66666666-6666-6666-6666-000000000001",
                "viajeroId": "77777777-7777-7777-7777-000000000001",
                "hotelId": "11111111-1111-1111-1111-000000000011",
                "reservaId": "33333333-3333-3333-3333-000000000001",
                "calificacion": 4,
                "comentario": "Buena",
                "fecha": datetime(2024, 4, 1),
                "verificada": True
            },
            "66666666-6666-6666-6666-000000000002": {
                "id": "66666666-6666-6666-6666-000000000002",
                "viajeroId": "77777777-7777-7777-7777-000000000001",
                "hotelId": "11111111-1111-1111-1111-000000000011",
                "reservaId": "33333333-3333-3333-3333-000000000002",
                "calificacion": 3,
                "comentario": "Buena",
                "fecha": datetime(2024, 4, 1),
                "verificada": True
            }
        }

        self._habitacion: Dict[str, Habitacion] = {
            "22222222-2222-2222-2222-000000000001": {
                "id": "22222222-2222-2222-2222-000000000001",
                "hotelId": "11111111-1111-1111-1111-000000000011",
                "tipo": "Doble",
                "categoria": "Deluxe",
                "capacidadMaxima": 2,
                "descripcion": "Vista ciudad",
                "imagenes": ["img1.jpg"],
                "tipo_habitacion": "Deluxe",
                "tipo_cama": ["king"],
                "tamano_habitacion": "35m2",
                "amenidades": ["AC", "IDK"]
            },
            "22222222-2222-2222-2222-000000000003": {
                "id": "22222222-2222-2222-2222-000000000003",
                "hotelId": "11111111-1111-1111-1111-000000000002",
                "tipo": "Doble",
                "categoria": "Deluxe",
                "capacidadMaxima": 2,
                "descripcion": "Vista ciudad",
                "imagenes": ["img1.jpg"],
                "tipo_habitacion": "Deluxe",
                "tipo_cama": ["king"],
                "tamano_habitacion": "35m2",
                "amenidades": ["AC", "IDK"]
            }
        }

        self._viajero: Dict[str, dict] = {
            "44444444-4444-4444-4444-000000000001": {
                "test": "test"
            },
            "44444444-4444-4444-4444-000000000002": {
                "test": "test"
            }
        }

    def booking_room(self, habitacionId: str, viajeroId: str, checkin: date,  checkout: date, numHuespedes: int) -> Reserva:
        noches = (checkout - checkin).days
        #Validar existencia de habitacion
        if habitacionId not in self._habitacion:
            raise RoomNotExist()
        #Validad existecion de usuario
        if viajeroId not in self._viajero:
            raise UserNotExist()
        #Validar que no hay reservas creadas
        for reserva in self._reserva.values():
            if reserva["habitacionId"] == habitacionId and reserva["estado"] == "CONFIRMADA":
                reserva_checkin = reserva["fechaCheckIn"].date()
                reserva_checkout = reserva["fechaCheckOut"].date()

                # Si los rangos se cruzan
                if checkin < reserva_checkout and checkout > reserva_checkin:
                    raise RoomAlreadyBooked()
        #Validar que los huespedes si caben en la habitación
        info_habitacion = self._habitacion[habitacionId]
        if numHuespedes > info_habitacion["capacidadMaxima"]:
            raise MaxGuestsExceededException()
        #Validar que exista tarifa vigente para la habitación en ese rango
        tarifa_encontrada = None

        for tarifa in self._tarifa.values():
            if tarifa["HabitacionId"] == habitacionId:

                fecha_inicio = tarifa["fechaInicio"].date()
                fecha_fin = tarifa["fechaFin"].date()

                # La tarifa cubre toda la estadía
                if checkin >= fecha_inicio and checkout <= fecha_fin:
                    tarifa_encontrada = tarifa
                    break

        if tarifa_encontrada is None:
            raise RateNotAvailableException()
        
        precio_base = tarifa_encontrada["precioBase"]
        descuento = tarifa_encontrada["descuento"]

        subtotal = precio_base * noches * (1 - descuento)

        impuesto = subtotal * 0.2

        #Crear reserva
        nueva_reserva: Reserva = {
            "id": str(uuid4()),
            "codigo": "Codigo123",
            "viajeroId": viajeroId,
            "habitacionId": habitacionId,
            "fechaCheckIn": checkin,
            "fechaCheckOut": checkout,
            "numHuespedes": numHuespedes,
            "estado": "PENDIENTE",
            "subtotal": subtotal,
            "impuestos": impuesto,
            "total": subtotal + impuesto,
            "moneda": tarifa_encontrada["moneda"]
        }

        return nueva_reserva

    def reviews_hotel(self, hotelId) -> list[Resena]:
        reviews_for_hotel = []
        for resena in self._resenas.values():
            if resena["hotelId"] == hotelId:
                reviews_for_hotel.append(resena)
        return reviews_for_hotel
# Booking App

Microservicio encargado de gestionar **reservas de habitaciones** y **consultar reseñas de hoteles**. Implementado en **Python 3 + FastAPI**, persistencia en PostgreSQL y empaquetado en Docker.

Expone endpoints para:

* Crear reservas autenticadas
* Consultar reseñas de hoteles
* Health check del servicio

---

## Índice

1. [Estructura](#estructura)
2. [Variables de entorno](#variables-de-entorno)
3. [Autenticación](#autenticación)
4. [Body / Query Parameters](#body--query-parameters)
5. [Ejecución](#ejecución)
6. [Documentación Endpoints](#documentación-endpoints)
7. [Autor](#autor)

---

## Estructura

Estructura de la **carpeta de la aplicación** (`booking_app/`):

```text
booking_app/
├─ Dockerfile                               # Imagen de la app (uvicorn + FastAPI)
├─ .dockerignore & .gitignore
├─ requirements.txt
├─ src/
│  ├─ error.py
│  ├─ config.py                             # Variables de entorno
│  ├─ main.py                               # Arranque de uvicorn
│  ├─ utils/
│  │  └─ decode.py                          # Decodificación JWT
│  ├─ domain/
│  │  ├─ models/
│  │  │  └─ models.py                       # Entidades y request models
│  │  ├─ ports/
│  │  │  └─ booking_repository_port.py      # Contrato repositorio
│  │  └─ use_cases/
│  ├─ adapters/
│  │  ├─ memory/
│  │  └─ postgres/
│  └─ entrypoints/
│     ├─ assembly.py                        # Inyección dependencias
│     └─ App.py                             # Endpoints
└─ tests/
```

---

## Variables de Entorno

Estas variables permiten configurar la aplicación según el entorno.

---

### Configuración General

| Variable   | Tipo   | Default   | Descripción                    |
| ---------- | ------ | --------- | ------------------------------ |
| `APP_HOST` | string | `0.0.0.0` | Host donde corre la aplicación |
| `APP_PORT` | string | `8000`    | Puerto del servicio            |

---

### Repositorio de Datos

| Variable          | Tipo   | Default  | Descripción                                           |
| ----------------- | ------ | -------- | ----------------------------------------------------- |
| `REPOSITORY_IMPL` | string | `memory` | Implementación del repositorio (`memory`, `postgres`) |

---

### Base de Datos

| Variable      | Tipo   | Default     |
| ------------- | ------ | ----------- |
| `DB_HOST`     | string | `localhost` |
| `DB_PORT`     | string | `5432`      |
| `DB_USER`     | string | `postgres`  |
| `DB_PASSWORD` | string | `postgres`  |
| `DB_NAME`     | string | `postgres`  |

---

## Autenticación

El endpoint de reservas requiere autenticación vía:

```http
Authorization: Bearer <token>
```

El token debe contener el identificador del usuario autenticado, el cual será usado como `viajeroId`.

---

## Body / Query Parameters

---

## POST `/api/v1/booking/booking_room`

### Body JSON

| Campo          | Tipo     | Requerido | Descripción          |
| -------------- | -------- | --------- | -------------------- |
| `habitacionId` | string   | Sí        | ID de la habitación  |
| `checkin`      | datetime | Sí        | Fecha y hora ingreso |
| `checkout`     | datetime | Sí        | Fecha y hora salida  |
| `numHuespedes` | integer  | Sí        | Número de huéspedes  |

### Ejemplo

```json
{
  "habitacionId": "22222222-2222-2222-2222-000000000001",
  "checkin": "2026-10-01T15:00:00",
  "checkout": "2026-10-12T12:00:00",
  "numHuespedes": 2
}
```

---

## GET `/api/v1/booking/reviews_hotel`

### Query Params

| Parámetro | Tipo   | Requerido | Descripción  |
| --------- | ------ | --------- | ------------ |
| `hotelId` | string | Sí        | ID del hotel |

---

## Ejecución

### Desarrollo local con pip

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 src/main.py
```

---

## Documentación Endpoints

---

# API Endpoints

* `POST /api/v1/booking/booking_room`
* `GET /api/v1/booking/reviews_hotel`
* `GET /api/v1/booking/ping`

---

## 1. Crear Reserva

**Descripción:** crea una reserva validando disponibilidad, fechas y capacidad.

```bash
curl --location 'http://localhost:8000/api/v1/booking/booking_room' \
--header 'Authorization: Bearer TOKEN' \
--header 'Content-Type: application/json' \
--data '{
  "habitacionId":"22222222-2222-2222-2222-000000000001",
  "checkin":"2026-10-01T15:00:00",
  "checkout":"2026-10-12T12:00:00",
  "numHuespedes":2
}'
```

### Respuesta Esperada

* Status: `200 OK`

```json
{
  "id": "1",
  "codigo": "RSV-10001",
  "viajeroId": "user-123",
  "habitacionId": "22222222-2222-2222-2222-000000000001",
  "fechaCheckIn": "2026-10-01T15:00:00",
  "fechaCheckOut": "2026-10-12T12:00:00",
  "numHuespedes": 2,
  "estado": "CONFIRMADA",
  "subtotal": 1000,
  "impuestos": 190,
  "total": 1190,
  "moneda": "USD"
}
```

---

## 2. Reserva con Check-in mayor o igual a Checkout

```bash
curl --location 'http://localhost:8000/api/v1/booking/booking_room'
```

### Respuesta Esperada

* Status: `400`

```text
the check-in date is later than the check-out date
```

---

## 3. Reserva con Check-in menor a hoy

### Respuesta Esperada

* Status: `400`

```text
the check-in date is lower than today
```

---

## 4. Habitación no existe

### Respuesta Esperada

* Status: `404`

```text
El recurso habitación no existe.
```

---

## 5. Usuario no existe

### Respuesta Esperada

* Status: `404`

```text
El recurso usuario no existe.
```

---

## 6. Tarifa no disponible

### Respuesta Esperada

* Status: `404`

```text
No existe tarifa para la habitación en ese periodo
```

---

## 7. Reserva duplicada

### Respuesta Esperada

* Status: `409`

```text
Reserva Duplicada
```

---

## 8. Habitación ocupada

### Respuesta Esperada

* Status: `409`

```text
La solicitud entra en conflicto con estado actual (ocupada).
```

---

## 9. Número de huéspedes excedido

### Respuesta Esperada

* Status: `422`

```text
NumGuest supera maxGuest
```

---

## 10. Consultar Reseñas Hotel

```bash
curl --location 'http://localhost:8000/booking/reviews_hotel?hotelId=11111111-1111-1111-1111-000000000001'
```

### Respuesta Esperada

* Status: `200`

```json
[
  {
    "id": "1",
    "viajeroId": "user-123",
    "calificacion": 5,
    "comentario": "Excelente experiencia",
    "fecha": "2026-01-10T10:00:00",
    "verificada": true
  }
]
```

---

## 11. Health Check

```bash
curl --location 'http://localhost:8000/booking/ping'
```

### Respuesta Esperada

* Status: `200`

```text
pong
```

---

## Autor

* Pablo Jose Rivera Herrera
* Contacto: `<p.riverah@uniandes.edu.co>`

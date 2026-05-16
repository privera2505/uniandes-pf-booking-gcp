import logging

import httpx

from config import NOTIFICATION_SERVICE_URL, INTERNAL_TOKEN
from domain.models.models import UpdateReserva

logger = logging.getLogger(__name__)


class NotificationClient:
    def __init__(self):
        self.base_url = NOTIFICATION_SERVICE_URL

    def send_notification(
        self,
        booking_id: str,
        status: str,
    ) -> None:

        payload = {
            "booking_id": booking_id,
            "status": status,
        }

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/notifications/send-notification",
                    json=payload,
                )

                response.raise_for_status()

                logger.info(
                    f"Notification enviada correctamente "
                    f"booking_id={booking_id}, status={status}"
                )

        except Exception as e:
            # NO lanzar excepción
            # Solo registrar el error
            logger.warning(
                f"Error enviando notificación "
                f"(booking_id={booking_id}, status={status}): {e}"
            )
    
    def send_notification_email(
        self,
        status: str,
        reserva: UpdateReserva
    ):
        payload = {
            "event_type": status,
            "user_id": reserva["viajeroId"],
            "payload": {
                "booking_id": reserva["id"],
                "hotel_name": reserva["hotel_name"],
                "check_in": reserva["fechaCheckIn"].isoformat(),
                "check_out": reserva["fechaCheckOut"].isoformat(),
                "total": reserva["total"],
                "currency": reserva["moneda"]
            }
        }

        headers = {
            "X-Internal-Token": INTERNAL_TOKEN,
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/notifications/events",
                    json=payload,
                    headers=headers,
                )

                response.raise_for_status()

                logger.info(
                    f"Email notification enviada correctamente "
                    f"booking_id={reserva['id']}, event_type={status}"
                )

        except Exception as e:
            # NO lanzar excepción
            # Solo registrar el error
            logger.warning(
                f"Error enviando email notification "
                f"(booking_id={reserva['id']}, event_type={status}): {e}"
            )

            
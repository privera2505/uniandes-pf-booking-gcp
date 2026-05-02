import base64
import json
from fastapi import Request, HTTPException

from error import UserNotExist

def decode_gateway_userinfo(value: str):
    padding = "=" * (-len(value) % 4)
    decoded = base64.urlsafe_b64decode(value + padding)
    return json.loads(decoded)

async def get_current_user_id(request: Request):
    data = request.headers.get("x-apigateway-api-userinfo")

    if not data:
        raise HTTPException(status_code=404, detail="El recurso usuario no existe.")
    
    payload = decode_gateway_userinfo(data)
    return payload["sub"]

async def get_id_filter(request: Request):
    data = request.headers.get("x-apigateway-api-userinfo")

    if not data:
        raise HTTPException(status_code=404, detail="El recurso usuario no existe.")
    
    payload = decode_gateway_userinfo(data)
    if payload.get("hotel_id") is not None:
        return payload["hotel_id"]

    return payload["sub"]

async def get_current_hotel_id(request: Request):
    data = request.headers.get("x-apigateway-api-userinfo")

    if not data:
        raise HTTPException(
            status_code=401,
            detail="No autenticado"
        )

    payload = decode_gateway_userinfo(data)

    hotel_id = payload.get("hotel_id")

    if not hotel_id:
        raise HTTPException(
            status_code=403,
            detail="Acción no autorizada: se requiere rol de hotel"
        )

    return hotel_id
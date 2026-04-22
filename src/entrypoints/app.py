from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

from entrypoints.routers import router

from config import ALLOWED_ORIGINS


app = FastAPI(title="Booking Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router, prefix="/api/v1/booking", tags=["booking"])
from datetime import datetime

def generate_reservation_code(viajeroId, habitacionId, checkin, checkout):
    return f"CODE-{viajeroId}-{habitacionId}-{checkin.isoformat()}-{checkout.isoformat()}"
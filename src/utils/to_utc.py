from datetime import datetime, timezone

def to_utc(dt:datetime) -> datetime:
    if dt.tzinfo is None:
        # asumir que viene en hora local → convertir a UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
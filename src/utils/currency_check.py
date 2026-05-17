from domain.models.models import Currency

from fastapi import Query, HTTPException

def currency_dep(
    moneda: str = Query(..., description="EUR, USD o COP")
) -> Currency:
    try:
        return Currency(moneda.upper())
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Moneda inválida. Use EUR, USD o COP"
        )
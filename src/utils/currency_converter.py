# Tasas base respecto a USD
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "COP": 4000.0
}

#Funcion para pasar 
def convert_price(
    price: float,
    price_currency: str,
    target_currency: str
) -> float:
    
    # 1. Convertir a USD (moneda base)
    price_in_usd = price / EXCHANGE_RATES[price_currency]
    
    # 2. Convertir de USD a moneda destino
    converted_price = price_in_usd * EXCHANGE_RATES[target_currency]
    
    return round(converted_price, 2)
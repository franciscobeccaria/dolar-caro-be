from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Dict, List, Any
from datetime import datetime

# Import our scrapers
from scrapers import scrape_nike_airforce_prices, scrape_adidas_argentina_jersey_prices, get_dolar_price

app = FastAPI(
    title="¿El dólar está caro en Argentina? - API",
    description="API para comparar precios entre Argentina y EEUU",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache para almacenar los datos y evitar múltiples scraping
cache = {
    "nike": None,
    "adidas_jersey": None,
    "last_update": None
}

# Función para verificar si el cache está actualizado (1 hora)
def is_cache_valid() -> bool:
    if not cache["last_update"]:
        return False
    now = datetime.now()
    diff = now - cache["last_update"]
    return diff.seconds < 3600  # 1 hora en segundos

# Función para obtener precios de Nike Air Force One
async def get_nike_data() -> Dict[str, Any]:
    if cache["nike"] and is_cache_valid():
        return cache["nike"]
    
    try:
        # Obtener datos de scraping
        nike_data = await scrape_nike_airforce_prices()
        dolar_price = get_dolar_price()
        
        result = {
            "producto": "Nike Air Force One",
            "precio_ars": nike_data["ar_price"],
            "precio_usd": nike_data["us_price"],
            "precio_ars_usd": round(nike_data["ar_price"] / dolar_price, 2),
            "url_ar": nike_data["ar_url"],
            "url_us": nike_data["us_url"],
            "dolar_blue": dolar_price
        }
        
        cache["nike"] = result
        cache["last_update"] = datetime.now()
        
        return result
    except Exception as e:
        print(f"Error obteniendo datos de Nike: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos de Nike: {str(e)}")

# Removed BigMac functionality as requested

# Función para obtener precios de la camiseta de Argentina de Adidas
async def get_adidas_jersey_data() -> Dict[str, Any]:
    if cache["adidas_jersey"] and is_cache_valid():
        return cache["adidas_jersey"]
    
    try:
        # Obtener datos de scraping
        jersey_data = await scrape_adidas_argentina_jersey_prices()
        dolar_price = get_dolar_price()
        
        result = {
            "producto": "Adidas Argentina Anniversary Jersey",
            "precio_ars": jersey_data["ar_price"],
            "precio_usd": jersey_data["us_price"],
            "precio_ars_usd": round(jersey_data["ar_price"] / dolar_price, 2),
            "url_ar": jersey_data["ar_url"],
            "url_us": jersey_data["us_url"],
            "dolar_blue": dolar_price
        }
        
        cache["adidas_jersey"] = result
        cache["last_update"] = datetime.now()
        
        return result
    except Exception as e:
        print(f"Error obteniendo datos de Adidas Jersey: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos de Adidas Jersey: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "¿El dólar está caro en Argentina? - API"}

@app.get("/nike")
async def get_nike():
    return await get_nike_data()

# BigMac endpoint removed as requested

@app.get("/adidas-jersey")
async def get_adidas_jersey():
    return await get_adidas_jersey_data()

@app.get("/all")
async def get_all():
    nike_data = await get_nike_data()
    adidas_jersey_data = await get_adidas_jersey_data()
    
    return {
        "dolar_blue": get_dolar_price(),
        "productos": [nike_data, adidas_jersey_data]
    }

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

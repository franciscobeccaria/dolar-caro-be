from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import os

# Import our services and database manager
from services import PriceService
from db_manager import DatabaseManager

app = FastAPI(
    title="¿El dólar está caro en Argentina? - API",
    description="API para obtener precios de productos en Argentina y EE.UU.",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache para almacenar los datos y evitar múltiples scraping
cache = {
    "nike": None,
    "adidas_jersey": None,
    "all": None,
    "last_update": None
}

# Función para verificar si el cache es válido (menos de 1 hora)
def is_cache_valid() -> bool:
    if not cache["last_update"]:
        return False
    return datetime.now() - cache["last_update"] < timedelta(hours=1)

# Dependency to get the price service
def get_price_service():
    return PriceService(debug=False)

@app.get("/")
def read_root():
    return {"message": "¿El dólar está caro en Argentina? - API"}

@app.get("/nike")
async def get_nike(service: PriceService = Depends(get_price_service)):
    """Get Nike Air Force 1 prices in Argentina and US"""
    if cache["nike"] and is_cache_valid():
        return cache["nike"]
    
    try:
        # Get data from service
        nike_data = await service.scrape_nike_prices()
        exchange_rate = await service.get_exchange_rate()
        
        # Format response to match existing API
        result = {
            "producto": "Nike Air Force One",
            "precio_ars": nike_data["ar_price"],
            "precio_usd": nike_data["us_price"],
            "precio_ars_usd": round(nike_data["ar_price"] / exchange_rate, 2),
            "url_ar": "https://www.nike.com.ar/nike-air-force-1--07-cw2288-111/p",
            "url_us": "https://www.nike.com/t/air-force-1-07-mens-shoes-5QFp5Z/CW2288-111",
            "dolar_blue": exchange_rate
        }
        
        # Update cache
        cache["nike"] = result
        cache["last_update"] = datetime.now()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos de Nike: {str(e)}")

@app.get("/adidas-jersey")
async def get_adidas_jersey(service: PriceService = Depends(get_price_service)):
    """Get Adidas Argentina Anniversary Jersey prices in Argentina and US"""
    if cache["adidas_jersey"] and is_cache_valid():
        return cache["adidas_jersey"]
    
    try:
        # Get data from service
        adidas_data = await service.scrape_adidas_prices()
        exchange_rate = await service.get_exchange_rate()
        
        # Format response to match existing API
        result = {
            "producto": "Adidas Argentina Anniversary Jersey",
            "precio_ars": adidas_data["ar_price"],
            "precio_usd": adidas_data["us_price"],
            "precio_ars_usd": round(adidas_data["ar_price"] / exchange_rate, 2),
            "url_ar": "https://www.adidas.com.ar/camiseta-aniversario-50-anos-seleccion-argentina/JF0395.html",
            "url_us": "https://www.adidas.com/us/argentina-anniversary-jersey/JF2641.html",
            "dolar_blue": exchange_rate
        }
        
        # Update cache
        cache["adidas_jersey"] = result
        cache["last_update"] = datetime.now()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos de Adidas Jersey: {str(e)}")

@app.get("/all")
async def get_all(service: PriceService = Depends(get_price_service)):
    """Get all product prices"""
    if cache["all"] and is_cache_valid():
        return cache["all"]
    
    try:
        # Get Nike data
        nike_data = await get_nike(service)
        
        # Get Adidas data
        adidas_data = await get_adidas_jersey(service)
        
        # Format response
        result = {
            "dolar_blue": await service.get_exchange_rate(),
            "productos": [nike_data, adidas_data]
        }
        
        # Update cache
        cache["all"] = result
        cache["last_update"] = datetime.now()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo todos los datos: {str(e)}")

@app.get("/history/{product}")
async def get_history(product: str, country: str = "AR", limit: int = Query(10, ge=1, le=100), service: PriceService = Depends(get_price_service)):
    """Get price history for a product"""
    try:
        # Map product names to internal names
        product_map = {
            "nike": "Nike Air Force 1",
            "adidas-jersey": "Argentina Anniversary Jersey"
        }
        
        if product not in product_map:
            raise HTTPException(status_code=400, detail=f"Invalid product. Must be one of: {list(product_map.keys())}")
        
        # Get price history
        history = service.get_price_history(product_map[product], country, limit)
        
        return history
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")

@app.post("/prices/manual")
async def add_manual_price(
    product_id: int,
    country_id: int,
    price_value: float,
    currency: str,
    source_type: str = "manual",
    description: Optional[str] = None,
    image: Optional[str] = None,
    date: Optional[str] = None,
    service: PriceService = Depends(get_price_service)
):
    """
    Add a manual price entry
    
    - **product_id**: ID of the product
    - **country_id**: ID of the country
    - **price_value**: The price value
    - **currency**: Currency code (e.g., USD, ARS)
    - **source_type**: Type of source (default: manual)
    - **description**: Optional description of the price entry
    - **image**: Optional image URL or base64 string
    - **date**: Optional date in ISO format (default: current date/time)
    """
    try:
        # Parse date if provided
        parsed_date = None
        if date:
            try:
                parsed_date = datetime.fromisoformat(date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        # Add manual price
        result = service.add_manual_price(
            product_id=product_id,
            country_id=country_id,
            price_value=price_value,
            currency=currency,
            source_type=source_type,
            description=description,
            image_url=image,
            date=parsed_date
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding manual price: {str(e)}")

@app.get("/products")
async def get_products(service: PriceService = Depends(get_price_service)):
    """Get all available products"""
    try:
        with DatabaseManager() as db:
            products = db.get_all_products()
            return {
                "products": [
                    {
                        "id": product.id,
                        "name": product.name,
                        "brand": product.brand,
                        "model": product.model,
                        "description": product.description,
                        "category": product.category.name if product.category else None
                    } for product in products
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting products: {str(e)}")

@app.get("/countries")
async def get_countries(service: PriceService = Depends(get_price_service)):
    """Get all available countries"""
    try:
        with DatabaseManager() as db:
            countries = db.get_all_countries()
            return {
                "countries": [
                    {
                        "id": country.id,
                        "name": country.name,
                        "code": country.code,
                        "currency": country.currency
                    } for country in countries
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting countries: {str(e)}")

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

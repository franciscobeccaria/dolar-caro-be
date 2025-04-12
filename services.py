from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from db_manager import DatabaseManager
from models import Country, Product, Category, Source, Price, ExchangeRate, ScraperRun
from scrapers import NikeScraper, AdidasScraper
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PriceService:
    """Service for managing product prices"""
    
    def __init__(self, db_url=None, debug=False):
        """Initialize the price service"""
        self.db_url = db_url
        self.debug = debug
        self.screenshots_dir = 'screenshots'
        
        # Initialize scrapers
        self.nike_scraper = NikeScraper(debug=debug, screenshots_dir=self.screenshots_dir)
        self.adidas_scraper = AdidasScraper(debug=debug, screenshots_dir=self.screenshots_dir)
    
    async def setup_database(self):
        """Set up the database with initial data"""
        with DatabaseManager(self.db_url) as db:
            # Create countries
            db.get_or_create_country("United States", "US", "USD")
            db.get_or_create_country("Argentina", "AR", "ARS")
            
            # Create categories
            db.get_or_create_category("Footwear", "Shoes and other footwear")
            db.get_or_create_category("Sportswear", "Sports clothing and jerseys")
            
            # Create sources
            db.get_or_create_source("Nike Website", "scraping", "https://www.nike.com")
            db.get_or_create_source("Adidas Website", "scraping", "https://www.adidas.com")
            db.get_or_create_source("DolarApi", "api", "https://dolarapi.com")
            
            # Create products
            db.get_or_create_product(
                name="Nike Air Force 1",
                brand="Nike",
                model="Air Force 1 '07",
                category_name="Footwear",
                description="Iconic Nike sneaker",
                url_template="https://www.nike.com/{country_code}/air-force-1"
            )
            
            db.get_or_create_product(
                name="Argentina Anniversary Jersey",
                brand="Adidas",
                model="Anniversary Edition",
                category_name="Sportswear",
                description="50th Anniversary Argentina National Team Jersey",
                url_template="https://www.adidas.com/{country_code}/argentina-jersey"
            )
            
            logger.info("Database setup complete with initial data")
    
    async def get_exchange_rate(self) -> float:
        """Get the current blue dollar exchange rate"""
        try:
            import requests
            response = requests.get("https://dolarapi.com/v1/dolares/blue")
            data = response.json()
            rate = data["venta"]
            
            # Save to database
            with DatabaseManager(self.db_url) as db:
                # Get source
                source = db.get_or_create_source("DolarApi", "api", "https://dolarapi.com")
                
                # Add exchange rate
                db.add_exchange_rate("ARS", "USD", rate, "DolarApi")
            
            return rate
        except Exception as e:
            logger.error(f"Error getting exchange rate: {e}")
            # Return a default value if API fails
            return 1375.0
    
    async def scrape_nike_prices(self):
        """Scrape Nike prices and save to database"""
        with DatabaseManager(self.db_url) as db:
            # Start scraper run
            run = db.start_scraper_run("Nike Scraper")
            
            try:
                # Get countries
                us = db.session.query(Country).filter_by(code="US").first()
                ar = db.session.query(Country).filter_by(code="AR").first()
                
                # Get product
                product = db.session.query(Product).filter_by(name="Nike Air Force 1").first()
                
                # Get source
                source = db.get_or_create_source("Nike Website", "scraping", "https://www.nike.com")
                
                # Scrape prices
                result = await self.nike_scraper.scrape('air_force_1')
                
                # Get exchange rate
                exchange_rate = await self.get_exchange_rate()
                
                # Save US price
                us_price = db.add_price(
                    product_id=product.id,
                    country_id=us.id,
                    source_id=source.id,
                    value=result['us_price'],
                    currency="USD",
                    is_fallback=result['us_price'] == self.nike_scraper.fallback_prices['air_force_1']['US'],
                    exchange_rate=1.0,  # USD to USD is 1:1
                    usd_value=result['us_price']
                )
                
                # Save Argentina price
                ar_price = db.add_price(
                    product_id=product.id,
                    country_id=ar.id,
                    source_id=source.id,
                    value=result['ar_price'],
                    currency="ARS",
                    is_fallback=result['ar_price'] == self.nike_scraper.fallback_prices['air_force_1']['AR'],
                    exchange_rate=exchange_rate,
                    usd_value=result['ar_price'] / exchange_rate
                )
                
                # Finish scraper run
                db.finish_scraper_run(run.id, True, 1)
                
                logger.info(f"Nike prices scraped successfully: US=${result['us_price']}, AR=${result['ar_price']}")
                return {
                    "product": "Nike Air Force 1",
                    "us_price": result['us_price'],
                    "ar_price": result['ar_price'],
                    "url_us": result['us_url'],
                    "url_ar": result['ar_url'],
                    "exchange_rate": exchange_rate,
                    "ar_price_usd": round(result['ar_price'] / exchange_rate, 2)
                }
                
            except Exception as e:
                logger.error(f"Error scraping Nike prices: {e}")
                db.finish_scraper_run(run.id, False, 0, str(e))
                raise
    
    async def scrape_adidas_prices(self):
        """Scrape Adidas prices and save to database"""
        with DatabaseManager(self.db_url) as db:
            # Start scraper run
            run = db.start_scraper_run("Adidas Scraper")
            
            try:
                # Get countries
                us = db.session.query(Country).filter_by(code="US").first()
                ar = db.session.query(Country).filter_by(code="AR").first()
                
                # Get product
                product = db.session.query(Product).filter_by(name="Argentina Anniversary Jersey").first()
                
                # Get source
                source = db.get_or_create_source("Adidas Website", "scraping", "https://www.adidas.com")
                
                # Scrape prices
                result = await self.adidas_scraper.scrape('argentina_jersey')
                
                # Get exchange rate
                exchange_rate = await self.get_exchange_rate()
                
                # Save US price
                us_price = db.add_price(
                    product_id=product.id,
                    country_id=us.id,
                    source_id=source.id,
                    value=result['us_price'],
                    currency="USD",
                    is_fallback=result['us_price'] == self.adidas_scraper.fallback_prices['argentina_jersey']['US'],
                    exchange_rate=1.0,  # USD to USD is 1:1
                    usd_value=result['us_price']
                )
                
                # Save Argentina price
                ar_price = db.add_price(
                    product_id=product.id,
                    country_id=ar.id,
                    source_id=source.id,
                    value=result['ar_price'],
                    currency="ARS",
                    is_fallback=result['ar_price'] == self.adidas_scraper.fallback_prices['argentina_jersey']['AR'],
                    exchange_rate=exchange_rate,
                    usd_value=result['ar_price'] / exchange_rate
                )
                
                # Finish scraper run
                db.finish_scraper_run(run.id, True, 1)
                
                logger.info(f"Adidas prices scraped successfully: US=${result['us_price']}, AR=${result['ar_price']}")
                return {
                    "product": "Argentina Anniversary Jersey",
                    "us_price": result['us_price'],
                    "ar_price": result['ar_price'],
                    "url_us": result['us_url'],
                    "url_ar": result['ar_url'],
                    "exchange_rate": exchange_rate,
                    "ar_price_usd": round(result['ar_price'] / exchange_rate, 2)
                }
                
            except Exception as e:
                logger.error(f"Error scraping Adidas prices: {e}")
                db.finish_scraper_run(run.id, False, 0, str(e))
                raise
    
    async def scrape_all_prices(self):
        """Scrape all product prices"""
        results = []
        
        try:
            # Scrape Nike prices
            nike_result = await self.scrape_nike_prices()
            results.append(nike_result)
        except Exception as e:
            logger.error(f"Error scraping Nike prices: {e}")
        
        try:
            # Scrape Adidas prices
            adidas_result = await self.scrape_adidas_prices()
            results.append(adidas_result)
        except Exception as e:
            logger.error(f"Error scraping Adidas prices: {e}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "exchange_rate": await self.get_exchange_rate(),
            "results": results
        }
    
    def get_price_history(self, product_name: str, country_code: str, limit: int = 10):
        """Get price history for a product in a country"""
        with DatabaseManager(self.db_url) as db:
            # Get product
            product = db.session.query(Product).filter_by(name=product_name).first()
            if not product:
                raise ValueError(f"Product not found: {product_name}")
            
            # Get country
            country = db.session.query(Country).filter_by(code=country_code).first()
            if not country:
                raise ValueError(f"Country not found: {country_code}")
            
            # Get price history
            prices = db.get_price_history(product.id, country.id, limit)
            
            return {
                "product": product_name,
                "country": country.name,
                "currency": country.currency,
                "prices": [
                    {
                        "value": price.value,
                        "currency": price.currency,
                        "date": price.date_obtained.isoformat(),
                        "usd_value": price.usd_value,
                        "exchange_rate": price.exchange_rate,
                        "is_fallback": price.is_fallback
                    } for price in prices
                ]
            }

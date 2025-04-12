from sqlalchemy.orm import Session
from models import Country, Product, Category, Source, Price, ExchangeRate, ScraperRun, setup_database
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_url=None):
        """Initialize the database manager"""
        self.engine, self.SessionFactory = setup_database(db_url)
        self.session = None
    
    def __enter__(self):
        """Context manager entry point"""
        self.session = self.SessionFactory()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point"""
        if exc_type is not None:
            # An exception occurred, rollback the transaction
            self.session.rollback()
            logger.error(f"Database transaction rolled back due to {exc_type.__name__}: {exc_val}")
        else:
            # No exception, commit the transaction
            self.session.commit()
        
        # Always close the session
        self.session.close()
        self.session = None
    
    def get_or_create_country(self, name: str, code: str, currency: str) -> Country:
        """Get or create a country record"""
        country = self.session.query(Country).filter_by(code=code).first()
        if not country:
            country = Country(name=name, code=code, currency=currency)
            self.session.add(country)
            self.session.flush()  # Flush to get the ID
            logger.info(f"Created new country: {name} ({code})")
        return country
    
    def get_or_create_category(self, name: str, description: str = None) -> Category:
        """Get or create a category record"""
        category = self.session.query(Category).filter_by(name=name).first()
        if not category:
            category = Category(name=name, description=description)
            self.session.add(category)
            self.session.flush()  # Flush to get the ID
            logger.info(f"Created new category: {name}")
        return category
    
    def get_or_create_product(self, name: str, brand: str, model: str, category_name: str, 
                             description: str = None, url_template: str = None) -> Product:
        """Get or create a product record"""
        product = self.session.query(Product).filter_by(name=name, brand=brand, model=model).first()
        if not product:
            # Get or create the category
            category = self.get_or_create_category(category_name)
            
            # Create the product
            product = Product(
                name=name,
                brand=brand,
                model=model,
                category_id=category.id,
                description=description,
                url_template=url_template
            )
            self.session.add(product)
            self.session.flush()  # Flush to get the ID
            logger.info(f"Created new product: {name} ({brand} {model})")
        return product
    
    def get_or_create_source(self, name: str, type_str: str, url: str = None, description: str = None) -> Source:
        """Get or create a source record"""
        source = self.session.query(Source).filter_by(name=name, type=type_str).first()
        if not source:
            source = Source(name=name, type=type_str, url=url, description=description)
            self.session.add(source)
            self.session.flush()  # Flush to get the ID
            logger.info(f"Created new source: {name} ({type_str})")
        return source
    
    def add_price(self, product_id: int, country_id: int, source_id: int, value: float, 
                 currency: str, is_fallback: bool = False, exchange_rate: float = None, 
                 usd_value: float = None) -> Price:
        """Add a new price record"""
        price = Price(
            product_id=product_id,
            country_id=country_id,
            source_id=source_id,
            value=value,
            currency=currency,
            is_fallback=is_fallback,
            exchange_rate=exchange_rate,
            usd_value=usd_value,
            date_obtained=datetime.now()
        )
        self.session.add(price)
        self.session.flush()  # Flush to get the ID
        logger.info(f"Added new price: {value} {currency} for product ID {product_id} in country ID {country_id}")
        return price
    
    def add_exchange_rate(self, from_currency: str, to_currency: str, rate: float, source: str = None) -> ExchangeRate:
        """Add a new exchange rate record"""
        exchange_rate = ExchangeRate(
            from_currency=from_currency,
            to_currency=to_currency,
            rate=rate,
            source=source,
            date=datetime.now()
        )
        self.session.add(exchange_rate)
        self.session.flush()  # Flush to get the ID
        logger.info(f"Added new exchange rate: {from_currency} to {to_currency} = {rate}")
        return exchange_rate
    
    def start_scraper_run(self, scraper_name: str) -> ScraperRun:
        """Start a new scraper run and return the record"""
        run = ScraperRun(
            scraper_name=scraper_name,
            start_time=datetime.now(),
            success=None  # Will be updated when the run finishes
        )
        self.session.add(run)
        self.session.flush()  # Flush to get the ID
        logger.info(f"Started new scraper run: {scraper_name}")
        return run
    
    def finish_scraper_run(self, run_id: int, success: bool, products_scraped: int, error_message: str = None):
        """Update a scraper run record when it finishes"""
        run = self.session.query(ScraperRun).filter_by(id=run_id).first()
        if run:
            run.end_time = datetime.now()
            run.success = success
            run.products_scraped = products_scraped
            run.error_message = error_message
            self.session.flush()
            logger.info(f"Finished scraper run {run_id}: success={success}, products={products_scraped}")
        else:
            logger.error(f"Could not find scraper run with ID {run_id}")
    
    def get_latest_price(self, product_id: int, country_id: int) -> Optional[Price]:
        """Get the latest price for a product in a country"""
        return self.session.query(Price)\
            .filter_by(product_id=product_id, country_id=country_id)\
            .order_by(Price.date_obtained.desc())\
            .first()
    
    def get_latest_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[ExchangeRate]:
        """Get the latest exchange rate between two currencies"""
        return self.session.query(ExchangeRate)\
            .filter_by(from_currency=from_currency, to_currency=to_currency)\
            .order_by(ExchangeRate.date.desc())\
            .first()
    
    def get_price_history(self, product_id: int, country_id: int, limit: int = 10) -> List[Price]:
        """Get price history for a product in a country"""
        return self.session.query(Price)\
            .filter_by(product_id=product_id, country_id=country_id)\
            .order_by(Price.date_obtained.desc())\
            .limit(limit)\
            .all()
    
    def get_all_products(self) -> List[Product]:
        """Get all products"""
        return self.session.query(Product).all()
    
    def get_all_countries(self) -> List[Country]:
        """Get all countries"""
        return self.session.query(Country).all()

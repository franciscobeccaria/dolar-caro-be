from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
import os

# Create the base class for our ORM models
Base = declarative_base()

# Define enums for our models
class SourceType(enum.Enum):
    MANUAL = "manual"
    SCRAPING = "scraping"
    API = "api"

class Currency(enum.Enum):
    ARS = "ARS"
    USD = "USD"
    BRL = "BRL"  # Brazilian Real
    CLP = "CLP"  # Chilean Peso

# Define our models
class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String(2), nullable=False, unique=True)
    currency = Column(String, nullable=False)
    
    # Relationships
    prices = relationship("Price", back_populates="country")
    
    def __repr__(self):
        return f"<Country(name='{self.name}', code='{self.code}', currency='{self.currency}')>"

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    brand = Column(String)
    model = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))
    url_template = Column(String)  # Template for product URL with placeholders for country
    
    # Relationships
    category = relationship("Category", back_populates="products")
    prices = relationship("Price", back_populates="product")
    
    def __repr__(self):
        return f"<Product(name='{self.name}', brand='{self.brand}', model='{self.model}')>"
    
    def get_latest_price(self, country_code):
        """Get the latest price for this product in the specified country"""
        # This would be implemented with a query to get the most recent price
        pass

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Using string instead of Enum for simplicity
    url = Column(String)
    description = Column(String)
    
    # Relationships
    prices = relationship("Price", back_populates="source")
    
    def __repr__(self):
        return f"<Source(name='{self.name}', type='{self.type}')>"

class Price(Base):
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    value = Column(Float, nullable=False)
    currency = Column(String, nullable=False)  # Using string instead of Enum for simplicity
    date_obtained = Column(DateTime, default=datetime.now, nullable=False)
    is_fallback = Column(Boolean, default=False)  # Whether this is a fallback price
    exchange_rate = Column(Float)  # Exchange rate to USD at the time of scraping
    usd_value = Column(Float)  # Value in USD based on exchange rate
    
    # Relationships
    product = relationship("Product", back_populates="prices")
    country = relationship("Country", back_populates="prices")
    source = relationship("Source", back_populates="prices")
    
    def __repr__(self):
        return f"<Price(product='{self.product.name}', country='{self.country.name}', value={self.value} {self.currency})>"

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True)
    from_currency = Column(String, nullable=False)
    to_currency = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.now, nullable=False)
    source = Column(String)  # Source of the exchange rate data
    
    def __repr__(self):
        return f"<ExchangeRate(from='{self.from_currency}', to='{self.to_currency}', rate={self.rate})>"

class ScraperRun(Base):
    __tablename__ = "scraper_runs"
    
    id = Column(Integer, primary_key=True)
    scraper_name = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.now, nullable=False)
    end_time = Column(DateTime)
    success = Column(Boolean)
    error_message = Column(String)
    products_scraped = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<ScraperRun(scraper='{self.scraper_name}', success={self.success}, products={self.products_scraped})>"

# Database setup function
def setup_database(db_url=None):
    """Setup the database connection and create tables if they don't exist"""
    if db_url is None:
        # Default to SQLite database in the project directory
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'price_data.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db_url = f"sqlite:///{db_path}"
    
    # Create engine and session
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    
    # Create tables
    Base.metadata.create_all(engine)
    
    return engine, Session

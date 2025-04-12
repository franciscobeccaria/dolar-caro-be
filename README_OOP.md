# Dolar Blue Price Checker

A Python-based backend project that compares product prices between Argentina and other countries, using the blue dollar exchange rate. The goal is to determine if things are expensive or cheap in Argentina when compared to places like the US, Chile, or Brazil.

## Features

- **Object-Oriented Design**: Models for Product, Country, Price, Source, etc.
- **Advanced Scraping**: Fetch prices from Nike, Adidas, and more using Playwright
- **Database Storage**: Store all data in SQLite using SQLAlchemy ORM
- **Historical Data**: Track price changes over time
- **CLI Interface**: Run scrapers and manage data from the command line
- **REST API**: Access price data via FastAPI endpoints

## Project Structure

```
dolar_blue_price_checker/
├── models.py           # SQLAlchemy ORM models
├── db_manager.py       # Database operations
├── scrapers/           # Scraper modules
│   ├── __init__.py
│   ├── base_scraper.py # Base scraper class
│   ├── nike_scraper.py # Nike-specific scraper
│   └── adidas_scraper.py # Adidas-specific scraper
├── services.py         # Business logic
├── api.py              # FastAPI endpoints
├── cli.py              # Command-line interface
├── utils.py            # Utility functions
├── db/                 # Database files
└── data/               # JSON data storage
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/franciscobeccaria/dolar-caro-be.git
cd dolar-caro-be
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
python -m playwright install chromium
```

4. Set up the database:

```bash
python cli.py setup
```

## Usage

### Command Line Interface

The project includes a CLI for running scrapers and managing data:

```bash
# Setup the database with initial data
python cli.py setup

# Scrape Nike prices
python cli.py nike

# Scrape Adidas prices
python cli.py adidas

# Scrape all prices
python cli.py all

# Enable debug mode (takes screenshots)
python cli.py all --debug

# Don't save results to JSON
python cli.py all --no-json
```

### API

Start the API server:

```bash
python api.py
```

Or with uvicorn:

```bash
uvicorn api:app --reload
```

The API will be available at http://localhost:8000

#### Endpoints

- `/nike` → Nike Air Force One prices in AR and US
- `/adidas-jersey` → Adidas Argentina Anniversary Jersey prices in AR and US
- `/all` → All products together
- `/history/{product}` → Price history for a product

## Database Structure

The project uses SQLAlchemy ORM with the following models:

- **Country**: Represents a country with its currency
- **Category**: Product categories (e.g., Footwear, Sportswear)
- **Product**: Products to track prices for
- **Source**: Where the price data comes from (scraping, API, manual)
- **Price**: Individual price records with timestamp and exchange rate
- **ExchangeRate**: Exchange rate records
- **ScraperRun**: Logs of scraper runs

## Adding New Scrapers

To add a new scraper:

1. Create a new scraper class in the `scrapers` directory, inheriting from `BaseScraper`
2. Implement the `scrape()` method
3. Add the scraper to the `PriceService` class in `services.py`
4. Add a new command to the CLI in `cli.py`
5. Add a new endpoint to the API in `api.py`

## Example: Adding a New Scraper

```python
# scrapers/new_scraper.py
from .base_scraper import BaseScraper

class NewScraper(BaseScraper):
    def __init__(self, debug=False, screenshots_dir=None):
        super().__init__(debug, screenshots_dir)
        self.product_urls = {
            'product_key': {
                'AR': "https://example.com.ar/product",
                'US': "https://example.com/product"
            }
        }
        
        self.fallback_prices = {
            'product_key': {
                'AR': 9999,  # ARS
                'US': 99     # USD
            }
        }
    
    async def scrape(self, product_key='product_key'):
        # Implementation here
        pass
```

## License

MIT

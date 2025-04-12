#!/usr/bin/env python3
import asyncio
import argparse
import logging
from services import PriceService
import os
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def setup_database(debug: bool = False):
    """Setup the database with initial data"""
    service = PriceService(debug=debug)
    await service.setup_database()
    logger.info("Database setup complete")

async def scrape_nike(debug: bool = False, save_json: bool = True):
    """Scrape Nike prices"""
    service = PriceService(debug=debug)
    result = await service.scrape_nike_prices()
    logger.info(f"Nike scraping complete: {result}")
    
    if save_json:
        save_to_json("nike", result)
    
    return result

async def scrape_adidas(debug: bool = False, save_json: bool = True):
    """Scrape Adidas prices"""
    service = PriceService(debug=debug)
    result = await service.scrape_adidas_prices()
    logger.info(f"Adidas scraping complete: {result}")
    
    if save_json:
        save_to_json("adidas", result)
    
    return result

async def scrape_all(debug: bool = False, save_json: bool = True):
    """Scrape all prices"""
    service = PriceService(debug=debug)
    result = await service.scrape_all_prices()
    logger.info(f"All scraping complete: {len(result['results'])} products")
    
    if save_json:
        save_to_json("all", result)
    
    return result

def save_to_json(name: str, data: dict):
    """Save data to a JSON file"""
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Create subdirectory for this scraper
    scraper_dir = os.path.join(data_dir, name)
    os.makedirs(scraper_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{timestamp}.json"
    filepath = os.path.join(scraper_dir, filename)
    
    # Add timestamp to data
    data_with_timestamp = data.copy()
    if 'timestamp' not in data_with_timestamp:
        data_with_timestamp['timestamp'] = datetime.now().isoformat()
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data_with_timestamp, f, ensure_ascii=False, indent=2)
    
    # Also save to latest.json
    latest_path = os.path.join(scraper_dir, 'latest.json')
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(data_with_timestamp, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Data saved to {filepath}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Dolar Blue Price Checker CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup database command
    setup_parser = subparsers.add_parser("setup", help="Setup the database")
    setup_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # Nike scraper command
    nike_parser = subparsers.add_parser("nike", help="Scrape Nike prices")
    nike_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    nike_parser.add_argument("--no-json", action="store_true", help="Don't save results to JSON")
    
    # Adidas scraper command
    adidas_parser = subparsers.add_parser("adidas", help="Scrape Adidas prices")
    adidas_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    adidas_parser.add_argument("--no-json", action="store_true", help="Don't save results to JSON")
    
    # All scrapers command
    all_parser = subparsers.add_parser("all", help="Scrape all prices")
    all_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    all_parser.add_argument("--no-json", action="store_true", help="Don't save results to JSON")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        asyncio.run(setup_database(args.debug))
    elif args.command == "nike":
        asyncio.run(scrape_nike(args.debug, not args.no_json))
    elif args.command == "adidas":
        asyncio.run(scrape_adidas(args.debug, not args.no_json))
    elif args.command == "all":
        asyncio.run(scrape_all(args.debug, not args.no_json))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

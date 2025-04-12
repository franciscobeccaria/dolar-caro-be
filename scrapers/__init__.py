# This file makes the scrapers directory a Python package
from .nike_scraper import NikeScraper
from .adidas_scraper import AdidasScraper

__all__ = ['NikeScraper', 'AdidasScraper']

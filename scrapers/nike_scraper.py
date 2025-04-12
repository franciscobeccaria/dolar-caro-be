from .base_scraper import BaseScraper
from typing import Dict, Any, List, Optional
import asyncio
import re
from playwright.async_api import async_playwright

class NikeScraper(BaseScraper):
    """Scraper for Nike products"""
    
    def __init__(self, debug: bool = False, screenshots_dir: str = None):
        super().__init__(debug, screenshots_dir)
        self.product_urls = {
            # Air Force 1
            'air_force_1': {
                'AR': "https://www.nike.com.ar/nike-air-force-1--07-cw2288-111/p",
                'US': "https://www.nike.com/t/air-force-1-07-mens-shoes-5QFp5Z/CW2288-111"
            }
            # Add more products as needed
        }
        
        # Fallback prices if scraping fails
        self.fallback_prices = {
            'air_force_1': {
                'AR': 199999,  # ARS
                'US': 110      # USD
            }
        }
    
    async def scrape(self, product_key: str = 'air_force_1') -> Dict[str, Any]:
        """Scrape prices for a Nike product"""
        if product_key not in self.product_urls:
            raise ValueError(f"Unknown product key: {product_key}")
        
        urls = self.product_urls[product_key]
        fallbacks = self.fallback_prices.get(product_key, {})
        
        ar_price = None
        us_price = None
        
        async with async_playwright() as p:
            # Scrape Argentina price
            ar_price = await self._scrape_argentina(p, urls.get('AR'), fallbacks.get('AR'))
            
            # Scrape US price
            us_price = await self._scrape_us(p, urls.get('US'), fallbacks.get('US'))
        
        return {
            "product_key": product_key,
            "ar_price": ar_price,
            "us_price": us_price,
            "ar_url": urls.get('AR'),
            "us_url": urls.get('US')
        }
    
    async def _scrape_argentina(self, playwright, url: str, fallback_price: float) -> float:
        """Scrape price from Nike Argentina"""
        if not url:
            self.logger.warning("No URL provided for Nike Argentina")
            return fallback_price
        
        self.logger.info(f"Scraping Nike Argentina: {url}")
        price = None
        
        try:
            # Create browser context for Argentina
            browser, context, page = await self.create_browser_context(playwright, 'AR')
            
            # Add cookies for Nike Argentina
            await context.add_cookies([{
                'name': 'accept_cookies',
                'value': 'true',
                'domain': '.nike.com.ar',
                'path': '/'
            }])
            
            # Navigate to the URL
            await page.goto(url, timeout=60000, wait_until='networkidle')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # Additional wait time
            
            # Take screenshot if debugging is enabled
            await self.take_screenshot(page, 'nike_ar')
            
            # Try multiple selectors to find the price
            selectors = [
                '.vtex-product-price-1-x-sellingPriceValue',
                '.vtex-product-price-1-x-currencyContainer',
                '.vtex-product-price-1-x-sellingPrice',
                '.nikear-store-components-0-x-sellingPrice',
                '.product-price'
            ]
            
            price = await self.extract_price_with_selectors(page, selectors)
            
            # If no price found with selectors, try to extract from entire page content
            if not price:
                self.logger.info("Trying to extract price from entire page content...")
                try:
                    content = await page.content()
                    # Look for price patterns in the HTML
                    price_patterns = [
                        r'\$\s*(\d+(?:[.,]\d+)*)',  # $199.999
                        r'precio[^\d]+(\d+(?:[.,]\d+)*)',  # precio: 199.999
                        r'price[^\d]+(\d+(?:[.,]\d+)*)',   # price: 199.999
                        r'valor[^\d]+(\d+(?:[.,]\d+)*)'    # valor: 199.999
                    ]
                    
                    for pattern in price_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            self.logger.info(f"Found price matches with pattern {pattern}: {matches}")
                            # Take the first match and clean it
                            price_str = re.sub(r'[.,]', '', matches[0])
                            if price_str.isdigit():
                                price = float(price_str)
                                self.logger.info(f"Successfully extracted price from content: {price} ARS")
                                break
                except Exception as content_error:
                    self.logger.error(f"Content extraction failed: {content_error}")
            
            # Close browser
            await browser.close()
            
        except Exception as e:
            self.logger.error(f"Error scraping Nike Argentina: {e}")
        
        # If all extraction methods fail, use the fallback price
        if not price:
            price = fallback_price
            self.logger.info(f"Using fallback price for Nike Argentina: {price} ARS")
        
        return price
    
    async def _scrape_us(self, playwright, url: str, fallback_price: float) -> float:
        """Scrape price from Nike US"""
        if not url:
            self.logger.warning("No URL provided for Nike US")
            return fallback_price
        
        self.logger.info(f"Scraping Nike US: {url}")
        price = None
        
        try:
            # Create browser context for US
            browser, context, page = await self.create_browser_context(playwright, 'US')
            
            # Add cookies for Nike US
            await context.add_cookies([{
                'name': 'NIKE_COMMERCE_COUNTRY',
                'value': 'US',
                'domain': '.nike.com',
                'path': '/'
            }, {
                'name': 'NIKE_COMMERCE_LANG_LOCALE',
                'value': 'en_US',
                'domain': '.nike.com',
                'path': '/'
            }])
            
            # Navigate to the URL
            await page.goto(url, timeout=60000, wait_until='networkidle')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # Additional wait time
            
            # Take screenshot if debugging is enabled
            await self.take_screenshot(page, 'nike_us')
            
            # Try multiple selectors to find the price
            selectors = [
                '[data-test="product-price"]',
                '.product-price',
                '.css-b9fpep',  # Common Nike price class
                '.css-1122yjz'  # Another common Nike price class
            ]
            
            price = await self.extract_price_with_selectors(page, selectors)
            
            # If no price found with selectors, try JavaScript evaluation
            if not price:
                self.logger.info("Trying to extract price using JavaScript evaluation...")
                try:
                    # Try to extract price using JavaScript evaluation
                    price_js = await page.evaluate('''
                        () => {
                            // Look for price in window.__PRELOADED_STATE__
                            if (window.__PRELOADED_STATE__) {
                                const state = window.__PRELOADED_STATE__;
                                if (state.Threads && state.Threads.products) {
                                    const products = Object.values(state.Threads.products);
                                    for (const product of products) {
                                        if (product.fullPrice) {
                                            return product.fullPrice;
                                        }
                                    }
                                }
                            }
                            
                            // Look for price in any data attribute
                            const priceElements = document.querySelectorAll('[data-price], [data-test="product-price"], [data-full-price]');
                            for (const el of priceElements) {
                                const price = el.getAttribute('data-price') || el.getAttribute('data-full-price') || el.textContent;
                                if (price && price.includes('$')) {
                                    return price;
                                }
                            }
                            
                            return null;
                        }
                    ''')
                    
                    if price_js:
                        self.logger.info(f"Found price via JavaScript: {price_js}")
                        price_match = re.search(r'\$\s*(\d+(?:\.\d+)?)', price_js)
                        if price_match:
                            price = float(price_match.group(1))
                            self.logger.info(f"Successfully extracted price via JavaScript: ${price} USD")
                except Exception as js_error:
                    self.logger.error(f"JavaScript evaluation failed: {js_error}")
            
            # Close browser
            await browser.close()
            
        except Exception as e:
            self.logger.error(f"Error scraping Nike US: {e}")
        
        # If all extraction methods fail, use the fallback price
        if not price:
            price = fallback_price
            self.logger.info(f"Using fallback price for Nike US: ${price} USD")
        
        return price

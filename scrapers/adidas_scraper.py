from .base_scraper import BaseScraper
from typing import Dict, Any, List, Optional
import asyncio
import re
from playwright.async_api import async_playwright

class AdidasScraper(BaseScraper):
    """Scraper for Adidas products"""
    
    def __init__(self, debug: bool = False, screenshots_dir: str = None):
        super().__init__(debug, screenshots_dir)
        self.product_urls = {
            # Argentina Anniversary Jersey
            'argentina_jersey': {
                'AR': "https://www.adidas.com.ar/camiseta-aniversario-50-anos-seleccion-argentina/JF0395.html",
                'US': "https://www.adidas.com/us/argentina-anniversary-jersey/JF2641.html"
            }
            # Add more products as needed
        }
        
        # Fallback prices if scraping fails
        self.fallback_prices = {
            'argentina_jersey': {
                'AR': 149999,  # ARS
                'US': 100      # USD
            }
        }
    
    async def scrape(self, product_key: str = 'argentina_jersey') -> Dict[str, Any]:
        """Scrape prices for an Adidas product"""
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
        """Scrape price from Adidas Argentina"""
        if not url:
            self.logger.warning("No URL provided for Adidas Argentina")
            return fallback_price
        
        self.logger.info(f"Scraping Adidas Argentina: {url}")
        price = None
        
        try:
            # Create browser context for Argentina
            browser, context, page = await self.create_browser_context(playwright, 'AR')
            
            # Add cookies for Adidas Argentina
            await context.add_cookies([{
                'name': 'accept_cookies',
                'value': 'true',
                'domain': '.adidas.com.ar',
                'path': '/'
            }])
            
            # Set extra headers specific to Adidas
            await page.set_extra_http_headers({
                'Accept-Language': 'es-AR,es;q=0.9',
                'Referer': 'https://www.adidas.com.ar/ropa-seleccion-argentina',
                'Sec-Ch-Ua': '"Chromium";v="122", "Google Chrome";v="122"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"'
            })
            
            # Navigate to the URL
            await page.goto(url, timeout=60000, wait_until='networkidle')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # Additional wait time
            
            # Take screenshot if debugging is enabled
            await self.take_screenshot(page, 'adidas_ar')
            
            # Try multiple selectors to find the price
            selectors = [
                '.product-price-container .price',
                '.product-price',
                '.gl-price-item',
                '.gl-price__value',
                '[data-auto-id="product-price"]',
                '[data-auto-id="sale-price"]'
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
            self.logger.error(f"Error scraping Adidas Argentina: {e}")
        
        # If all extraction methods fail, use the fallback price
        if not price:
            price = fallback_price
            self.logger.info(f"Using fallback price for Adidas Argentina: {price} ARS")
        
        return price
    
    async def _scrape_us(self, playwright, url: str, fallback_price: float) -> float:
        """Scrape price from Adidas US"""
        if not url:
            self.logger.warning("No URL provided for Adidas US")
            return fallback_price
        
        self.logger.info(f"Scraping Adidas US: {url}")
        price = None
        
        try:
            # Create browser context for US
            browser, context, page = await self.create_browser_context(playwright, 'US')
            
            # Add cookies for Adidas US
            await context.add_cookies([{
                'name': 'geo_country',
                'value': 'US',
                'domain': '.adidas.com',
                'path': '/'
            }, {
                'name': 'languageLocale',
                'value': 'en_US',
                'domain': '.adidas.com',
                'path': '/'
            }])
            
            # Set extra headers specific to Adidas
            await page.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.adidas.com/us/soccer-jerseys',
                'Sec-Ch-Ua': '"Chromium";v="122", "Google Chrome";v="122"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"'
            })
            
            # Navigate to the URL
            await page.goto(url, timeout=60000, wait_until='networkidle')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # Additional wait time
            
            # Take screenshot if debugging is enabled
            await self.take_screenshot(page, 'adidas_us')
            
            # Try multiple selectors to find the price
            selectors = [
                '.gl-price-item',
                '.gl-price__value',
                '[data-auto-id="product-price"]',
                '[data-auto-id="sale-price"]',
                '.product-price'
            ]
            
            price = await self.extract_price_with_selectors(page, selectors)
            
            # If no price found with selectors, try JavaScript evaluation
            if not price:
                self.logger.info("Trying to extract price using JavaScript evaluation...")
                try:
                    # Try to extract price using JavaScript evaluation
                    price_js = await page.evaluate('''
                        () => {
                            // Look for price in window.adobeDataLayer
                            if (window.adobeDataLayer) {
                                for (const item of window.adobeDataLayer) {
                                    if (item.product && item.product.price) {
                                        return item.product.price;
                                    }
                                }
                            }
                            
                            // Look for price in any data attribute
                            const priceElements = document.querySelectorAll('[data-auto-id="product-price"], [data-auto-id="sale-price"]');
                            for (const el of priceElements) {
                                const price = el.textContent;
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
            self.logger.error(f"Error scraping Adidas US: {e}")
        
        # If all extraction methods fail, use the fallback price
        if not price:
            price = fallback_price
            self.logger.info(f"Using fallback price for Adidas US: ${price} USD")
        
        return price

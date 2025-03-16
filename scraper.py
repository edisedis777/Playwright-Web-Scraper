import asyncio
import csv
import logging
import re
import random
import time
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError

class WebScraper:
    def __init__(self, url, output_file, delay_range=(1, 3)):
        self.url = url
        self.output_file = output_file
        self.delay_range = delay_range
        self.setup_logger()
        
    def setup_logger(self):
        logging.basicConfig(
            filename=f'scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger()
        
    async def initialize_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.page = await self.context.new_page()
        self.logger.info(f"Browser initialized for {self.url}")
        
    async def navigate_to_url(self, url=None, timeout=30000):
        target_url = url or self.url
        try:
            response = await self.page.goto(target_url, timeout=timeout, wait_until="networkidle")
            if response.status >= 400:
                self.logger.error(f"Failed to navigate to {target_url}: HTTP {response.status}")
                return False
            self.logger.info(f"Successfully navigated to {target_url}")
            return True
        except TimeoutError:
            self.logger.error(f"Timeout while navigating to {target_url}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to navigate to {target_url}: {str(e)}")
            return False
            
    async def get_total_pages(self):
        try:
            page_links = await self.page.query_selector_all("a[href*='?page=']")
            pages = []
            for link in page_links:
                href = await link.get_attribute("href")
                match = re.search(r"\?page=(\d+)", href)
                if match:
                    pages.append(int(match.group(1)))
            if pages:
                return max(pages)
            return 1
        except Exception as e:
            self.logger.error(f"Failed to get total pages: {str(e)}")
            return 1
            
    async def random_delay(self):
        delay = random.uniform(*self.delay_range)
        self.logger.debug(f"Waiting for {delay:.2f} seconds")
        await asyncio.sleep(delay)
            
    async def extract_data(self):
        try:
            companies = await self.page.query_selector_all(".company-item")
            results = []
            for company in companies:
                name_elem = await company.query_selector(".name")
                location_elem = await company.query_selector(".location")
                revenue_elem = await company.query_selector(".revenue")
                employees_elem = await company.query_selector(".employees")
                
                name = await name_elem.inner_text() if name_elem else "N/A"
                location = await location_elem.inner_text() if location_elem else "N/A"
                revenue = await revenue_elem.inner_text() if revenue_elem else "N/A"
                employees = await employees_elem.inner_text() if employees_elem else "N/A"
                
                results.append({
                    "name": name.strip(),
                    "location": location.strip(),
                    "revenue": revenue.strip(),
                    "employees": employees.strip(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            self.logger.info(f"Extracted {len(results)} companies")
            return results
        except Exception as e:
            self.logger.error(f"Data extraction failed: {str(e)}")
            return []
            
    def save_to_csv(self, data, mode='w'):
        try:
            if not data:
                self.logger.warning("No data to save")
                return False
                
            field_names = list(data[0].keys()) if data else []
            
            file_mode = mode
            header = True
            
            # If appending and file exists, don't write header
            if mode == 'a':
                try:
                    with open(self.output_file, 'r', newline='', encoding='utf-8') as f:
                        header = False
                except FileNotFoundError:
                    header = True
            
            with open(self.output_file, file_mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=field_names)
                if header:
                    writer.writeheader()
                writer.writerows(data)
                
            self.logger.info(f"Data saved to {self.output_file} ({len(data)} records)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save CSV: {str(e)}")
            return False
            
    async def close(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
        self.logger.info("Browser closed")
        
    async def run(self, max_pages=None):
        self.logger.info("Starting web scraping job")
        await self.initialize_browser()
        
        if await self.navigate_to_url():
            total_pages = await self.get_total_pages()
            if max_pages and max_pages < total_pages:
                total_pages = max_pages
                
            self.logger.info(f"Found {total_pages} total pages to scrape")
            
            all_data = []
            for page in range(1, total_pages + 1):
                if page > 1:
                    page_url = f"{self.url}{'&' if '?' in self.url else '?'}page={page}"
                    success = await self.navigate_to_url(page_url)
                    if not success:
                        self.logger.warning(f"Skipping page {page} due to navigation failure")
                        continue
                
                data = await self.extract_data()
                all_data.extend(data)
                
                self.logger.info(f"Extracted {len(data)} items from page {page}/{total_pages}")
                
                # Save incrementally to avoid data loss in case of errors
                if page % 5 == 0 or page == total_pages:
                    self.save_to_csv(all_data)
                    all_data = []
                
                if page < total_pages:
                    await self.random_delay()
            
            # Save any remaining data
            if all_data:
                self.save_to_csv(all_data)
                
        await self.close()
        self.logger.info("Web scraping job completed")


class ScraperManager:
    def __init__(self):
        self.scrapers = []
        
    def add_scraper(self, url, output_file, delay_range=(1, 3)):
        scraper = WebScraper(url, output_file, delay_range)
        self.scrapers.append(scraper)
        return scraper
        
    async def run_sequential(self):
        for scraper in self.scrapers:
            await scraper.run()
            
    async def run_concurrent(self):
        tasks = [scraper.run() for scraper in self.scrapers]
        await asyncio.gather(*tasks)
        
    def run(self, concurrent=False):
        if concurrent:
            return asyncio.run(self.run_concurrent())
        else:
            return asyncio.run(self.run_sequential())


if __name__ == "__main__":
    manager = ScraperManager()
    
    # Add target URLs
    manager.add_scraper(
        "https://www.dnb.com/business-directory/company-information.manufacturing.de.html", 
        "manufacturing_companies.csv",
        delay_range=(2, 5)
    )
    
    # Run scrapers sequentially (more polite to the servers)
    manager.run(concurrent=False)
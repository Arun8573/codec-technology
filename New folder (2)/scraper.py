import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict, Any, Optional, List
import time
import logging
from config import DEFAULT_USER_AGENT, DEFAULT_TIMEOUT, DEFAULT_WAIT_TIME

class WebScraper:
    def __init__(self, use_selenium: bool = False, headless: bool = True):
        self.use_selenium = use_selenium
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': DEFAULT_USER_AGENT})
        
        if use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver with Chrome"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--user-agent={DEFAULT_USER_AGENT}")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(DEFAULT_TIMEOUT)
        except Exception as e:
            logging.error(f"Failed to setup Selenium: {e}")
            self.use_selenium = False
    
    def scrape_with_requests(self, url: str) -> Dict[str, Any]:
        """Scrape website using requests and BeautifulSoup"""
        try:
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract main content (customize based on target website)
            content = self._extract_content(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, response)
            
            return {
                'url': url,
                'title': title_text,
                'content': content,
                'metadata': metadata,
                'source': 'requests',
                'status': 'success'
            }
            
        except Exception as e:
            logging.error(f"Error scraping {url} with requests: {e}")
            return {
                'url': url,
                'title': '',
                'content': '',
                'metadata': {},
                'source': 'requests',
                'status': f'error: {str(e)}'
            }
    
    def scrape_with_selenium(self, url: str) -> Dict[str, Any]:
        """Scrape website using Selenium"""
        if not self.driver:
            return {
                'url': url,
                'title': '',
                'content': '',
                'metadata': {},
                'source': 'selenium',
                'status': 'error: Selenium not initialized'
            }
        
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, DEFAULT_WAIT_TIME).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Allow JavaScript to execute
            time.sleep(2)
            
            # Extract information
            title = self.driver.title
            content = self._extract_content_selenium()
            metadata = self._extract_metadata_selenium()
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'metadata': metadata,
                'source': 'selenium',
                'status': 'success'
            }
            
        except Exception as e:
            logging.error(f"Error scraping {url} with Selenium: {e}")
            return {
                'url': url,
                'title': '',
                'content': '',
                'metadata': {},
                'source': 'selenium',
                'status': f'error: {str(e)}'
            }
    
    def scrape(self, url: str) -> Dict[str, Any]:
        """Main scraping method that chooses between requests and Selenium"""
        if self.use_selenium:
            return self.scrape_with_selenium(url)
        else:
            return self.scrape_with_requests(url)
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from BeautifulSoup object"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main', 'article', '.content', '.main-content', 
            '#content', '#main', '.post-content', '.entry-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=' ', strip=True)
        
        # Fallback to body text
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_content_selenium(self) -> str:
        """Extract main content from Selenium WebDriver"""
        try:
            # Try to find main content areas
            content_selectors = [
                'main', 'article', '.content', '.main-content', 
                '#content', '#main', '.post-content', '.entry-content'
            ]
            
            for selector in content_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element.text.strip()
                except:
                    continue
            
            # Fallback to body text
            body = self.driver.find_element(By.TAG_NAME, "body")
            return body.text.strip()
            
        except Exception as e:
            logging.error(f"Error extracting content with Selenium: {e}")
            return ""
    
    def _extract_metadata(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """Extract metadata from BeautifulSoup object"""
        metadata = {}
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Links
        links = soup.find_all('a', href=True)
        metadata['links'] = [link['href'] for link in links[:10]]  # First 10 links
        
        # Images
        images = soup.find_all('img', src=True)
        metadata['images'] = [img['src'] for img in images[:10]]  # First 10 images
        
        # Response info
        metadata['status_code'] = response.status_code
        metadata['content_type'] = response.headers.get('content-type', '')
        
        return metadata
    
    def _extract_metadata_selenium(self) -> Dict[str, Any]:
        """Extract metadata from Selenium WebDriver"""
        metadata = {}
        
        try:
            # Meta tags
            meta_elements = self.driver.find_elements(By.TAG_NAME, "meta")
            for meta in meta_elements:
                name = meta.get_attribute('name') or meta.get_attribute('property')
                content = meta.get_attribute('content')
                if name and content:
                    metadata[name] = content
            
            # Links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            metadata['links'] = [link.get_attribute('href') for link in links[:10] if link.get_attribute('href')]
            
            # Images
            images = self.driver.find_elements(By.TAG_NAME, "img")
            metadata['images'] = [img.get_attribute('src') for img in images[:10] if img.get_attribute('src')]
            
        except Exception as e:
            logging.error(f"Error extracting metadata with Selenium: {e}")
        
        return metadata
    
    def close(self):
        """Close Selenium WebDriver if it exists"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class ScrapingManager:
    def __init__(self, use_selenium: bool = False):
        self.use_selenium = use_selenium
        self.scrapers = {}
    
    def get_scraper(self, url: str) -> WebScraper:
        """Get or create a scraper for a specific URL"""
        if url not in self.scrapers:
            self.scrapers[url] = WebScraper(use_selenium=self.use_selenium)
        return self.scrapers[url]
    
    def scrape_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs"""
        results = []
        for url in urls:
            scraper = self.get_scraper(url)
            result = scraper.scrape(url)
            results.append(result)
        return results
    
    def close_all(self):
        """Close all scrapers"""
        for scraper in self.scrapers.values():
            scraper.close()
        self.scrapers.clear()

#!/usr/bin/env python3
"""
Example Usage of the Automated Web Scraper
This script demonstrates how to use the web scraper programmatically
"""

import time
from database import DatabaseManager
from scraper import WebScraper, ScrapingManager
from scheduler import ScrapingScheduler

def example_basic_scraping():
    """Example of basic scraping functionality"""
    print("=== Basic Scraping Example ===")
    
    # Example URLs to scrape
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml"
    ]
    
    print(f"Scraping {len(urls)} URLs...")
    
    # Use BeautifulSoup (default)
    with WebScraper(use_selenium=False) as scraper:
        for url in urls:
            print(f"\nScraping: {url}")
            result = scraper.scrape(url)
            print(f"Title: {result['title'][:50]}...")
            print(f"Status: {result['status']}")
            print(f"Content length: {len(result['content'])} characters")

def example_selenium_scraping():
    """Example of Selenium scraping for JavaScript-heavy sites"""
    print("\n=== Selenium Scraping Example ===")
    
    # Note: This requires Chrome/Chromium to be installed
    try:
        with WebScraper(use_selenium=True, headless=True) as scraper:
            url = "https://httpbin.org/html"
            print(f"Scraping with Selenium: {url}")
            result = scraper.scrape(url)
            print(f"Title: {result['title']}")
            print(f"Status: {result['status']}")
    except Exception as e:
        print(f"Selenium scraping failed (Chrome not available): {e}")

def example_database_operations():
    """Example of database operations"""
    print("\n=== Database Operations Example ===")
    
    db = DatabaseManager()
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Database statistics: {stats}")
    
    # Get recent data
    recent_data = db.get_scraped_data(limit=5)
    print(f"Recent records: {len(recent_data)}")
    
    # Export to CSV
    try:
        csv_path = db.export_to_csv("example_export.csv")
        print(f"Data exported to: {csv_path}")
    except Exception as e:
        print(f"Export failed: {e}")

def example_scheduling():
    """Example of scheduling scraping jobs"""
    print("\n=== Scheduling Example ===")
    
    scheduler = ScrapingScheduler()
    
    # Schedule a URL for hourly scraping
    try:
        job_id = scheduler.schedule_url(
            url="https://httpbin.org/html",
            schedule="hourly",
            use_selenium=False
        )
        print(f"Scheduled hourly scraping job with ID: {job_id}")
        
        # Get scheduled jobs
        jobs = scheduler.get_scheduled_jobs()
        print(f"Active scheduled jobs: {len(jobs)}")
        
        # Remove the scheduled job
        scheduler.remove_scheduled_job(job_id)
        print(f"Removed scheduled job {job_id}")
        
    except Exception as e:
        print(f"Scheduling failed: {e}")

def example_batch_scraping():
    """Example of batch scraping"""
    print("\n=== Batch Scraping Example ===")
    
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml"
    ]
    
    try:
        scheduler = ScrapingScheduler()
        task_id = scheduler.run_batch_scrape(urls, use_selenium=False)
        print(f"Batch scraping task started with ID: {task_id}")
        
        # Wait a bit and check status
        time.sleep(2)
        status = scheduler.get_task_status(task_id)
        print(f"Task status: {status}")
        
    except Exception as e:
        print(f"Batch scraping failed: {e}")

def example_custom_scraping():
    """Example of custom scraping with specific selectors"""
    print("\n=== Custom Scraping Example ===")
    
    # This would be a custom scraper for a specific website
    # You can extend the WebScraper class for site-specific logic
    print("Custom scraping would involve extending the WebScraper class")
    print("to handle specific website structures and selectors.")

def main():
    """Run all examples"""
    print("Automated Web Scraper - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_scraping()
        example_selenium_scraping()
        example_database_operations()
        example_scheduling()
        example_batch_scraping()
        example_custom_scraping()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("\nTo run the scraper with command line interface:")
        print("python main.py --help")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure all dependencies are installed and the database is accessible.")

if __name__ == "__main__":
    main()

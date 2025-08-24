#!/usr/bin/env python3
"""
Automated Web Scraper with Scheduler
Main application entry point
"""

import argparse
import sys
import logging
from typing import List, Optional
from datetime import datetime
import json

from config import SUPPORTED_FORMATS
from database import DatabaseManager
from scraper import ScrapingManager, WebScraper
from scheduler import ScrapingScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scrape_single_url(url: str, use_selenium: bool = False, save_to_db: bool = True) -> dict:
    """Scrape a single URL and optionally save to database"""
    try:
        logger.info(f"Scraping URL: {url}")
        
        with WebScraper(use_selenium=use_selenium) as scraper:
            result = scraper.scrape(url)
        
        if save_to_db:
            db = DatabaseManager()
            record_id = db.insert_scraped_data(result)
            logger.info(f"Data saved to database with ID: {record_id}")
            result['database_id'] = record_id
        
        return result
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {
            'url': url,
            'error': str(e),
            'status': 'failed'
        }

def scrape_multiple_urls(urls: List[str], use_selenium: bool = False, save_to_db: bool = True) -> List[dict]:
    """Scrape multiple URLs"""
    results = []
    
    for url in urls:
        result = scrape_single_url(url, use_selenium, save_to_db)
        results.append(result)
        
        # Add a small delay between requests to be respectful
        import time
        time.sleep(1)
    
    return results

def schedule_scraping(url: str, schedule: str, use_selenium: bool = False) -> int:
    """Schedule a URL for periodic scraping"""
    try:
        scheduler = ScrapingScheduler()
        job_id = scheduler.schedule_url(url, schedule, use_selenium)
        logger.info(f"Scheduled scraping for {url} with job ID: {job_id}")
        return job_id
    except Exception as e:
        logger.error(f"Error scheduling scraping for {url}: {e}")
        raise

def export_data(format_type: str, filename: Optional[str] = None) -> str:
    """Export scraped data to specified format"""
    if format_type not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {format_type}. Supported formats: {SUPPORTED_FORMATS}")
    
    db = DatabaseManager()
    
    if format_type == 'csv':
        return db.export_to_csv(filename)
    elif format_type == 'json':
        # Export to JSON
        data = db.get_scraped_data(limit=10000)  # Get all data
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.json"
        
        import os
        os.makedirs("exports", exist_ok=True)
        file_path = f"exports/{filename}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return file_path
    else:
        raise ValueError(f"Export format {format_type} not yet implemented")

def show_statistics():
    """Display database statistics"""
    db = DatabaseManager()
    stats = db.get_statistics()
    
    print("\n=== Database Statistics ===")
    print(f"Total Records: {stats['total_records']}")
    print(f"Active Jobs: {stats['active_jobs']}")
    
    if stats['status_counts']:
        print("\nRecords by Status:")
        for status, count in stats['status_counts'].items():
            print(f"  {status}: {count}")
    
    if stats['source_counts']:
        print("\nRecords by Source:")
        for source, count in stats['source_counts'].items():
            print(f"  {source}: {count}")

def show_recent_data(limit: int = 10):
    """Show recent scraped data"""
    db = DatabaseManager()
    data = db.get_scraped_data(limit=limit)
    
    print(f"\n=== Recent Scraped Data (Last {limit} records) ===")
    for i, record in enumerate(data, 1):
        print(f"\n{i}. URL: {record['url']}")
        print(f"   Title: {record['title'][:100]}{'...' if len(record['title']) > 100 else ''}")
        print(f"   Status: {record['status']}")
        print(f"   Scraped: {record['scraped_at']}")
        print(f"   Source: {record['source']}")

def main():
    parser = argparse.ArgumentParser(
        description="Automated Web Scraper with Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single URL
  python main.py scrape --url "https://example.com"
  
  # Scrape with Selenium (for JavaScript-heavy sites)
  python main.py scrape --url "https://example.com" --selenium
  
  # Scrape multiple URLs
  python main.py scrape --urls "https://example1.com,https://example2.com"
  
  # Schedule hourly scraping
  python main.py schedule --url "https://example.com" --schedule hourly
  
  # Export data to CSV
  python main.py export --format csv
  
  # Show statistics
  python main.py stats
  
  # Show recent data
  python main.py show --limit 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape websites')
    scrape_parser.add_argument('--url', help='Single URL to scrape')
    scrape_parser.add_argument('--urls', help='Comma-separated list of URLs to scrape')
    scrape_parser.add_argument('--selenium', action='store_true', help='Use Selenium for JavaScript-heavy sites')
    scrape_parser.add_argument('--no-save', action='store_true', help='Do not save to database')
    scrape_parser.add_argument('--output', help='Output file for results (JSON format)')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule periodic scraping')
    schedule_parser.add_argument('--url', required=True, help='URL to schedule')
    schedule_parser.add_argument('--schedule', required=True, 
                               choices=['hourly', 'daily', 'weekly', 'cron'],
                               help='Scraping schedule')
    schedule_parser.add_argument('--selenium', action='store_true', help='Use Selenium')
    schedule_parser.add_argument('--cron-expr', help='Custom cron expression (e.g., "0,30,*,*,*" for every 30 minutes)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export scraped data')
    export_parser.add_argument('--format', required=True, choices=SUPPORTED_FORMATS, help='Export format')
    export_parser.add_argument('--filename', help='Output filename')
    
    # Statistics command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show recent scraped data')
    show_parser.add_argument('--limit', type=int, default=10, help='Number of records to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'scrape':
            if args.url:
                # Single URL scraping
                result = scrape_single_url(args.url, args.selenium, not args.no_save)
                print(json.dumps(result, indent=2, default=str))
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(result, f, indent=2, default=str)
                    print(f"\nResults saved to: {args.output}")
                    
            elif args.urls:
                # Multiple URLs scraping
                url_list = [url.strip() for url in args.urls.split(',')]
                results = scrape_multiple_urls(url_list, args.selenium, not args.no_save)
                print(json.dumps(results, indent=2, default=str))
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(results, f, indent=2, default=str)
                    print(f"\nResults saved to: {args.output}")
            else:
                scrape_parser.error("Either --url or --urls must be specified")
        
        elif args.command == 'schedule':
            schedule_type = args.schedule
            if args.schedule == 'cron' and args.cron_expr:
                schedule_type = f"cron:{args.cron_expr}"
            
            job_id = schedule_scraping(args.url, schedule_type, args.selenium)
            print(f"Successfully scheduled scraping for {args.url} with job ID: {job_id}")
        
        elif args.command == 'export':
            file_path = export_data(args.format, args.filename)
            print(f"Data exported to: {file_path}")
        
        elif args.command == 'stats':
            show_statistics()
        
        elif args.command == 'show':
            show_recent_data(args.limit)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

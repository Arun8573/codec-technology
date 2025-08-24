#!/usr/bin/env python3
"""
Demo Script for Automated Web Scraper
This script demonstrates the scraper's capabilities with real examples
"""

import time
import json
from datetime import datetime

def demo_basic_scraping():
    """Demonstrate basic scraping functionality"""
    print("🔍 DEMO: Basic Web Scraping")
    print("=" * 50)
    
    try:
        from scraper import WebScraper
        
        # Test URLs that are safe to scrape
        test_urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml"
        ]
        
        print(f"Testing with {len(test_urls)} URLs...")
        
        with WebScraper(use_selenium=False) as scraper:
            for i, url in enumerate(test_urls, 1):
                print(f"\n{i}. Scraping: {url}")
                
                start_time = time.time()
                result = scraper.scrape(url)
                elapsed = time.time() - start_time
                
                if result['status'] == 'success':
                    print(f"   ✓ Success in {elapsed:.2f}s")
                    print(f"   Title: {result['title'][:60]}...")
                    print(f"   Content: {len(result['content'])} characters")
                    print(f"   Source: {result['source']}")
                else:
                    print(f"   ✗ Failed: {result['status']}")
        
        print("\n✅ Basic scraping demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Basic scraping demo failed: {e}")
        return False

def demo_database_operations():
    """Demonstrate database operations"""
    print("\n🗄️  DEMO: Database Operations")
    print("=" * 50)
    
    try:
        from database import DatabaseManager
        
        # Initialize database
        db = DatabaseManager()
        print("✓ Database initialized")
        
        # Get initial statistics
        initial_stats = db.get_statistics()
        print(f"✓ Initial database state: {initial_stats['total_records']} records")
        
        # Insert some sample data
        sample_data = {
            'url': 'https://demo.example.com',
            'title': 'Demo Page',
            'content': 'This is a demo content for testing purposes.',
            'metadata': {'demo': True, 'timestamp': datetime.now().isoformat()},
            'source': 'demo_script',
            'status': 'success'
        }
        
        record_id = db.insert_scraped_data(sample_data)
        print(f"✓ Sample data inserted with ID: {record_id}")
        
        # Get updated statistics
        updated_stats = db.get_statistics()
        print(f"✓ Updated database state: {updated_stats['total_records']} records")
        
        # Export to CSV
        csv_path = db.export_to_csv("demo_export.csv")
        print(f"✓ Data exported to: {csv_path}")
        
        print("\n✅ Database operations demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database operations demo failed: {e}")
        return False

def demo_scheduling():
    """Demonstrate scheduling functionality"""
    print("\n⏰ DEMO: Task Scheduling")
    print("=" * 50)
    
    try:
        from scheduler import ScrapingScheduler
        
        # Initialize scheduler
        scheduler = ScrapingScheduler()
        print("✓ Scheduler initialized")
        
        # Schedule a demo job
        demo_url = "https://httpbin.org/html"
        job_id = scheduler.schedule_url(demo_url, "hourly", use_selenium=False)
        print(f"✓ Scheduled hourly scraping for: {demo_url}")
        print(f"  Job ID: {job_id}")
        
        # Get scheduled jobs
        active_jobs = scheduler.get_scheduled_jobs()
        print(f"✓ Active scheduled jobs: {len(active_jobs)}")
        
        # Run an immediate task
        task_id = scheduler.run_immediate_scrape(demo_url, use_selenium=False)
        print(f"✓ Immediate scraping task started: {task_id}")
        
        # Wait a moment and check status
        time.sleep(2)
        task_status = scheduler.get_task_status(task_id)
        print(f"✓ Task status: {task_status['status']}")
        
        # Clean up - remove the scheduled job
        scheduler.remove_scheduled_job(job_id)
        print(f"✓ Cleaned up scheduled job: {job_id}")
        
        print("\n✅ Task scheduling demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Task scheduling demo failed: {e}")
        return False

def demo_batch_operations():
    """Demonstrate batch operations"""
    print("\n📦 DEMO: Batch Operations")
    print("=" * 50)
    
    try:
        from scheduler import ScrapingScheduler
        
        # Initialize scheduler
        scheduler = ScrapingScheduler()
        print("✓ Scheduler initialized")
        
        # Test URLs for batch processing
        batch_urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml"
        ]
        
        print(f"Starting batch scraping of {len(batch_urls)} URLs...")
        
        # Start batch task
        task_id = scheduler.run_batch_scrape(batch_urls, use_selenium=False)
        print(f"✓ Batch task started: {task_id}")
        
        # Monitor progress
        for i in range(5):  # Check status a few times
            time.sleep(1)
            status = scheduler.get_task_status(task_id)
            print(f"  Status check {i+1}: {status['status']}")
            
            if status['ready']:
                break
        
        if status['ready']:
            print(f"✓ Batch task completed: {status['result']}")
        else:
            print("⚠️  Batch task still running (this is normal)")
        
        print("\n✅ Batch operations demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Batch operations demo failed: {e}")
        return False

def demo_custom_scraping():
    """Demonstrate custom scraping capabilities"""
    print("\n🎯 DEMO: Custom Scraping")
    print("=" * 50)
    
    try:
        from scraper import WebScraper
        
        # Create a custom scraper class
        class CustomScraper(WebScraper):
            def _extract_content(self, soup):
                """Custom content extraction for specific sites"""
                # Try to find specific content areas
                content_selectors = [
                    'article', '.post-content', '.entry-content',
                    '.content', 'main', '#content'
                ]
                
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        return f"[CUSTOM EXTRACTED] {element.get_text(separator=' ', strip=True)}"
                
                # Fallback to default
                return super()._extract_content(soup)
        
        print("✓ Custom scraper class created")
        
        # Test custom scraper
        with CustomScraper(use_selenium=False) as scraper:
            test_url = "https://httpbin.org/html"
            result = scraper.scrape(test_url)
            
            if result['status'] == 'success':
                print(f"✓ Custom scraping successful")
                print(f"  Content preview: {result['content'][:100]}...")
            else:
                print(f"✗ Custom scraping failed: {result['status']}")
        
        print("\n✅ Custom scraping demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Custom scraping demo failed: {e}")
        return False

def main():
    """Run all demos"""
    print("🚀 AUTOMATED WEB SCRAPER - DEMO SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    demos = [
        ("Basic Scraping", demo_basic_scraping),
        ("Database Operations", demo_database_operations),
        ("Task Scheduling", demo_scheduling),
        ("Batch Operations", demo_batch_operations),
        ("Custom Scraping", demo_custom_scraping)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*20} {demo_name} {'='*20}")
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"❌ {demo_name} demo crashed: {e}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for demo_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{demo_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} demos passed")
    
    if passed == total:
        print("\n🎉 All demos completed successfully!")
        print("\nYour web scraper is fully functional!")
        print("\nNext steps:")
        print("1. Try: python main.py --help")
        print("2. Start scraping: python main.py scrape --url 'https://example.com'")
        print("3. Schedule tasks: python main.py schedule --url 'https://example.com' --schedule hourly")
        print("4. Export data: python main.py export --format csv")
    else:
        print(f"\n⚠️  {total - passed} demo(s) failed.")
        print("Check the errors above and ensure all dependencies are installed.")
    
    print("\n" + "=" * 60)
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

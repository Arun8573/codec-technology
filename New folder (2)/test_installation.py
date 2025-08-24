#!/usr/bin/env python3
"""
Test Installation Script
Run this to verify that all components are working correctly
"""

import sys
import importlib
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing module imports...")
    
    required_modules = [
        'requests',
        'bs4',
        'selenium',
        'celery',
        'pandas',
        'lxml',
        'webdriver_manager'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\nAll required modules imported successfully!")
        return True

def test_local_modules():
    """Test if local project modules can be imported"""
    print("\nTesting local module imports...")
    
    local_modules = [
        'config',
        'database',
        'scraper',
        'scheduler'
    ]
    
    failed_imports = []
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed to import local modules: {', '.join(failed_imports)}")
        return False
    else:
        print("\nAll local modules imported successfully!")
        return True

def test_database():
    """Test database initialization"""
    print("\nTesting database initialization...")
    
    try:
        from database import DatabaseManager
        
        # Test database creation
        db = DatabaseManager()
        print("✓ Database manager created")
        
        # Test statistics
        stats = db.get_statistics()
        print("✓ Database statistics retrieved")
        
        # Test data retrieval
        data = db.get_scraped_data(limit=1)
        print("✓ Database data retrieval working")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_scraper():
    """Test basic scraper functionality"""
    print("\nTesting scraper functionality...")
    
    try:
        from scraper import WebScraper
        
        # Test scraper creation
        with WebScraper(use_selenium=False) as scraper:
            print("✓ Scraper created successfully")
            
            # Test with a simple URL
            test_url = "https://httpbin.org/html"
            result = scraper.scrape(test_url)
            
            if result['status'] == 'success':
                print("✓ Basic scraping working")
                print(f"  Title: {result['title'][:50]}...")
                print(f"  Content length: {len(result['content'])} characters")
            else:
                print(f"✗ Scraping failed: {result['status']}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Scraper test failed: {e}")
        return False

def test_scheduler():
    """Test scheduler functionality"""
    print("\nTesting scheduler functionality...")
    
    try:
        from scheduler import ScrapingScheduler
        
        # Test scheduler creation
        scheduler = ScrapingScheduler()
        print("✓ Scheduler created successfully")
        
        # Test getting scheduled jobs
        jobs = scheduler.get_scheduled_jobs()
        print(f"✓ Retrieved {len(jobs)} scheduled jobs")
        
        return True
        
    except Exception as e:
        print(f"✗ Scheduler test failed: {e}")
        return False

def test_celery():
    """Test Celery configuration"""
    print("\nTesting Celery configuration...")
    
    try:
        from scheduler import celery_app
        
        # Test Celery app configuration
        print(f"✓ Celery app: {celery_app.main}")
        print(f"✓ Broker URL: {celery_app.conf.broker_url}")
        print(f"✓ Result backend: {celery_app.conf.result_backend}")
        
        return True
        
    except Exception as e:
        print(f"✗ Celery test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Automated Web Scraper - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Local Modules", test_local_modules),
        ("Database", test_database),
        ("Scraper", test_scraper),
        ("Scheduler", test_scheduler),
        ("Celery", test_celery)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your installation is working correctly.")
        print("\nYou can now:")
        print("1. Run: python main.py --help")
        print("2. Try: python example_usage.py")
        print("3. Start scraping: python main.py scrape --url 'https://example.com'")
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check Python version (requires 3.7+)")
        print("3. Ensure all files are in the same directory")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

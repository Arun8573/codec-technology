#!/usr/bin/env python3
"""
Celery Beat Scheduler for Web Scraper
Run this script to start the Celery beat scheduler that triggers periodic scraping tasks
"""

import os
import sys
import logging
from celery import Celery
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_beat():
    """Start the Celery beat scheduler"""
    try:
        # Initialize Celery app
        app = Celery('web_scraper')
        app.config_from_object({
            'broker_url': CELERY_BROKER_URL,
            'result_backend': CELERY_RESULT_BACKEND,
            'task_serializer': 'json',
            'accept_content': ['json'],
            'result_serializer': 'json',
            'timezone': 'UTC',
            'enable_utc': True,
            'beat_schedule_filename': 'celerybeat-schedule',
            'beat_sync_every': 1,
        })
        
        # Import tasks and scheduler to register them
        from scheduler import scrape_url_task, scrape_multiple_urls_task, ScrapingScheduler
        
        # Load existing scheduled jobs from database
        scheduler = ScrapingScheduler()
        active_jobs = scheduler.get_scheduled_jobs()
        
        logger.info("Starting Celery beat scheduler for web scraper...")
        logger.info(f"Broker URL: {CELERY_BROKER_URL}")
        logger.info(f"Result Backend: {CELERY_RESULT_BACKEND}")
        logger.info(f"Found {len(active_jobs)} active scheduled jobs")
        
        # Start beat scheduler
        app.worker_main([
            'beat',
            '--loglevel=info',
            '--scheduler=celery.beat:PersistentScheduler'
        ])
        
    except KeyboardInterrupt:
        logger.info("Beat scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting beat scheduler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_beat()

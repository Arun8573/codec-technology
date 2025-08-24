#!/usr/bin/env python3
"""
Celery Worker for Web Scraper
Run this script to start the Celery worker that processes scraping tasks
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

def start_worker():
    """Start the Celery worker"""
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
            'worker_prefetch_multiplier': 1,
            'task_acks_late': True,
            'worker_max_tasks_per_child': 1000,
        })
        
        # Import tasks to register them
        from scheduler import scrape_url_task, scrape_multiple_urls_task
        
        logger.info("Starting Celery worker for web scraper...")
        logger.info(f"Broker URL: {CELERY_BROKER_URL}")
        logger.info(f"Result Backend: {CELERY_RESULT_BACKEND}")
        
        # Start worker
        app.worker_main([
            'worker',
            '--loglevel=info',
            '--queues=scraping',
            '--concurrency=2',
            '--hostname=scraper-worker@%h'
        ])
        
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_worker()

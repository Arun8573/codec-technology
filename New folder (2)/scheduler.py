from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
import json
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, DEFAULT_SCHEDULE_INTERVAL
from database import DatabaseManager
from scraper import ScrapingManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery('web_scraper')
celery_app.config_from_object({
    'broker_url': CELERY_BROKER_URL,
    'result_backend': CELERY_RESULT_BACKEND,
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
})

@celery_app.task(bind=True, max_retries=3)
def scrape_url_task(self, url: str, use_selenium: bool = False) -> Dict[str, Any]:
    """Celery task to scrape a single URL"""
    try:
        logger.info(f"Starting scraping task for URL: {url}")
        
        # Initialize scraper
        with ScrapingManager(use_selenium=use_selenium) as scraping_manager:
            scraper = scraping_manager.get_scraper(url)
            result = scraper.scrape(url)
        
        # Store result in database
        db = DatabaseManager()
        record_id = db.insert_scraped_data(result)
        
        logger.info(f"Successfully scraped {url}, record ID: {record_id}")
        return {
            'success': True,
            'record_id': record_id,
            'url': url,
            'result': result
        }
        
    except Exception as exc:
        logger.error(f"Error scraping {url}: {exc}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying scraping {url} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)
        else:
            logger.error(f"Max retries reached for {url}")
            
            # Store error in database
            error_result = {
                'url': url,
                'title': '',
                'content': '',
                'metadata': {},
                'source': 'celery_task',
                'status': f'error: {str(exc)}'
            }
            
            db = DatabaseManager()
            db.insert_scraped_data(error_result)
            
            return {
                'success': False,
                'url': url,
                'error': str(exc)
            }

@celery_app.task
def scrape_multiple_urls_task(urls: List[str], use_selenium: bool = False) -> Dict[str, Any]:
    """Celery task to scrape multiple URLs"""
    try:
        logger.info(f"Starting batch scraping task for {len(urls)} URLs")
        
        results = []
        with ScrapingManager(use_selenium=use_selenium) as scraping_manager:
            for url in urls:
                try:
                    scraper = scraping_manager.get_scraper(url)
                    result = scraper.scrape(url)
                    results.append(result)
                    
                    # Store in database
                    db = DatabaseManager()
                    db.insert_scraped_data(result)
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    error_result = {
                        'url': url,
                        'title': '',
                        'content': '',
                        'metadata': {},
                        'source': 'batch_task',
                        'status': f'error: {str(e)}'
                    }
                    results.append(error_result)
                    
                    # Store error in database
                    db = DatabaseManager()
                    db.insert_scraped_data(error_result)
        
        logger.info(f"Completed batch scraping task. Successfully scraped {len([r for r in results if r['status'] == 'success'])} URLs")
        return {
            'success': True,
            'total_urls': len(urls),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] != 'success']),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error in batch scraping task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

class ScrapingScheduler:
    def __init__(self):
        self.celery_app = celery_app
        self.db = DatabaseManager()
    
    def schedule_url(self, url: str, schedule: str, use_selenium: bool = False) -> int:
        """Schedule a URL for periodic scraping"""
        try:
            # Add to database
            job_id = self.db.add_scraping_job(url, schedule)
            
            # Parse schedule and add to Celery
            if schedule == 'hourly':
                self._schedule_hourly(url, job_id, use_selenium)
            elif schedule == 'daily':
                self._schedule_daily(url, job_id, use_selenium)
            elif schedule == 'weekly':
                self._schedule_weekly(url, job_id, use_selenium)
            elif schedule.startswith('cron:'):
                self._schedule_cron(url, job_id, schedule, use_selenium)
            else:
                # Default to hourly
                self._schedule_hourly(url, job_id, use_selenium)
            
            logger.info(f"Scheduled URL {url} with job ID {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error scheduling URL {url}: {e}")
            raise
    
    def _schedule_hourly(self, url: str, job_id: int, use_selenium: bool):
        """Schedule hourly scraping"""
        self.celery_app.conf.beat_schedule[f'scrape_hourly_{job_id}'] = {
            'task': 'scheduler.scrape_url_task',
            'schedule': crontab(minute=0),  # Every hour at minute 0
            'args': (url, use_selenium),
            'options': {'queue': 'scraping'}
        }
    
    def _schedule_daily(self, url: str, job_id: int, use_selenium: bool):
        """Schedule daily scraping"""
        self.celery_app.conf.beat_schedule[f'scrape_daily_{job_id}'] = {
            'task': 'scheduler.scrape_url_task',
            'schedule': crontab(hour=0, minute=0),  # Every day at midnight
            'args': (url, use_selenium),
            'options': {'queue': 'scraping'}
        }
    
    def _schedule_weekly(self, url: str, job_id: int, use_selenium: bool):
        """Schedule weekly scraping"""
        self.celery_app.conf.beat_schedule[f'scrape_weekly_{job_id}'] = {
            'task': 'scheduler.scrape_url_task',
            'schedule': crontab(day_of_week=0, hour=0, minute=0),  # Every Sunday at midnight
            'args': (url, use_selenium),
            'options': {'queue': 'scraping'}
        }
    
    def _schedule_cron(self, url: str, job_id: int, cron_schedule: str, use_selenium: bool):
        """Schedule with custom cron expression"""
        try:
            # Parse cron:minute,hour,day,month,day_of_week
            cron_parts = cron_schedule.replace('cron:', '').split(',')
            if len(cron_parts) == 5:
                minute, hour, day, month, day_of_week = cron_parts
                
                self.celery_app.conf.beat_schedule[f'scrape_cron_{job_id}'] = {
                    'task': 'scheduler.scrape_url_task',
                    'schedule': crontab(
                        minute=minute if minute != '*' else None,
                        hour=hour if hour != '*' else None,
                        day=day if day != '*' else None,
                        month=month if month != '*' else None,
                        day_of_week=day_of_week if day_of_week != '*' else None
                    ),
                    'args': (url, use_selenium),
                    'options': {'queue': 'scraping'}
                }
            else:
                raise ValueError("Invalid cron format. Use: cron:minute,hour,day,month,day_of_week")
                
        except Exception as e:
            logger.error(f"Error parsing cron schedule {cron_schedule}: {e}")
            # Fallback to hourly
            self._schedule_hourly(url, job_id, use_selenium)
    
    def remove_scheduled_job(self, job_id: int):
        """Remove a scheduled scraping job"""
        try:
            # Update database status
            self.db.update_job_status(job_id, 'inactive')
            
            # Remove from Celery beat schedule
            schedule_keys = [
                f'scrape_hourly_{job_id}',
                f'scrape_daily_{job_id}',
                f'scrape_weekly_{job_id}',
                f'scrape_cron_{job_id}'
            ]
            
            for key in schedule_keys:
                if key in self.celery_app.conf.beat_schedule:
                    del self.celery_app.conf.beat_schedule[key]
            
            logger.info(f"Removed scheduled job {job_id}")
            
        except Exception as e:
            logger.error(f"Error removing scheduled job {job_id}: {e}")
            raise
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs"""
        return self.db.get_active_jobs()
    
    def run_immediate_scrape(self, url: str, use_selenium: bool = False) -> str:
        """Run an immediate scraping task"""
        task = scrape_url_task.delay(url, use_selenium)
        return task.id
    
    def run_batch_scrape(self, urls: List[str], use_selenium: bool = False) -> str:
        """Run a batch scraping task"""
        task = scrape_multiple_urls_task.delay(urls, use_selenium)
        return task.id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a Celery task"""
        try:
            task_result = self.celery_app.AsyncResult(task_id)
            return {
                'task_id': task_id,
                'status': task_result.status,
                'result': task_result.result if task_result.ready() else None,
                'ready': task_result.ready()
            }
        except Exception as e:
            logger.error(f"Error getting task status for {task_id}: {e}")
            return {
                'task_id': task_id,
                'status': 'error',
                'error': str(e)
            }

# Configure Celery beat schedule
celery_app.conf.beat_schedule = {}

# Configure Celery routes
celery_app.conf.task_routes = {
    'scheduler.scrape_url_task': {'queue': 'scraping'},
    'scheduler.scrape_multiple_urls_task': {'queue': 'scraping'}
}

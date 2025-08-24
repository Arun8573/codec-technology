import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_PATH = "scraper_data.db"
CSV_EXPORT_PATH = "exports/"

# Scraping Configuration
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
DEFAULT_TIMEOUT = 30
DEFAULT_WAIT_TIME = 5

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Scheduler Configuration
DEFAULT_SCHEDULE_INTERVAL = 3600  # 1 hour in seconds
MAX_RETRIES = 3
RETRY_DELAY = 300  # 5 minutes

# Export Configuration
SUPPORTED_FORMATS = ['csv', 'json', 'sqlite']
MAX_EXPORT_SIZE = 10000  # Maximum records per export file

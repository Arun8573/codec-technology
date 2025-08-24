# Automated Web Scraper with Scheduler

A powerful and flexible web scraping tool built with Python that supports both BeautifulSoup and Selenium scraping, automated scheduling with Celery, and data storage in SQLite with export capabilities.

## Features

- **Dual Scraping Engines**: BeautifulSoup for static content, Selenium for JavaScript-heavy sites
- **Automated Scheduling**: Schedule scraping jobs hourly, daily, weekly, or with custom cron expressions
- **Task Queue Management**: Built-in Celery integration for background processing
- **Data Storage**: SQLite database with automatic data management
- **Export Options**: Export data to CSV, JSON, or keep in SQLite
- **Command Line Interface**: Easy-to-use CLI for all operations
- **Programmatic API**: Python classes for custom integrations
- **Error Handling**: Robust error handling with retry mechanisms
- **Logging**: Comprehensive logging for monitoring and debugging

## Requirements

- Python 3.7+
- Chrome/Chromium browser (for Selenium scraping)
- Redis (for Celery broker - optional, can use SQLite as fallback)

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome/Chromium** (for Selenium support):
   - Windows: Download from [Chrome](https://www.google.com/chrome/)
   - macOS: `brew install --cask google-chrome`
   - Linux: `sudo apt-get install chromium-browser`

4. **Optional: Install Redis** (for production use):
   - Windows: Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
   - macOS: `brew install redis`
   - Linux: `sudo apt-get install redis-server`

## Quick Start

### 1. Basic Scraping

Scrape a single website:
```bash
python main.py scrape --url "https://example.com"
```

Scrape multiple websites:
```bash
python main.py scrape --urls "https://example1.com,https://example2.com"
```

Use Selenium for JavaScript-heavy sites:
```bash
python main.py scrape --url "https://example.com" --selenium
```

### 2. Scheduled Scraping

Schedule hourly scraping:
```bash
python main.py schedule --url "https://example.com" --schedule hourly
```

Schedule daily scraping:
```bash
python main.py schedule --url "https://example.com" --schedule daily
```

Schedule weekly scraping:
```bash
python main.py schedule --url "https://example.com" --schedule weekly
```

Custom cron schedule (every 30 minutes):
```bash
python main.py schedule --url "https://example.com" --schedule cron --cron-expr "0,30,*,*,*"
```

### 3. Data Management

View database statistics:
```bash
python main.py stats
```

Show recent scraped data:
```bash
python main.py show --limit 10
```

Export data to CSV:
```bash
python main.py export --format csv
```

Export data to JSON:
```bash
python main.py export --format json
```

## Advanced Usage

### Running with Celery (Background Processing)

1. **Start the Celery worker** (in one terminal):
   ```bash
   python celery_worker.py
   ```

2. **Start the Celery beat scheduler** (in another terminal):
   ```bash
   python celery_beat.py
   ```

3. **Run scraping tasks** (in main terminal):
   ```bash
   python main.py scrape --url "https://example.com"
   ```

### Programmatic Usage

```python
from scraper import WebScraper
from database import DatabaseManager
from scheduler import ScrapingScheduler

# Basic scraping
with WebScraper(use_selenium=False) as scraper:
    result = scraper.scrape("https://example.com")
    print(result['title'])

# Database operations
db = DatabaseManager()
stats = db.get_statistics()
print(f"Total records: {stats['total_records']}")

# Scheduling
scheduler = ScrapingScheduler()
job_id = scheduler.schedule_url("https://example.com", "hourly")
```

### Custom Scraping

Extend the `WebScraper` class for site-specific logic:

```python
from scraper import WebScraper

class CustomScraper(WebScraper):
    def _extract_content(self, soup):
        # Custom content extraction logic
        content = soup.find('div', class_='article-content')
        return content.get_text() if content else ""

# Use custom scraper
with CustomScraper() as scraper:
    result = scraper.scrape("https://example.com")
```

## Configuration

Edit `config.py` to customize:

- Database paths
- Scraping timeouts and delays
- Celery broker settings
- Export options
- User agent strings

## File Structure

```
├── main.py              # Main CLI application
├── scraper.py           # Core scraping functionality
├── database.py          # Database management
├── scheduler.py         # Task scheduling with Celery
├── config.py            # Configuration settings
├── celery_worker.py     # Celery worker script
├── celery_beat.py       # Celery beat scheduler
├── example_usage.py     # Usage examples
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Database Schema

The application creates three main tables:

1. **scraped_data**: Stores all scraped content
2. **scraping_jobs**: Manages scheduled scraping tasks
3. **export_history**: Tracks data export operations

## Error Handling

The scraper includes comprehensive error handling:

- Network timeouts and connection errors
- HTML parsing errors
- Selenium WebDriver issues
- Database connection problems
- Automatic retry mechanisms for failed tasks

## Logging

All operations are logged with timestamps:

```bash
2024-01-15 10:30:00 - scraper - INFO - Starting scraping task for URL: https://example.com
2024-01-15 10:30:02 - scraper - INFO - Successfully scraped https://example.com
```

## Performance Considerations

- **Concurrency**: Celery worker supports multiple concurrent scraping tasks
- **Memory Management**: Automatic cleanup of Selenium WebDriver instances
- **Database Optimization**: Efficient SQLite queries with proper indexing
- **Rate Limiting**: Built-in delays between requests to be respectful to websites

## Troubleshooting

### Common Issues

1. **Chrome/Chromium not found**: Install Chrome browser or update ChromeDriver
2. **Selenium errors**: Ensure Chrome is installed and accessible
3. **Database errors**: Check file permissions for SQLite database
4. **Celery connection issues**: Verify Redis is running or update broker settings

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

Run the example script to see all features in action:
```bash
python example_usage.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example usage
3. Check the logs for error details
4. Open an issue with detailed information

## Roadmap

- [ ] Web interface for management
- [ ] Support for more export formats
- [ ] Advanced scheduling options
- [ ] Proxy support
- [ ] Rate limiting configuration
- [ ] Email notifications
- [ ] API endpoints for external integration

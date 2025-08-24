@echo off
echo Starting Automated Web Scraper Services...
echo.

echo Starting Celery Worker...
start "Celery Worker" cmd /k "python celery_worker.py"

echo Starting Celery Beat Scheduler...
start "Celery Beat" cmd /k "python celery_beat.py"

echo.
echo Services started in separate windows.
echo.
echo To use the scraper, open a new command prompt and run:
echo   python main.py --help
echo.
echo Press any key to exit this window...
pause > nul

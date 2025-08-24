import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
from config import DATABASE_PATH, CSV_EXPORT_PATH

class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        # Only create directory if db_path contains a directory
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create scraped_data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    content TEXT,
                    metadata TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    status TEXT DEFAULT 'success'
                )
            ''')
            
            # Create scraping_jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraping_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    schedule TEXT,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create export_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS export_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    format TEXT NOT NULL,
                    record_count INTEGER,
                    exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT
                )
            ''')
            
            conn.commit()
    
    def insert_scraped_data(self, data: Dict[str, Any]) -> int:
        """Insert scraped data into the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scraped_data (url, title, content, metadata, source, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('url'),
                data.get('title'),
                data.get('content'),
                json.dumps(data.get('metadata', {})),
                data.get('source'),
                data.get('status', 'success')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_scraped_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve scraped data from the database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM scraped_data 
                ORDER BY scraped_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def add_scraping_job(self, url: str, schedule: str) -> int:
        """Add a new scraping job to the scheduler"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scraping_jobs (url, schedule)
                VALUES (?, ?)
            ''', (url, schedule))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_job_status(self, job_id: int, status: str, last_run: Optional[datetime] = None):
        """Update the status of a scraping job"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if last_run:
                cursor.execute('''
                    UPDATE scraping_jobs 
                    SET status = ?, last_run = ?
                    WHERE id = ?
                ''', (status, last_run, job_id))
            else:
                cursor.execute('''
                    UPDATE scraping_jobs 
                    SET status = ?
                    WHERE id = ?
                ''', (status, job_id))
            
            conn.commit()
    
    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get all active scraping jobs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM scraping_jobs 
                WHERE status = 'active'
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export scraped data to CSV format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.csv"
        
        os.makedirs(CSV_EXPORT_PATH, exist_ok=True)
        file_path = os.path.join(CSV_EXPORT_PATH, filename)
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('''
                SELECT url, title, content, metadata, scraped_at, source, status
                FROM scraped_data
                ORDER BY scraped_at DESC
            ''', conn)
            
            df.to_csv(file_path, index=False)
            
            # Record export in history
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO export_history (format, record_count, file_path)
                VALUES (?, ?, ?)
            ''', ('csv', len(df), file_path))
            conn.commit()
        
        return file_path
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total records
            cursor.execute('SELECT COUNT(*) FROM scraped_data')
            total_records = cursor.fetchone()[0]
            
            # Records by status
            cursor.execute('SELECT status, COUNT(*) FROM scraped_data GROUP BY status')
            status_counts = dict(cursor.fetchall())
            
            # Records by source
            cursor.execute('SELECT source, COUNT(*) FROM scraped_data GROUP BY source')
            source_counts = dict(cursor.fetchall())
            
            # Active jobs
            cursor.execute('SELECT COUNT(*) FROM scraping_jobs WHERE status = "active"')
            active_jobs = cursor.fetchone()[0]
            
            return {
                'total_records': total_records,
                'status_counts': status_counts,
                'source_counts': source_counts,
                'active_jobs': active_jobs
            }

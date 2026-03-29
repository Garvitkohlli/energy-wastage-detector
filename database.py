"""
Database module for storing energy monitoring data
"""
import sqlite3
from datetime import datetime
import json
from contextlib import contextmanager

DATABASE_NAME = 'energy_monitor.db'

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance TEXT NOT NULL,
                power_watts REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                hour INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                is_anomaly BOOLEAN DEFAULT 0,
                anomaly_score REAL,
                deviation_percent REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Anomalies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance TEXT NOT NULL,
                power_watts REAL NOT NULL,
                expected_power REAL NOT NULL,
                deviation_percent REAL NOT NULL,
                anomaly_score REAL NOT NULL,
                severity TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cutoffs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cutoffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance TEXT NOT NULL,
                power_watts REAL NOT NULL,
                expected_power REAL NOT NULL,
                deviation_percent REAL NOT NULL,
                reason TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Model performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance TEXT NOT NULL,
                model_name TEXT NOT NULL,
                accuracy REAL,
                precision_score REAL,
                recall REAL,
                f1_score REAL,
                training_samples INTEGER,
                timestamp DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                total_readings INTEGER DEFAULT 0,
                total_anomalies INTEGER DEFAULT 0,
                total_cutoffs INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ Database initialized successfully")

def save_reading(appliance, power, timestamp, hour, day_of_week, is_anomaly=False, anomaly_score=None, deviation=None):
    """Save a power reading to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO readings (appliance, power_watts, timestamp, hour, day_of_week, 
                                is_anomaly, anomaly_score, deviation_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (appliance, power, timestamp, hour, day_of_week, is_anomaly, anomaly_score, deviation))
        return cursor.lastrowid

def save_anomaly(appliance, power, expected_power, deviation, anomaly_score, severity, timestamp):
    """Save an anomaly detection to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO anomalies (appliance, power_watts, expected_power, deviation_percent,
                                 anomaly_score, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (appliance, power, expected_power, deviation, anomaly_score, severity, timestamp))
        return cursor.lastrowid

def save_cutoff(appliance, power, expected_power, deviation, reason, timestamp):
    """Save a power cutoff event to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cutoffs (appliance, power_watts, expected_power, deviation_percent,
                               reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (appliance, power, expected_power, deviation, reason, timestamp))
        return cursor.lastrowid

def save_model_performance(appliance, model_name, accuracy, precision, recall, f1, training_samples, timestamp):
    """Save model performance metrics"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO model_performance (appliance, model_name, accuracy, precision_score,
                                         recall, f1_score, training_samples, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (appliance, model_name, accuracy, precision, recall, f1, training_samples, timestamp))
        return cursor.lastrowid

def get_readings(appliance, limit=100):
    """Get recent readings for an appliance"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM readings 
            WHERE appliance = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (appliance, limit))
        return [dict(row) for row in cursor.fetchall()]

def get_anomalies(appliance, limit=50):
    """Get recent anomalies for an appliance"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM anomalies 
            WHERE appliance = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (appliance, limit))
        return [dict(row) for row in cursor.fetchall()]

def get_cutoffs(appliance, limit=50):
    """Get recent cutoffs for an appliance"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM cutoffs 
            WHERE appliance = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (appliance, limit))
        return [dict(row) for row in cursor.fetchall()]

def get_statistics(appliance):
    """Get statistics for an appliance"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total readings
        cursor.execute('SELECT COUNT(*) as count FROM readings WHERE appliance = ?', (appliance,))
        total_readings = cursor.fetchone()['count']
        
        # Total anomalies
        cursor.execute('SELECT COUNT(*) as count FROM anomalies WHERE appliance = ?', (appliance,))
        total_anomalies = cursor.fetchone()['count']
        
        # Total cutoffs
        cursor.execute('SELECT COUNT(*) as count FROM cutoffs WHERE appliance = ?', (appliance,))
        total_cutoffs = cursor.fetchone()['count']
        
        # Average power
        cursor.execute('SELECT AVG(power_watts) as avg FROM readings WHERE appliance = ?', (appliance,))
        avg_power = cursor.fetchone()['avg'] or 0
        
        return {
            'total_readings': total_readings,
            'total_anomalies': total_anomalies,
            'total_cutoffs': total_cutoffs,
            'average_power': round(avg_power, 2)
        }

def start_session(appliance):
    """Start a new monitoring session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (appliance, start_time)
            VALUES (?, ?)
        ''', (appliance, datetime.now().isoformat()))
        return cursor.lastrowid

def end_session(session_id, readings, anomalies, cutoffs):
    """End a monitoring session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, total_readings = ?, total_anomalies = ?, total_cutoffs = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), readings, anomalies, cutoffs, session_id))

if __name__ == '__main__':
    init_database()

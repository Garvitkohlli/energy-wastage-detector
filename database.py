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
        
        # IoT Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                device_name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                ip_address TEXT,
                mac_address TEXT,
                status TEXT DEFAULT 'offline',
                last_seen DATETIME,
                power_state TEXT DEFAULT 'off',
                current_power REAL DEFAULT 0,
                total_energy REAL DEFAULT 0,
                firmware_version TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # IoT Readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                voltage REAL,
                current REAL,
                power REAL NOT NULL,
                energy REAL,
                power_factor REAL,
                temperature REAL,
                timestamp DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES iot_devices(device_id)
            )
        ''')
        
        # IoT Commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                command TEXT NOT NULL,
                parameters TEXT,
                status TEXT DEFAULT 'pending',
                response TEXT,
                sent_at DATETIME NOT NULL,
                completed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES iot_devices(device_id)
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


# ============= IoT Device Functions =============

def register_iot_device(device_id, device_name, device_type, ip_address=None, mac_address=None, firmware_version=None):
    """Register a new IoT device"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO iot_devices 
            (device_id, device_name, device_type, ip_address, mac_address, firmware_version, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (device_id, device_name, device_type, ip_address, mac_address, firmware_version, datetime.now().isoformat()))
        return cursor.lastrowid

def update_device_status(device_id, status, power_state=None, current_power=None):
    """Update IoT device status"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE iot_devices 
            SET status = ?, power_state = COALESCE(?, power_state), 
                current_power = COALESCE(?, current_power),
                last_seen = ?, updated_at = ?
            WHERE device_id = ?
        ''', (status, power_state, current_power, datetime.now().isoformat(), datetime.now().isoformat(), device_id))

def get_all_iot_devices():
    """Get all registered IoT devices"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM iot_devices ORDER BY device_name')
        return [dict(row) for row in cursor.fetchall()]

def get_iot_device(device_id):
    """Get specific IoT device"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM iot_devices WHERE device_id = ?', (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def save_iot_reading(device_id, power, voltage=None, current=None, energy=None, power_factor=None, temperature=None, timestamp=None):
    """Save IoT device reading"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO iot_readings 
            (device_id, voltage, current, power, energy, power_factor, temperature, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (device_id, voltage, current, power, energy, power_factor, temperature, timestamp))
        
        # Update device current power
        cursor.execute('''
            UPDATE iot_devices 
            SET current_power = ?, total_energy = COALESCE(?, total_energy), 
                last_seen = ?, updated_at = ?
            WHERE device_id = ?
        ''', (power, energy, timestamp, datetime.now().isoformat(), device_id))
        
        return cursor.lastrowid

def get_iot_readings(device_id, limit=100):
    """Get recent readings for an IoT device"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM iot_readings 
            WHERE device_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (device_id, limit))
        return [dict(row) for row in cursor.fetchall()]

def save_iot_command(device_id, command, parameters=None):
    """Save IoT command"""
    with get_db() as conn:
        cursor = conn.cursor()
        params_json = json.dumps(parameters) if parameters else None
        cursor.execute('''
            INSERT INTO iot_commands (device_id, command, parameters, sent_at)
            VALUES (?, ?, ?, ?)
        ''', (device_id, command, params_json, datetime.now().isoformat()))
        return cursor.lastrowid

def update_command_status(command_id, status, response=None):
    """Update command status"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE iot_commands 
            SET status = ?, response = ?, completed_at = ?
            WHERE id = ?
        ''', (status, response, datetime.now().isoformat(), command_id))

def get_device_commands(device_id, limit=50):
    """Get recent commands for a device"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM iot_commands 
            WHERE device_id = ? 
            ORDER BY sent_at DESC 
            LIMIT ?
        ''', (device_id, limit))
        return [dict(row) for row in cursor.fetchall()]

def delete_iot_device(device_id):
    """Delete an IoT device and its data"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM iot_readings WHERE device_id = ?', (device_id,))
        cursor.execute('DELETE FROM iot_commands WHERE device_id = ?', (device_id,))
        cursor.execute('DELETE FROM iot_devices WHERE device_id = ?', (device_id,))
        return cursor.rowcount > 0

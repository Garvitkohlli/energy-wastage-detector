"""
Database Inspection Tool
Run this script to view all data stored in the database
"""
import sqlite3
from datetime import datetime
import json

DATABASE_NAME = 'energy_monitor.db'

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_table(headers, rows, max_width=20):
    """Print data in table format"""
    if not rows:
        print("  No data found")
        return
    
    # Print headers
    header_line = "  ".join(str(h)[:max_width].ljust(max_width) for h in headers)
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = "  ".join(str(v)[:max_width].ljust(max_width) for v in row)
        print(row_line)

def inspect_database():
    """Inspect all tables in the database"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Database Overview
        print_section("DATABASE OVERVIEW")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nTotal Tables: {len(tables)}")
        print(f"Tables: {', '.join(tables)}")
        
        # Readings Table
        print_section("READINGS TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM readings")
        total = cursor.fetchone()[0]
        print(f"\nTotal Readings: {total}")
        
        if total > 0:
            cursor.execute("""
                SELECT appliance, COUNT(*) as count, 
                       AVG(power_watts) as avg_power,
                       MIN(power_watts) as min_power,
                       MAX(power_watts) as max_power
                FROM readings 
                GROUP BY appliance
            """)
            print("\nBy Appliance:")
            rows = cursor.fetchall()
            print_table(
                ["Appliance", "Count", "Avg Power", "Min Power", "Max Power"],
                [(r[0], r[1], f"{r[2]:.2f}W", f"{r[3]:.2f}W", f"{r[4]:.2f}W") for r in rows]
            )
            
            print("\nRecent Readings (Last 10):")
            cursor.execute("""
                SELECT appliance, power_watts, timestamp, is_anomaly, deviation_percent
                FROM readings 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            print_table(
                ["Appliance", "Power", "Timestamp", "Anomaly", "Deviation"],
                [(r[0], f"{r[1]:.2f}W", r[2][:19], "Yes" if r[3] else "No", f"{r[4]:.1f}%" if r[4] else "N/A") for r in rows]
            )
        
        # Anomalies Table
        print_section("ANOMALIES TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM anomalies")
        total = cursor.fetchone()[0]
        print(f"\nTotal Anomalies: {total}")
        
        if total > 0:
            cursor.execute("""
                SELECT appliance, COUNT(*) as count, AVG(deviation_percent) as avg_deviation
                FROM anomalies 
                GROUP BY appliance
            """)
            print("\nBy Appliance:")
            rows = cursor.fetchall()
            print_table(
                ["Appliance", "Count", "Avg Deviation"],
                [(r[0], r[1], f"{r[2]:.1f}%") for r in rows]
            )
            
            print("\nRecent Anomalies (Last 10):")
            cursor.execute("""
                SELECT appliance, power_watts, expected_power, deviation_percent, severity, timestamp
                FROM anomalies 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            print_table(
                ["Appliance", "Actual", "Expected", "Deviation", "Severity", "Time"],
                [(r[0], f"{r[1]:.2f}W", f"{r[2]:.2f}W", f"{r[3]:.1f}%", r[4], r[5][:19]) for r in rows]
            )
        
        # Cutoffs Table
        print_section("CUTOFFS TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM cutoffs")
        total = cursor.fetchone()[0]
        print(f"\nTotal Cutoffs: {total}")
        
        if total > 0:
            cursor.execute("""
                SELECT appliance, COUNT(*) as count
                FROM cutoffs 
                GROUP BY appliance
            """)
            print("\nBy Appliance:")
            rows = cursor.fetchall()
            print_table(
                ["Appliance", "Count"],
                [(r[0], r[1]) for r in rows]
            )
            
            print("\nRecent Cutoffs (Last 10):")
            cursor.execute("""
                SELECT appliance, power_watts, expected_power, deviation_percent, reason, timestamp
                FROM cutoffs 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            print_table(
                ["Appliance", "Power", "Expected", "Deviation", "Reason", "Time"],
                [(r[0], f"{r[1]:.2f}W", f"{r[2]:.2f}W", f"{r[3]:.1f}%", r[4][:15], r[5][:19]) for r in rows]
            )
        
        # Model Performance Table
        print_section("MODEL PERFORMANCE TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM model_performance")
        total = cursor.fetchone()[0]
        print(f"\nTotal Records: {total}")
        
        if total > 0:
            print("\nLatest Model Performance:")
            cursor.execute("""
                SELECT appliance, model_name, accuracy, precision_score, recall, f1_score, training_samples, timestamp
                FROM model_performance 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            print_table(
                ["Appliance", "Model", "Accuracy", "Precision", "Recall", "F1", "Samples"],
                [(r[0], r[1], f"{r[2]:.3f}", f"{r[3]:.3f}", f"{r[4]:.3f}", f"{r[5]:.3f}", r[6]) for r in rows]
            )
        
        # Sessions Table
        print_section("SESSIONS TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM sessions")
        total = cursor.fetchone()[0]
        print(f"\nTotal Sessions: {total}")
        
        if total > 0:
            print("\nRecent Sessions:")
            cursor.execute("""
                SELECT appliance, start_time, end_time, total_readings, total_anomalies, total_cutoffs
                FROM sessions 
                ORDER BY start_time DESC 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            print_table(
                ["Appliance", "Start", "End", "Readings", "Anomalies", "Cutoffs"],
                [(r[0], r[1][:19] if r[1] else "N/A", r[2][:19] if r[2] else "Active", r[3], r[4], r[5]) for r in rows]
            )
        
        # IoT Devices Table
        print_section("IOT DEVICES TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM iot_devices")
        total = cursor.fetchone()[0]
        print(f"\nTotal IoT Devices: {total}")
        
        if total > 0:
            cursor.execute("""
                SELECT device_id, device_name, device_type, status, power_state, current_power, last_seen
                FROM iot_devices 
                ORDER BY device_name
            """)
            rows = cursor.fetchall()
            print_table(
                ["Device ID", "Name", "Type", "Status", "Power", "Current", "Last Seen"],
                [(r[0], r[1], r[2], r[3], r[4], f"{r[5]:.2f}W", r[6][:19] if r[6] else "Never") for r in rows]
            )
        
        # IoT Readings Table
        print_section("IOT READINGS TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM iot_readings")
        total = cursor.fetchone()[0]
        print(f"\nTotal IoT Readings: {total}")
        
        if total > 0:
            cursor.execute("""
                SELECT device_id, COUNT(*) as count, AVG(power) as avg_power
                FROM iot_readings 
                GROUP BY device_id
            """)
            print("\nBy Device:")
            rows = cursor.fetchall()
            print_table(
                ["Device ID", "Count", "Avg Power"],
                [(r[0], r[1], f"{r[2]:.2f}W") for r in rows]
            )
            
            print("\nRecent IoT Readings (Last 10):")
            cursor.execute("""
                SELECT device_id, power, voltage, current, temperature, timestamp
                FROM iot_readings 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            print_table(
                ["Device ID", "Power", "Voltage", "Current", "Temp", "Timestamp"],
                [(r[0], f"{r[1]:.2f}W", f"{r[2]:.1f}V" if r[2] else "N/A", f"{r[3]:.2f}A" if r[3] else "N/A", f"{r[4]:.1f}C" if r[4] else "N/A", r[5][:19]) for r in rows]
            )
        
        # IoT Commands Table
        print_section("IOT COMMANDS TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM iot_commands")
        total = cursor.fetchone()[0]
        print(f"\nTotal Commands: {total}")
        
        if total > 0:
            print("\nRecent Commands (Last 10):")
            cursor.execute("""
                SELECT device_id, command, status, sent_at, completed_at
                FROM iot_commands 
                ORDER BY sent_at DESC 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            print_table(
                ["Device ID", "Command", "Status", "Sent", "Completed"],
                [(r[0], r[1], r[2], r[3][:19], r[4][:19] if r[4] else "Pending") for r in rows]
            )
        
        # Summary Statistics
        print_section("SUMMARY STATISTICS")
        cursor.execute("SELECT COUNT(*) FROM readings")
        total_readings = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM anomalies")
        total_anomalies = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM cutoffs")
        total_cutoffs = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM iot_devices")
        total_devices = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM iot_readings")
        total_iot_readings = cursor.fetchone()[0]
        
        print(f"\nTotal Readings: {total_readings}")
        print(f"Total Anomalies: {total_anomalies}")
        print(f"Total Cutoffs: {total_cutoffs}")
        print(f"Total IoT Devices: {total_devices}")
        print(f"Total IoT Readings: {total_iot_readings}")
        
        if total_readings > 0:
            anomaly_rate = (total_anomalies / total_readings) * 100
            cutoff_rate = (total_cutoffs / total_readings) * 100
            print(f"\nAnomaly Rate: {anomaly_rate:.2f}%")
            print(f"Cutoff Rate: {cutoff_rate:.2f}%")
        
        print("\n" + "="*80)
        print("  Inspection Complete")
        print("="*80 + "\n")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\nError accessing database: {e}")
    except FileNotFoundError:
        print(f"\nDatabase file '{DATABASE_NAME}' not found!")
        print("Make sure the application has been run at least once to create the database.")

if __name__ == '__main__':
    print("\n" + "="*80)
    print("  ENERGY MONITOR DATABASE INSPECTOR")
    print("="*80)
    inspect_database()

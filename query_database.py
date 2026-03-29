"""
Simple Database Query Tool
Run custom SQL queries on the database
"""
import sqlite3
import sys

DATABASE_NAME = 'energy_monitor.db'

def run_query(query):
    """Execute a SQL query and display results"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query)
        
        # Check if it's a SELECT query
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            
            if not rows:
                print("No results found.")
                return
            
            # Print column headers
            headers = rows[0].keys()
            header_line = " | ".join(str(h).ljust(20) for h in headers)
            print("\n" + header_line)
            print("-" * len(header_line))
            
            # Print rows
            for row in rows:
                row_line = " | ".join(str(row[h])[:20].ljust(20) for h in headers)
                print(row_line)
            
            print(f"\nTotal rows: {len(rows)}")
        else:
            conn.commit()
            print(f"Query executed successfully. Rows affected: {cursor.rowcount}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def show_tables():
    """Show all tables in the database"""
    query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    print("\nAvailable Tables:")
    run_query(query)

def show_schema(table_name):
    """Show schema for a specific table"""
    query = f"PRAGMA table_info({table_name})"
    print(f"\nSchema for table '{table_name}':")
    run_query(query)

def interactive_mode():
    """Interactive query mode"""
    print("\n" + "="*80)
    print("  ENERGY MONITOR DATABASE QUERY TOOL")
    print("="*80)
    print("\nCommands:")
    print("  tables          - Show all tables")
    print("  schema <table>  - Show table schema")
    print("  quit or exit    - Exit the tool")
    print("  Or enter any SQL query")
    print("\n" + "="*80 + "\n")
    
    while True:
        try:
            query = input("SQL> ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if query.lower() == 'tables':
                show_tables()
                continue
            
            if query.lower().startswith('schema '):
                table_name = query.split()[1]
                show_schema(table_name)
                continue
            
            run_query(query)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

# Common useful queries
COMMON_QUERIES = {
    '1': ('Show all appliances', 'SELECT DISTINCT appliance FROM readings'),
    '2': ('Count readings per appliance', 'SELECT appliance, COUNT(*) as count FROM readings GROUP BY appliance'),
    '3': ('Show recent readings', 'SELECT * FROM readings ORDER BY timestamp DESC LIMIT 20'),
    '4': ('Show all anomalies', 'SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT 20'),
    '5': ('Show all cutoffs', 'SELECT * FROM cutoffs ORDER BY timestamp DESC LIMIT 20'),
    '6': ('Show IoT devices', 'SELECT * FROM iot_devices'),
    '7': ('Show recent IoT readings', 'SELECT * FROM iot_readings ORDER BY timestamp DESC LIMIT 20'),
    '8': ('Show model performance', 'SELECT * FROM model_performance ORDER BY timestamp DESC'),
    '9': ('Show sessions', 'SELECT * FROM sessions ORDER BY start_time DESC'),
    '10': ('Show hourly usage pattern', '''
        SELECT hour, appliance, AVG(power_watts) as avg_power, COUNT(*) as count 
        FROM readings 
        GROUP BY hour, appliance 
        ORDER BY appliance, hour
    '''),
}

def quick_queries():
    """Show common queries menu"""
    print("\n" + "="*80)
    print("  QUICK QUERIES")
    print("="*80)
    
    for key, (desc, _) in COMMON_QUERIES.items():
        print(f"  {key}. {desc}")
    
    print("\n  0. Back to main menu")
    print("="*80 + "\n")
    
    choice = input("Select query (0-10): ").strip()
    
    if choice == '0':
        return
    
    if choice in COMMON_QUERIES:
        desc, query = COMMON_QUERIES[choice]
        print(f"\nExecuting: {desc}")
        print(f"Query: {query}\n")
        run_query(query)
    else:
        print("Invalid choice!")

def main_menu():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("  ENERGY MONITOR DATABASE QUERY TOOL")
        print("="*80)
        print("\n1. Quick Queries (Common queries)")
        print("2. Interactive Mode (Custom SQL)")
        print("3. Show All Tables")
        print("4. Exit")
        print("\n" + "="*80 + "\n")
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == '1':
            quick_queries()
        elif choice == '2':
            interactive_mode()
        elif choice == '3':
            show_tables()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run query from command line
        query = ' '.join(sys.argv[1:])
        print(f"Executing: {query}\n")
        run_query(query)
    else:
        # Show main menu
        main_menu()

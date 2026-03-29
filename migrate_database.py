"""
Database Migration Script
Recreates database with new user-based schema
"""
import os
import shutil
from datetime import datetime

def backup_old_database():
    """Backup existing database if it exists"""
    if os.path.exists('energy_monitor.db'):
        backup_name = f'energy_monitor_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy('energy_monitor.db', backup_name)
        print(f"✓ Backed up existing database to: {backup_name}")
        return True
    return False

def delete_old_database():
    """Delete old database"""
    if os.path.exists('energy_monitor.db'):
        os.remove('energy_monitor.db')
        print("✓ Deleted old database")
        return True
    return False

def create_new_database():
    """Create new database with user schema"""
    import database as db
    db.init_database()
    print("✓ Created new database with user authentication schema")

def main():
    print("\n" + "="*70)
    print("  DATABASE MIGRATION")
    print("="*70)
    print("\nThis will:")
    print("  1. Backup existing database (if exists)")
    print("  2. Delete old database")
    print("  3. Create new database with user authentication")
    print("\n⚠️  WARNING: All existing data will be lost!")
    print("="*70 + "\n")
    
    response = input("Continue with migration? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\nMigration cancelled.")
        return
    
    print("\n" + "="*70)
    print("  STARTING MIGRATION")
    print("="*70 + "\n")
    
    # Step 1: Backup
    if backup_old_database():
        print("Step 1: Backup completed")
    else:
        print("Step 1: No existing database to backup")
    
    # Step 2: Delete
    if delete_old_database():
        print("Step 2: Old database deleted")
    else:
        print("Step 2: No database to delete")
    
    # Step 3: Create new
    print("\nStep 3: Creating new database...")
    create_new_database()
    
    print("\n" + "="*70)
    print("  MIGRATION COMPLETE")
    print("="*70)
    print("\nNew database created with:")
    print("  ✓ User authentication tables")
    print("  ✓ Per-user appliances")
    print("  ✓ Per-user hourly patterns")
    print("  ✓ User-isolated data")
    print("\nYou can now:")
    print("  1. Run: python app_advanced.py")
    print("  2. Visit: http://localhost:5000/signup")
    print("  3. Create your account")
    print("  4. Start monitoring!")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

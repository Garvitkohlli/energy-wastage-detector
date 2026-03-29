"""
Fix User Appliances
Ensures all users have appliances initialized
"""
import database as db

def fix_all_users():
    """Initialize appliances for all users who don't have them"""
    
    print("\n" + "="*70)
    print("  FIXING USER APPLIANCES")
    print("="*70)
    
    # Initialize database
    db.init_database()
    
    # Get all users
    import sqlite3
    conn = sqlite3.connect('energy_monitor.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users')
    users = [dict(row) for row in cursor.fetchall()]
    
    print(f"\nFound {len(users)} users in database")
    
    if not users:
        print("\n⚠️  No users found. Please sign up first!")
        print("   Visit: http://localhost:5000/signup")
        conn.close()
        return
    
    for user in users:
        user_id = user['id']
        username = user['username']
        
        print(f"\nChecking user: {username} (ID: {user_id})")
        
        # Check if user has appliances
        appliances = db.get_user_appliances(user_id)
        
        if appliances:
            print(f"   ✓ User has {len(appliances)} appliances")
            for app in appliances:
                print(f"      - {app['appliance_name']}")
        else:
            print(f"   ⚠️  User has NO appliances - initializing...")
            db.initialize_user_appliances(user_id)
            
            appliances = db.get_user_appliances(user_id)
            print(f"   ✓ Initialized {len(appliances)} appliances")
            for app in appliances:
                print(f"      - {app['appliance_name']}")
        
        # Check hourly patterns
        if appliances:
            patterns = db.get_user_hourly_patterns(user_id, appliances[0]['appliance_name'])
            zero_count = sum(1 for p in patterns if p['reading_count'] == 0)
            print(f"   ✓ Hourly patterns: {len(patterns)} total, {zero_count} with zero readings")
    
    conn.close()
    
    print("\n" + "="*70)
    print("  ✓ ALL USERS FIXED")
    print("="*70)
    print("\nYou can now:")
    print("  1. Login at: http://localhost:5000/login")
    print("  2. Go to Dashboard")
    print("  3. Select an appliance")
    print("  4. Start monitoring!")
    print("="*70 + "\n")

if __name__ == '__main__':
    fix_all_users()

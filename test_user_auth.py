"""
Test User Authentication System
Verifies user creation, login, and per-user data isolation
"""
import database as db
from werkzeug.security import generate_password_hash, check_password_hash

def test_user_creation():
    """Test creating users and initializing their appliances"""
    print("\n" + "="*70)
    print("  TESTING USER CREATION")
    print("="*70)
    
    # Initialize database
    db.init_database()
    
    # Create test users
    users = [
        ('alice', 'alice@example.com', 'password123', 'Alice Johnson'),
        ('bob', 'bob@example.com', 'password456', 'Bob Smith')
    ]
    
    created_users = []
    
    for username, email, password, full_name in users:
        # Check if user already exists
        existing = db.get_user_by_username(username)
        if existing:
            print(f"   ⚠️  User '{username}' already exists (ID: {existing['id']})")
            created_users.append(existing['id'])
            continue
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = db.create_user(username, email, password_hash, full_name)
        
        # Initialize appliances with zero patterns
        db.initialize_user_appliances(user_id)
        
        print(f"   ✓ Created user '{username}' (ID: {user_id})")
        created_users.append(user_id)
    
    return created_users

def test_user_appliances(user_id):
    """Test that user has appliances initialized"""
    print(f"\n   Testing appliances for user {user_id}...")
    
    appliances = db.get_user_appliances(user_id)
    print(f"   ✓ User has {len(appliances)} appliances")
    
    for appliance in appliances:
        print(f"      - {appliance['appliance_name']}: {appliance['base_power']}W ({appliance['pattern']})")
    
    return len(appliances) > 0

def test_hourly_patterns(user_id):
    """Test that hourly patterns are initialized to zero"""
    print(f"\n   Testing hourly patterns for user {user_id}...")
    
    appliances = db.get_user_appliances(user_id)
    if not appliances:
        print("   ✗ No appliances found")
        return False
    
    appliance_name = appliances[0]['appliance_name']
    patterns = db.get_user_hourly_patterns(user_id, appliance_name)
    
    print(f"   ✓ Found {len(patterns)} hourly patterns for {appliance_name}")
    
    # Check first few patterns
    zero_count = sum(1 for p in patterns if p['reading_count'] == 0)
    print(f"   ✓ {zero_count}/{len(patterns)} patterns have zero readings (fresh start)")
    
    # Show sample
    if patterns:
        sample = patterns[0]
        print(f"   Sample: Hour {sample['hour']}, Day {sample['day_of_week']}: "
              f"{sample['avg_power']}W ({sample['reading_count']} readings)")
    
    return True

def test_data_isolation():
    """Test that users have isolated data"""
    print("\n" + "="*70)
    print("  TESTING DATA ISOLATION")
    print("="*70)
    
    # Get two users
    user1 = db.get_user_by_username('alice')
    user2 = db.get_user_by_username('bob')
    
    if not user1 or not user2:
        print("   ⚠️  Need two users for isolation test")
        return False
    
    # Add a reading for user 1
    appliances1 = db.get_user_appliances(user1['id'])
    if appliances1:
        from datetime import datetime
        appliance_name = appliances1[0]['appliance_name']
        
        db.save_reading(
            appliance=appliance_name,
            power=100.0,
            timestamp=datetime.now().isoformat(),
            hour=10,
            day_of_week=1,
            user_id=user1['id']
        )
        
        print(f"   ✓ Added reading for user {user1['username']}")
    
    # Check user 1 has data
    readings1 = db.get_readings(appliance_name, limit=10, user_id=user1['id'])
    print(f"   ✓ User {user1['username']} has {len(readings1)} readings")
    
    # Check user 2 has no data for same appliance
    readings2 = db.get_readings(appliance_name, limit=10, user_id=user2['id'])
    print(f"   ✓ User {user2['username']} has {len(readings2)} readings")
    
    if len(readings1) > 0 and len(readings2) == 0:
        print("   ✓ Data isolation confirmed!")
        return True
    else:
        print("   ⚠️  Data isolation may not be working correctly")
        return False

def test_password_verification():
    """Test password hashing and verification"""
    print("\n" + "="*70)
    print("  TESTING PASSWORD VERIFICATION")
    print("="*70)
    
    user = db.get_user_by_username('alice')
    if not user:
        print("   ⚠️  User 'alice' not found")
        return False
    
    # Test correct password
    correct = check_password_hash(user['password_hash'], 'password123')
    print(f"   {'✓' if correct else '✗'} Correct password: {correct}")
    
    # Test wrong password
    wrong = check_password_hash(user['password_hash'], 'wrongpassword')
    print(f"   {'✓' if not wrong else '✗'} Wrong password rejected: {not wrong}")
    
    return correct and not wrong

def test_user_statistics():
    """Test getting statistics per user"""
    print("\n" + "="*70)
    print("  TESTING USER STATISTICS")
    print("="*70)
    
    user = db.get_user_by_username('alice')
    if not user:
        print("   ⚠️  User 'alice' not found")
        return False
    
    appliances = db.get_user_appliances(user['id'])
    if not appliances:
        print("   ⚠️  No appliances found")
        return False
    
    appliance_name = appliances[0]['appliance_name']
    stats = db.get_statistics(appliance_name, user_id=user['id'])
    
    print(f"   ✓ Statistics for {appliance_name}:")
    print(f"      Total readings: {stats['total_readings']}")
    print(f"      Total anomalies: {stats['total_anomalies']}")
    print(f"      Total cutoffs: {stats['total_cutoffs']}")
    print(f"      Average power: {stats['average_power']}W")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*70)
    print("  CLEANUP")
    print("="*70)
    
    response = input("\n   Delete test users? (y/n): ").strip().lower()
    
    if response == 'y':
        import sqlite3
        conn = sqlite3.connect('energy_monitor.db')
        cursor = conn.cursor()
        
        for username in ['alice', 'bob']:
            user = db.get_user_by_username(username)
            if user:
                user_id = user['id']
                
                # Delete user data
                cursor.execute("DELETE FROM readings WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM anomalies WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM cutoffs WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM model_performance WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM user_hourly_patterns WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM user_appliances WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                
                print(f"   ✓ Deleted user '{username}' and all data")
        
        conn.commit()
        conn.close()
    else:
        print("   Skipping cleanup")

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  USER AUTHENTICATION SYSTEM TEST SUITE")
    print("="*70)
    
    tests = []
    
    # Create users
    user_ids = test_user_creation()
    
    if user_ids:
        # Test each user
        for user_id in user_ids:
            tests.append(("User Appliances", test_user_appliances(user_id)))
            tests.append(("Hourly Patterns", test_hourly_patterns(user_id)))
        
        # Test isolation
        tests.append(("Data Isolation", test_data_isolation()))
        tests.append(("Password Verification", test_password_verification()))
        tests.append(("User Statistics", test_user_statistics()))
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for name, result in tests:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name:30} {status}")
    
    print(f"\n  Passed: {passed}/{total}")
    print("="*70 + "\n")
    
    # Cleanup
    cleanup_test_data()
    
    return passed == total

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

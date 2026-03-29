"""
Test Hourly Patterns Display
Verifies that hourly patterns are stored and retrieved correctly
"""
import database as db

def test_hourly_patterns():
    """Test that hourly patterns are in database"""
    
    print("\n" + "="*70)
    print("  TESTING HOURLY PATTERNS")
    print("="*70)
    
    # Initialize database
    db.init_database()
    
    # Get demo user
    user = db.get_user_by_username('demo')
    if not user:
        print("\n✗ Demo user not found")
        return False
    
    user_id = user['id']
    print(f"\n✓ Found user: {user['username']} (ID: {user_id})")
    
    # Get appliances
    appliances = db.get_user_appliances(user_id)
    if not appliances:
        print("\n✗ No appliances found")
        return False
    
    print(f"✓ User has {len(appliances)} appliances\n")
    
    # Check each appliance
    all_good = True
    
    for appliance in appliances:
        appliance_name = appliance['appliance_name']
        print(f"\n{appliance_name}:")
        print("-" * 50)
        
        # Get hourly patterns
        patterns = db.get_user_hourly_patterns(user_id, appliance_name)
        
        if not patterns:
            print("  ✗ No patterns found")
            all_good = False
            continue
        
        # Count patterns with data
        patterns_with_data = [p for p in patterns if p['reading_count'] > 0]
        
        print(f"  Total patterns: {len(patterns)}")
        print(f"  Patterns with data: {len(patterns_with_data)}")
        
        if len(patterns_with_data) == 0:
            print("  ✗ No patterns have data!")
            all_good = False
            continue
        
        # Aggregate by hour
        hourly_data = {}
        for hour in range(24):
            hour_patterns = [p for p in patterns if p['hour'] == hour]
            total_readings = sum(p['reading_count'] for p in hour_patterns)
            
            if total_readings > 0:
                weighted_avg = sum(p['avg_power'] * p['reading_count'] for p in hour_patterns) / total_readings
                hourly_data[hour] = {
                    'avg': weighted_avg,
                    'count': total_readings
                }
        
        # Show sample hours
        print(f"\n  Sample Hours:")
        sample_hours = [0, 6, 12, 18, 23]
        for hour in sample_hours:
            if hour in hourly_data:
                data = hourly_data[hour]
                print(f"    {hour:2d}:00 - {data['avg']:7.2f}W (avg) - {data['count']} readings")
            else:
                print(f"    {hour:2d}:00 - No data")
        
        # Find best and worst
        if hourly_data:
            best_hour = min(hourly_data.items(), key=lambda x: x[1]['avg'])
            worst_hour = max(hourly_data.items(), key=lambda x: x[1]['avg'])
            
            print(f"\n  Best cutoff time: {best_hour[0]:2d}:00 ({best_hour[1]['avg']:.2f}W)")
            print(f"  Peak usage time:  {worst_hour[0]:2d}:00 ({worst_hour[1]['avg']:.2f}W)")
            print(f"  ✓ Patterns look good!")
        else:
            print("  ✗ No hourly data found")
            all_good = False
    
    print("\n" + "="*70)
    if all_good:
        print("  ✓ ALL PATTERNS VERIFIED")
        print("\nYou can now:")
        print("  1. Restart the app: python app_advanced.py")
        print("  2. Login and go to Analytics")
        print("  3. Select an appliance")
        print("  4. See the 24-hour pattern!")
    else:
        print("  ✗ SOME PATTERNS MISSING")
        print("\nTo fix:")
        print("  1. Run: python populate_realistic_data.py")
        print("  2. Enter username: demo")
        print("  3. Enter days: 7")
        print("  4. Confirm: y")
    print("="*70 + "\n")
    
    return all_good

if __name__ == '__main__':
    import sys
    success = test_hourly_patterns()
    sys.exit(0 if success else 1)

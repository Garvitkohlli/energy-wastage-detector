"""
Test API Endpoint Directly
"""
import database as db
import json

def test_usage_analysis_logic():
    """Test the exact logic used in the API endpoint"""
    
    print("\n" + "="*70)
    print("  TESTING USAGE ANALYSIS LOGIC")
    print("="*70)
    
    # Initialize database
    db.init_database()
    
    # Get demo user
    user = db.get_user_by_username('demo')
    if not user:
        print("\n✗ Demo user not found")
        return False
    
    user_id = user['id']
    appliance = 'Air Conditioner'
    
    print(f"\nUser ID: {user_id}")
    print(f"Appliance: {appliance}")
    
    # Get hourly patterns from DATABASE (same as API)
    db_patterns = db.get_user_hourly_patterns(user_id, appliance)
    
    print(f"\nDatabase patterns found: {len(db_patterns)}")
    
    if not db_patterns:
        print("✗ No patterns in database!")
        return False
    
    # Show sample patterns
    print("\nSample patterns from database:")
    for i in range(min(5, len(db_patterns))):
        p = db_patterns[i]
        print(f"  Hour {p['hour']}, Day {p['day_of_week']}: {p['avg_power']:.2f}W ({p['reading_count']} readings)")
    
    # Aggregate by hour (same logic as API)
    hourly_stats = {}
    for hour in range(24):
        hour_data = [p for p in db_patterns if p['hour'] == hour]
        
        if hour_data:
            total_readings = sum(p['reading_count'] for p in hour_data)
            if total_readings > 0:
                weighted_avg = sum(p['avg_power'] * p['reading_count'] for p in hour_data) / total_readings
                all_mins = [p['min_power'] for p in hour_data if p['reading_count'] > 0]
                all_maxs = [p['max_power'] for p in hour_data if p['reading_count'] > 0]
                
                hourly_stats[hour] = {
                    'avg': round(weighted_avg, 2),
                    'min': round(min(all_mins) if all_mins else 0, 2),
                    'max': round(max(all_maxs) if all_maxs else 0, 2),
                    'count': total_readings
                }
            else:
                hourly_stats[hour] = {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
        else:
            hourly_stats[hour] = {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
    
    # Show results
    print("\n" + "="*70)
    print("  HOURLY STATS (What API should return)")
    print("="*70)
    
    hours_with_data = sum(1 for h in hourly_stats.values() if h['count'] > 0)
    print(f"\nHours with data: {hours_with_data}/24")
    
    print("\nSample hours:")
    for hour in [0, 6, 12, 18, 23]:
        stats = hourly_stats[hour]
        print(f"  {hour:2d}:00 - {stats['avg']:7.2f}W - {stats['count']} readings")
    
    # Find best and worst
    valid_hours = {h: s for h, s in hourly_stats.items() if s['count'] > 0}
    if valid_hours:
        best_cutoff_hour = min(valid_hours.items(), key=lambda x: x[1]['avg'])
        worst_hour = max(valid_hours.items(), key=lambda x: x[1]['avg'])
        
        print(f"\nBest cutoff: {best_cutoff_hour[0]:2d}:00 ({best_cutoff_hour[1]['avg']:.2f}W)")
        print(f"Peak usage:  {worst_hour[0]:2d}:00 ({worst_hour[1]['avg']:.2f}W)")
    
    # Create JSON response (same as API)
    db_stats = db.get_statistics(appliance, user_id=user_id)
    
    result = {
        'hourly_stats': hourly_stats,
        'best_cutoff_hour': best_cutoff_hour[0] if valid_hours else 0,
        'best_cutoff_avg': best_cutoff_hour[1]['avg'] if valid_hours else 0,
        'worst_hour': worst_hour[0] if valid_hours else 0,
        'worst_hour_avg': worst_hour[1]['avg'] if valid_hours else 0,
        'total_readings': db_stats['total_readings'],
        'total_anomalies': db_stats['total_anomalies'],
        'total_cutoffs': db_stats['total_cutoffs']
    }
    
    # Save to file for inspection
    with open('api_response_test.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "="*70)
    print("  ✓ API Response saved to: api_response_test.json")
    print("="*70)
    
    # Show JSON structure
    print("\nJSON structure:")
    print(f"  hourly_stats: {type(result['hourly_stats'])} with {len(result['hourly_stats'])} keys")
    print(f"  best_cutoff_hour: {result['best_cutoff_hour']}")
    print(f"  worst_hour: {result['worst_hour']}")
    print(f"  total_readings: {result['total_readings']}")
    
    print("\nSample hourly_stats entries:")
    for hour in [0, 12]:
        print(f"  hourly_stats[{hour}]: {result['hourly_stats'][hour]}")
    
    return hours_with_data == 24

if __name__ == '__main__':
    import sys
    success = test_usage_analysis_logic()
    
    if success:
        print("\n✓ Test passed! API should return correct data.")
        print("\nNext steps:")
        print("  1. Check api_response_test.json")
        print("  2. Restart the app")
        print("  3. Check browser console for what it receives")
    else:
        print("\n✗ Test failed!")
    
    sys.exit(0 if success else 1)

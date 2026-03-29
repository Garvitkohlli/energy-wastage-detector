"""
Populate Realistic Hourly Data for All Appliances
Creates realistic usage patterns for each hour of the day
"""
import database as db
from datetime import datetime, timedelta
import random

# Realistic hourly patterns for each appliance
APPLIANCE_PATTERNS = {
    'Light Bulb': {
        # Low during day (6 AM - 6 PM), High at night (6 PM - 11 PM), Medium late night
        'hourly_power': {
            0: 8,   # 12 AM - Low (bedroom lights)
            1: 5,   # 1 AM - Very low
            2: 3,   # 2 AM - Very low
            3: 2,   # 3 AM - Very low
            4: 2,   # 4 AM - Very low
            5: 3,   # 5 AM - Very low
            6: 5,   # 6 AM - Starting to wake up
            7: 8,   # 7 AM - Morning routine
            8: 6,   # 8 AM - Leaving for work
            9: 3,   # 9 AM - Away (minimal)
            10: 2,  # 10 AM - Away
            11: 2,  # 11 AM - Away
            12: 3,  # 12 PM - Lunch time
            13: 2,  # 1 PM - Away
            14: 2,  # 2 PM - Away
            15: 2,  # 3 PM - Away
            16: 3,  # 4 PM - Starting to return
            17: 5,  # 5 PM - Coming home
            18: 10, # 6 PM - Peak evening (all lights on)
            19: 12, # 7 PM - Peak (cooking, activities)
            20: 11, # 8 PM - Evening activities
            21: 10, # 9 PM - Winding down
            22: 9,  # 10 PM - Getting ready for bed
            23: 8,  # 11 PM - Bedroom lights
        },
        'variance': 2
    },
    
    'Refrigerator': {
        # Constant with slight variations (compressor cycles)
        # Higher during hot hours, lower at night
        'hourly_power': {
            0: 145,  # 12 AM
            1: 140,  # 1 AM
            2: 138,  # 2 AM
            3: 135,  # 3 AM - Lowest (coolest time)
            4: 136,  # 4 AM
            5: 138,  # 5 AM
            6: 142,  # 6 AM - Door opening
            7: 155,  # 7 AM - Morning use (breakfast)
            8: 158,  # 8 AM - Peak morning
            9: 150,  # 9 AM
            10: 148, # 10 AM
            11: 152, # 11 AM
            12: 160, # 12 PM - Lunch (door opening)
            13: 165, # 1 PM - Hottest part of day
            14: 168, # 2 PM - Peak (ambient heat)
            15: 165, # 3 PM
            16: 162, # 4 PM
            17: 158, # 5 PM
            18: 165, # 6 PM - Dinner prep (door opening)
            19: 170, # 7 PM - Peak dinner time
            20: 160, # 8 PM
            21: 155, # 9 PM
            22: 150, # 10 PM
            23: 148, # 11 PM
        },
        'variance': 10
    },
    
    'Laptop': {
        # High during work hours, low/off otherwise
        'hourly_power': {
            0: 5,   # 12 AM - Sleep mode
            1: 3,   # 1 AM - Off
            2: 2,   # 2 AM - Off
            3: 2,   # 3 AM - Off
            4: 2,   # 4 AM - Off
            5: 3,   # 5 AM - Off
            6: 5,   # 6 AM - Starting up
            7: 25,  # 7 AM - Morning check
            8: 45,  # 8 AM - Starting work
            9: 70,  # 9 AM - Peak work (video calls, heavy tasks)
            10: 75, # 10 AM - Peak work
            11: 72, # 11 AM - Peak work
            12: 50, # 12 PM - Lunch break (idle)
            13: 68, # 1 PM - Afternoon work
            14: 75, # 2 PM - Peak afternoon
            15: 70, # 3 PM - Work continues
            16: 65, # 4 PM - Winding down
            17: 55, # 5 PM - End of work day
            18: 30, # 6 PM - Personal use
            19: 35, # 7 PM - Evening browsing
            20: 40, # 8 PM - Entertainment/browsing
            21: 35, # 9 PM - Light use
            22: 25, # 10 PM - Winding down
            23: 10, # 11 PM - Sleep mode
        },
        'variance': 8
    },
    
    'Air Conditioner': {
        # High during hot hours (afternoon), low at night
        'hourly_power': {
            0: 200,   # 12 AM - Low (sleeping, cooler outside)
            1: 150,   # 1 AM - Lower
            2: 100,   # 2 AM - Minimal (coolest time)
            3: 80,    # 3 AM - Minimal
            4: 90,    # 4 AM - Minimal
            5: 120,   # 5 AM - Starting to warm up
            6: 250,   # 6 AM - Morning warmth
            7: 400,   # 7 AM - Getting warmer
            8: 600,   # 8 AM - Warming up
            9: 900,   # 9 AM - Hot
            10: 1200, # 10 AM - Very hot
            11: 1400, # 11 AM - Peak heat building
            12: 1600, # 12 PM - Peak heat
            13: 1700, # 1 PM - Hottest (peak)
            14: 1750, # 2 PM - Absolute peak
            15: 1700, # 3 PM - Still very hot
            16: 1600, # 4 PM - Starting to cool
            17: 1400, # 5 PM - Cooling down
            18: 1200, # 6 PM - Evening
            19: 1000, # 7 PM - Cooler
            20: 800,  # 8 PM - Much cooler
            21: 600,  # 9 PM - Night cooling
            22: 400,  # 10 PM - Low
            23: 300,  # 11 PM - Low
        },
        'variance': 100
    }
}

def generate_realistic_readings(user_id, appliance_name, pattern, days=7, readings_per_hour=5):
    """Generate realistic readings for an appliance over multiple days"""
    
    print(f"\nGenerating data for {appliance_name}...")
    print(f"  Pattern: {days} days × 24 hours × {readings_per_hour} readings/hour")
    
    hourly_power = pattern['hourly_power']
    variance = pattern['variance']
    
    total_readings = 0
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        day_of_week = current_date.weekday()
        
        for hour in range(24):
            base_power = hourly_power[hour]
            
            # Generate multiple readings per hour for better data
            for reading_num in range(readings_per_hour):
                # Add realistic variance
                power = base_power + random.uniform(-variance, variance)
                power = max(0, power)  # Ensure non-negative
                
                # Create timestamp within the hour
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                timestamp = current_date.replace(hour=hour, minute=minute, second=second)
                
                # Save to database
                db.save_reading(
                    appliance=appliance_name,
                    power=power,
                    timestamp=timestamp.isoformat(),
                    hour=hour,
                    day_of_week=day_of_week,
                    is_anomaly=False,
                    anomaly_score=0.0,
                    deviation=0.0,
                    user_id=user_id
                )
                
                total_readings += 1
    
    print(f"  ✓ Generated {total_readings} readings")
    
    # Show sample hourly averages
    stats = db.get_statistics(appliance_name, user_id=user_id)
    print(f"  ✓ Average power: {stats['average_power']:.2f}W")
    
    return total_readings

def populate_user_data(username, days=7):
    """Populate realistic data for a user"""
    
    print("\n" + "="*70)
    print(f"  POPULATING REALISTIC DATA FOR USER: {username}")
    print("="*70)
    
    # Get user
    user = db.get_user_by_username(username)
    if not user:
        print(f"\n✗ User '{username}' not found")
        print("  Run: python create_demo_user.py")
        return False
    
    user_id = user['id']
    print(f"\n✓ Found user: {user['username']} (ID: {user_id})")
    
    # Get appliances
    appliances = db.get_user_appliances(user_id)
    if not appliances:
        print("\n✗ No appliances found")
        print("  Run: python fix_user_appliances.py")
        return False
    
    print(f"✓ User has {len(appliances)} appliances")
    
    # Generate data for each appliance
    total_readings = 0
    
    for appliance in appliances:
        appliance_name = appliance['appliance_name']
        
        if appliance_name in APPLIANCE_PATTERNS:
            pattern = APPLIANCE_PATTERNS[appliance_name]
            readings = generate_realistic_readings(user_id, appliance_name, pattern, days)
            total_readings += readings
        else:
            print(f"\n⚠️  No pattern defined for {appliance_name}, skipping...")
    
    print("\n" + "="*70)
    print(f"  ✓ COMPLETED")
    print("="*70)
    print(f"\nTotal readings generated: {total_readings}")
    print(f"Days of data: {days}")
    print(f"Appliances populated: {len([a for a in appliances if a['appliance_name'] in APPLIANCE_PATTERNS])}")
    
    # Show hourly pattern summary
    print("\n" + "="*70)
    print("  HOURLY PATTERN SUMMARY")
    print("="*70)
    
    for appliance in appliances:
        appliance_name = appliance['appliance_name']
        if appliance_name in APPLIANCE_PATTERNS:
            patterns = db.get_user_hourly_patterns(user_id, appliance_name)
            if patterns:
                # Show a few sample hours
                print(f"\n{appliance_name}:")
                sample_hours = [0, 6, 12, 18]  # Midnight, Morning, Noon, Evening
                for hour in sample_hours:
                    hour_patterns = [p for p in patterns if p['hour'] == hour]
                    if hour_patterns:
                        avg_power = sum(p['avg_power'] for p in hour_patterns) / len(hour_patterns)
                        total_readings = sum(p['reading_count'] for p in hour_patterns)
                        print(f"  {hour:2d}:00 - {avg_power:7.2f}W (avg) - {total_readings} readings")
    
    print("\n" + "="*70)
    print("  You can now:")
    print("  1. Login to the app")
    print("  2. Go to Dashboard or Analytics")
    print("  3. See realistic hourly patterns")
    print("  4. Get accurate ML recommendations")
    print("="*70 + "\n")
    
    return True

def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("  REALISTIC DATA POPULATION TOOL")
    print("="*70)
    print("\nThis will generate realistic hourly data for all appliances")
    print("based on typical usage patterns:")
    print("\n  • Light Bulb: High at night, low during day")
    print("  • Refrigerator: Constant with peaks during hot hours")
    print("  • Laptop: High during work hours (9 AM - 5 PM)")
    print("  • Air Conditioner: Peak in afternoon (1-3 PM)")
    print("\n" + "="*70)
    
    # Initialize database
    db.init_database()
    
    # Get username
    username = input("\nEnter username (default: demo): ").strip() or 'demo'
    
    # Get number of days
    days_input = input("Enter number of days of data (default: 7): ").strip()
    days = int(days_input) if days_input.isdigit() else 7
    
    # Confirm
    print(f"\nWill generate {days} days of realistic data for user '{username}'")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("\nCancelled.")
        return
    
    # Populate data
    success = populate_user_data(username, days)
    
    if success:
        print("\n✓ Data population complete!")
    else:
        print("\n✗ Data population failed!")

if __name__ == '__main__':
    main()

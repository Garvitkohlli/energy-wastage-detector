"""
Test Retrain Functionality
Adds sample data and tests retraining
"""
import database as db
from datetime import datetime
import random

def add_sample_data(user_id, appliance_name, num_readings=100):
    """Add sample readings for testing"""
    print(f"\nAdding {num_readings} sample readings for {appliance_name}...")
    
    for i in range(num_readings):
        hour = i % 24
        day = i % 7
        power = 50 + random.uniform(-10, 10) + (20 if 18 <= hour <= 23 else 0)
        
        db.save_reading(
            appliance=appliance_name,
            power=power,
            timestamp=datetime.now().isoformat(),
            hour=hour,
            day_of_week=day,
            is_anomaly=False,
            anomaly_score=0.0,
            deviation=0.0,
            user_id=user_id
        )
    
    print(f"✓ Added {num_readings} readings")

def test_retrain():
    """Test the retrain functionality"""
    print("\n" + "="*70)
    print("  TESTING RETRAIN FUNCTIONALITY")
    print("="*70)
    
    # Initialize database
    db.init_database()
    
    # Get demo user
    user = db.get_user_by_username('demo')
    if not user:
        print("\n✗ Demo user not found. Run: python create_demo_user.py")
        return False
    
    user_id = user['id']
    print(f"\n✓ Found user: {user['username']} (ID: {user_id})")
    
    # Get appliances
    appliances = db.get_user_appliances(user_id)
    if not appliances:
        print("\n✗ No appliances found. Run: python fix_user_appliances.py")
        return False
    
    print(f"✓ User has {len(appliances)} appliances")
    
    # Use first appliance
    appliance = appliances[0]
    appliance_name = appliance['appliance_name']
    
    print(f"\nTesting with: {appliance_name}")
    
    # Check current readings
    stats = db.get_statistics(appliance_name, user_id=user_id)
    print(f"\nCurrent statistics:")
    print(f"  Total readings: {stats['total_readings']}")
    print(f"  Average power: {stats['average_power']}W")
    
    # Add sample data if needed
    if stats['total_readings'] < 50:
        print(f"\n⚠️  Not enough data for retraining (need 50+)")
        response = input("Add 100 sample readings? (y/n): ").strip().lower()
        
        if response == 'y':
            add_sample_data(user_id, appliance_name, 100)
            
            # Check again
            stats = db.get_statistics(appliance_name, user_id=user_id)
            print(f"\nUpdated statistics:")
            print(f"  Total readings: {stats['total_readings']}")
            print(f"  Average power: {stats['average_power']}W")
        else:
            print("\nSkipping test - not enough data")
            return False
    
    # Test retrain function
    print("\n" + "="*70)
    print("  TESTING RETRAIN FUNCTION")
    print("="*70)
    
    from ml_models import EnsembleEnergyModel
    from app_advanced import retrain_model_from_database
    
    # Create a model
    model = EnsembleEnergyModel(f"test_{appliance_name}")
    
    # Initial training with minimal data
    print("\n1. Initial training with synthetic data...")
    power_data = [50 + random.uniform(-5, 5) for _ in range(168)]
    hours = [i % 24 for i in range(168)]
    days = [i % 7 for i in range(168)]
    model.train(power_data, hours, days)
    print(f"   ✓ Model trained with {len(model.training_data)} samples")
    
    # Retrain from database
    print("\n2. Retraining from database...")
    success = retrain_model_from_database(user_id, appliance_name, model)
    
    if success:
        print(f"\n✓ Retrain test PASSED")
        print(f"   Model now has {len(model.training_data)} training samples")
        return True
    else:
        print(f"\n✗ Retrain test FAILED")
        return False

def main():
    """Run test"""
    print("\n" + "="*70)
    print("  RETRAIN FUNCTIONALITY TEST")
    print("="*70)
    
    success = test_retrain()
    
    print("\n" + "="*70)
    if success:
        print("  ✓ ALL TESTS PASSED")
        print("\nYou can now:")
        print("  1. Login to the app")
        print("  2. Go to Dashboard")
        print("  3. Select an appliance")
        print("  4. Click 'Retrain Model from Database'")
    else:
        print("  ✗ TESTS FAILED")
        print("\nTroubleshooting:")
        print("  1. Make sure demo user exists: python create_demo_user.py")
        print("  2. Make sure appliances exist: python fix_user_appliances.py")
        print("  3. Add sample data when prompted")
    print("="*70 + "\n")
    
    return success

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

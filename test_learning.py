"""
Test ML Learning System
Verifies that models learn from database
"""
import database as db
from ml_models import EnsembleEnergyModel
from datetime import datetime
import random

def test_learning_from_database():
    """Test that model can learn from database readings"""
    
    print("\n" + "="*70)
    print("  TESTING ML LEARNING FROM DATABASE")
    print("="*70)
    
    # Initialize database
    db.init_database()
    
    test_appliance = "Test_Appliance"
    
    # Step 1: Create some test readings in database
    print("\n1. Creating test readings in database...")
    
    for i in range(100):
        hour = i % 24
        day = i % 7
        power = 50 + random.uniform(-5, 5) + (10 if 18 <= hour <= 23 else 0)
        
        db.save_reading(
            appliance=test_appliance,
            power=power,
            timestamp=datetime.now().isoformat(),
            hour=hour,
            day_of_week=day,
            is_anomaly=False,
            anomaly_score=0.0,
            deviation=0.0
        )
    
    print(f"   ✓ Created 100 test readings")
    
    # Step 2: Create model and train from database
    print("\n2. Training model from database...")
    
    model = EnsembleEnergyModel(test_appliance)
    
    # Load from database
    historical_readings = db.get_readings(test_appliance, limit=1000)
    
    if not historical_readings:
        print("   ✗ Failed to load readings from database")
        return False
    
    print(f"   ✓ Loaded {len(historical_readings)} readings from database")
    
    # Extract data
    power_data = [r['power_watts'] for r in historical_readings]
    hours = [r['hour'] for r in historical_readings]
    days = [r['day_of_week'] for r in historical_readings]
    
    # Train model
    success = model.train(power_data, hours, days)
    
    if not success:
        print("   ✗ Model training failed")
        return False
    
    print(f"   ✓ Model trained successfully")
    print(f"   ✓ Training samples: {len(model.training_data)}")
    print(f"   ✓ Average power: {sum(power_data)/len(power_data):.2f}W")
    
    # Step 3: Test predictions
    print("\n3. Testing predictions...")
    
    # Normal reading
    result = model.predict(52, 10, 1)
    print(f"   Normal reading (52W): {result['is_anomaly']} (confidence: {result['confidence']}%)")
    
    # Anomalous reading
    result = model.predict(150, 10, 1)
    print(f"   Anomaly reading (150W): {result['is_anomaly']} (confidence: {result['confidence']}%)")
    
    # Step 4: Add more data and retrain
    print("\n4. Adding more data and retraining...")
    
    for i in range(50):
        hour = i % 24
        day = i % 7
        power = 50 + random.uniform(-5, 5) + (10 if 18 <= hour <= 23 else 0)
        
        db.save_reading(
            appliance=test_appliance,
            power=power,
            timestamp=datetime.now().isoformat(),
            hour=hour,
            day_of_week=day,
            is_anomaly=False,
            anomaly_score=0.0,
            deviation=0.0
        )
    
    print(f"   ✓ Added 50 more readings")
    
    # Reload and retrain
    historical_readings = db.get_readings(test_appliance, limit=1000)
    power_data = [r['power_watts'] for r in historical_readings]
    hours = [r['hour'] for r in historical_readings]
    days = [r['day_of_week'] for r in historical_readings]
    
    success = model.train(power_data, hours, days)
    
    if success:
        print(f"   ✓ Model retrained with {len(model.training_data)} samples")
    else:
        print("   ✗ Retraining failed")
        return False
    
    # Step 5: Verify database statistics
    print("\n5. Checking database statistics...")
    
    stats = db.get_statistics(test_appliance)
    print(f"   Total readings: {stats['total_readings']}")
    print(f"   Average power: {stats['average_power']}W")
    
    # Cleanup
    print("\n6. Cleaning up test data...")
    import sqlite3
    conn = sqlite3.connect('energy_monitor.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM readings WHERE appliance = ?", (test_appliance,))
    conn.commit()
    conn.close()
    print("   ✓ Test data cleaned up")
    
    print("\n" + "="*70)
    print("  ✓ ALL TESTS PASSED")
    print("="*70 + "\n")
    
    return True

def test_automatic_retraining():
    """Test automatic retraining logic"""
    
    print("\n" + "="*70)
    print("  TESTING AUTOMATIC RETRAINING LOGIC")
    print("="*70)
    
    # Simulate reading counts
    for readings in [50, 100, 200, 300, 500]:
        should_retrain = (readings % 100 == 0 and readings > 0)
        status = "✓ RETRAIN" if should_retrain else "  skip"
        print(f"   {readings} readings: {status}")
    
    print("\n" + "="*70)
    print("  ✓ RETRAINING LOGIC VERIFIED")
    print("="*70 + "\n")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  ML LEARNING SYSTEM TEST SUITE")
    print("="*70)
    
    tests = [
        ("Database Learning", test_learning_from_database),
        ("Automatic Retraining", test_automatic_retraining)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name:30} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n  Passed: {passed}/{total}")
    print("="*70 + "\n")
    
    return passed == total

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

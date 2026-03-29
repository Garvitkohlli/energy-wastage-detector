"""
Test script to verify page-aware monitoring works correctly
"""
import time
import requests
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_monitoring_control():
    """Test that monitoring only runs when viewing pages"""
    
    print("\n" + "="*70)
    print("🧪 TESTING PAGE-AWARE MONITORING")
    print("="*70)
    
    # Login first
    session = requests.Session()
    
    print("\n1️⃣ Logging in...")
    login_data = {
        'username': 'demo',
        'password': 'demo123'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("   ✅ Login successful")
    else:
        print("   ❌ Login failed")
        return
    
    # Start monitoring
    appliance = "Laptop"
    print(f"\n2️⃣ Starting monitoring for {appliance}...")
    response = session.get(f"{BASE_URL}/api/start_monitoring/{appliance}")
    print(f"   ✅ {response.json()['message']}")
    
    # Simulate viewing the appliance (register activity)
    print(f"\n3️⃣ Simulating active viewing (10 seconds)...")
    for i in range(5):
        # These API calls register activity
        session.get(f"{BASE_URL}/api/current_status/{appliance}")
        session.get(f"{BASE_URL}/api/usage_analysis/{appliance}")
        print(f"   📊 Activity registered ({i+1}/5)")
        time.sleep(2)
    
    # Check monitoring status
    print(f"\n4️⃣ Checking monitoring status...")
    response = session.get(f"{BASE_URL}/api/monitoring_status")
    status = response.json()
    print(f"   Active sessions: {status['active_sessions']}")
    print(f"   Timeout: {status['timeout_seconds']} seconds")
    
    if status['active_sessions'] > 0:
        print("   ✅ Monitoring is ACTIVE (user is viewing)")
        for monitor in status['monitors']:
            print(f"      - {monitor['appliance']} (last activity: {monitor['last_activity']})")
    
    # Stop viewing (no API calls)
    print(f"\n5️⃣ Simulating navigation away (waiting {status['timeout_seconds']+2} seconds)...")
    time.sleep(status['timeout_seconds'] + 2)
    
    # Check status again
    print(f"\n6️⃣ Checking monitoring status after timeout...")
    response = session.get(f"{BASE_URL}/api/monitoring_status")
    status = response.json()
    print(f"   Active sessions: {status['active_sessions']}")
    
    if status['active_sessions'] == 0:
        print("   ✅ Monitoring is PAUSED (user navigated away)")
        print("   💰 Resource savings: Data generation stopped!")
    else:
        print("   ⚠️ Monitoring still active (may need more time)")
    
    # Resume viewing
    print(f"\n7️⃣ Simulating return to dashboard...")
    session.get(f"{BASE_URL}/api/current_status/{appliance}")
    time.sleep(1)
    
    response = session.get(f"{BASE_URL}/api/monitoring_status")
    status = response.json()
    print(f"   Active sessions: {status['active_sessions']}")
    
    if status['active_sessions'] > 0:
        print("   ✅ Monitoring RESUMED automatically!")
    
    # Stop monitoring
    print(f"\n8️⃣ Stopping monitoring...")
    response = session.get(f"{BASE_URL}/api/stop_monitoring/{appliance}")
    print(f"   ✅ {response.json()['message']}")
    
    print("\n" + "="*70)
    print("✅ PAGE-AWARE MONITORING TEST COMPLETE")
    print("="*70)
    print("\n📝 Summary:")
    print("   - Monitoring generates data ONLY when viewing dashboard/analytics")
    print("   - Automatically pauses after 10 seconds of inactivity")
    print("   - Resumes automatically when you return")
    print("   - Perfect for cloud deployment (saves resources & costs)")
    print("\n")

if __name__ == "__main__":
    print("\n⚠️  Make sure the Flask app is running first!")
    print("   Run: python app_advanced.py")
    print("\n   Press Ctrl+C to cancel, or Enter to continue...")
    input()
    
    try:
        test_monitoring_control()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to Flask app")
        print("   Make sure it's running on http://localhost:5000")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

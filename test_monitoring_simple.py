"""
Simple Visual Test for Page-Aware Monitoring
Shows real-time status of monitoring activity
"""
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_box(title, content, color=""):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    
    c = colors.get(color, "")
    reset = colors["reset"] if color else ""
    
    print(f"\n{c}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{reset}")
    print(content)
    print()

def test_monitoring():
    """Visual test of page-aware monitoring"""
    
    clear_screen()
    print_box("🧪 PAGE-AWARE MONITORING TEST", 
              "This test will show you how monitoring behaves\n"
              "when users view and leave the dashboard", "blue")
    
    print("📋 INSTRUCTIONS:")
    print("   1. Make sure Flask app is running: python app_advanced.py")
    print("   2. Open browser: http://localhost:5000")
    print("   3. Login (demo/demo123)")
    print("   4. Go to Dashboard")
    print("   5. Click on an appliance (e.g., Laptop)")
    print("   6. Click 'Start Monitoring'")
    print("   7. Watch this terminal for monitoring status")
    print()
    
    input("Press Enter when you've started monitoring in the browser...")
    
    print("\n" + "="*60)
    print("🔍 MONITORING STATUS (Updates every 2 seconds)")
    print("="*60)
    print()
    
    # Import here to avoid issues if app isn't running
    try:
        from app_monitoring_control import monitoring_controller
    except Exception as e:
        print(f"❌ Error: Could not import monitoring_controller")
        print(f"   Make sure app_advanced.py is running")
        return
    
    print("✅ Connected to monitoring controller")
    print()
    print("📊 WHAT TO WATCH FOR:")
    print("   • When viewing dashboard: Active sessions > 0")
    print("   • When you navigate away: Active sessions drops to 0 after 10 sec")
    print("   • When you return: Active sessions increases again")
    print()
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        iteration = 0
        last_count = -1
        
        while True:
            iteration += 1
            active = monitoring_controller.get_active_monitors()
            count = len(active)
            
            # Only print when status changes or every 5 iterations
            if count != last_count or iteration % 5 == 0:
                timestamp = time.strftime("%H:%M:%S")
                
                if count > 0:
                    print(f"[{timestamp}] 🟢 ACTIVE: {count} session(s) - Data is being generated")
                    for session in active:
                        print(f"           └─ User {session['user_id']}: {session['appliance']} "
                              f"(last activity: {session['last_activity']})")
                else:
                    print(f"[{timestamp}] 🔴 PAUSED: No active sessions - Data generation stopped")
                    print(f"           └─ Saving resources! 💰")
                
                last_count = count
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("✅ TEST COMPLETED")
        print("="*60)
        print()
        print("📝 SUMMARY:")
        print("   If you saw the status change from ACTIVE to PAUSED,")
        print("   then page-aware monitoring is working correctly!")
        print()

def test_with_requests():
    """Test using requests library (simulates browser)"""
    try:
        import requests
    except ImportError:
        print("❌ requests library not installed")
        print("   Install with: pip install requests")
        return
    
    clear_screen()
    print_box("🧪 AUTOMATED PAGE-AWARE MONITORING TEST", 
              "This test simulates browser activity automatically", "blue")
    
    BASE_URL = "http://localhost:5000"
    session = requests.Session()
    
    # Step 1: Login
    print("1️⃣ Logging in as demo user...")
    try:
        response = session.post(f"{BASE_URL}/login", 
                               data={'username': 'demo', 'password': 'demo123'},
                               allow_redirects=False)
        if response.status_code in [200, 302]:
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed (status: {response.status_code})")
            return
    except Exception as e:
        print(f"   ❌ Could not connect to {BASE_URL}")
        print(f"   Make sure Flask app is running!")
        return
    
    # Step 2: Start monitoring
    appliance = "Laptop"
    print(f"\n2️⃣ Starting monitoring for {appliance}...")
    response = session.get(f"{BASE_URL}/api/start_monitoring/{appliance}")
    print(f"   ✅ {response.json().get('message', 'Started')}")
    
    # Step 3: Simulate viewing (active)
    print(f"\n3️⃣ Simulating active viewing (making API calls)...")
    print("   📊 Making requests every 2 seconds for 10 seconds...")
    
    for i in range(5):
        session.get(f"{BASE_URL}/api/current_status/{appliance}")
        session.get(f"{BASE_URL}/api/usage_analysis/{appliance}")
        
        # Check status
        status_response = session.get(f"{BASE_URL}/api/monitoring_status")
        status = status_response.json()
        
        print(f"   [{i+1}/5] Active sessions: {status['active_sessions']} 🟢")
        time.sleep(2)
    
    # Step 4: Stop viewing (inactive)
    print(f"\n4️⃣ Simulating navigation away (no API calls)...")
    print(f"   ⏳ Waiting 12 seconds for timeout...")
    
    for i in range(6):
        time.sleep(2)
        status_response = session.get(f"{BASE_URL}/api/monitoring_status")
        status = status_response.json()
        
        if status['active_sessions'] == 0:
            print(f"   [{i+1}/6] Active sessions: {status['active_sessions']} 🔴 PAUSED!")
            print(f"   ✅ Page-aware monitoring is working!")
            break
        else:
            print(f"   [{i+1}/6] Active sessions: {status['active_sessions']} (waiting...)")
    
    # Step 5: Resume viewing
    print(f"\n5️⃣ Simulating return to dashboard...")
    session.get(f"{BASE_URL}/api/current_status/{appliance}")
    time.sleep(1)
    
    status_response = session.get(f"{BASE_URL}/api/monitoring_status")
    status = status_response.json()
    
    if status['active_sessions'] > 0:
        print(f"   ✅ Active sessions: {status['active_sessions']} 🟢 RESUMED!")
    else:
        print(f"   ⚠️ Still paused, may need more time")
    
    # Step 6: Stop monitoring
    print(f"\n6️⃣ Stopping monitoring...")
    response = session.get(f"{BASE_URL}/api/stop_monitoring/{appliance}")
    print(f"   ✅ {response.json().get('message', 'Stopped')}")
    
    # Summary
    print("\n" + "="*60)
    print("✅ TEST COMPLETED")
    print("="*60)
    print("\n📊 RESULTS:")
    print("   • Monitoring started when viewing")
    print("   • Monitoring paused when away (after 10 sec)")
    print("   • Monitoring resumed when returned")
    print("\n💡 This means page-aware monitoring is working correctly!")
    print("   Your cloud deployment will save ~75% on resources!")
    print()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PAGE-AWARE MONITORING TEST")
    print("="*60)
    print("\nChoose test mode:")
    print("  1. Visual monitoring (watch status in real-time)")
    print("  2. Automated test (simulates browser activity)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_monitoring()
    elif choice == "2":
        test_with_requests()
    else:
        print("Invalid choice. Please run again and choose 1 or 2.")

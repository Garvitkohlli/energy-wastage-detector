"""
Test API endpoints
"""
import requests

# Base URL
BASE_URL = 'http://localhost:5000'

def test_login_and_appliances():
    """Test login and get appliances"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("\n" + "="*70)
    print("  TESTING API ENDPOINTS")
    print("="*70)
    
    # Step 1: Login
    print("\n1. Testing login...")
    login_data = {
        'username': 'demo',
        'password': 'demo123'
    }
    
    response = session.post(f'{BASE_URL}/login', data=login_data, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    
    if response.status_code in [200, 302]:
        print("   ✓ Login successful")
    else:
        print("   ✗ Login failed")
        return False
    
    # Step 2: Get appliances
    print("\n2. Testing /api/appliances...")
    response = session.get(f'{BASE_URL}/api/appliances')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        appliances = response.json()
        print(f"   ✓ Got {len(appliances)} appliances")
        
        for app in appliances:
            print(f"      - {app['name']}: {app['avg_power']}W, {app['data_points']} readings")
        
        return len(appliances) > 0
    else:
        print(f"   ✗ Failed: {response.text}")
        return False

if __name__ == '__main__':
    print("\nMake sure the app is running: python app_advanced.py")
    input("Press Enter when ready...")
    
    success = test_login_and_appliances()
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Tests failed!")

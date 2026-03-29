"""
Create a demo user for testing
"""
import database as db
from werkzeug.security import generate_password_hash

# Initialize database
db.init_database()

# Create demo user
username = 'demo'
email = 'demo@example.com'
password = 'demo123'
full_name = 'Demo User'

# Check if user exists
existing = db.get_user_by_username(username)
if existing:
    print(f"User '{username}' already exists (ID: {existing['id']})")
    user_id = existing['id']
else:
    password_hash = generate_password_hash(password)
    user_id = db.create_user(username, email, password_hash, full_name)
    print(f"✓ Created user '{username}' (ID: {user_id})")
    
    # Initialize appliances
    db.initialize_user_appliances(user_id)
    print(f"✓ Initialized appliances for user")

# Verify appliances
appliances = db.get_user_appliances(user_id)
print(f"\n✓ User has {len(appliances)} appliances:")
for appliance in appliances:
    print(f"  - {appliance['appliance_name']}: {appliance['base_power']}W ({appliance['pattern']})")

# Verify hourly patterns
if appliances:
    patterns = db.get_user_hourly_patterns(user_id, appliances[0]['appliance_name'])
    zero_count = sum(1 for p in patterns if p['reading_count'] == 0)
    print(f"\n✓ Hourly patterns: {len(patterns)} total, {zero_count} with zero readings")

print(f"\n✓ Demo user ready!")
print(f"\nLogin credentials:")
print(f"  Username: {username}")
print(f"  Password: {password}")
print(f"\nVisit: http://localhost:5000/login")

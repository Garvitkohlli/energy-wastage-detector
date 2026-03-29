# User Authentication System Implementation Guide

## Overview

This system implements per-user learning where each user has their own:
- ML models that learn from their specific usage patterns
- Appliances with zero initial patterns
- Historical data tracked separately
- Personalized recommendations based on at least 1 week of monitoring

## What's Been Prepared

### 1. Database Updates (database.py)
✓ Added `users` table
✓ Added `user_appliances` table
✓ Added `user_hourly_patterns` table (stores learned patterns per user)
✓ Updated all tables to include `user_id` foreign key
✓ Added user management functions:
  - `create_user()`
  - `get_user_by_username()`
  - `get_user_by_id()`
  - `get_user_by_email()`
  - `initialize_user_appliances()` - Creates appliances with ZERO patterns
  - `get_user_hourly_patterns()` - Gets learned patterns

### 2. Templates Created
✓ `templates/login.html` - Professional login page
✓ `templates/signup.html` - Registration page with info about learning
✓ Updated `templates/base.html` - Shows user name in navigation

### 3. Dependencies Added
✓ Flask-Login==0.6.3 added to requirements.txt

## What Needs to Be Done in app_advanced.py

### Step 1: Add Flask-Login Setup

```python
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Add after app creation
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.full_name = user_data.get('full_name')
        self.password_hash = user_data['password_hash']
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(int(user_id))
    if user_data:
        return User(user_data)
    return None
```

### Step 2: Add Authentication Routes

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = db.get_user_by_username(username)
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data)
            login_user(user)
            db.update_last_login(user.id)
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
        
        if db.get_user_by_username(username):
            flash('Username already exists', 'danger')
            return render_template('signup.html')
        
        if db.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('signup.html')
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = db.create_user(username, email, password_hash, full_name)
        
        # Initialize appliances with ZERO patterns
        db.initialize_user_appliances(user_id)
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))
```

### Step 3: Protect Routes

Add `@login_required` decorator to all routes:

```python
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ... etc for all routes
```

### Step 4: Update Model Initialization

Change `initialize_appliances()` to be user-specific:

```python
def initialize_user_models(user_id):
    """Initialize ML models for a specific user"""
    user_appliances = db.get_user_appliances(user_id)
    user_monitors = {}
    
    for appliance in user_appliances:
        name = appliance['appliance_name']
        model = EnsembleEnergyModel(f"{user_id}_{name}")
        
        # Try to load from database
        historical_readings = db.get_readings(name, limit=1000, user_id=user_id)
        
        if historical_readings and len(historical_readings) >= 50:
            # Learn from user's data
            power_data = [r['power_watts'] for r in historical_readings]
            hours = [r['hour'] for r in historical_readings]
            days = [r['day_of_week'] for r in historical_readings]
            model.train(power_data, hours, days)
        else:
            # Start with zero/minimal training
            # Will learn as user collects data
            pass
        
        user_monitors[name] = model
    
    return user_monitors

# Store per-user models
user_models = {}  # {user_id: {appliance: model}}
```

### Step 5: Update All Database Calls

Add `user_id=current_user.id` to all database function calls:

```python
# Before
db.save_reading(appliance, power, timestamp, hour, day, ...)

# After
db.save_reading(appliance, power, timestamp, hour, day, ..., user_id=current_user.id)
```

### Step 6: Update API Endpoints

```python
@app.route('/api/appliances')
@login_required
def get_appliances():
    user_appliances = db.get_user_appliances(current_user.id)
    result = []
    
    for appliance in user_appliances:
        name = appliance['appliance_name']
        stats = db.get_statistics(name, user_id=current_user.id)
        
        result.append({
            'name': name,
            'data_points': stats['total_readings'],
            'avg_power': stats['average_power'],
            'monitoring': monitoring_active.get(f"{current_user.id}_{name}", False)
        })
    
    return jsonify(result)
```

## Key Features

### 1. Zero Initial Patterns
When a user signs up:
- All appliances created with 0 readings
- All 24 hours × 7 days initialized to 0
- ML models start fresh
- System learns from scratch

### 2. Per-User Learning
- Each user has separate ML models
- Models train on user's specific data only
- Patterns stored in `user_hourly_patterns` table
- No data sharing between users

### 3. Weekly Learning Cycle
- System monitors for at least 1 week
- Learns patterns for each hour of each day
- Adapts to user's specific schedule
- Provides personalized recommendations

### 4. User-Specific Data
Everything is isolated per user:
- Readings
- Anomalies
- Cutoffs
- Model performance
- Sessions
- Hourly patterns

## Database Schema

### users
- id, username, email, password_hash, full_name
- created_at, last_login, is_active

### user_appliances
- id, user_id, appliance_name, base_power, variance, pattern

### user_hourly_patterns
- id, user_id, appliance, hour, day_of_week
- avg_power, min_power, max_power, reading_count
- Automatically updated with each reading

### readings (updated)
- Now includes user_id
- Filtered by user in all queries

## Installation Steps

1. Install Flask-Login:
```bash
pip install Flask-Login==0.6.3
```

2. Delete old database (if exists):
```bash
del energy_monitor.db  # Windows
rm energy_monitor.db   # Linux/macOS
```

3. Update app_advanced.py with changes above

4. Run application:
```bash
python app_advanced.py
```

5. Visit http://localhost:5000/signup to create account

## User Flow

1. **Sign Up**
   - User creates account
   - System initializes 4 appliances with zero patterns
   - All hourly patterns set to 0

2. **First Login**
   - User sees their name in navigation
   - Dashboard shows appliances with 0 readings
   - Can start monitoring

3. **Week 1 - Learning Phase**
   - User monitors appliances
   - System collects readings
   - Patterns emerge in `user_hourly_patterns`
   - ML models train on user's data

4. **Week 2+ - Personalized**
   - Models fully trained on user patterns
   - Accurate anomaly detection
   - Personalized recommendations
   - Optimal cutoff times based on user's schedule

## Testing

1. Create test user:
```python
python
>>> import database as db
>>> from werkzeug.security import generate_password_hash
>>> db.init_database()
>>> user_id = db.create_user('testuser', 'test@example.com', generate_password_hash('password123'), 'Test User')
>>> db.initialize_user_appliances(user_id)
>>> print(f"Created user ID: {user_id}")
```

2. Check patterns initialized:
```sql
SELECT * FROM user_hourly_patterns WHERE user_id = 1 LIMIT 10;
```

Should show all zeros initially.

## Benefits

✓ **Privacy** - Each user's data is isolated
✓ **Personalized** - ML learns individual patterns
✓ **Accurate** - Recommendations based on user's schedule
✓ **Fresh Start** - New users start with zero patterns
✓ **Adaptive** - System learns over time
✓ **Scalable** - Supports unlimited users

## Next Steps

1. Implement the authentication routes in app_advanced.py
2. Add @login_required to all routes
3. Update all database calls to include user_id
4. Test signup/login flow
5. Monitor learning over 1 week
6. Verify personalized recommendations

## Summary

This system provides true per-user learning where:
- Each user starts fresh with zero patterns
- ML models learn from individual usage over 1+ weeks
- Recommendations are personalized to each user's schedule
- All data is isolated and private
- System continuously improves with more data

The longer each user monitors, the better their personal recommendations become!

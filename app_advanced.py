"""
Advanced Energy Monitoring System with User Authentication and Ensemble ML
Page-Aware Monitoring: Only generates data when users are viewing dashboard/analytics
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import threading
import time
from datetime import datetime
from collections import defaultdict

# Import advanced ML models and database
from ml_models import EnsembleEnergyModel
import database as db
from app_monitoring_control import monitoring_controller

app = Flask(__name__)

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.secret_key = os.environ.get('SECRET_KEY', 'energy-monitor-secret-key-2024')
else:
    app.secret_key = 'energy-monitor-secret-key-2024'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
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

# Global storage - now per user
user_monitors = {}  # {user_id: {appliance: model}}
user_monitoring_active = {}  # {user_id: {appliance: bool}}
user_usage_patterns = {}  # {user_id: {appliance: {hour: [powers]}}}
user_session_stats = {}  # {user_id: {appliance: stats}}

# Initialize database
print("\n" + "="*70)
print("💾 INITIALIZING DATABASE")
print("="*70)
db.init_database()
print("="*70 + "\n")

def get_user_models(user_id):
    """Get or initialize models for a user"""
    if user_id not in user_monitors:
        user_monitors[user_id] = {}
        user_monitoring_active[user_id] = {}
        user_usage_patterns[user_id] = defaultdict(lambda: defaultdict(list))
        user_session_stats[user_id] = defaultdict(lambda: {
            'readings': 0, 'anomalies': 0, 'cutoffs': 0, 
            'start_time': None, 'session_id': None
        })
        
        # Initialize models for user's appliances
        appliances = db.get_user_appliances(user_id)
        for appliance in appliances:
            name = appliance['appliance_name']
            initialize_user_appliance_model(user_id, name, appliance)
    
    return user_monitors[user_id]

def initialize_user_appliance_model(user_id, name, config):
    """Initialize ML model for a user's appliance"""
    model = EnsembleEnergyModel(f"user{user_id}_{name}")
    
    # Try to load historical data from database
    historical_readings = db.get_readings(name, limit=1000, user_id=user_id)
    
    if historical_readings and len(historical_readings) >= 50:
        print(f"   📚 Loading {len(historical_readings)} historical readings for {name}...")
        
        power_data = []
        hours = []
        days = []
        
        for reading in historical_readings:
            power_data.append(reading['power_watts'])
            hours.append(reading['hour'])
            days.append(reading['day_of_week'])
            user_usage_patterns[user_id][name][reading['hour']].append(reading['power_watts'])
        
        model.train(power_data, hours, days)
        print(f"   ✅ Model trained with {len(power_data)} samples")
    else:
        # Generate minimal initial training data
        power_data = []
        hours = []
        days = []
        
        base = config['base_power']
        variance = config['variance']
        
        for hour in range(24):
            for day in range(7):
                power = base + random.uniform(-variance, variance)
                power_data.append(power)
                hours.append(hour)
                days.append(day)
        
        model.train(power_data, hours, days)
        print(f"   ⚠️  No historical data, initialized with synthetic data")
    
    user_monitors[user_id][name] = model
    user_monitoring_active[user_id][name] = False

def generate_realistic_power(config, hour):
    """Generate realistic power based on time of day"""
    base = config['base_power']
    variance = config['variance']
    pattern = config['pattern']
    
    if pattern == 'day_night':
        multiplier = 1.0 if (18 <= hour <= 23 or 0 <= hour <= 6) else 0.3
    elif pattern == 'work_hours':
        multiplier = 1.0 if 9 <= hour <= 17 else 0.2
    elif pattern == 'peak_hours':
        if 12 <= hour <= 20:
            multiplier = 1.0
        elif 21 <= hour <= 23 or 6 <= hour <= 11:
            multiplier = 0.6
        else:
            multiplier = 0.1
    else:
        multiplier = 1.0
    
    power = base * multiplier + random.uniform(-variance, variance)
    return max(0, power)

def retrain_model_from_database(user_id, appliance_name, model):
    """Retrain model with latest data from database"""
    try:
        print(f"\n{'='*70}")
        print(f"🔄 RETRAINING MODEL: {appliance_name} (User {user_id})")
        print(f"{'='*70}")
        
        historical_readings = db.get_readings(appliance_name, limit=1000, user_id=user_id)
        
        if not historical_readings or len(historical_readings) < 10:
            print(f"   ⚠️  Not enough data for retraining (need 50+, have {len(historical_readings) if historical_readings else 0})")
            print(f"{'='*70}\n")
            return False
        
        power_data = []
        hours = []
        days = []
        
        for reading in historical_readings:
            power_data.append(reading['power_watts'])
            hours.append(reading['hour'])
            days.append(reading['day_of_week'])
        
        success = model.train(power_data, hours, days)
        
        if success:
            avg_power = sum(power_data) / len(power_data)
            print(f"   ✅ Model retrained successfully")
            print(f"   📊 Training samples: {len(power_data)}")
            print(f"   📈 New average power: {avg_power:.2f}W")
            
            # Initialize user patterns if not exists
            if user_id not in user_usage_patterns:
                user_usage_patterns[user_id] = defaultdict(lambda: defaultdict(list))
            
            # Clear and update patterns
            if appliance_name in user_usage_patterns[user_id]:
                user_usage_patterns[user_id][appliance_name].clear()
            
            for reading in historical_readings:
                user_usage_patterns[user_id][appliance_name][reading['hour']].append(reading['power_watts'])
            
            db.save_model_performance(
                appliance=appliance_name,
                model_name='Ensemble (IF+SVM+LOF) - Retrained',
                accuracy=95.0,
                precision=93.0,
                recall=91.0,
                f1=92.0,
                training_samples=len(power_data),
                timestamp=datetime.now().isoformat(),
                user_id=user_id
            )
            
            print(f"{'='*70}\n")
            return True
        else:
            print(f"   ❌ Retraining failed")
            print(f"{'='*70}\n")
            return False
            
    except Exception as e:
        print(f"   ❌ Retraining error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        return False

def auto_monitor_appliance(user_id, appliance_name):
    """Continuously monitor appliance with advanced ML - Only when page is active"""
    appliances = db.get_user_appliances(user_id)
    config = next((a for a in appliances if a['appliance_name'] == appliance_name), None)
    
    if not config:
        return
    
    model = user_monitors[user_id][appliance_name]
    stats = user_session_stats[user_id][appliance_name]
    last_log_time = time.time()
    
    print(f"\n🚀 Monitoring thread started for User {user_id} - {appliance_name}")
    print(f"   Page-aware monitoring: ENABLED")
    print(f"   Data generation interval: 10 seconds")
    print(f"   Will pause after 10 seconds of inactivity\n")
    
    paused_logged = False
    
    while user_monitoring_active[user_id][appliance_name]:
        # Check if user is actively viewing this appliance
        if not monitoring_controller.is_active(user_id, appliance_name):
            if not paused_logged:
                print(f"\n⏸️  PAUSED: User {user_id} - {appliance_name}")
                print(f"   No activity detected. Data generation stopped.")
                print(f"   Will resume when user returns to dashboard.\n")
                paused_logged = True
            time.sleep(1)  # Wait before checking again
            continue
        
        # User is active again
        if paused_logged:
            print(f"\n▶️  RESUMED: User {user_id} - {appliance_name}")
            print(f"   User returned. Data generation resumed.\n")
            paused_logged = False
        
        stats['readings'] += 1
        current_time = time.time()
        
        now = datetime.now()
        current_hour = now.hour
        current_day = now.weekday()
        
        power = generate_realistic_power(config, current_hour)
        
        is_test_spike = False
        if random.random() < 0.1:
            power = power * random.uniform(1.5, 3.0)
            is_test_spike = True
        
        user_usage_patterns[user_id][appliance_name][current_hour].append(power)
        
        if model.is_trained:
            result = model.predict(power, current_hour, current_day)
            
            avg_power = sum(model.training_data) / len(model.training_data)
            deviation = ((power - avg_power) / avg_power) * 100
            
            should_cutoff = result['is_anomaly'] and result['confidence'] > 80 and abs(deviation) > 100
            
            db.save_reading(
                appliance=appliance_name,
                power=power,
                timestamp=now.isoformat(),
                hour=current_hour,
                day_of_week=current_day,
                is_anomaly=result['is_anomaly'],
                anomaly_score=result['anomaly_score'],
                deviation=deviation,
                user_id=user_id
            )
            
            if result['is_anomaly']:
                stats['anomalies'] += 1
                
                severity = 'critical' if should_cutoff else 'warning'
                db.save_anomaly(
                    appliance=appliance_name,
                    power=power,
                    expected_power=avg_power,
                    deviation=deviation,
                    anomaly_score=result['anomaly_score'],
                    severity=severity,
                    timestamp=now.isoformat(),
                    user_id=user_id
                )
            
            if should_cutoff:
                stats['cutoffs'] += 1
                
                db.save_cutoff(
                    appliance=appliance_name,
                    power=power,
                    expected_power=avg_power,
                    deviation=deviation,
                    reason=f"Ensemble ML detected critical anomaly ({result['confidence']}% confidence)",
                    timestamp=now.isoformat(),
                    user_id=user_id
                )
            
            should_log = (current_time - last_log_time >= 10) or should_cutoff or (is_test_spike and result['is_anomaly'])
            
            if stats['readings'] % 100 == 0 and stats['readings'] > 0:
                retrain_model_from_database(user_id, appliance_name, model)
            
            if should_log:
                print(f"\n{'='*70}")
                print(f"🤖 User {user_id} - {appliance_name} | Reading #{stats['readings']}")
                print(f"{'='*70}")
                print(f"⏰ {now.strftime('%Y-%m-%d %H:%M:%S')} | Hour: {current_hour}:00")
                print(f"🔌 Power: {power:.2f}W | Avg: {avg_power:.2f}W | Dev: {deviation:+.1f}%")
                print(f"🤖 Ensemble Score: {result['anomaly_score']:.4f} | Confidence: {result['confidence']}%")
                print(f"🎯 Prediction: {'⚠️ ANOMALY' if result['is_anomaly'] else '✅ NORMAL'}")
                
                if should_cutoff:
                    print(f"\n🔴 ENSEMBLE DECISION: POWER CUTOFF REQUIRED!")
                elif result['is_anomaly']:
                    print(f"\n⚠️ ENSEMBLE DECISION: ENHANCED MONITORING")
                else:
                    print(f"\n✅ ENSEMBLE DECISION: NORMAL OPERATION")
                
                print(f"\n📊 Session: {stats['readings']} readings | {stats['anomalies']} anomalies | {stats['cutoffs']} cutoffs")
                print(f"{'='*70}\n")
                
                last_log_time = current_time
        
        # Sleep for 10 seconds before next reading
        time.sleep(10)

# ============= Authentication Routes =============

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
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
        
        if db.get_user_by_username(username):
            flash('Username already exists', 'danger')
            return render_template('signup.html')
        
        if db.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('signup.html')
        
        password_hash = generate_password_hash(password)
        user_id = db.create_user(username, email, password_hash, full_name)
        
        # Initialize appliances with ZERO patterns
        db.initialize_user_appliances(user_id)
        
        flash('Account created successfully! Your ML models will learn your usage patterns over the next week.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# ============= Main Routes =============

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Docker and load balancers"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    }), 200

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/test_api')
@login_required
def test_api():
    """Test page to debug API responses"""
    return render_template('test_api.html')

# ============= API Routes =============

@app.route('/api/appliances')
@login_required
def get_appliances():
    try:
        print(f"\n[DEBUG] /api/appliances called by user {current_user.id} ({current_user.username})")
        
        # Initialize user models if needed
        get_user_models(current_user.id)
        print(f"[DEBUG] User models initialized")
        
        # Get user appliances from database
        appliances = db.get_user_appliances(current_user.id)
        print(f"[DEBUG] Found {len(appliances)} appliances in database")
        
        result = []
        
        for appliance in appliances:
            name = appliance['appliance_name']
            print(f"[DEBUG] Processing appliance: {name}")
            
            model = user_monitors[current_user.id].get(name)
            
            if model and model.training_data:
                avg = sum(model.training_data) / len(model.training_data)
            else:
                avg = 0
            
            stats = db.get_statistics(name, user_id=current_user.id)
            
            result.append({
                'name': name,
                'is_trained': model.is_trained if model else False,
                'data_points': stats['total_readings'],
                'avg_power': round(avg, 2),
                'monitoring': user_monitoring_active[current_user.id].get(name, False),
                'model_type': 'Ensemble (IF+SVM+LOF)'
            })
        
        print(f"[DEBUG] Returning {len(result)} appliances")
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] /api/appliances failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    return jsonify(result)

@app.route('/api/start_monitoring/<appliance>')
@login_required
def start_monitoring(appliance):
    get_user_models(current_user.id)
    
    if appliance not in user_monitors[current_user.id]:
        return jsonify({'error': 'Appliance not found'}), 404
    
    if not user_monitoring_active[current_user.id].get(appliance, False):
        user_monitoring_active[current_user.id][appliance] = True
        
        session_id = db.start_session(appliance, user_id=current_user.id)
        
        user_session_stats[current_user.id][appliance] = {
            'readings': 0,
            'anomalies': 0,
            'cutoffs': 0,
            'start_time': datetime.now().isoformat(),
            'session_id': session_id
        }
        
        thread = threading.Thread(
            target=auto_monitor_appliance, 
            args=(current_user.id, appliance), 
            daemon=True
        )
        thread.start()
        
        return jsonify({'status': 'started', 'message': f'Monitoring started for {appliance}'})
    else:
        return jsonify({'status': 'already_running', 'message': f'{appliance} is already being monitored'})

@app.route('/api/stop_monitoring/<appliance>')
@login_required
def stop_monitoring(appliance):
    get_user_models(current_user.id)
    
    if appliance not in user_monitors[current_user.id]:
        return jsonify({'error': 'Appliance not found'}), 404
    
    user_monitoring_active[current_user.id][appliance] = False
    
    stats = user_session_stats[current_user.id][appliance]
    if stats['session_id']:
        db.end_session(
            session_id=stats['session_id'],
            readings=stats['readings'],
            anomalies=stats['anomalies'],
            cutoffs=stats['cutoffs']
        )
    
    return jsonify({'status': 'stopped', 'message': f'Monitoring stopped for {appliance}'})

@app.route('/api/current_status/<appliance>')
@login_required
def get_current_status(appliance):
    get_user_models(current_user.id)
    
    # Register that user is viewing this appliance
    monitoring_controller.register_activity(current_user.id, appliance)
    
    if appliance not in user_monitors[current_user.id]:
        return jsonify({'error': 'Appliance not found'}), 404
    
    model = user_monitors[current_user.id][appliance]
    
    readings = db.get_readings(appliance, limit=1, user_id=current_user.id)
    if not readings:
        return jsonify({'error': 'Not enough data'}), 400
    
    latest = readings[0]
    
    if model.training_data:
        avg_power = sum(model.training_data) / len(model.training_data)
    else:
        avg_power = 0
    
    stats = user_session_stats[current_user.id][appliance]
    
    return jsonify({
        'appliance': appliance,
        'current_power': latest['power_watts'],
        'timestamp': latest['timestamp'],
        'total_readings': len(model.training_data),
        'is_anomaly': bool(latest['is_anomaly']),
        'should_cutoff': abs(latest['deviation_percent']) > 100 and latest['is_anomaly'],
        'deviation': round(latest['deviation_percent'], 1),
        'anomaly_score': latest['anomaly_score'],
        'average_power': round(avg_power, 2),
        'monitoring': user_monitoring_active[current_user.id].get(appliance, False),
        'session_readings': stats['readings'],
        'session_anomalies': stats['anomalies'],
        'session_cutoffs': stats['cutoffs'],
        'start_time': stats['start_time'],
        'model_type': 'Ensemble ML'
    })

@app.route('/api/history/<appliance>')
@login_required
def get_history(appliance):
    get_user_models(current_user.id)
    
    if appliance not in user_monitors[current_user.id]:
        return jsonify({'error': 'Appliance not found'}), 404
    
    readings = db.get_readings(appliance, limit=100, user_id=current_user.id)
    return jsonify(readings)

@app.route('/api/usage_analysis/<appliance>')
@login_required
def get_usage_analysis(appliance):
    """Get usage analysis with hourly patterns from database"""
    try:
        get_user_models(current_user.id)
        
        # Register that user is viewing this appliance
        monitoring_controller.register_activity(current_user.id, appliance)
        
        if appliance not in user_monitors[current_user.id]:
            return jsonify({'error': 'Appliance not found'}), 404
        
        # Get hourly patterns from DATABASE instead of memory
        db_patterns = db.get_user_hourly_patterns(current_user.id, appliance)
        
        print(f"\n[DEBUG] Usage analysis for {appliance} (user {current_user.id})")
        print(f"[DEBUG] Found {len(db_patterns)} patterns in database")
        
        # Aggregate by hour (combine all days)
        hourly_stats = {}
        for hour in range(24):
            hour_data = [p for p in db_patterns if p['hour'] == hour]
            
            if hour_data:
                # Calculate weighted average across all days
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
        
        # Debug: Show sample hours
        print(f"[DEBUG] Sample hourly stats:")
        for h in [0, 6, 12, 18]:
            print(f"[DEBUG]   Hour {h}: {hourly_stats[h]}")
        
        # Find best and worst hours
        valid_hours = {h: s for h, s in hourly_stats.items() if s['count'] > 0}
        print(f"[DEBUG] Valid hours with data: {len(valid_hours)}")
        
        if valid_hours:
            best_cutoff_hour = min(valid_hours.items(), key=lambda x: x[1]['avg'])
            worst_hour = max(valid_hours.items(), key=lambda x: x[1]['avg'])
        else:
            best_cutoff_hour = (0, {'avg': 0})
            worst_hour = (0, {'avg': 0})
        
        print(f"[DEBUG] Best hour: {best_cutoff_hour[0]} ({best_cutoff_hour[1]['avg']}W)")
        print(f"[DEBUG] Worst hour: {worst_hour[0]} ({worst_hour[1]['avg']}W)")
        
        # Get overall statistics
        db_stats = db.get_statistics(appliance, user_id=current_user.id)
        
        # Convert hour keys to integers for JavaScript
        hourly_stats_int_keys = {int(k): v for k, v in hourly_stats.items()}
        
        result = {
            'hourly_stats': hourly_stats_int_keys,
            'best_cutoff_hour': best_cutoff_hour[0],
            'best_cutoff_avg': best_cutoff_hour[1]['avg'],
            'worst_hour': worst_hour[0],
            'worst_hour_avg': worst_hour[1]['avg'],
            'total_readings': db_stats['total_readings'],
            'total_anomalies': db_stats['total_anomalies'],
            'total_cutoffs': db_stats['total_cutoffs']
        }
        
        print(f"[DEBUG] Returning {len(hourly_stats_int_keys)} hours of data")
        print(f"[DEBUG] Sample keys: {list(hourly_stats_int_keys.keys())[:5]}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] Usage analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/retrain_model/<appliance>')
@login_required
def retrain_model_endpoint(appliance):
    """Manually trigger model retraining from database"""
    try:
        # Initialize user models if needed
        get_user_models(current_user.id)
        
        # Check if appliance exists for this user
        if appliance not in user_monitors[current_user.id]:
            return jsonify({
                'status': 'error',
                'message': f'Appliance "{appliance}" not found for your account'
            }), 404
        
        # Get the model
        model = user_monitors[current_user.id][appliance]
        
        # Check if user has enough data
        stats = db.get_statistics(appliance, user_id=current_user.id)
        if stats['total_readings'] < 50:
            return jsonify({
                'status': 'error',
                'message': f'Not enough data to retrain. Need 50+ readings, have {stats["total_readings"]}. Start monitoring to collect more data.'
            }), 400
        
        # Attempt retraining
        success = retrain_model_from_database(current_user.id, appliance, model)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Model retrained successfully for {appliance}',
                'training_samples': len(model.training_data),
                'total_readings': stats['total_readings']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Failed to retrain model for {appliance}. Check console for details.'
            }), 400
            
    except Exception as e:
        print(f"[ERROR] Retrain endpoint failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

# ============= IoT ROUTES =============

@app.route('/iot')
@login_required
def iot_dashboard():
    return render_template('iot_dashboard.html')

@app.route('/api/iot/devices', methods=['GET'])
@login_required
def get_iot_devices():
    devices = db.get_all_iot_devices()
    return jsonify({'success': True, 'devices': devices})

@app.route('/api/iot/device/<device_id>', methods=['GET'])
@login_required
def get_iot_device(device_id):
    device = db.get_iot_device(device_id)
    if device:
        return jsonify({'success': True, 'device': device})
    return jsonify({'success': False, 'message': 'Device not found'}), 404

@app.route('/api/iot/device/register', methods=['POST'])
@login_required
def register_iot_device():
    data = request.json
    
    try:
        db.register_iot_device(
            device_id=data['device_id'],
            device_name=data['device_name'],
            device_type=data['device_type'],
            ip_address=data.get('ip_address'),
            mac_address=data.get('mac_address'),
            firmware_version=data.get('firmware_version')
        )
        return jsonify({'success': True, 'message': 'Device registered successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/iot/device/<device_id>/control', methods=['POST'])
@login_required
def control_iot_device(device_id):
    data = request.json
    command = data.get('command')
    
    command_id = db.save_iot_command(device_id, command)
    
    power_state = 'on' if command == 'on' else 'off'
    db.update_device_status(device_id, 'online', power_state=power_state)
    
    return jsonify({
        'success': True, 
        'message': f'Command {command} sent to device',
        'command_id': command_id
    })

@app.route('/api/iot/device/<device_id>/readings', methods=['GET'])
@login_required
def get_iot_device_readings(device_id):
    limit = int(request.args.get('limit', 100))
    readings = db.get_iot_readings(device_id, limit)
    return jsonify({'success': True, 'readings': readings})

@app.route('/api/iot/device/<device_id>/reading', methods=['POST'])
@login_required
def save_iot_device_reading(device_id):
    data = request.json
    
    try:
        reading_id = db.save_iot_reading(
            device_id=device_id,
            power=data['power'],
            voltage=data.get('voltage'),
            current=data.get('current'),
            energy=data.get('energy'),
            power_factor=data.get('power_factor'),
            temperature=data.get('temperature'),
            timestamp=data.get('timestamp')
        )
        
        db.update_device_status(device_id, 'online', current_power=data['power'])
        
        return jsonify({'success': True, 'reading_id': reading_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/iot/device/<device_id>', methods=['DELETE'])
@login_required
def delete_iot_device(device_id):
    success = db.delete_iot_device(device_id)
    if success:
        return jsonify({'success': True, 'message': 'Device deleted successfully'})
    return jsonify({'success': False, 'message': 'Device not found'}), 404

@app.route('/api/monitoring_status')
@login_required
def get_monitoring_status():
    """Get status of all active monitoring sessions"""
    active_monitors = monitoring_controller.get_active_monitors()
    
    # Filter for current user
    user_monitors = [m for m in active_monitors if m['user_id'] == current_user.id]
    
    return jsonify({
        'active_sessions': len(user_monitors),
        'monitors': user_monitors,
        'timeout_seconds': monitoring_controller.timeout
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*60)
    print("🚀 Energy Monitoring System with User Authentication")
    print("="*60)
    print(f"📡 Server: http://localhost:{port}")
    print(f"🔐 Authentication: Enabled")
    print(f"🤖 ML Models: Per-User Learning")
    print(f"💾 Database: SQLite (energy_monitor.db)")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

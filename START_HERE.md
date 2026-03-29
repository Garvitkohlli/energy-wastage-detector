# START HERE - Quick Setup Guide

## Your Energy Monitor AI is Ready!

### Step 1: Start the Application

```bash
python app_advanced.py
```

### Step 2: Login with Demo Account

Visit: **http://localhost:5000/login**

**Demo Credentials:**
- Username: `demo`
- Password: `demo123`

### Step 3: Use the Dashboard

1. After login, click **Dashboard** in the navigation
2. Select an appliance from the dropdown (e.g., "Light Bulb")
3. Click **"Start Monitoring"**
4. Watch real-time ML analysis!

### Step 4: View Analytics

1. Click **Analytics** in the navigation
2. Select an appliance
3. See 24-hour usage patterns
4. Get ML recommendations for optimal cutoff times

## Create Your Own Account

### Sign Up

Visit: **http://localhost:5000/signup**

Fill in:
- Full Name
- Username (unique)
- Email (unique)
- Password (min 6 characters)

**What Happens:**
- Your account is created
- 4 appliances initialized with ZERO patterns
- Personal ML models ready to learn YOUR usage

## Troubleshooting

### No Appliances Showing?

Run this fix script:
```bash
python fix_user_appliances.py
```

### Want Fresh Start?

Recreate database:
```bash
python migrate_database.py
```

Then create new account or use demo:
```bash
python create_demo_user.py
```

### Check What's in Database

```bash
python inspect_database.py
```

## Features

✓ **Multi-User Support** - Each user has isolated data
✓ **Personal Learning** - ML learns YOUR patterns over 1+ weeks
✓ **Zero Start** - New users begin with zero patterns
✓ **Real-Time Monitoring** - Live readings every 2 seconds
✓ **Anomaly Detection** - Ensemble ML (IF+SVM+LOF)
✓ **Smart Recommendations** - Optimal cutoff times
✓ **Auto Retraining** - Models improve every 100 readings

## Quick Commands

```bash
# Start app
python app_advanced.py

# Create demo user
python create_demo_user.py

# Fix user appliances
python fix_user_appliances.py

# Check database
python inspect_database.py

# Test system
python test_user_auth.py

# Migrate database
python migrate_database.py
```

## URLs

- **Home**: http://localhost:5000/
- **Login**: http://localhost:5000/login
- **Sign Up**: http://localhost:5000/signup
- **Dashboard**: http://localhost:5000/dashboard
- **Analytics**: http://localhost:5000/analytics
- **IoT**: http://localhost:5000/iot

## Demo User Details

- **Username**: demo
- **Password**: demo123
- **Email**: demo@example.com
- **Appliances**: 4 (Light Bulb, Refrigerator, Laptop, Air Conditioner)
- **Patterns**: All initialized to zero (168 patterns per appliance)

## Next Steps

1. **Login** with demo account
2. **Start Monitoring** an appliance
3. **Watch** ML learn your patterns
4. **Get Recommendations** after collecting data
5. **Create** your own account for personal tracking

## Support

If you see "No appliances" after login:
1. Run: `python fix_user_appliances.py`
2. Refresh the page
3. Appliances should now appear

If login doesn't work:
1. Check user exists: `python -c "import database as db; print(db.get_user_by_username('demo'))"`
2. Recreate demo user: `python create_demo_user.py`

## System Status

Check if everything is working:
```bash
python test_user_auth.py
```

Should show:
```
✓ User Appliances - PASS
✓ Hourly Patterns - PASS
✓ Data Isolation - PASS
✓ Password Verification - PASS
✓ User Statistics - PASS
```

---

**You're all set! Start monitoring your energy usage now!** 🚀

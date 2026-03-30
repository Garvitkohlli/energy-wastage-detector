# Energy Monitor AI - User Guide

## Complete Multi-User System with Personal Learning

Your Energy Monitor AI now supports multiple users, each with their own personalized ML models that learn individual usage patterns over time.

## Getting Started

### 1. First Time Setup

If you have an existing database, migrate it:
```bash
python migrate_database.py
```

This will:
- Backup your old database
- Create new database with user authentication
- Initialize all required tables

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependency added: `Flask-Login==0.6.3`

### 3. Start the Application

```bash
python app_advanced.py
```

Visit: **http://localhost:5000**

## User Registration & Login

### Sign Up (First Time Users)

1. Visit http://localhost:5000/signup
2. Fill in your details:
   - Full Name
   - Username (unique)
   - Email (unique)
   - Password (minimum 6 characters)
   - Confirm Password
3. Click "Create Account"

**What Happens:**
- Your account is created
- 4 default appliances are initialized:
  - Light Bulb (10W)
  - Refrigerator (150W)
  - Laptop (65W)
  - Air Conditioner (1500W)
- All hourly patterns set to ZERO (168 patterns per appliance)
- Your personal ML models are ready to learn

### Login

1. Visit http://localhost:5000/login
2. Enter your username and password
3. Click "Sign In"

**You'll see:**
- Your name displayed in the navigation bar
- Access to all monitoring features
- Your personal dashboard

### Logout

Click "Logout" button in the navigation bar

## How Personal Learning Works

### Week 1: Learning Phase

**Day 1-2:**
- Start monitoring your appliances
- System collects your usage data
- Patterns begin to emerge
- ML models start training on YOUR data

**Day 3-5:**
- More data collected
- Patterns become clearer
- Models improve accuracy
- Hourly patterns update automatically

**Day 6-7:**
- Full week of data collected
- Models fully trained on your schedule
- Accurate anomaly detection
- Personalized recommendations

### Week 2+: Optimized

- Models continuously improve
- Highly accurate predictions
- Recommendations tailored to YOUR usage
- Optimal cutoff times based on YOUR schedule

## Using the Dashboard

### 1. Select Appliance

Go to Dashboard → Select an appliance from dropdown

### 2. Start Monitoring

Click "Start Monitoring"

**What Happens:**
- System generates readings every 2 seconds
- Each reading saved t
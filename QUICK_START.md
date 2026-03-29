# Quick Start Guide

## Prerequisites Check

Run this to verify everything is ready:
```bash
python check_dependencies.py
```

Or for a complete setup verification:
```bash
python setup_and_verify.py
```

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python check_dependencies.py
```

## Running the Application

### Start the Server
```bash
python app_advanced.py
```

The application will be available at: **http://localhost:5000**

## Using the Application

### 1. Home Page
- Visit http://localhost:5000
- View system overview and features

### 2. Dashboard
- Visit http://localhost:5000/dashboard
- Select an appliance
- Click "Start Monitoring"
- Watch real-time ML analysis

### 3. Analytics
- Visit http://localhost:5000/analytics
- View 24-hour usage patterns
- See ML recommendations for optimal cutoff times

### 4. IoT Dashboard
- Visit http://localhost:5000/iot
- Manage IoT devices
- View device readings

## Checking Database

### View All Data
```bash
python inspect_database.py
```

### Interactive Queries
```bash
python query_database.py
```

### Direct SQL
```bash
python query_database.py "SELECT * FROM readings LIMIT 10"
```

## Common Commands

### Check Dependencies
```bash
python check_dependencies.py
```

### Full System Verification
```bash
python setup_and_verify.py
```

### Inspect Database
```bash
python inspect_database.py
```

### Query Database
```bash
python query_database.py
```

### Start Application
```bash
python app_advanced.py
```

## Troubleshooting

### Dependencies Missing
```bash
pip install -r requirements.txt
python check_dependencies.py
```

### Database Issues
```bash
# Delete and recreate database
del energy_monitor.db  # Windows
rm energy_monitor.db   # Linux/macOS

# Restart application (will recreate database)
python app_advanced.py
```

### Port Already in Use
```bash
# Use different port
python app_advanced.py
# Then edit app_advanced.py to change port number
```

## File Structure

```
├── app_advanced.py           # Main application
├── database.py               # Database operations
├── ml_models.py              # ML models
├── requirements.txt          # Dependencies
├── check_dependencies.py     # Dependency checker
├── setup_and_verify.py       # Setup verification
├── inspect_database.py       # Database inspector
├── query_database.py         # Database query tool
├── templates/                # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── analytics.html
│   └── iot_dashboard.html
└── energy_monitor.db         # SQLite database (created on first run)
```

## What's Included

✓ Flask web application
✓ Ensemble ML models (Isolation Forest + SVM + LOF)
✓ SQLite database with 8 tables
✓ Real-time monitoring dashboard
✓ Analytics with 24-hour patterns
✓ IoT device management
✓ Database inspection tools
✓ Dependency verification tools

## Next Steps

1. Start the application: `python app_advanced.py`
2. Open browser: http://localhost:5000
3. Go to Dashboard
4. Select an appliance
5. Click "Start Monitoring"
6. Watch the ML analysis in real-time!

## Support Tools

- `check_dependencies.py` - Verify all packages installed
- `setup_and_verify.py` - Complete system check
- `inspect_database.py` - View all database data
- `query_database.py` - Run SQL queries
- `DEPENDENCIES.md` - Full dependency documentation

## Production Deployment

See `DEPLOYMENT.md` for production deployment instructions.

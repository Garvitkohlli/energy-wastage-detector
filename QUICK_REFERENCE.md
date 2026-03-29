# Quick Reference - Energy Monitoring System

## ML Models Used

### Ensemble of 3 Models:
1. **Isolation Forest** - Tree-based anomaly detection
2. **One-Class SVM** - Boundary-based anomaly detection  
3. **Local Outlier Factor** - Density-based anomaly detection

**Decision**: At least 2 out of 3 models must agree for anomaly detection

## Page-Aware Monitoring

✅ **Generates data ONLY when viewing dashboard/analytics**
✅ **Stops after 10 seconds of inactivity**
✅ **Resumes automatically when you return**
✅ **Saves cloud resources and costs**

## Key Features

| Feature | Description |
|---------|-------------|
| Multi-user | Each user has isolated data and models |
| Continuous Learning | Models retrain every 100 readings |
| Hourly Patterns | Learns usage patterns for each hour |
| Anomaly Detection | 3-level system (Normal/Enhanced/Cutoff) |
| Real-time Monitoring | 2-second updates when active |
| Historical Analysis | View patterns across days/weeks |

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout

### Monitoring
- `GET /api/start_monitoring/<appliance>` - Start monitoring
- `GET /api/stop_monitoring/<appliance>` - Stop monitoring
- `GET /api/current_status/<appliance>` - Get current reading
- `GET /api/monitoring_status` - Check active sessions

### Data
- `GET /api/appliances` - List user's appliances
- `GET /api/history/<appliance>` - Get reading history
- `GET /api/usage_analysis/<appliance>` - Get hourly patterns
- `GET /api/statistics/<appliance>` - Get overall stats

## Anomaly Levels

### ✅ Normal (Score > 0)
- 0-1 models detect anomaly
- Continue normal operation
- No action needed

### ⚠️ Enhanced Monitoring (Score 0 to -1)
- 2 models detect anomaly
- Confidence: 66.7%
- Deviation < 100%
- Watch closely

### 🔴 Power Cutoff (Score < -1)
- 2-3 models detect anomaly
- Confidence ≥ 66.7%
- Deviation > 100%
- Cut power immediately

## Cloud Deployment

### Easiest Options:
1. **Heroku**: `git push heroku main`
2. **Railway**: Connect GitHub, auto-deploy
3. **DigitalOcean**: App Platform, one-click deploy

### Required Files:
- ✅ `Procfile` - Already created
- ✅ `requirements.txt` - Already configured
- ✅ `app_advanced.py` - Main application

### Environment Variables:
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
PORT=5000  # Auto-set by most platforms
```

## Testing

### Test Page-Aware Monitoring:
```bash
python test_page_aware_monitoring.py
```

### Test Locally:
```bash
python app_advanced.py
# Visit: http://localhost:5000
```

### Test with Production Server:
```bash
gunicorn app_advanced:app
```

## Database

### SQLite (Development):
- File: `energy_monitor.db`
- Automatic creation
- No setup needed

### PostgreSQL (Production):
- Recommended for cloud
- Set `DATABASE_URL` environment variable
- Auto-configured on Heroku

## Monitoring Resource Usage

### Check Active Sessions:
```bash
curl http://localhost:5000/api/monitoring_status
```

### Response:
```json
{
  "active_sessions": 2,
  "monitors": [
    {"user_id": 1, "appliance": "Laptop", "last_activity": "16:30:45"}
  ],
  "timeout_seconds": 10
}
```

## Common Commands

### Start Application:
```bash
python app_advanced.py
```

### Populate Test Data:
```bash
python populate_realistic_data.py
# Username: demo
# Days: 7
# Confirm: y
```

### Check Database:
```bash
python inspect_database.py
```

### Run Tests:
```bash
python test_hourly_patterns.py
python test_page_aware_monitoring.py
```

## File Structure

```
├── app_advanced.py              # Main Flask application
├── app_monitoring_control.py    # Page-aware monitoring logic
├── ml_models.py                 # Ensemble ML models
├── database.py                  # Database operations
├── templates/                   # HTML templates
│   ├── dashboard.html          # Main dashboard
│   ├── analytics.html          # Analytics page
│   └── login.html              # Login page
├── requirements.txt            # Python dependencies
├── Procfile                    # Heroku deployment
└── energy_monitor.db           # SQLite database
```

## Troubleshooting

### Issue: Monitoring not stopping
**Fix**: Check timeout in `app_monitoring_control.py`

### Issue: No data showing
**Fix**: Run `populate_realistic_data.py` first

### Issue: Login fails
**Fix**: Check if user exists, or create new account

### Issue: High CPU usage
**Fix**: Page-aware monitoring should prevent this. Check `/api/monitoring_status`

## Support

- 📖 Full ML explanation: `ML_MODELS_EXPLAINED.md`
- ☁️ Deployment guide: `CLOUD_DEPLOYMENT_GUIDE.md`
- 📚 User guide: `USER_GUIDE.md`
- 🚀 Quick start: `QUICK_START.md`

## Key Metrics

- **Training Data**: Minimum 50 readings per appliance
- **Retraining**: Every 100 new readings
- **Update Frequency**: 2 seconds when active
- **Inactivity Timeout**: 10 seconds
- **Anomaly Threshold**: 2/3 models must agree
- **Cutoff Threshold**: >100% deviation + anomaly

## Default Users

### Demo Account:
- Username: `demo`
- Password: `demo123`
- Has 7 days of realistic data

### Create New User:
1. Visit `/signup`
2. Fill in details
3. Login and start monitoring

---

**Version**: 2.0 (Page-Aware Monitoring)
**ML Models**: Isolation Forest + One-Class SVM + LOF
**Framework**: Flask + Scikit-learn
**Database**: SQLite (dev) / PostgreSQL (prod)

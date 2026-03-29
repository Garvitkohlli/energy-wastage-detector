# Cloud Deployment Guide - Energy Monitoring System

## ML Models Used

Your system uses an **Ensemble ML approach** combining three powerful anomaly detection algorithms:

### 1. Isolation Forest
- **Type**: Tree-based anomaly detection
- **Purpose**: Identifies anomalies by isolating outliers in the data
- **How it works**: Anomalies are easier to isolate (require fewer splits in decision trees)
- **Parameters**: 100 estimators, 10% contamination rate

### 2. One-Class SVM (Support Vector Machine)
- **Type**: Boundary-based anomaly detection
- **Purpose**: Learns the boundary of normal behavior
- **How it works**: Creates a hyperplane that separates normal data from anomalies
- **Parameters**: RBF kernel, auto gamma, 10% nu (outlier fraction)

### 3. Local Outlier Factor (LOF)
- **Type**: Density-based anomaly detection
- **Purpose**: Detects anomalies based on local density deviation
- **How it works**: Compares local density of a point with its neighbors
- **Parameters**: 20 neighbors, 10% contamination, novelty detection enabled

### Ensemble Decision Making
- **Voting System**: At least 2 out of 3 models must agree for anomaly detection
- **Confidence Score**: Percentage of models agreeing on the prediction
- **Feature Engineering**: Uses cyclical time features (sine/cosine) for hour and day patterns

## Page-Aware Monitoring System

The system now includes **intelligent monitoring control** that:

✅ **Only generates data when users are actively viewing dashboard/analytics pages**
✅ **Automatically stops data generation when users navigate away**
✅ **Reduces cloud resource usage and costs**
✅ **10-second timeout after last activity**

### How It Works

1. When you view an appliance on dashboard/analytics, the system registers your activity
2. The monitoring thread checks if you're still viewing before generating each data point
3. If you navigate away or close the page, monitoring pauses after 10 seconds
4. When you return, monitoring resumes automatically

## Cloud Deployment Options

### Option 1: Heroku (Easiest)

#### Prerequisites
```bash
# Install Heroku CLI
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew install heroku/brew/heroku
# Linux: curl https://cli-assets.heroku.com/install.sh | sh
```

#### Deployment Steps

1. **Create Heroku account** at https://heroku.com

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Procfile** (already included if not present)
```bash
echo "web: gunicorn app_advanced:app" > Procfile
```

4. **Update requirements.txt** (add gunicorn)
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

5. **Initialize Git** (if not already done)
```bash
git init
git add .
git commit -m "Initial commit for deployment"
```

6. **Create Heroku app**
```bash
heroku create your-energy-monitor
```

7. **Deploy**
```bash
git push heroku main
```

8. **Open your app**
```bash
heroku open
```

#### Heroku Configuration
```bash
# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here

# View logs
heroku logs --tail

# Scale dynos (free tier: 1 dyno)
heroku ps:scale web=1
```

### Option 2: AWS Elastic Beanstalk

#### Prerequisites
```bash
pip install awsebcli
```

#### Deployment Steps

1. **Initialize EB**
```bash
eb init -p python-3.11 energy-monitor
```

2. **Create environment**
```bash
eb create energy-monitor-env
```

3. **Deploy**
```bash
eb deploy
```

4. **Open app**
```bash
eb open
```

### Option 3: Google Cloud Platform (App Engine)

#### Prerequisites
```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install
```

#### Create app.yaml
```yaml
runtime: python311

instance_class: F2

env_variables:
  FLASK_ENV: 'production'

handlers:
- url: /static
  static_dir: static

- url: /.*
  script: auto
```

#### Deployment Steps
```bash
# Login
gcloud auth login

# Create project
gcloud projects create energy-monitor-project

# Set project
gcloud config set project energy-monitor-project

# Deploy
gcloud app deploy
```

### Option 4: DigitalOcean App Platform

1. **Connect GitHub repository** to DigitalOcean
2. **Select Python app**
3. **Set build command**: `pip install -r requirements.txt`
4. **Set run command**: `gunicorn app_advanced:app`
5. **Deploy**

### Option 5: Railway.app (Simplest)

1. **Visit** https://railway.app
2. **Connect GitHub repository**
3. **Railway auto-detects Python app**
4. **Deploy automatically**

## Production Configuration

### 1. Update app_advanced.py for production

Add at the end before `if __name__ == '__main__':`:

```python
# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    # Use environment variable for secret key
    app.secret_key = os.environ.get('SECRET_KEY', app.secret_key)
```

### 2. Database Configuration

For production, consider using PostgreSQL instead of SQLite:

```python
# In database.py, add:
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///energy_monitor.db')

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
```

### 3. Environment Variables

Set these on your cloud platform:

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=your-database-url  # If using PostgreSQL
PORT=5000  # Usually auto-set by platform
```

### 4. Security Enhancements

```python
# Add to app_advanced.py
from flask_talisman import Talisman

# Force HTTPS in production
if os.environ.get('FLASK_ENV') == 'production':
    Talisman(app, content_security_policy=None)
```

## Cost Optimization

### Free Tier Options

1. **Heroku**: 550-1000 free dyno hours/month
2. **Railway**: $5 free credit/month
3. **Google Cloud**: $300 free credit (90 days)
4. **AWS**: 750 hours free EC2 (12 months)

### Resource Usage

With page-aware monitoring:
- **Idle**: Minimal CPU/memory (no data generation)
- **Active**: Moderate CPU (only when viewing dashboard)
- **Database**: SQLite < 100MB (or PostgreSQL for production)

### Monitoring Costs

Check active sessions:
```bash
curl https://your-app.com/api/monitoring_status
```

Response:
```json
{
  "active_sessions": 2,
  "monitors": [
    {"user_id": 1, "appliance": "Laptop", "last_activity": "16:30:45"},
    {"user_id": 1, "appliance": "AC", "last_activity": "16:30:43"}
  ],
  "timeout_seconds": 10
}
```

## Testing Before Deployment

```bash
# Test locally with production settings
export FLASK_ENV=production
python app_advanced.py

# Test with gunicorn
gunicorn app_advanced:app --bind 0.0.0.0:5000
```

## Post-Deployment Checklist

- [ ] App loads successfully
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard displays appliances
- [ ] Monitoring starts/stops correctly
- [ ] Data generation pauses when navigating away
- [ ] Analytics page shows hourly patterns
- [ ] Database persists data
- [ ] HTTPS is enabled
- [ ] Environment variables are set

## Troubleshooting

### Issue: App crashes on startup
**Solution**: Check logs for missing dependencies
```bash
heroku logs --tail  # Heroku
eb logs            # AWS
gcloud app logs tail  # GCP
```

### Issue: Database not persisting
**Solution**: Use PostgreSQL for production (SQLite doesn't work well on some platforms)

### Issue: High resource usage
**Solution**: Page-aware monitoring should prevent this. Check active sessions:
```bash
curl https://your-app.com/api/monitoring_status
```

### Issue: Monitoring not stopping
**Solution**: Increase timeout in `app_monitoring_control.py`:
```python
self.timeout = 30  # 30 seconds instead of 10
```

## Monitoring & Maintenance

### View Active Sessions
```python
# Add to dashboard.html
fetch('/api/monitoring_status')
  .then(r => r.json())
  .then(data => console.log('Active sessions:', data.active_sessions));
```

### Database Backup
```bash
# SQLite
cp energy_monitor.db energy_monitor_backup.db

# PostgreSQL (Heroku)
heroku pg:backups:capture
heroku pg:backups:download
```

## Support & Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Scikit-learn ML Docs**: https://scikit-learn.org/
- **Heroku Python Guide**: https://devcenter.heroku.com/categories/python-support
- **AWS EB Python**: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-apps.html

## Summary

Your energy monitoring system is now optimized for cloud deployment with:

✅ **3 ML models** working together (Isolation Forest, One-Class SVM, LOF)
✅ **Page-aware monitoring** that saves resources
✅ **Multi-user support** with authentication
✅ **Persistent database** with hourly pattern learning
✅ **Production-ready** configuration options

Choose your preferred cloud platform and follow the deployment steps above!

# ⚡ Energy Wastage Detection System

ML-powered web application that monitors appliance power consumption, detects anomalies, and automatically recommends power cutoff when excessive usage is detected.

## 🌟 Features

- **Real-time Monitoring**: Track power consumption across multiple appliances
- **ML-Based Detection**: Isolation Forest algorithm identifies unusual patterns
- **Smart Notifications**: Get alerts when appliances use more/less power than usual
- **Auto Power Cutoff**: Intelligent recommendations to prevent energy waste
- **Visual Analytics**: Charts and insights for power consumption patterns
- **Web Interface**: Three intuitive pages (Home, Dashboard, Analytics)

## 📋 Pages

1. **Home** - Add appliances and quick start guide
2. **Dashboard** - Record readings, train models, check anomalies
3. **Analytics** - Visualize consumption patterns with charts and insights

## 🚀 Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open browser: `http://localhost:5000`

### Windows Quick Install
```bash
install.bat
python app.py
```

## ☁️ Cloud Deployment

### Deploy to Heroku

1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

2. Login and create app:
```bash
heroku login
heroku create your-energy-monitor-app
```

3. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-random-secret-key-here
```

4. Deploy:
```bash
git push heroku main
```

5. Open app:
```bash
heroku open
```

### Deploy to Render

1. Create account at https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Add environment variable: `SECRET_KEY`
5. Click "Create Web Service"

### Deploy to Railway

1. Create account at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python and deploys
5. Add environment variable `SECRET_KEY` in settings

## 📦 Git Setup

```bash
# Initialize repository
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Energy wastage detection system"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/energy-monitor.git

# Push to GitHub
git push -u origin main
```

## 🔧 How It Works

1. **Data Collection**: Records power consumption with timestamps and context
2. **Training**: ML model learns normal usage patterns (requires 10+ readings)
3. **Detection**: Identifies anomalies based on deviation from learned patterns
4. **Action**: Notifies user and recommends power cutoff for critical cases

## 🛠️ Configuration

Edit `energy_monitor.py` to customize:
- `contamination`: Expected anomaly proportion (default: 0.1)
- `power_cutoff_threshold`: Anomaly score for cutoff (default: -0.5)

## 📊 API Endpoints

- `GET /` - Home page
- `GET /dashboard` - Monitoring dashboard
- `GET /analytics` - Analytics page
- `POST /api/add_appliance` - Add new appliance
- `POST /api/record_power` - Record power reading
- `POST /api/train_model` - Train ML model
- `POST /api/check_anomaly` - Check for anomalies
- `GET /api/history/<appliance>` - Get reading history

## 🔐 Security

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Never commit `.env` file to Git

## 📝 License

MIT License - Feel free to use and modify

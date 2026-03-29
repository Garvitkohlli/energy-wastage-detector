# Deployment Guide

## Prerequisites

- Git installed
- GitHub account
- Cloud platform account (Heroku/Render/Railway)

## Step 1: Prepare Repository

```bash
# Initialize Git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Energy wastage detection system"
```

## Step 2: Push to GitHub

1. Create new repository on GitHub: https://github.com/new

2. Add remote and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Cloud

### Option A: Heroku (Free Tier Available)

1. Install Heroku CLI:
   - Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
   - Run: `heroku --version` to verify

2. Login and create app:
```bash
heroku login
heroku create your-app-name
```

3. Set environment variables:
```bash
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

4. Deploy:
```bash
git push heroku main
```

5. Open your app:
```bash
heroku open
```

6. View logs:
```bash
heroku logs --tail
```

### Option B: Render (Recommended - Easy Setup)

1. Go to https://render.com and sign up

2. Click "New +" → "Web Service"

3. Connect your GitHub repository

4. Configure:
   - **Name**: energy-monitor
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

5. Add Environment Variable:
   - Key: `SECRET_KEY`
   - Value: Generate random string (use password generator)

6. Click "Create Web Service"

7. Wait for deployment (2-3 minutes)

8. Access your app at: `https://your-app-name.onrender.com`

### Option C: Railway (Fastest Deployment)

1. Go to https://railway.app and sign up with GitHub

2. Click "New Project" → "Deploy from GitHub repo"

3. Select your repository

4. Railway automatically detects Python and deploys

5. Go to Settings → Variables → Add:
   - `SECRET_KEY`: (generate random string)

6. Your app will be live at the provided URL

### Option D: PythonAnywhere (Free Tier)

1. Sign up at https://www.pythonanywhere.com

2. Go to "Web" tab → "Add a new web app"

3. Choose Flask and Python 3.11

4. Upload your files or clone from Git:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

5. Configure WSGI file to point to your app

6. Install requirements in bash console:
```bash
pip install -r requirements.txt
```

7. Reload web app

## Step 4: Verify Deployment

1. Visit your deployed URL
2. Add an appliance on the home page
3. Go to dashboard and generate sample data
4. Train the model
5. Check for anomalies
6. View analytics

## Troubleshooting

### App won't start
- Check logs: `heroku logs --tail` (Heroku) or view logs in dashboard (Render/Railway)
- Verify all dependencies in requirements.txt
- Ensure SECRET_KEY is set

### Database/Model errors
- Models are stored in memory by default
- For persistence, add database (PostgreSQL) or file storage

### Port issues
- App uses PORT environment variable (automatically set by cloud platforms)
- Local development uses port 5000

## Environment Variables

Required:
- `SECRET_KEY`: Random secret key for Flask sessions

Optional:
- `PORT`: Port number (auto-set by cloud platforms)

## Updating Your Deployment

```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push origin main

# For Heroku
git push heroku main

# For Render/Railway - auto-deploys from GitHub
```

## Custom Domain (Optional)

### Heroku
```bash
heroku domains:add www.yourdomain.com
```

### Render/Railway
- Go to Settings → Custom Domain
- Follow DNS configuration instructions

## Monitoring

- **Heroku**: `heroku logs --tail`
- **Render**: View logs in dashboard
- **Railway**: View logs in deployment section

## Scaling (Paid Plans)

### Heroku
```bash
heroku ps:scale web=2
```

### Render/Railway
- Upgrade instance type in dashboard
- Enable auto-scaling

## Backup Strategy

1. Export model files regularly
2. Store in cloud storage (S3, Google Cloud Storage)
3. Keep Git repository updated

## Security Checklist

- ✅ SECRET_KEY set and random
- ✅ .env file in .gitignore
- ✅ No hardcoded credentials
- ✅ HTTPS enabled (automatic on most platforms)
- ✅ Dependencies up to date

## Cost Estimates

- **Render Free**: $0/month (sleeps after inactivity)
- **Railway Free**: $0/month (limited hours)
- **Heroku Hobby**: $7/month (always on)
- **Render Starter**: $7/month (always on)

## Support

For issues:
1. Check logs first
2. Verify environment variables
3. Test locally before deploying
4. Check platform status pages

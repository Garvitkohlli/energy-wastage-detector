# ML Learning System Documentation

## Overview

The Energy Monitor system uses **continuous learning** where ML models improve over time by learning from actual data stored in the database.

## How It Works

### 1. Initial Training

When the application starts:

```
┌─────────────────────────────────────────┐
│  Check Database for Historical Data    │
└─────────────────────────────────────────┘
                  │
                  ├─── Has 50+ readings?
                  │
        ┌─────────┴─────────┐
        │                   │
       YES                 NO
        │                   │
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ Load from DB │    │ Generate     │
│ (Historical) │    │ Synthetic    │
└──────────────┘    └──────────────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
        ┌──────────────────┐
        │  Train ML Model  │
        └──────────────────┘
```

### 2. Continuous Learning

During monitoring, the model automatically retrains:

- **Every 100 readings** - Model retrains with latest database data
- **Manual trigger** - User can click "Retrain Model from Database"
- **On restart** - Always loads latest historical data

### 3. Data Flow

```
New Reading → Save to Database → Every 100 readings → Retrain Model
                                                            │
                                                            ▼
                                                    Updated Model
                                                            │
                                                            ▼
                                                Better Predictions
```

## Key Features

### Automatic Retraining

```python
# Happens automatically every 100 readings
if stats['readings'] % 100 == 0:
    retrain_model_from_database(appliance_name, model)
```

### Database-Driven Learning

```python
# Loads up to 1000 most recent readings
historical_readings = db.get_readings(appliance_name, limit=1000)

# Extracts features
for reading in historical_readings:
    power_data.append(reading['power_watts'])
    hours.append(reading['hour'])
    days.append(reading['day_of_week'])

# Retrains model
model.train(power_data, hours, days)
```

### Manual Retraining

Users can manually trigger retraining via:
- Dashboard button: "Retrain Model from Database"
- API endpoint: `/api/retrain_model/<appliance>`

## Benefits

### 1. Adapts to Real Usage Patterns
- Learns from actual appliance behavior
- Adjusts to seasonal changes
- Recognizes new usage patterns

### 2. Improves Over Time
- More data = Better predictions
- Reduces false positives
- Increases anomaly detection accuracy

### 3. Personalized Models
- Each appliance has unique patterns
- Models learn specific behaviors
- Customized to your usage

## Training Data Sources

### Priority Order:
1. **Database Historical Data** (Preferred)
   - Real readings from actual usage
   - Includes time patterns (hour, day)
   - Up to 1000 most recent readings

2. **Synthetic Data** (Fallback)
   - Generated only if < 50 historical readings
   - Based on realistic patterns
   - Replaced by real data as it accumulates

## Model Training Process

### Step 1: Data Collection
```python
# From database
readings = db.get_readings(appliance, limit=1000)

# Extract features
power_data = [r['power_watts'] for r in readings]
hours = [r['hour'] for r in readings]
days = [r['day_of_week'] for r in readings]
```

### Step 2: Feature Engineering
```python
# 9 features extracted per reading:
- Raw power value
- Hour of day
- Day of week
- Cyclical hour (sine)
- Cyclical hour (cosine)
- Cyclical day (sine)
- Cyclical day (cosine)
- Power ratio to average
- Power difference from average
```

### Step 3: Ensemble Training
```python
# Three models trained:
1. Isolation Forest
2. One-Class SVM
3. Local Outlier Factor

# Voting system for predictions
```

### Step 4: Model Update
```python
# Model stored in memory
# Performance metrics saved to database
# Usage patterns updated
```

## Monitoring the Learning Process

### Console Output

When model retrains:
```
======================================================================
🔄 RETRAINING MODEL: Light Bulb
======================================================================
   ✅ Model retrained successfully
   📊 Training samples: 847
   📈 New average power: 8.34W
   🎯 Model updated with latest patterns
======================================================================
```

### Database Tracking

Model performance saved to `model_performance` table:
```sql
SELECT * FROM model_performance 
ORDER BY timestamp DESC 
LIMIT 10;
```

Shows:
- Appliance name
- Model type
- Training samples
- Timestamp
- Performance metrics

## API Endpoints

### Get Appliance Info
```
GET /api/appliances
```
Returns training data count and model status

### Retrain Model
```
GET /api/retrain_model/<appliance>
```
Manually triggers retraining from database

Response:
```json
{
  "status": "success",
  "message": "Model retrained successfully for Light Bulb",
  "training_samples": 847
}
```

## Best Practices

### 1. Let It Learn
- Run monitoring for at least 24 hours
- Cover different times of day
- Include weekdays and weekends

### 2. Regular Retraining
- Automatic every 100 readings
- Manual retrain after major changes
- Restart app to load latest data

### 3. Monitor Performance
- Check console logs for retraining events
- Review model performance in database
- Compare predictions before/after retraining

## Example Learning Timeline

### Day 1: Initial Training
```
Start: 0 readings in database
→ Uses synthetic data (840 samples)
→ Model trained with estimated patterns
```

### Day 1: After 100 Readings
```
Readings: 100 real readings collected
→ Automatic retrain triggered
→ Model now uses 100 real + 840 synthetic
```

### Day 2: After 500 Readings
```
Readings: 500 real readings
→ Multiple retrains occurred
→ Model primarily uses real data
→ Predictions more accurate
```

### Week 1: After 5000 Readings
```
Readings: 5000+ real readings
→ Model uses 1000 most recent
→ Fully adapted to real patterns
→ High accuracy predictions
```

## Checking Model Status

### Via Dashboard
1. Select appliance
2. View "Total Readings" in status
3. Click "Retrain Model from Database"

### Via Database Inspector
```bash
python inspect_database.py
```

Shows:
- Total readings per appliance
- Model performance history
- Training sample counts

### Via Query Tool
```bash
python query_database.py
```

Run:
```sql
SELECT appliance, COUNT(*) as readings 
FROM readings 
GROUP BY appliance;
```

## Troubleshooting

### Model Not Learning?

**Check readings count:**
```sql
SELECT COUNT(*) FROM readings WHERE appliance = 'Light Bulb';
```

**Need 50+ for database training**

### Predictions Not Improving?

**Retrain manually:**
1. Go to Dashboard
2. Select appliance
3. Click "Retrain Model from Database"

**Or via API:**
```bash
curl http://localhost:5000/api/retrain_model/Light%20Bulb
```

### Want Fresh Start?

**Clear database:**
```bash
# Windows
del energy_monitor.db

# Linux/macOS
rm energy_monitor.db

# Restart app
python app_advanced.py
```

## Advanced Features

### Incremental Learning
- Model updates without forgetting old patterns
- Balances historical and recent data
- Adapts to gradual changes

### Pattern Recognition
- Learns hourly usage patterns
- Recognizes day-of-week variations
- Detects seasonal trends

### Anomaly Adaptation
- Learns what's normal for each hour
- Adjusts thresholds based on history
- Reduces false alarms over time

## Performance Metrics

### Tracked Automatically:
- Training sample count
- Average power consumption
- Anomaly detection rate
- Model confidence scores

### Stored in Database:
- `model_performance` table
- Timestamped entries
- Historical comparison

## Summary

The ML learning system:

✓ **Starts** with synthetic or historical data
✓ **Learns** from every reading saved to database
✓ **Retrains** automatically every 100 readings
✓ **Improves** predictions over time
✓ **Adapts** to real usage patterns
✓ **Remembers** historical patterns
✓ **Updates** continuously

The longer you run it, the smarter it gets!

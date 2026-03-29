# ML Learning System - Summary

## What Changed

The ML models now **learn from actual data stored in the database** instead of only using synthetic training data.

## Key Features

### 1. Database-First Training
- On startup, models check database for historical readings
- If 50+ readings exist, uses real data
- Otherwise, generates synthetic data as fallback

### 2. Automatic Retraining
- Model retrains **every 100 readings** automatically
- Uses up to 1000 most recent readings from database
- Happens in background during monitoring

### 3. Manual Retraining
- New button on Dashboard: "Retrain Model from Database"
- API endpoint: `/api/retrain_model/<appliance>`
- Useful after collecting significant new data

### 4. Continuous Improvement
- More data = Better predictions
- Adapts to real usage patterns
- Learns seasonal and time-based variations

## How to Use

### Start Fresh
```bash
python app_advanced.py
```
Models will use synthetic data initially.

### After Monitoring
After running for a while:
1. Go to Dashboard
2. Select appliance
3. Click "Retrain Model from Database"
4. Model now uses your real data!

### Check Learning Progress
```bash
python inspect_database.py
```
Shows total readings per appliance.

### Test the System
```bash
python test_learning.py
```
Verifies learning system works correctly.

## Benefits

✓ **Personalized** - Learns YOUR usage patterns
✓ **Adaptive** - Adjusts to changes over time
✓ **Accurate** - Real data = Better predictions
✓ **Automatic** - Retrains without manual intervention
✓ **Persistent** - Data saved in database forever

## Technical Details

### Training Data Priority
1. Database historical data (preferred)
2. Synthetic data (fallback)

### Retraining Triggers
- Every 100 readings (automatic)
- Manual button click
- Application restart

### Data Used
- Up to 1000 most recent readings
- Includes: power, hour, day of week
- Extracts 9 features per reading

## Files Modified

- `app_advanced.py` - Added database learning and retraining
- `templates/dashboard.html` - Added retrain button
- `templates/index.html` - Updated description

## New Files

- `ML_LEARNING_SYSTEM.md` - Complete documentation
- `test_learning.py` - Test suite
- `LEARNING_SUMMARY.md` - This file

## Verification

Run the test:
```bash
python test_learning.py
```

Expected output:
```
✓ Database Learning - PASS
✓ Automatic Retraining - PASS
Passed: 2/2
```

## Example Timeline

**Day 1 - Hour 1:**
- 0 readings in database
- Uses synthetic training data
- Model ready but not personalized

**Day 1 - Hour 2:**
- 100+ readings collected
- Automatic retrain triggered
- Model now uses real data

**Day 2:**
- 1000+ readings collected
- Multiple retrains occurred
- Model fully adapted to your patterns

**Week 1:**
- 5000+ readings collected
- Model uses 1000 most recent
- Highly accurate predictions

## Console Output

When retraining happens:
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

## Database Tables Used

- `readings` - All power readings (source data)
- `model_performance` - Training history
- `anomalies` - Detected anomalies
- `cutoffs` - Power cutoff events

## API Endpoints

### Get Appliances
```
GET /api/appliances
```
Shows training data count

### Retrain Model
```
GET /api/retrain_model/<appliance>
```
Triggers manual retraining

Response:
```json
{
  "status": "success",
  "message": "Model retrained successfully",
  "training_samples": 847
}
```

## Troubleshooting

### Model not learning?
Check readings count:
```bash
python query_database.py "SELECT COUNT(*) FROM readings WHERE appliance='Light Bulb'"
```

Need 50+ readings for database training.

### Want to force retrain?
1. Dashboard → Select appliance
2. Click "Retrain Model from Database"

### Start completely fresh?
```bash
# Delete database
del energy_monitor.db  # Windows
rm energy_monitor.db   # Linux/macOS

# Restart app
python app_advanced.py
```

## Summary

The system now:
- ✓ Learns from database automatically
- ✓ Retrains every 100 readings
- ✓ Improves predictions over time
- ✓ Adapts to real usage patterns
- ✓ Provides manual retrain option

**The longer you run it, the smarter it gets!**

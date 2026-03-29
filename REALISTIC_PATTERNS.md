# Realistic Hourly Power Consumption Patterns

## Overview

The system now has realistic hourly patterns for all appliances based on typical usage scenarios.

## Appliance Patterns

### 1. Light Bulb (10W base)

**Usage Pattern:** High at night, low during day

```
Hour  | Power | Usage Scenario
------|-------|------------------------------------------
00:00 |   8W  | Bedroom lights (sleeping)
01-05 |  2-5W | Very low (sleeping)
06:00 |   5W  | Starting to wake up
07:00 |   8W  | Morning routine
08:00 |   6W  | Leaving for work
09-16 |  2-3W | Away from home (minimal)
17:00 |   5W  | Coming home
18:00 |  10W  | Peak evening (all lights on)
19:00 |  12W  | Peak (cooking, activities)
20:00 |  11W  | Evening activities
21:00 |  10W  | Winding down
22:00 |   9W  | Getting ready for bed
23:00 |   8W  | Bedroom lights
```

**Best Cutoff Time:** 12 PM - 3 PM (2-3W)
**Peak Usage:** 7 PM (12W)

---

### 2. Refrigerator (150W base)

**Usage Pattern:** Constant with variations based on ambient temperature and door openings

```
Hour  | Power  | Usage Scenario
------|--------|------------------------------------------
00-05 | 135-145W | Night (coolest, minimal door opening)
06:00 | 142W   | Morning (door opening starts)
07:00 | 155W   | Breakfast time (frequent opening)
08:00 | 158W   | Peak morning use
09-11 | 148-152W | Warming up outside
12:00 | 160W   | Lunch time (door opening)
13:00 | 165W   | Hottest part of day
14:00 | 168W   | Peak (maximum ambient heat)
15-17 | 158-165W | Still hot
18:00 | 165W   | Dinner prep (door opening)
19:00 | 170W   | Peak dinner time
20-23 | 148-160W | Cooling down
```

**Best Cutoff Time:** 3-5 AM (135-138W)
**Peak Usage:** 7 PM (170W)

---

### 3. Laptop (65W base)

**Usage Pattern:** High during work hours, low/off otherwise

```
Hour  | Power | Usage Scenario
------|-------|------------------------------------------
00-05 |  2-5W | Off/Sleep mode
06:00 |   5W  | Starting up
07:00 |  25W  | Morning email check
08:00 |  45W  | Starting work
09:00 |  70W  | Peak work (video calls, heavy tasks)
10:00 |  75W  | Peak work
11:00 |  72W  | Peak work
12:00 |  50W  | Lunch break (idle)
13:00 |  68W  | Afternoon work
14:00 |  75W  | Peak afternoon
15:00 |  70W  | Work continues
16:00 |  65W  | Winding down work
17:00 |  55W  | End of work day
18:00 |  30W  | Personal use
19:00 |  35W  | Evening browsing
20:00 |  40W  | Entertainment/browsing
21:00 |  35W  | Light use
22:00 |  25W  | Winding down
23:00 |  10W  | Sleep mode
```

**Best Cutoff Time:** 2-5 AM (2-3W)
**Peak Usage:** 10 AM & 2 PM (75W)

---

### 4. Air Conditioner (1500W base)

**Usage Pattern:** Peak during hot afternoon hours, low at night

```
Hour  | Power  | Usage Scenario
------|--------|------------------------------------------
00:00 |  200W  | Low (sleeping, cooler outside)
01:00 |  150W  | Lower
02-04 | 80-100W | Minimal (coolest time of day)
05:00 |  120W  | Starting to warm up
06:00 |  250W  | Morning warmth
07:00 |  400W  | Getting warmer
08:00 |  600W  | Warming up significantly
09:00 |  900W  | Hot
10:00 | 1200W  | Very hot
11:00 | 1400W  | Peak heat building
12:00 | 1600W  | Peak heat
13:00 | 1700W  | Hottest hour
14:00 | 1750W  | Absolute peak (hottest)
15:00 | 1700W  | Still very hot
16:00 | 1600W  | Starting to cool
17:00 | 1400W  | Cooling down
18:00 | 1200W  | Evening
19:00 | 1000W  | Cooler
20:00 |  800W  | Much cooler
21:00 |  600W  | Night cooling
22:00 |  400W  | Low
23:00 |  300W  | Low
```

**Best Cutoff Time:** 3-4 AM (80-90W)
**Peak Usage:** 2 PM (1750W)

---

## Data Generation Details

### Coverage
- **7 days** of historical data
- **24 hours** per day
- **5 readings per hour** for accuracy
- **Total: 840 readings per appliance**
- **Grand Total: 3,360 readings**

### Variance
Each appliance has realistic variance:
- Light Bulb: ±2W
- Refrigerator: ±10W
- Laptop: ±8W
- Air Conditioner: ±100W

### Day-of-Week Patterns
All 7 days of the week are covered, allowing the ML model to learn:
- Weekday patterns (Monday-Friday)
- Weekend patterns (Saturday-Sunday)
- Daily variations

## ML Learning Benefits

With this realistic data, the ML models can:

1. **Accurate Anomaly Detection**
   - Knows normal range for each hour
   - Detects unusual spikes/drops
   - Adapts to time-of-day patterns

2. **Optimal Cutoff Recommendations**
   - Identifies lowest usage hours
   - Minimizes impact on user
   - Considers daily patterns

3. **Personalized Insights**
   - Learns user's specific schedule
   - Adapts to seasonal changes
   - Improves over time

## Usage

### Populate Data for Demo User
```bash
python populate_realistic_data.py
# Enter: demo
# Enter: 7 (days)
# Enter: y (confirm)
```

### Populate Data for Your Account
```bash
python populate_realistic_data.py
# Enter: your_username
# Enter: 7 (or more days)
# Enter: y (confirm)
```

### View Patterns in App
1. Login to the app
2. Go to **Analytics**
3. Select an appliance
4. See the 24-hour pattern chart
5. View ML recommendations

## Expected ML Recommendations

Based on the patterns:

### Light Bulb
- **Best Cutoff:** 12 PM - 3 PM (away from home)
- **Avoid:** 7 PM - 9 PM (peak usage)
- **Savings:** ~10W difference

### Refrigerator
- **Best Cutoff:** 3 AM - 5 AM (coolest time)
- **Avoid:** 7 PM (dinner time)
- **Savings:** ~35W difference

### Laptop
- **Best Cutoff:** 2 AM - 5 AM (off/sleep)
- **Avoid:** 10 AM - 2 PM (work hours)
- **Savings:** ~73W difference

### Air Conditioner
- **Best Cutoff:** 3 AM - 4 AM (coolest)
- **Avoid:** 2 PM - 3 PM (hottest)
- **Savings:** ~1670W difference (huge!)

## Verification

Check the data was populated:
```bash
python inspect_database.py
```

Should show:
- 840 readings per appliance
- 3,360 total readings
- Hourly patterns populated
- Average power values matching patterns

## Summary

✓ **Realistic patterns** based on typical usage
✓ **7 days of data** for comprehensive learning
✓ **5 readings per hour** for accuracy
✓ **All appliances covered** with unique patterns
✓ **ML models ready** to provide accurate recommendations

The system now has meaningful data that reflects real-world usage patterns!

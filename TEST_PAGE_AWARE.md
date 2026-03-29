# How to Test Page-Aware Monitoring

## What is Page-Aware Monitoring?

Your system now only generates data when you're actively viewing the dashboard or analytics page. When you navigate away or close the tab, it automatically stops generating data after 10 seconds, saving cloud resources and costs.

## Quick Test (5 Minutes)

### Step 1: Start the App
```bash
python app_advanced.py
```

You should see:
```
🚀 Energy Monitoring System with User Authentication
📡 Server: http://localhost:5000
```

### Step 2: Open Browser
Go to: http://localhost:5000

### Step 3: Login
- Username: `demo`
- Password: `demo123`

### Step 4: Start Monitoring
1. Click on "Dashboard" in the menu
2. Click on any appliance (e.g., "Laptop")
3. Click the "Start Monitoring" button

**Watch the terminal!** You should see:
```
🚀 Monitoring thread started for User 3 - Laptop
   Page-aware monitoring: ENABLED
   Will pause after 10 seconds of inactivity
```

### Step 5: Watch It Work
Keep the browser on the appliance page. You'll see:
- Real-time chart updating every 2 seconds
- Terminal showing readings being generated
- Status: "Monitoring Active 🟢"

### Step 6: Navigate Away
Click on "Home" or "Analytics" (any page except the appliance detail)

**Watch the terminal!** After ~10 seconds you should see:
```
⏸️  PAUSED: User 3 - Laptop
   No activity detected. Data generation stopped.
   Will resume when user returns to dashboard.
```

**This is page-aware monitoring working!** 🎉

### Step 7: Return to Dashboard
Go back to Dashboard → Click on the appliance again

**Watch the terminal!** You should see:
```
▶️  RESUMED: User 3 - Laptop
   User returned. Data generation resumed.
```

### Step 8: Stop Monitoring
Click "Stop Monitoring" button

---

## Automated Test

If you want to test without manually clicking:

```bash
python test_monitoring_simple.py
```

Choose option 2 for automated test.

---

## What You Should See

### ✅ Working Correctly:
- Monitoring starts when viewing appliance
- Terminal shows "PAUSED" after navigating away
- Terminal shows "RESUMED" when returning
- Data generation stops when paused
- Data generation resumes when active

### ❌ Not Working:
- Monitoring never pauses (keeps generating data)
- No "PAUSED" message in terminal
- Data generates even when not viewing

---

## Troubleshooting

### Issue: Never shows "PAUSED"
**Cause**: You're still on the appliance detail page
**Fix**: Navigate to a different page (Home, Analytics, etc.)

### Issue: Shows "PAUSED" immediately
**Cause**: Not making API calls to register activity
**Fix**: Make sure you're on the appliance detail page (with the chart)

### Issue: Takes longer than 10 seconds to pause
**Cause**: Last API call resets the timer
**Fix**: This is normal. Wait up to 12 seconds after last activity

---

## Visual Test (Real-Time Monitoring)

Run this in a separate terminal while using the app:

```bash
python test_monitoring_simple.py
```

Choose option 1. This will show you real-time status:

```
[16:30:45] 🟢 ACTIVE: 1 session(s) - Data is being generated
           └─ User 3: Laptop (last activity: 16:30:45)

[16:31:00] 🔴 PAUSED: No active sessions - Data generation stopped
           └─ Saving resources! 💰
```

---

## Why This Matters for Cloud Deployment

### Without Page-Aware Monitoring:
```
CPU Usage:  ████████████████████ 80% (24/7)
Cost:       $$$$ per month
```

### With Page-Aware Monitoring:
```
CPU Usage:  ████░░░░░░░░░░░░░░░░ 20% (only when viewing)
Cost:       $ per month (75% savings!)
```

---

## API Endpoint to Check Status

You can also check monitoring status via API:

```bash
# While logged in, check status
curl http://localhost:5000/api/monitoring_status \
  -H "Cookie: session=your-session-cookie"
```

Response when active:
```json
{
  "active_sessions": 1,
  "monitors": [
    {
      "user_id": 3,
      "appliance": "Laptop",
      "last_activity": "16:30:45"
    }
  ],
  "timeout_seconds": 10
}
```

Response when paused:
```json
{
  "active_sessions": 0,
  "monitors": [],
  "timeout_seconds": 10
}
```

---

## Summary

Page-aware monitoring is working if:

✅ You see "PAUSED" message when navigating away
✅ You see "RESUMED" message when returning
✅ Data generation stops when paused
✅ Monitoring status API shows 0 active sessions when away

This feature will save you significant cloud costs by only using resources when users are actively viewing the dashboard!

"""
Test AWS SNS Email Notifications
"""
from sns_notifications import sns_notifier
import os

print("\n" + "="*70)
print("  AWS SNS EMAIL NOTIFICATION TEST")
print("="*70)

# Check configuration
print("\n📋 Configuration:")
print(f"   SNS Enabled: {sns_notifier.enabled}")

if sns_notifier.enabled:
    print(f"   AWS Region: {sns_notifier.region}")
    print(f"   Topic ARN: {sns_notifier.topic_arn}")
    
    print("\n" + "="*70)
    print("  SENDING TEST NOTIFICATIONS")
    print("="*70)
    
    # Test anomaly alert
    print("\n1️⃣ Testing ANOMALY alert (warning level)...")
    result = sns_notifier.send_anomaly_alert(
        user_id=1,
        username="Test User",
        appliance="Test Laptop",
        power=150.5,
        avg_power=75.0,
        deviation=100.7,
        confidence=85.5
    )
    
    if result:
        print(f"   ✅ Anomaly alert sent! Message ID: {result}")
    else:
        print("   ❌ Failed to send anomaly alert")
    
    # Test cutoff alert
    print("\n2️⃣ Testing CUTOFF alert (critical level)...")
    result = sns_notifier.send_cutoff_alert(
        user_id=1,
        username="Test User",
        appliance="Test Air Conditioner",
        power=3500.0,
        avg_power=1750.0,
        deviation=200.0,
        confidence=95.0
    )
    
    if result:
        print(f"   ✅ Cutoff alert sent! Message ID: {result}")
    else:
        print("   ❌ Failed to send cutoff alert")
    
    # Test generic notification
    print("\n3️⃣ Testing generic notification...")
    result = sns_notifier.send_test_notification("test@example.com")
    
    if result['success']:
        print(f"   ✅ Test notification sent! Message ID: {result['message_id']}")
    else:
        print(f"   ❌ Failed: {result['message']}")
    
    print("\n" + "="*70)
    print("  CHECK YOUR EMAIL")
    print("="*70)
    print("\n📧 If you're subscribed to the SNS topic, you should receive:")
    print("   1. Anomaly alert email (warning)")
    print("   2. Cutoff alert email (critical)")
    print("   3. Test notification email")
    print("\n⚠️  Check your spam folder if you don't see them!")
    
else:
    print("\n❌ SNS is NOT enabled")
    print("\n📋 To enable SNS notifications:")
    print("\n   1. Set environment variables:")
    print("      export SNS_ENABLED=true")
    print("      export AWS_REGION=eu-north-1")
    print("      export SNS_TOPIC_ARN=arn:aws:sns:eu-north-1:093529868142:energyalerts")
    print("\n   2. Configure AWS credentials:")
    print("      - Option A: Use IAM role (recommended for EC2)")
    print("      - Option B: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    print("\n   3. Subscribe to SNS topic:")
    print("      - Go to AWS Console → SNS → Topics")
    print("      - Find topic: energyalerts")
    print("      - Create email subscription")
    print("      - Confirm subscription in your email")
    print("\n   4. Restart the app")
    print("\n📖 See SNS_SETUP.txt for detailed instructions")

print("\n" + "="*70)

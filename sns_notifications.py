"""
AWS SNS Email Notification System
Sends alerts for anomalies and power cutoffs
"""
import boto3
import os
from datetime import datetime

class SNSNotifier:
    def __init__(self):
        self.enabled = os.environ.get('SNS_ENABLED', 'false').lower() == 'true'
        
        if self.enabled:
            self.region = os.environ.get('AWS_REGION', 'eu-north-1')
            self.topic_arn = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:eu-north-1:093529868142:energyalerts')
            
            try:
                self.sns_client = boto3.client('sns', region_name=self.region)
                print(f"SNS Notifications: ENABLED (Region: {self.region})")
            except Exception as e:
                print(f"SNS Notifications: FAILED to initialize - {e}")
                self.enabled = False
        else:
            print("SNS Notifications: DISABLED")
    
    def send_anomaly_alert(self, user_id, username, appliance, power, avg_power, deviation, confidence):
        """Send email alert for anomaly detection"""
        if not self.enabled:
            return None
        
        try:
            subject = f"⚠️ Energy Alert: Unusual {appliance} Usage Detected"
            
            message = f"""
Energy Monitoring Alert
=======================

User: {username} (ID: {user_id})
Appliance: {appliance}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANOMALY DETECTED
----------------
Current Power: {power:.2f}W
Average Power: {avg_power:.2f}W
Deviation: {deviation:+.1f}%
Confidence: {confidence}%

Status: Enhanced Monitoring
Action: Please check your {appliance}

---
Energy Monitoring System
"""
            
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            
            print(f"SNS Alert sent: {response['MessageId']} (Anomaly - {appliance})")
            return response['MessageId']
            
        except Exception as e:
            print(f"Failed to send SNS alert: {e}")
            return None
    
    def send_cutoff_alert(self, user_id, username, appliance, power, avg_power, deviation, confidence):
        """Send email alert for power cutoff"""
        if not self.enabled:
            return None
        
        try:
            subject = f"🔴 URGENT: {appliance} Power Cutoff Required"
            
            message = f"""
URGENT ENERGY ALERT
===================

User: {username} (ID: {user_id})
Appliance: {appliance}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CRITICAL ANOMALY - POWER CUTOFF REQUIRED
-----------------------------------------
Current Power: {power:.2f}W
Average Power: {avg_power:.2f}W
Deviation: {deviation:+.1f}%
Confidence: {confidence}%

Status: CRITICAL
Action: Power has been cut off to prevent damage

IMMEDIATE ACTION REQUIRED:
1. Check your {appliance} immediately
2. Investigate the cause of unusual power consumption
3. Ensure the appliance is safe before restarting

---
Energy Monitoring System
Automated Safety Alert
"""
            
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            
            print(f"SNS Alert sent: {response['MessageId']} (CUTOFF - {appliance})")
            return response['MessageId']
            
        except Exception as e:
            print(f"Failed to send SNS cutoff alert: {e}")
            return None
    
    def send_test_notification(self, email):
        """Send test notification to verify SNS setup"""
        if not self.enabled:
            return {"success": False, "message": "SNS is disabled"}
        
        try:
            subject = "Test: Energy Monitoring System"
            message = f"""
This is a test notification from your Energy Monitoring System.

If you received this email, SNS notifications are working correctly!

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Region: {self.region}

---
Energy Monitoring System
"""
            
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            
            return {
                "success": True,
                "message_id": response['MessageId'],
                "message": "Test notification sent successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send test notification: {str(e)}"
            }

# Global instance
sns_notifier = SNSNotifier()

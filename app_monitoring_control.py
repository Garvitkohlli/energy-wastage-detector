"""
Page-Aware Monitoring Control System
Only generates data when users are actively viewing dashboard/analytics
"""
import threading
import time
from datetime import datetime

class MonitoringController:
    """Controls monitoring based on active page views"""
    
    def __init__(self):
        self.active_sessions = {}  # {user_id: {appliance: last_activity_time}}
        self.monitoring_threads = {}  # {user_id: {appliance: thread}}
        self.lock = threading.Lock()
        self.timeout = 10  # Stop monitoring after 10 seconds of inactivity
        
    def register_activity(self, user_id, appliance_name):
        """Register that user is viewing this appliance"""
        with self.lock:
            if user_id not in self.active_sessions:
                self.active_sessions[user_id] = {}
            self.active_sessions[user_id][appliance_name] = time.time()
    
    def is_active(self, user_id, appliance_name):
        """Check if monitoring should be active for this appliance"""
        with self.lock:
            if user_id not in self.active_sessions:
                return False
            if appliance_name not in self.active_sessions[user_id]:
                return False
            
            last_activity = self.active_sessions[user_id][appliance_name]
            return (time.time() - last_activity) < self.timeout
    
    def cleanup_inactive(self):
        """Remove inactive sessions"""
        with self.lock:
            current_time = time.time()
            users_to_remove = []
            
            for user_id, appliances in self.active_sessions.items():
                appliances_to_remove = []
                for appliance, last_activity in appliances.items():
                    if (current_time - last_activity) > self.timeout:
                        appliances_to_remove.append(appliance)
                
                for appliance in appliances_to_remove:
                    del appliances[appliance]
                
                if not appliances:
                    users_to_remove.append(user_id)
            
            for user_id in users_to_remove:
                del self.active_sessions[user_id]
    
    def get_active_monitors(self):
        """Get list of all active monitoring sessions"""
        with self.lock:
            active = []
            current_time = time.time()
            for user_id, appliances in self.active_sessions.items():
                for appliance, last_activity in appliances.items():
                    if (current_time - last_activity) < self.timeout:
                        active.append({
                            'user_id': user_id,
                            'appliance': appliance,
                            'last_activity': datetime.fromtimestamp(last_activity).strftime('%H:%M:%S')
                        })
            return active

# Global controller instance
monitoring_controller = MonitoringController()

def cleanup_loop():
    """Background thread to cleanup inactive sessions"""
    while True:
        time.sleep(5)
        monitoring_controller.cleanup_inactive()

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
cleanup_thread.start()

#!/usr/bin/env python3
"""
Error Handling and Logging System
Provides comprehensive error tracking, logging, and recovery mechanisms
"""

import logging
import traceback
import json
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
import os

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        self.error_log_file = os.path.join(log_dir, "errors.json")
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging system"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Main logger
        self.logger = logging.getLogger('MoroccoBot')
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler (INFO and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # File handler for all logs
        file_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'bot_detailed.log')
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'bot_errors.log')
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with context to JSON file"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        
        # Log to logger
        self.logger.error(
            f"{error_entry['error_type']}: {error_entry['error_message']}",
            exc_info=True
        )
        
        # Append to JSON file
        try:
            errors = []
            if os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'r') as f:
                    try:
                        errors = json.load(f)
                    except json.JSONDecodeError:
                        errors = []
            
            errors.append(error_entry)
            
            # Keep only last 100 errors
            errors = errors[-100:]
            
            with open(self.error_log_file, 'w') as f:
                json.dump(errors, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to write error log: {e}")
    
    def get_recent_errors(self, count: int = 10) -> list:
        """Get recent errors from log"""
        try:
            if os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'r') as f:
                    errors = json.load(f)
                    return errors[-count:]
            return []
        except Exception as e:
            self.logger.error(f"Failed to read error log: {e}")
            return []
    
    def clear_error_log(self):
        """Clear error log file"""
        try:
            if os.path.exists(self.error_log_file):
                os.remove(self.error_log_file)
            self.logger.info("Error log cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear error log: {e}")

def handle_errors(error_handler: ErrorHandler, user_message: str = "An error occurred. Please try again."):
    """Decorator for handling errors in bot functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error
                context = {
                    "function": func.__name__,
                    "args": str(args)[:200],  # Limit size
                    "kwargs": str(kwargs)[:200]
                }
                error_handler.log_error(e, context)
                
                # Try to send user-friendly message
                try:
                    # Assume first arg is self (bot instance) and second is chat_id
                    if len(args) >= 2 and hasattr(args[0], 'send_message'):
                        bot = args[0]
                        chat_id = args[1]
                        bot.send_message(
                            chat_id,
                            f"❌ **Error:** {user_message}\n\n"
                            f"_Error type: {type(e).__name__}_\n\n"
                            f"If this persists, use `/reset` to restart."
                        )
                except:
                    pass  # Fail silently if we can't send message
                
                return None
        return wrapper
    return decorator

class RateLimiter:
    """Simple rate limiter to prevent API abuse"""
    
    def __init__(self):
        self.requests = {}  # {user_id: [timestamps]}
        self.max_requests = 10  # Max requests per window
        self.window_seconds = 60  # Time window in seconds
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make request"""
        now = datetime.now().timestamp()
        
        # Clean old requests
        if user_id in self.requests:
            self.requests[user_id] = [
                ts for ts in self.requests[user_id]
                if now - ts < self.window_seconds
            ]
        else:
            self.requests[user_id] = []
        
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # Add new request
        self.requests[user_id].append(now)
        return True
    
    def get_wait_time(self, user_id: int) -> int:
        """Get seconds user needs to wait"""
        if user_id not in self.requests or not self.requests[user_id]:
            return 0
        
        now = datetime.now().timestamp()
        oldest = self.requests[user_id][0]
        wait_time = self.window_seconds - (now - oldest)
        
        return max(0, int(wait_time))

class HealthCheck:
    """System health monitoring"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.last_error = None
    
    def record_request(self):
        """Record a request"""
        self.request_count += 1
    
    def record_error(self, error: Exception):
        """Record an error"""
        self.error_count += 1
        self.last_error = {
            "type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_uptime(self) -> str:
        """Get uptime as string"""
        delta = datetime.now() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def get_error_rate(self) -> float:
        """Get error rate as percentage"""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100
    
    def get_status(self) -> Dict[str, Any]:
        """Get health status"""
        return {
            "uptime": self.get_uptime(),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": f"{self.get_error_rate():.2f}%",
            "last_error": self.last_error,
            "status": "healthy" if self.get_error_rate() < 5 else "degraded"
        }

# Global instances
error_handler = ErrorHandler()
rate_limiter = RateLimiter()
health_check = HealthCheck()

if __name__ == "__main__":
    # Test error handling
    print("🧪 Testing Error Handler...\n")
    
    # Test logging
    error_handler.logger.info("Test info message")
    error_handler.logger.warning("Test warning message")
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_handler.log_error(e, {"test": "context"})
    
    # Test recent errors
    recent = error_handler.get_recent_errors(5)
    print(f"✅ Recent errors: {len(recent)}")
    
    # Test rate limiter
    print("\n🧪 Testing Rate Limiter...")
    user_id = 12345
    for i in range(12):
        allowed = rate_limiter.is_allowed(user_id)
        print(f"Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
    
    wait_time = rate_limiter.get_wait_time(user_id)
    print(f"Wait time: {wait_time}s")
    
    # Test health check
    print("\n🧪 Testing Health Check...")
    health_check.record_request()
    health_check.record_request()
    health_check.record_error(ValueError("Test"))
    
    status = health_check.get_status()
    print(f"Status: {json.dumps(status, indent=2)}")
    
    print("\n✅ Error handler tests complete!")

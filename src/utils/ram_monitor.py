"""
RAM Monitor - Track system memory usage and enforce limits
"""

import psutil
import time
from typing import Optional, Callable


class RAMMonitor:
    """Monitor system RAM usage and enforce safety limits."""
    
    def __init__(
        self,
        max_ram_gb: float = 15.0,  # 15GB max - streaming should use minimal RAM
        warning_threshold_gb: float = 10.0,  # Warn at 10GB
        check_interval: float = 1.0  # Check every second
    ):
        """
        Initialize RAM monitor.
        
        Args:
            max_ram_gb: Maximum RAM usage in GB before aborting
            warning_threshold_gb: RAM usage in GB to start warning
            check_interval: How often to check RAM usage (seconds)
        """
        self.max_ram_gb = max_ram_gb
        self.warning_threshold_gb = warning_threshold_gb
        self.check_interval = check_interval
        self.total_ram_gb = psutil.virtual_memory().total / (1024**3)
        self.warning_issued = False
        
    def get_ram_usage_gb(self) -> float:
        """Get current RAM usage in GB."""
        mem = psutil.virtual_memory()
        return mem.used / (1024**3)
    
    def get_ram_percent(self) -> float:
        """Get current RAM usage as percentage."""
        mem = psutil.virtual_memory()
        return mem.percent
    
    def check_ram_limit(self):
        """
        Check if RAM usage exceeds limits.
        
        Returns:
            (is_over_limit, message)
        """
        used_gb = self.get_ram_usage_gb()
        used_percent = self.get_ram_percent()
        
        if used_gb >= self.max_ram_gb:
            return True, (
                f"CRITICAL: RAM usage {used_gb:.1f}GB ({used_percent:.1f}%) "
                f"exceeds limit of {self.max_ram_gb}GB. Aborting to prevent system crash."
            )
        
        if used_gb >= self.warning_threshold_gb and not self.warning_issued:
            self.warning_issued = True
            return False, (
                f"WARNING: RAM usage {used_gb:.1f}GB ({used_percent:.1f}%) "
                f"approaching limit of {self.max_ram_gb}GB"
            )
        
        return False, ""
    
    def get_status(self) -> dict:
        """Get current RAM status."""
        used_gb = self.get_ram_usage_gb()
        used_percent = self.get_ram_percent()
        available_gb = psutil.virtual_memory().available / (1024**3)
        
        return {
            "used_gb": used_gb,
            "available_gb": available_gb,
            "total_gb": self.total_ram_gb,
            "percent": used_percent,
            "limit_gb": self.max_ram_gb,
            "warning_gb": self.warning_threshold_gb,
            "over_limit": used_gb >= self.max_ram_gb,
            "near_limit": used_gb >= self.warning_threshold_gb
        }


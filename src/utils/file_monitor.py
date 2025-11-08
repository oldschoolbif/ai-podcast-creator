"""
File Monitoring Utility
Monitors file growth to show progress during long-running operations.
"""

import os
import time
from pathlib import Path
from threading import Thread, Event
from typing import Optional, Callable, List


class FileMonitor:
    """Monitor file size growth and report progress."""
    
    def __init__(self, file_path: Path, update_callback: Optional[Callable[[float, float, str], None]] = None, check_interval: float = 2.0):
        """
        Initialize file monitor.
        
        Args:
            file_path: Path to file to monitor
            update_callback: Function called with (current_size_mb, growth_rate_mb_per_sec, stall_warning)
            check_interval: Seconds between checks
        """
        self.file_path = Path(file_path)
        self.update_callback = update_callback
        self.check_interval = check_interval
        self.stop_event = Event()
        self.monitor_thread: Optional[Thread] = None
        self.last_size = 0.0
        self.last_time = time.time()
        self.start_time = time.time()  # Track when monitoring started
        self.file_creation_time: Optional[float] = None  # When file was first created
        self.growth_rate = 0.0
        self.growth_samples: List[float] = []  # Track all growth rate samples for averaging
        self.stall_time = 0.0
        self.stall_threshold = 30.0  # Consider stalled if no growth for 30 seconds
        self.final_size_mb: Optional[float] = None  # Final file size when monitoring stops
        
    def start(self):
        """Start monitoring file growth in background thread."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
            
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop(self):
        """Stop monitoring."""
        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        # Record final file size
        try:
            if self.file_path.exists():
                self.final_size_mb = self.file_path.stat().st_size / (1024 * 1024)
        except (OSError, FileNotFoundError):
            pass
            
    def _monitor_loop(self):
        """Background monitoring loop."""
        file_created = False
        while not self.stop_event.is_set():
            try:
                if self.file_path.exists():
                    if not file_created:
                        file_created = True
                        self.file_creation_time = time.time()
                        if self.update_callback:
                            self.update_callback(0.0, 0.0, "")  # File created signal
                    
                    current_size = self.file_path.stat().st_size / (1024 * 1024)  # MB
                    current_time = time.time()
                    
                    # Calculate growth rate
                    if self.last_size > 0:
                        time_delta = current_time - self.last_time
                        size_delta = current_size - self.last_size
                        
                        if time_delta > 0:
                            self.growth_rate = size_delta / time_delta  # MB/sec
                            # Store growth rate sample for averaging
                            if self.growth_rate > 0:  # Only track positive growth rates
                                self.growth_samples.append(self.growth_rate)
                            
                            # Check for stall
                            if size_delta < 0.01:  # Less than 0.01 MB growth
                                self.stall_time += time_delta
                            else:
                                self.stall_time = 0.0
                            
                            # Call update callback with stall warning
                            if self.update_callback:
                                stall_warning = ""
                                if self.stall_time > 10.0:  # Warn after 10 seconds
                                    stall_warning = f" [⚠️ Stalled {int(self.stall_time)}s]"
                                self.update_callback(current_size, self.growth_rate, stall_warning)
                    
                    self.last_size = current_size
                    self.last_time = current_time
                else:
                    # File doesn't exist yet
                    if file_created:
                        # File was deleted? Reset
                        file_created = False
                    self.last_size = 0.0
                    self.stall_time = 0.0
                    
            except (OSError, FileNotFoundError):
                # File may be locked or doesn't exist yet
                pass
                
            self.stop_event.wait(self.check_interval)
    
    def is_stalled(self) -> bool:
        """Check if file growth appears stalled."""
        return self.stall_time >= self.stall_threshold
    
    def get_current_size_mb(self) -> float:
        """Get current file size in MB."""
        try:
            if self.file_path.exists():
                return self.file_path.stat().st_size / (1024 * 1024)
        except (OSError, FileNotFoundError):
            pass
        return 0.0
    
    def get_growth_rate(self) -> float:
        """Get current growth rate in MB/sec."""
        return self.growth_rate
    
    def get_average_growth_rate(self) -> float:
        """Get average growth rate over the monitoring period."""
        if not self.growth_samples:
            return 0.0
        return sum(self.growth_samples) / len(self.growth_samples)
    
    def get_file_creation_time_sec(self) -> Optional[float]:
        """Get time from monitoring start to file creation (in seconds)."""
        if self.file_creation_time:
            return self.file_creation_time - self.start_time
        return None
    
    def get_metrics_summary(self) -> dict:
        """Get summary of file creation metrics."""
        return {
            "file_creation_time_sec": self.get_file_creation_time_sec(),
            "final_size_mb": self.final_size_mb,
            "average_growth_rate_mb_per_sec": self.get_average_growth_rate(),
            "growth_samples_count": len(self.growth_samples),
        }


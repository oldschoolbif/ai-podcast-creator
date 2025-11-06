"""
Metrics Tracking Module
Tracks generation times, GPU utilization, CPU usage, RAM usage, and performance metrics
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


def _get_cpu_ram_usage() -> Dict[str, float]:
    """Get current CPU and RAM usage using psutil."""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)  # Quick sample
        ram = psutil.virtual_memory()
        return {
            "cpu_percent": cpu_percent,
            "ram_used_gb": ram.used / (1024**3),
            "ram_total_gb": ram.total / (1024**3),
            "ram_percent": ram.percent,
        }
    except (ImportError, Exception):
        return {"cpu_percent": 0.0, "ram_used_gb": 0.0, "ram_total_gb": 0.0, "ram_percent": 0.0}


@dataclass
class ComponentMetrics:
    """Metrics for a single component (TTS, avatar, etc.)"""
    component: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    gpu_memory_before: Dict[str, float] = field(default_factory=dict)
    gpu_memory_after: Dict[str, float] = field(default_factory=dict)
    gpu_utilization_before: Dict[str, float] = field(default_factory=dict)  # GPU compute utilization %
    gpu_utilization_after: Dict[str, float] = field(default_factory=dict)
    gpu_utilization_avg: Optional[float] = None  # Average GPU utilization during component
    cpu_usage_before: Dict[str, float] = field(default_factory=dict)
    cpu_usage_after: Dict[str, float] = field(default_factory=dict)
    cpu_usage_avg: Optional[float] = None
    ram_usage_before: Dict[str, float] = field(default_factory=dict)
    ram_usage_after: Dict[str, float] = field(default_factory=dict)
    # File creation/growth metrics
    output_file_path: Optional[str] = None
    output_file_size_mb: Optional[float] = None
    file_growth_rate_mb_per_sec: Optional[float] = None  # Average growth rate during creation
    file_creation_time_sec: Optional[float] = None  # Time from start to first file creation
    error: Optional[str] = None
    
    def finish(self, gpu_manager=None):
        """Mark component as finished and calculate metrics."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        
        # Get final resource usage
        if gpu_manager and gpu_manager.gpu_available:
            self.gpu_memory_after = gpu_manager.get_memory_usage()
            self.gpu_utilization_after = gpu_manager.get_utilization()
            
            # For subprocess-based components (like Wav2Lip), sample multiple times during execution
            # This gives us a better average than just before/after
            gpu_samples = []
            
            # Check if component provided continuous GPU samples (e.g., from avatar_generator)
            # This is set by components that monitor GPU during subprocess execution
            if hasattr(gpu_manager, '_component_gpu_samples'):
                component_samples = getattr(gpu_manager, '_component_gpu_samples', [])
                if component_samples:
                    gpu_samples.extend(component_samples)
                    # Clear the samples after using them
                    delattr(gpu_manager, '_component_gpu_samples')
            
            # Add before/after samples if we don't have continuous samples
            if not gpu_samples:
                if self.gpu_utilization_before:
                    gpu_samples.append(self.gpu_utilization_before.get("gpu_percent", 0.0))
                if self.gpu_utilization_after:
                    gpu_samples.append(self.gpu_utilization_after.get("gpu_percent", 0.0))
            
            # Calculate average GPU utilization
            # For subprocess-based components with continuous monitoring, use all samples
            # For others, use before/after average or peak if workload was active
            if gpu_samples:
                self.gpu_utilization_avg = sum(gpu_samples) / len(gpu_samples)
                # If we have many samples (continuous monitoring), the average is accurate
                # If we only have 2 samples (before/after), use peak if workload was active
                if len(gpu_samples) >= 2 and len(gpu_samples) < 10:
                    peak_util = max(gpu_samples)
                    if peak_util > gpu_samples[0] * 1.2:  # 20% increase indicates work
                        self.gpu_utilization_avg = peak_util  # Use peak utilization
        
        # Get CPU and RAM usage
        cpu_ram_after = _get_cpu_ram_usage()
        self.cpu_usage_after = {"cpu_percent": cpu_ram_after["cpu_percent"]}
        self.ram_usage_after = {
            "ram_used_gb": cpu_ram_after["ram_used_gb"],
            "ram_total_gb": cpu_ram_after["ram_total_gb"],
            "ram_percent": cpu_ram_after["ram_percent"],
        }
        
        # Calculate average CPU usage
        if self.cpu_usage_before and self.cpu_usage_after:
            cpu_before = self.cpu_usage_before.get("cpu_percent", 0.0)
            cpu_after = self.cpu_usage_after.get("cpu_percent", 0.0)
            self.cpu_usage_avg = (cpu_before + cpu_after) / 2.0


@dataclass
class GenerationMetrics:
    """Complete metrics for a podcast generation session"""
    session_id: str
    script_path: str
    output_path: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    
    # Component metrics
    components: List[ComponentMetrics] = field(default_factory=list)
    
    # System info
    gpu_name: Optional[str] = None
    gpu_memory_gb: Optional[float] = None
    quality_preset: Optional[str] = None
    
    # Flags
    used_avatar: bool = False
    used_visualization: bool = False
    used_background: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "script_path": str(self.script_path),
            "output_path": str(self.output_path) if self.output_path else None,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration": self.total_duration,
            "gpu_name": self.gpu_name,
            "gpu_memory_gb": self.gpu_memory_gb,
            "quality_preset": self.quality_preset,
            "used_avatar": self.used_avatar,
            "used_visualization": self.used_visualization,
            "used_background": self.used_background,
            "components": [
                {
                    "component": c.component,
                    "duration": c.duration,
                    "gpu_memory_before": c.gpu_memory_before,
                    "gpu_memory_after": c.gpu_memory_after,
                    "gpu_utilization_before": c.gpu_utilization_before,
                    "gpu_utilization_after": c.gpu_utilization_after,
                    "gpu_utilization_avg": c.gpu_utilization_avg,
                    "cpu_usage_before": c.cpu_usage_before,
                    "cpu_usage_after": c.cpu_usage_after,
                    "cpu_usage_avg": c.cpu_usage_avg,
                    "ram_usage_before": c.ram_usage_before,
                    "ram_usage_after": c.ram_usage_after,
                    "output_file_path": c.output_file_path,
                    "output_file_size_mb": c.output_file_size_mb,
                    "file_growth_rate_mb_per_sec": c.file_growth_rate_mb_per_sec,
                    "file_creation_time_sec": c.file_creation_time_sec,
                    "error": c.error,
                }
                for c in self.components
            ],
        }


class MetricsTracker:
    """Track performance metrics during podcast generation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize metrics tracker.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.metrics_dir = Path(config["storage"]["cache_dir"]) / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[GenerationMetrics] = None
        self.gpu_manager = None
        
        # Try to get GPU manager
        try:
            from src.utils.gpu_utils import get_gpu_manager
            self.gpu_manager = get_gpu_manager()
        except Exception:
            pass
    
    def start_session(self, script_path: str, output_path: Optional[str] = None) -> str:
        """
        Start a new generation session.
        
        Returns:
            Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        self.current_session = GenerationMetrics(
            session_id=session_id,
            script_path=script_path,
            output_path=output_path,
        )
        
        # Record GPU info
        if self.gpu_manager:
            self.current_session.gpu_name = self.gpu_manager.gpu_name
            self.current_session.gpu_memory_gb = self.gpu_manager.gpu_memory
        
        return session_id
    
    def start_component(self, component_name: str) -> ComponentMetrics:
        """
        Start tracking a component.
        
        Args:
            component_name: Name of component (e.g., "tts", "avatar", "video_composition")
        
        Returns:
            ComponentMetrics object
        """
        if not self.current_session:
            # Create a default session if none exists
            self.start_session("unknown")
        
        # Get initial resource usage
        gpu_memory_before = {}
        gpu_utilization_before = {}
        if self.gpu_manager and self.gpu_manager.gpu_available:
            gpu_memory_before = self.gpu_manager.get_memory_usage()
            gpu_utilization_before = self.gpu_manager.get_utilization()
        
        cpu_ram_before = _get_cpu_ram_usage()
        cpu_usage_before = {"cpu_percent": cpu_ram_before["cpu_percent"]}
        ram_usage_before = {
            "ram_used_gb": cpu_ram_before["ram_used_gb"],
            "ram_total_gb": cpu_ram_before["ram_total_gb"],
            "ram_percent": cpu_ram_before["ram_percent"],
        }
        
        metrics = ComponentMetrics(
            component=component_name,
            start_time=time.time(),
            gpu_memory_before=gpu_memory_before,
            gpu_utilization_before=gpu_utilization_before,
            cpu_usage_before=cpu_usage_before,
            ram_usage_before=ram_usage_before,
        )
        
        self.current_session.components.append(metrics)
        return metrics
    
    def finish_component(self, metrics: ComponentMetrics, error: Optional[str] = None, file_monitor=None):
        """
        Finish tracking a component.
        
        Args:
            metrics: ComponentMetrics to finish
            error: Optional error message
            file_monitor: Optional FileMonitor instance to extract file creation metrics
        """
        if error:
            metrics.error = error
        
        # Extract file creation metrics from FileMonitor if provided
        if file_monitor:
            monitor_summary = file_monitor.get_metrics_summary()
            metrics.output_file_path = str(file_monitor.file_path)
            metrics.output_file_size_mb = monitor_summary.get("final_size_mb")
            metrics.file_growth_rate_mb_per_sec = monitor_summary.get("average_growth_rate_mb_per_sec")
            metrics.file_creation_time_sec = monitor_summary.get("file_creation_time_sec")
        
        metrics.finish(self.gpu_manager)
    
    def finish_session(self, output_path: Optional[str] = None):
        """Finish the current session and save metrics."""
        if not self.current_session:
            return
        
        self.current_session.end_time = datetime.now()
        self.current_session.total_duration = (
            self.current_session.end_time - self.current_session.start_time
        ).total_seconds()
        
        if output_path:
            self.current_session.output_path = str(output_path)
        
        # Save metrics
        self._save_metrics()
        
        # Print summary
        self._print_summary()
    
    def set_quality(self, quality: str):
        """Set quality preset for session."""
        if self.current_session:
            self.current_session.quality_preset = quality
    
    def set_flags(self, avatar: bool = False, visualization: bool = False, background: bool = False):
        """Set feature flags for session."""
        if self.current_session:
            self.current_session.used_avatar = avatar
            self.current_session.used_visualization = visualization
            self.current_session.used_background = background
    
    def _save_metrics(self):
        """Save metrics to JSON file."""
        if not self.current_session:
            return
        
        metrics_file = self.metrics_dir / f"{self.current_session.session_id}.json"
        
        try:
            with open(metrics_file, "w") as f:
                json.dump(self.current_session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save metrics: {e}")
    
    def _print_summary(self):
        """Print metrics summary to console."""
        if not self.current_session:
            return
        
        print("\n" + "=" * 60)
        print("📊 GENERATION METRICS")
        print("=" * 60)
        print(f"Total Duration: {self.current_session.total_duration:.2f}s")
        print(f"GPU: {self.current_session.gpu_name or 'CPU'}")
        if self.current_session.gpu_memory_gb:
            print(f"GPU Memory: {self.current_session.gpu_memory_gb:.1f} GB")
        print(f"Quality: {self.current_session.quality_preset or 'default'}")
        print()
        print("Component Breakdown:")
        
        for comp in self.current_session.components:
            status = "❌" if comp.error else "✅"
            duration = f"{comp.duration:.2f}s" if comp.duration else "N/A"
            print(f"  {status} {comp.component:20s} {duration:>8s}")
            
            # GPU metrics
            if comp.gpu_memory_after and comp.gpu_memory_before:
                mem_used = comp.gpu_memory_after.get("allocated_gb", 0) - comp.gpu_memory_before.get("allocated_gb", 0)
                if abs(mem_used) > 0.01:  # Only show if significant change
                    print(f"      GPU Memory: {mem_used:+.2f} GB")
            
            if comp.gpu_utilization_avg is not None:
                gpu_util = comp.gpu_utilization_avg
                util_icon = "🔥" if gpu_util > 50 else "⚡" if gpu_util > 10 else "💤"
                print(f"      GPU Utilization: {util_icon} {gpu_util:.1f}%")
            
            # CPU metrics
            if comp.cpu_usage_avg is not None:
                cpu_util = comp.cpu_usage_avg
                cpu_icon = "🔥" if cpu_util > 50 else "⚡" if cpu_util > 10 else "💤"
                print(f"      CPU Usage: {cpu_icon} {cpu_util:.1f}%")
            
            # RAM metrics
            if comp.ram_usage_after:
                ram_used = comp.ram_usage_after.get("ram_used_gb", 0)
                ram_total = comp.ram_usage_after.get("ram_total_gb", 0)
                ram_percent = comp.ram_usage_after.get("ram_percent", 0)
                if ram_total > 0:
                    print(f"      RAM Usage: {ram_used:.1f}/{ram_total:.1f} GB ({ram_percent:.1f}%)")
            
            # File creation metrics
            if comp.output_file_size_mb is not None:
                print(f"      Output File: {comp.output_file_size_mb:.2f} MB")
                if comp.file_growth_rate_mb_per_sec is not None:
                    print(f"      Encoding Rate: {comp.file_growth_rate_mb_per_sec:.2f} MB/s")
                if comp.file_creation_time_sec is not None:
                    print(f"      File Creation Time: {comp.file_creation_time_sec:.2f}s")
        
        print("=" * 60 + "\n")


# Global metrics tracker instance
_metrics_tracker: Optional[MetricsTracker] = None


def get_metrics_tracker(config: Optional[Dict[str, Any]] = None) -> Optional[MetricsTracker]:
    """Get or create global metrics tracker instance."""
    global _metrics_tracker
    
    if config:
        _metrics_tracker = MetricsTracker(config)
    elif _metrics_tracker is None and config is None:
        # Try to load from default config
        try:
            from src.utils.config import load_config
            _metrics_tracker = MetricsTracker(load_config())
        except Exception:
            pass
    
    return _metrics_tracker


"""
Performance monitoring and optimization utilities for the Markdown translator.

This module provides performance monitoring capabilities including memory usage tracking,
API response time monitoring, and performance optimization recommendations.
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
from statistics import mean, median
import logging


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    api_response_times: List[float] = field(default_factory=list)
    chunk_processing_times: List[float] = field(default_factory=list)
    memory_usage_samples: List[float] = field(default_factory=list)
    error_rates: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    concurrent_operations: List[int] = field(default_factory=list)
    throughput_samples: List[float] = field(default_factory=list)
    
    def add_api_response_time(self, duration: float, success: bool) -> None:
        """Record an API response time."""
        self.api_response_times.append(duration)
        if not success:
            self.error_rates['api_errors'] += 1
    
    def add_chunk_processing_time(self, duration: float) -> None:
        """Record chunk processing time."""
        self.chunk_processing_times.append(duration)
    
    def add_memory_sample(self, memory_mb: float) -> None:
        """Record memory usage sample."""
        self.memory_usage_samples.append(memory_mb)
    
    def add_concurrent_operations(self, count: int) -> None:
        """Record number of concurrent operations."""
        self.concurrent_operations.append(count)
    
    def add_throughput_sample(self, chunks_per_second: float) -> None:
        """Record throughput sample."""
        self.throughput_samples.append(chunks_per_second)


@dataclass
class PerformanceReport:
    """Performance analysis report."""
    avg_api_response_time: float
    median_api_response_time: float
    max_api_response_time: float
    avg_chunk_processing_time: float
    median_chunk_processing_time: float
    peak_memory_usage_mb: float
    avg_memory_usage_mb: float
    error_rate_percentage: float
    avg_concurrent_operations: float
    avg_throughput_chunks_per_second: float
    recommendations: List[str]
    total_samples: int


class PerformanceMonitor:
    """
    Performance monitoring system for the Markdown translator.
    
    Tracks various performance metrics including API response times,
    memory usage, processing times, and provides optimization recommendations.
    """
    
    def __init__(self, sample_window_size: int = 1000):
        """
        Initialize the performance monitor.
        
        Args:
            sample_window_size: Maximum number of samples to keep in memory
        """
        self.sample_window_size = sample_window_size
        self.metrics = PerformanceMetrics()
        self.start_time = time.time()
        self.logger = logging.getLogger(__name__)
        self._monitoring_active = False
        self._memory_monitor_thread = None
        self._lock = threading.Lock()
        
        # Performance thresholds for recommendations
        self.thresholds = {
            'api_response_time_slow': 5.0,  # seconds
            'memory_usage_high': 1024.0,    # MB
            'error_rate_high': 5.0,         # percentage
            'low_throughput': 1.0           # chunks per second
        }
    
    def start_monitoring(self) -> None:
        """Start continuous performance monitoring."""
        with self._lock:
            if self._monitoring_active:
                return
            
            self._monitoring_active = True
            self._memory_monitor_thread = threading.Thread(
                target=self._monitor_memory_usage,
                daemon=True
            )
            self._memory_monitor_thread.start()
            self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop continuous performance monitoring."""
        with self._lock:
            self._monitoring_active = False
            if self._memory_monitor_thread:
                self._memory_monitor_thread.join(timeout=1.0)
            self.logger.info("Performance monitoring stopped")
    
    def _monitor_memory_usage(self) -> None:
        """Background thread to monitor memory usage."""
        process = psutil.Process()
        
        while self._monitoring_active:
            try:
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
                
                with self._lock:
                    self.metrics.add_memory_sample(memory_mb)
                    self._trim_samples()
                
                time.sleep(1.0)  # Sample every second
            except Exception as e:
                self.logger.warning(f"Error monitoring memory usage: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def record_api_call(self, duration: float, success: bool) -> None:
        """
        Record an API call performance metric.
        
        Args:
            duration: Time taken for the API call in seconds
            success: Whether the API call was successful
        """
        with self._lock:
            self.metrics.add_api_response_time(duration, success)
            self._trim_samples()
        
        if duration > self.thresholds['api_response_time_slow']:
            self.logger.warning(f"Slow API response detected: {duration:.2f}s")
    
    def record_chunk_processing(self, duration: float) -> None:
        """
        Record chunk processing time.
        
        Args:
            duration: Time taken to process the chunk in seconds
        """
        with self._lock:
            self.metrics.add_chunk_processing_time(duration)
            self._trim_samples()
    
    def record_concurrent_operations(self, count: int) -> None:
        """
        Record the number of concurrent operations.
        
        Args:
            count: Number of concurrent operations
        """
        with self._lock:
            self.metrics.add_concurrent_operations(count)
            self._trim_samples()
    
    def record_throughput(self, chunks_processed: int, time_window: float) -> None:
        """
        Record throughput measurement.
        
        Args:
            chunks_processed: Number of chunks processed
            time_window: Time window in seconds
        """
        if time_window > 0:
            throughput = chunks_processed / time_window
            with self._lock:
                self.metrics.add_throughput_sample(throughput)
                self._trim_samples()
    
    def get_current_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Current memory usage in megabytes
        """
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024
        except Exception as e:
            self.logger.warning(f"Error getting memory usage: {e}")
            return 0.0
    
    def get_system_memory_info(self) -> Dict[str, float]:
        """
        Get system memory information.
        
        Returns:
            Dictionary with system memory statistics
        """
        try:
            memory = psutil.virtual_memory()
            return {
                'total_mb': memory.total / 1024 / 1024,
                'available_mb': memory.available / 1024 / 1024,
                'used_mb': memory.used / 1024 / 1024,
                'percentage': memory.percent
            }
        except Exception as e:
            self.logger.warning(f"Error getting system memory info: {e}")
            return {}
    
    def _trim_samples(self) -> None:
        """Trim sample lists to maintain window size."""
        if len(self.metrics.api_response_times) > self.sample_window_size:
            self.metrics.api_response_times = self.metrics.api_response_times[-self.sample_window_size:]
        
        if len(self.metrics.chunk_processing_times) > self.sample_window_size:
            self.metrics.chunk_processing_times = self.metrics.chunk_processing_times[-self.sample_window_size:]
        
        if len(self.metrics.memory_usage_samples) > self.sample_window_size:
            self.metrics.memory_usage_samples = self.metrics.memory_usage_samples[-self.sample_window_size:]
        
        if len(self.metrics.concurrent_operations) > self.sample_window_size:
            self.metrics.concurrent_operations = self.metrics.concurrent_operations[-self.sample_window_size:]
        
        if len(self.metrics.throughput_samples) > self.sample_window_size:
            self.metrics.throughput_samples = self.metrics.throughput_samples[-self.sample_window_size:]
    
    def generate_performance_report(self) -> PerformanceReport:
        """
        Generate a comprehensive performance report.
        
        Returns:
            PerformanceReport with analysis and recommendations
        """
        with self._lock:
            metrics = self.metrics
            
            # Calculate API response time statistics
            api_times = metrics.api_response_times
            avg_api_time = mean(api_times) if api_times else 0.0
            median_api_time = median(api_times) if api_times else 0.0
            max_api_time = max(api_times) if api_times else 0.0
            
            # Calculate chunk processing statistics
            chunk_times = metrics.chunk_processing_times
            avg_chunk_time = mean(chunk_times) if chunk_times else 0.0
            median_chunk_time = median(chunk_times) if chunk_times else 0.0
            
            # Calculate memory statistics
            memory_samples = metrics.memory_usage_samples
            peak_memory = max(memory_samples) if memory_samples else 0.0
            avg_memory = mean(memory_samples) if memory_samples else 0.0
            
            # Calculate error rate
            total_api_calls = len(api_times)
            api_errors = metrics.error_rates.get('api_errors', 0)
            error_rate = (api_errors / total_api_calls * 100) if total_api_calls > 0 else 0.0
            
            # Calculate concurrency statistics
            concurrent_ops = metrics.concurrent_operations
            avg_concurrent = mean(concurrent_ops) if concurrent_ops else 0.0
            
            # Calculate throughput statistics
            throughput_samples = metrics.throughput_samples
            avg_throughput = mean(throughput_samples) if throughput_samples else 0.0
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                avg_api_time, peak_memory, error_rate, avg_throughput, avg_concurrent
            )
            
            total_samples = len(api_times) + len(chunk_times) + len(memory_samples)
            
            return PerformanceReport(
                avg_api_response_time=avg_api_time,
                median_api_response_time=median_api_time,
                max_api_response_time=max_api_time,
                avg_chunk_processing_time=avg_chunk_time,
                median_chunk_processing_time=median_chunk_time,
                peak_memory_usage_mb=peak_memory,
                avg_memory_usage_mb=avg_memory,
                error_rate_percentage=error_rate,
                avg_concurrent_operations=avg_concurrent,
                avg_throughput_chunks_per_second=avg_throughput,
                recommendations=recommendations,
                total_samples=total_samples
            )
    
    def _generate_recommendations(self, avg_api_time: float, peak_memory: float, 
                                error_rate: float, avg_throughput: float, 
                                avg_concurrent: float) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # API performance recommendations
        if avg_api_time > self.thresholds['api_response_time_slow']:
            recommendations.append(
                f"API response time is slow ({avg_api_time:.2f}s). "
                "Consider reducing concurrency or checking network connectivity."
            )
        
        # Memory usage recommendations
        if peak_memory > self.thresholds['memory_usage_high']:
            recommendations.append(
                f"High memory usage detected ({peak_memory:.1f}MB). "
                "Consider reducing chunk size or processing fewer chunks concurrently."
            )
        
        # Error rate recommendations
        if error_rate > self.thresholds['error_rate_high']:
            recommendations.append(
                f"High error rate detected ({error_rate:.1f}%). "
                "Check API configuration and network stability."
            )
        
        # Throughput recommendations
        if avg_throughput < self.thresholds['low_throughput']:
            recommendations.append(
                f"Low throughput detected ({avg_throughput:.2f} chunks/s). "
                "Consider increasing concurrency if system resources allow."
            )
        
        # Concurrency recommendations
        if avg_concurrent < 2:
            recommendations.append(
                "Low concurrency detected. Consider increasing concurrency for better performance."
            )
        elif avg_concurrent > 20:
            recommendations.append(
                "Very high concurrency detected. This may cause API rate limiting or system overload."
            )
        
        # System resource recommendations
        system_memory = self.get_system_memory_info()
        if system_memory and system_memory.get('percentage', 0) > 80:
            recommendations.append(
                "System memory usage is high. Consider reducing processing load."
            )
        
        if not recommendations:
            recommendations.append("Performance looks good! No specific optimizations needed.")
        
        return recommendations
    
    def log_performance_summary(self) -> None:
        """Log a performance summary to the logger."""
        report = self.generate_performance_report()
        
        self.logger.info("=== Performance Summary ===")
        self.logger.info(f"Average API Response Time: {report.avg_api_response_time:.2f}s")
        self.logger.info(f"Peak Memory Usage: {report.peak_memory_usage_mb:.1f}MB")
        self.logger.info(f"Error Rate: {report.error_rate_percentage:.1f}%")
        self.logger.info(f"Average Throughput: {report.avg_throughput_chunks_per_second:.2f} chunks/s")
        self.logger.info(f"Total Samples: {report.total_samples}")
        
        if report.recommendations:
            self.logger.info("Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                self.logger.info(f"  {i}. {rec}")
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        with self._lock:
            self.metrics = PerformanceMetrics()
            self.start_time = time.time()
        self.logger.info("Performance metrics reset")
    
    def export_metrics(self) -> Dict[str, Any]:
        """
        Export metrics for external analysis.
        
        Returns:
            Dictionary containing all performance metrics
        """
        with self._lock:
            return {
                'api_response_times': self.metrics.api_response_times.copy(),
                'chunk_processing_times': self.metrics.chunk_processing_times.copy(),
                'memory_usage_samples': self.metrics.memory_usage_samples.copy(),
                'error_rates': dict(self.metrics.error_rates),
                'concurrent_operations': self.metrics.concurrent_operations.copy(),
                'throughput_samples': self.metrics.throughput_samples.copy(),
                'monitoring_duration': time.time() - self.start_time,
                'sample_window_size': self.sample_window_size
            }


class PerformanceOptimizer:
    """
    Performance optimization utilities.
    
    Provides methods to optimize processing based on current performance metrics
    and system resources.
    """
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        """
        Initialize the performance optimizer.
        
        Args:
            performance_monitor: PerformanceMonitor instance to use for metrics
        """
        self.monitor = performance_monitor
        self.logger = logging.getLogger(__name__)
    
    def suggest_optimal_concurrency(self, current_concurrency: int) -> int:
        """
        Suggest optimal concurrency based on current performance.
        
        Args:
            current_concurrency: Current concurrency level
            
        Returns:
            Suggested optimal concurrency level
        """
        report = self.monitor.generate_performance_report()
        
        # Get system resources
        system_memory = self.monitor.get_system_memory_info()
        cpu_count = psutil.cpu_count()
        
        # Base suggestion on current performance
        if report.error_rate_percentage > 10:
            # High error rate, reduce concurrency
            suggested = max(1, current_concurrency // 2)
            self.logger.info(f"High error rate detected, suggesting reduced concurrency: {suggested}")
        elif report.avg_api_response_time > 10:
            # Slow API responses, reduce concurrency
            suggested = max(1, current_concurrency - 2)
            self.logger.info(f"Slow API responses detected, suggesting reduced concurrency: {suggested}")
        elif system_memory and system_memory.get('percentage', 0) > 85:
            # High memory usage, reduce concurrency
            suggested = max(1, current_concurrency - 1)
            self.logger.info(f"High memory usage detected, suggesting reduced concurrency: {suggested}")
        elif (report.avg_api_response_time < 2 and 
              report.error_rate_percentage < 2 and
              report.avg_throughput_chunks_per_second > 2):
            # Good performance, can increase concurrency
            max_concurrency = min(cpu_count * 2, 20)  # Cap at reasonable limit
            suggested = min(max_concurrency, current_concurrency + 2)
            self.logger.info(f"Good performance detected, suggesting increased concurrency: {suggested}")
        else:
            # Keep current concurrency
            suggested = current_concurrency
        
        return suggested
    
    def suggest_optimal_chunk_size(self, current_chunk_size: int) -> int:
        """
        Suggest optimal chunk size based on current performance.
        
        Args:
            current_chunk_size: Current chunk size in lines
            
        Returns:
            Suggested optimal chunk size
        """
        report = self.monitor.generate_performance_report()
        
        if report.peak_memory_usage_mb > 1024:
            # High memory usage, reduce chunk size
            suggested = max(100, current_chunk_size // 2)
            self.logger.info(f"High memory usage detected, suggesting smaller chunks: {suggested}")
        elif report.avg_chunk_processing_time > 30:
            # Slow processing, reduce chunk size
            suggested = max(100, current_chunk_size - 100)
            self.logger.info(f"Slow chunk processing detected, suggesting smaller chunks: {suggested}")
        elif (report.avg_chunk_processing_time < 5 and 
              report.peak_memory_usage_mb < 512):
            # Fast processing and low memory, can increase chunk size
            suggested = min(2000, current_chunk_size + 200)
            self.logger.info(f"Fast processing detected, suggesting larger chunks: {suggested}")
        else:
            # Keep current chunk size
            suggested = current_chunk_size
        
        return suggested
    
    def should_pause_processing(self) -> bool:
        """
        Determine if processing should be paused due to resource constraints.
        
        Returns:
            True if processing should be paused
        """
        system_memory = self.monitor.get_system_memory_info()
        
        # Pause if system memory usage is critically high
        if system_memory and system_memory.get('percentage', 0) > 95:
            self.logger.warning("System memory critically high, suggesting pause")
            return True
        
        # Pause if current process memory is extremely high
        current_memory = self.monitor.get_current_memory_usage()
        if current_memory > 2048:  # 2GB
            self.logger.warning("Process memory extremely high, suggesting pause")
            return True
        
        return False

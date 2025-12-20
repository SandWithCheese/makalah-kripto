"""
Memory profiler for cryptographic operations using tracemalloc

This module provides peak memory usage measurements specific to
crypto function calls, useful for resource-constrained environments.
"""
import tracemalloc
from typing import Callable, Dict


def measure_memory_usage(
    func: Callable,
    iterations: int = 100
) -> Dict[str, float]:
    """
    Measure peak memory usage during crypto operation
    
    Args:
        func: The function to profile
        iterations: Number of iterations to average (default: 100)
    
    Returns:
        Dictionary containing:
        - 'current_kb': Current memory usage in KB
        - 'peak_kb': Peak memory usage in KB
        - 'avg_peak_kb': Average peak across iterations
    
    Note:
        tracemalloc has overhead, so use fewer iterations than timing tests
    
    Example:
        >>> def encrypt_op():
        ...     cipher.encrypt_command(b"unlock" * 10, b"lock_id")
        >>> mem = measure_memory_usage(encrypt_op)
        >>> print(f"Peak memory: {mem['peak_kb']:.2f} KB")
    """
    peak_measurements = []
    
    for i in range(iterations):
        # Start fresh memory tracking
        tracemalloc.start()
        
        # Execute crypto operation
        func()
        
        # Capture memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        peak_measurements.append(peak)
        
        if (i + 1) % 20 == 0:
            print(f"    Memory profiling progress: {i + 1}/{iterations}")
    
    # Convert to KB
    avg_peak_kb = sum(peak_measurements) / len(peak_measurements) / 1024
    max_peak_kb = max(peak_measurements) / 1024
    
    return {
        'avg_peak_kb': avg_peak_kb,
        'max_peak_kb': max_peak_kb,
        'min_peak_kb': min(peak_measurements) / 1024
    }


def measure_single_operation_memory(func: Callable) -> Dict[str, float]:
    """
    Measure memory for a single operation (useful for quick tests)
    
    Args:
        func: The function to profile
    
    Returns:
        Dictionary with 'current_kb' and 'peak_kb'
    """
    tracemalloc.start()
    func()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return {
        'current_kb': current / 1024,
        'peak_kb': peak / 1024
    }

"""
High-resolution timing profiler for cryptographic operations

This module provides precise execution time measurements using
time.perf_counter() with warm-up rounds to avoid CPU scaling bias.
"""
import time
import statistics
from typing import Callable, Dict, List


def measure_execution_time(
    func: Callable, 
    iterations: int = 10000, 
    warmup: int = 100
) -> Dict[str, float]:
    """
    Measure execution time with warm-up rounds and statistical analysis
    
    Args:
        func: The function to benchmark (should be a lambda/callable)
        iterations: Number of iterations to measure (default: 10000)
        warmup: Number of warm-up iterations to discard (default: 100)
    
    Returns:
        Dictionary containing:
        - 'mean_us': Mean execution time in microseconds
        - 'std_us': Standard deviation in microseconds
        - 'min_us': Minimum execution time in microseconds
        - 'max_us': Maximum execution time in microseconds
        - 'median_us': Median execution time in microseconds
    
    Example:
        >>> def encrypt_op():
        ...     cipher.encrypt_command(b"unlock", b"lock_id_123")
        >>> stats = measure_execution_time(encrypt_op, iterations=1000)
        >>> print(f"Mean: {stats['mean_us']:.2f} μs")
    """
    # Warm-up rounds to stabilize CPU frequency and cache
    print(f"  Running {warmup} warm-up iterations...")
    for _ in range(warmup):
        func()
    
    # Actual measurement
    print(f"  Measuring {iterations} iterations...")
    times: List[float] = []
    
    for i in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)
        
        # Progress indicator for long runs
        if (i + 1) % 1000 == 0:
            print(f"    Progress: {i + 1}/{iterations}")
    
    # Convert to microseconds for better readability
    times_us = [t * 1_000_000 for t in times]
    
    return {
        'mean_us': statistics.mean(times_us),
        'std_us': statistics.stdev(times_us) if len(times_us) > 1 else 0,
        'min_us': min(times_us),
        'max_us': max(times_us),
        'median_us': statistics.median(times_us)
    }


def calculate_throughput(mean_time_seconds: float) -> float:
    """
    Calculate throughput in operations per second
    
    Args:
        mean_time_seconds: Mean execution time in seconds
    
    Returns:
        Operations per second (ops/sec)
    """
    if mean_time_seconds > 0:
        return 1.0 / mean_time_seconds
    return 0.0

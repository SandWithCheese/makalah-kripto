"""
Main benchmark orchestrator for ASCON-128 vs AES-128-GCM comparison

This script runs comprehensive benchmarks including:
- Encryption/Decryption timing
- Memory footprint analysis
- Throughput calculations
- Authentication failure testing
- Nonce uniqueness verification
"""
import os
import sys
import csv
from datetime import datetime
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crypto_engine import AsconLock, AESLock
from timing_profiler import measure_execution_time, calculate_throughput
from memory_profiler import measure_memory_usage


class BenchmarkRunner:
    """Orchestrates all cryptographic benchmarks"""
    
    def __init__(
        self,
        plaintext_size: int = 64,
        iterations: int = 10000,
        warmup: int = 100,
        memory_iterations: int = 100
    ):
        """
        Initialize benchmark parameters
        
        Args:
            plaintext_size: Size of test plaintext in bytes (default: 64)
            iterations: Number of timing iterations (default: 10000)
            warmup: Number of warm-up rounds (default: 100)
            memory_iterations: Memory profiling iterations (default: 100)
        """
        self.plaintext_size = plaintext_size
        self.iterations = iterations
        self.warmup = warmup
        self.memory_iterations = memory_iterations
        
        # Generate test data
        self.key = os.urandom(16)  # Shared 128-bit key for fair comparison
        self.plaintext = b"unlock_bike_12345_" + os.urandom(plaintext_size - 18)
        self.associated_data = b"lock_id_bike_station_A_slot_42"
        
        # Initialize ciphers
        self.ascon = AsconLock(key=self.key)
        self.aes = AESLock(key=self.key)
        
        # Results storage
        self.results: List[Dict] = []
    
    def test_nonce_uniqueness(self, cipher, num_tests: int = 1000) -> bool:
        """
        Verify that nonces are never repeated
        
        Args:
            cipher: The cipher instance to test
            num_tests: Number of encryptions to test
        
        Returns:
            True if all nonces are unique, False otherwise
        """
        print(f"\n  Testing nonce uniqueness ({num_tests} encryptions)...")
        nonces = set()
        
        for i in range(num_tests):
            nonce, _ = cipher.encrypt_command(self.plaintext, self.associated_data)
            nonces.add(nonce)
            
            if (i + 1) % 200 == 0:
                print(f"    Progress: {i + 1}/{num_tests}")
        
        is_unique = len(nonces) == num_tests
        print(f"  Result: {'✓ All nonces unique' if is_unique else '✗ Duplicate nonces found!'}")
        return is_unique
    
    def test_authentication_failure(self, cipher) -> bool:
        """
        Test that modified ciphertext fails authentication
        
        Args:
            cipher: The cipher instance to test
        
        Returns:
            True if authentication properly fails, False otherwise
        """
        print("\n  Testing authentication failure detection...")
        
        # Encrypt normally
        nonce, ciphertext = cipher.encrypt_command(self.plaintext, self.associated_data)
        
        # Tamper with ciphertext (flip one bit)
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0x01
        tampered = bytes(tampered)
        
        # Attempt decryption
        result = cipher.decrypt_command(nonce, self.associated_data, tampered)
        
        auth_works = (result is None)
        print(f"  Result: {'✓ Authentication failure detected' if auth_works else '✗ Tampered data accepted!'}")
        return auth_works
    
    def benchmark_algorithm(self, algorithm_name: str, cipher) -> Dict:
        """
        Run complete benchmark suite for one algorithm
        
        Args:
            algorithm_name: Name of the algorithm (for reporting)
            cipher: The cipher instance to benchmark
        
        Returns:
            Dictionary with all benchmark results
        """
        print(f"\n{'='*60}")
        print(f"Benchmarking: {algorithm_name}")
        print(f"{'='*60}")
        
        results = {
            'algorithm': algorithm_name,
            'timestamp': datetime.now().isoformat(),
            'plaintext_size': self.plaintext_size,
            'iterations': self.iterations
        }
        
        # 1. Nonce Uniqueness Test
        results['nonce_unique'] = self.test_nonce_uniqueness(cipher, 1000)
        
        # 2. Authentication Failure Test
        results['auth_failure_works'] = self.test_authentication_failure(cipher)
        
        # 3. Encryption Timing
        print(f"\n[Encryption Timing]")
        enc_stats = measure_execution_time(
            lambda: cipher.encrypt_command(self.plaintext, self.associated_data),
            iterations=self.iterations,
            warmup=self.warmup
        )
        results.update({
            'encrypt_mean_us': enc_stats['mean_us'],
            'encrypt_std_us': enc_stats['std_us'],
            'encrypt_min_us': enc_stats['min_us'],
            'encrypt_max_us': enc_stats['max_us']
        })
        
        # 4. Decryption Timing (prepare encrypted data first)
        nonce, ciphertext = cipher.encrypt_command(self.plaintext, self.associated_data)
        print(f"\n[Decryption Timing]")
        dec_stats = measure_execution_time(
            lambda: cipher.decrypt_command(nonce, self.associated_data, ciphertext),
            iterations=self.iterations,
            warmup=self.warmup
        )
        results.update({
            'decrypt_mean_us': dec_stats['mean_us'],
            'decrypt_std_us': dec_stats['std_us'],
            'decrypt_min_us': dec_stats['min_us'],
            'decrypt_max_us': dec_stats['max_us']
        })
        
        # 5. Throughput
        results['encrypt_throughput_ops_sec'] = calculate_throughput(enc_stats['mean_us'] / 1_000_000)
        results['decrypt_throughput_ops_sec'] = calculate_throughput(dec_stats['mean_us'] / 1_000_000)
        
        # 6. Memory Profiling
        print(f"\n[Memory Profiling]")
        mem_stats = measure_memory_usage(
            lambda: cipher.encrypt_command(self.plaintext, self.associated_data),
            iterations=self.memory_iterations
        )
        results.update({
            'memory_avg_peak_kb': mem_stats['avg_peak_kb'],
            'memory_max_peak_kb': mem_stats['max_peak_kb']
        })
        
        # Print summary
        print(f"\n{'-'*60}")
        print(f"Summary for {algorithm_name}:")
        print(f"  Encryption: {enc_stats['mean_us']:.2f} ± {enc_stats['std_us']:.2f} μs")
        print(f"  Decryption: {dec_stats['mean_us']:.2f} ± {dec_stats['std_us']:.2f} μs")
        print(f"  Throughput: {results['encrypt_throughput_ops_sec']:.0f} ops/sec")
        print(f"  Peak Memory: {mem_stats['avg_peak_kb']:.2f} KB")
        print(f"{'-'*60}")
        
        return results
    
    def run_all_benchmarks(self):
        """Run benchmarks for both ASCON and AES"""
        print("\n" + "="*60)
        print("ASCON-128 vs AES-128-GCM Bicycle Lock Benchmark")
        print("="*60)
        print(f"\nConfiguration:")
        print(f"  Plaintext size: {self.plaintext_size} bytes")
        print(f"  Timing iterations: {self.iterations}")
        print(f"  Warm-up rounds: {self.warmup}")
        print(f"  Memory iterations: {self.memory_iterations}")
        
        # Benchmark ASCON-128
        ascon_results = self.benchmark_algorithm("ASCON-128", self.ascon)
        self.results.append(ascon_results)
        
        # Benchmark AES-128-GCM
        aes_results = self.benchmark_algorithm("AES-128-GCM", self.aes)
        self.results.append(aes_results)
        
        return self.results
    
    def save_results_csv(self, filepath: str = "results/benchmark_results.csv"):
        """
        Save results to CSV file
        
        Args:
            filepath: Path to save CSV (default: results/benchmark_results.csv)
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            if self.results:
                writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                writer.writeheader()
                writer.writerows(self.results)
        
        print(f"\n✓ Results saved to: {filepath}")
    
    def print_comparison(self):
        """Print side-by-side comparison of both algorithms"""
        if len(self.results) != 2:
            return
        
        ascon = self.results[0]
        aes = self.results[1]
        
        print("\n" + "="*60)
        print("COMPARATIVE ANALYSIS")
        print("="*60)
        
        print(f"\n{'Metric':<30} {'ASCON-128':<15} {'AES-128-GCM':<15}")
        print("-" * 60)
        
        print(f"{'Encryption (μs)':<30} {ascon['encrypt_mean_us']:>14.2f} {aes['encrypt_mean_us']:>14.2f}")
        print(f"{'Decryption (μs)':<30} {ascon['decrypt_mean_us']:>14.2f} {aes['decrypt_mean_us']:>14.2f}")
        print(f"{'Throughput (ops/sec)':<30} {ascon['encrypt_throughput_ops_sec']:>14.0f} {aes['encrypt_throughput_ops_sec']:>14.0f}")
        print(f"{'Peak Memory (KB)':<30} {ascon['memory_avg_peak_kb']:>14.2f} {aes['memory_avg_peak_kb']:>14.2f}")
        
        # Calculate percentages
        enc_diff = ((ascon['encrypt_mean_us'] - aes['encrypt_mean_us']) / aes['encrypt_mean_us']) * 100
        mem_diff = ((ascon['memory_avg_peak_kb'] - aes['memory_avg_peak_kb']) / aes['memory_avg_peak_kb']) * 100
        
        print("\n" + "-" * 60)
        print("Differences (ASCON vs AES):")
        print(f"  Encryption time: {enc_diff:+.1f}%")
        print(f"  Memory usage: {mem_diff:+.1f}%")
        print("="*60)


def main():
    """Main entry point"""
    # Create benchmark runner with default parameters
    runner = BenchmarkRunner(
        plaintext_size=64,
        iterations=10000,
        warmup=100,
        memory_iterations=100
    )
    
    # Run all benchmarks
    runner.run_all_benchmarks()
    
    # Save results
    runner.save_results_csv()
    
    # Print comparison
    runner.print_comparison()


if __name__ == "__main__":
    main()

"""
Multi-payload size benchmark for ASCON-128 vs AES-128-GCM

This script tests performance across different message sizes to analyze
how efficiency scales with payload. ASCON often shows better relative
performance with smaller messages typical of IoT/bicycle lock commands.
"""
import os
import sys
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crypto_engine import AsconLock, AESLock
from timing_profiler import measure_execution_time, calculate_throughput
from memory_profiler import measure_memory_usage


class MultiPayloadBenchmark:
    """Benchmark across multiple payload sizes"""
    
    def __init__(
        self,
        payload_sizes=[8, 16, 32, 64],
        iterations=10000,
        warmup=100,
        memory_iterations=100
    ):
        """
        Initialize multi-payload benchmark
        
        Args:
            payload_sizes: List of payload sizes in bytes
            iterations: Number of timing iterations per size
            warmup: Warm-up rounds
            memory_iterations: Memory profiling iterations
        """
        self.payload_sizes = payload_sizes
        self.iterations = iterations
        self.warmup = warmup
        self.memory_iterations = memory_iterations
        
        # Shared key for fair comparison
        self.key = os.urandom(16)
        self.associated_data = b"lock_id_bike_station_A"
        
        # Results storage
        self.results = []
    
    def generate_payload(self, size: int) -> bytes:
        """Generate test payload of specified size"""
        if size <= 18:
            return b"unlock_cmd_" + os.urandom(max(0, size - 11))
        else:
            return b"unlock_bike_123_" + os.urandom(size - 16)
    
    def benchmark_payload_size(self, size: int):
        """Run benchmarks for one payload size"""
        print(f"\n{'='*60}")
        print(f"Payload Size: {size} bytes")
        print(f"{'='*60}")
        
        # Generate test payload
        plaintext = self.generate_payload(size)
        
        # Initialize ciphers
        ascon = AsconLock(key=self.key)
        aes = AESLock(key=self.key)
        
        for algorithm_name, cipher in [("ASCON-128", ascon), ("AES-128-GCM", aes)]:
            print(f"\n[{algorithm_name}]")
            
            result = {
                'payload_size': size,
                'algorithm': algorithm_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Encryption timing
            print("  Measuring encryption...")
            enc_stats = measure_execution_time(
                lambda: cipher.encrypt_command(plaintext, self.associated_data),
                iterations=self.iterations,
                warmup=self.warmup
            )
            
            result.update({
                'encrypt_mean_us': enc_stats['mean_us'],
                'encrypt_std_us': enc_stats['std_us'],
                'encrypt_min_us': enc_stats['min_us'],
                'encrypt_max_us': enc_stats['max_us']
            })
            
            # Decryption timing
            nonce, ciphertext = cipher.encrypt_command(plaintext, self.associated_data)
            print("  Measuring decryption...")
            dec_stats = measure_execution_time(
                lambda: cipher.decrypt_command(nonce, self.associated_data, ciphertext),
                iterations=self.iterations,
                warmup=self.warmup
            )
            
            result.update({
                'decrypt_mean_us': dec_stats['mean_us'],
                'decrypt_std_us': dec_stats['std_us']
            })
            
            # Throughput
            result['encrypt_throughput_ops_sec'] = calculate_throughput(
                enc_stats['mean_us'] / 1_000_000
            )
            
            # Memory profiling
            print("  Measuring memory...")
            mem_stats = measure_memory_usage(
                lambda: cipher.encrypt_command(plaintext, self.associated_data),
                iterations=self.memory_iterations
            )
            
            result['memory_avg_peak_kb'] = mem_stats['avg_peak_kb']
            
            # Print summary
            print(f"  Encryption: {enc_stats['mean_us']:.2f} μs")
            print(f"  Throughput: {result['encrypt_throughput_ops_sec']:.0f} ops/sec")
            print(f"  Memory: {mem_stats['avg_peak_kb']:.2f} KB")
            
            self.results.append(result)
    
    def run_all_benchmarks(self):
        """Run benchmarks for all payload sizes"""
        print("\n" + "="*60)
        print("Multi-Payload Size Benchmark: ASCON-128 vs AES-128-GCM")
        print("="*60)
        print(f"\nPayload sizes: {self.payload_sizes} bytes")
        print(f"Iterations per size: {self.iterations}")
        
        for size in self.payload_sizes:
            self.benchmark_payload_size(size)
        
        return self.results
    
    def save_results(self, filepath="results/multi_payload_results.csv"):
        """Save results to CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            if self.results:
                writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                writer.writeheader()
                writer.writerows(self.results)
        
        print(f"\n✓ Results saved to: {filepath}")
    
    def generate_comparison_graphs(self):
        """Generate payload size comparison graphs"""
        df = pd.DataFrame(self.results)
        
        # Separate data by algorithm
        ascon_data = df[df['algorithm'] == 'ASCON-128'].sort_values('payload_size')
        aes_data = df[df['algorithm'] == 'AES-128-GCM'].sort_values('payload_size')
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('ASCON-128 vs AES-128-GCM: Performance Across Payload Sizes', 
                     fontsize=16, fontweight='bold')
        
        # 1. Encryption Time vs Payload Size
        ax1.plot(ascon_data['payload_size'], ascon_data['encrypt_mean_us'], 
                'o-', label='ASCON-128', linewidth=2, markersize=8, color='#3498db')
        ax1.plot(aes_data['payload_size'], aes_data['encrypt_mean_us'], 
                's-', label='AES-128-GCM', linewidth=2, markersize=8, color='#e74c3c')
        ax1.set_xlabel('Payload Size (bytes)', fontweight='bold')
        ax1.set_ylabel('Encryption Time (μs)', fontweight='bold')
        ax1.set_title('Encryption Time vs Payload Size')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # 2. Throughput vs Payload Size
        ax2.plot(ascon_data['payload_size'], ascon_data['encrypt_throughput_ops_sec'], 
                'o-', label='ASCON-128', linewidth=2, markersize=8, color='#2ecc71')
        ax2.plot(aes_data['payload_size'], aes_data['encrypt_throughput_ops_sec'], 
                's-', label='AES-128-GCM', linewidth=2, markersize=8, color='#f39c12')
        ax2.set_xlabel('Payload Size (bytes)', fontweight='bold')
        ax2.set_ylabel('Throughput (ops/sec)', fontweight='bold')
        ax2.set_title('Throughput vs Payload Size')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        # 3. Memory vs Payload Size
        ax3.plot(ascon_data['payload_size'], ascon_data['memory_avg_peak_kb'], 
                'o-', label='ASCON-128', linewidth=2, markersize=8, color='#9b59b6')
        ax3.plot(aes_data['payload_size'], aes_data['memory_avg_peak_kb'], 
                's-', label='AES-128-GCM', linewidth=2, markersize=8, color='#e67e22')
        ax3.set_xlabel('Payload Size (bytes)', fontweight='bold')
        ax3.set_ylabel('Peak Memory (KB)', fontweight='bold')
        ax3.set_title('Memory Usage vs Payload Size')
        ax3.legend()
        ax3.grid(alpha=0.3)
        
        # 4. Efficiency Ratio (AES time / ASCON time)
        efficiency_ratio = []
        for size in ascon_data['payload_size']:
            ascon_time = ascon_data[ascon_data['payload_size'] == size]['encrypt_mean_us'].values[0]
            aes_time = aes_data[aes_data['payload_size'] == size]['encrypt_mean_us'].values[0]
            efficiency_ratio.append(ascon_time / aes_time)
        
        ax4.plot(ascon_data['payload_size'], efficiency_ratio, 
                'D-', linewidth=2, markersize=8, color='#1abc9c')
        ax4.axhline(y=1.0, color='red', linestyle='--', label='Equal Performance')
        ax4.set_xlabel('Payload Size (bytes)', fontweight='bold')
        ax4.set_ylabel('ASCON/AES Time Ratio', fontweight='bold')
        ax4.set_title('Relative Efficiency (Lower is Better for ASCON)')
        ax4.legend()
        ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('results/graphs/payload_size_analysis.png', dpi=300)
        print("\n✓ Graph saved: results/graphs/payload_size_analysis.png")
        
        # Create summary table
        self.print_summary_table(ascon_data, aes_data)
    
    def print_summary_table(self, ascon_data, aes_data):
        """Print comparative summary table"""
        print("\n" + "="*80)
        print("SUMMARY: Performance Across Payload Sizes")
        print("="*80)
        print(f"\n{'Size':<8} {'ASCON Time':<15} {'AES Time':<15} {'Speedup':<12} {'Memory (ASCON)':<18}")
        print("-" * 80)
        
        for size in sorted(ascon_data['payload_size'].unique()):
            ascon_row = ascon_data[ascon_data['payload_size'] == size].iloc[0]
            aes_row = aes_data[aes_data['payload_size'] == size].iloc[0]
            
            speedup = aes_row['encrypt_mean_us'] / ascon_row['encrypt_mean_us']
            
            print(f"{size:<8} {ascon_row['encrypt_mean_us']:>12.2f} μs "
                  f"{aes_row['encrypt_mean_us']:>12.2f} μs "
                  f"{speedup:>10.2f}x "
                  f"{ascon_row['memory_avg_peak_kb']:>15.2f} KB")
        
        print("="*80)


def main():
    """Main entry point"""
    benchmark = MultiPayloadBenchmark(
        payload_sizes=[8, 16, 32, 64],
        iterations=10000,
        warmup=100,
        memory_iterations=100
    )
    
    # Run benchmarks
    benchmark.run_all_benchmarks()
    
    # Save results
    benchmark.save_results()
    
    # Generate visualizations
    benchmark.generate_comparison_graphs()


if __name__ == "__main__":
    main()

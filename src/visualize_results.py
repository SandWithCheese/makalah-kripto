"""
Visualization module for benchmark results

Generates comparison charts for ASCON-128 vs AES-128-GCM performance
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_results(csv_path: str = "results/benchmark_results.csv") -> pd.DataFrame:
    """Load benchmark results from CSV"""
    return pd.read_csv(csv_path)


def create_comparison_charts(df: pd.DataFrame, output_dir: str = "results/graphs"):
    """
    Generate all comparison charts
    
    Args:
        df: DataFrame with benchmark results
        output_dir: Directory to save graphs
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # 1. Encryption/Decryption Time Comparison
    create_timing_chart(df, output_dir)
    
    # 2. Memory Footprint Comparison
    create_memory_chart(df, output_dir)
    
    # 3. Throughput Comparison
    create_throughput_chart(df, output_dir)
    
    # 4. Combined Overview
    create_overview_chart(df, output_dir)
    
    print(f"\n✓ All graphs saved to: {output_dir}/")


def create_timing_chart(df: pd.DataFrame, output_dir: str):
    """Create bar chart comparing encryption/decryption times"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    algorithms = df['algorithm'].tolist()
    encrypt_times = df['encrypt_mean_us'].tolist()
    decrypt_times = df['decrypt_mean_us'].tolist()
    encrypt_stds = df['encrypt_std_us'].tolist()
    decrypt_stds = df['decrypt_std_us'].tolist()
    
    x = np.arange(len(algorithms))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, encrypt_times, width, 
                   yerr=encrypt_stds, label='Encryption',
                   color='#3498db', capsize=5)
    bars2 = ax.bar(x + width/2, decrypt_times, width,
                   yerr=decrypt_stds, label='Decryption',
                   color='#e74c3c', capsize=5)
    
    ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (μs)', fontsize=12, fontweight='bold')
    ax.set_title('Encryption/Decryption Performance Comparison', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/timing_comparison.png", dpi=300)
    plt.close()
    print(f"  ✓ Created: timing_comparison.png")


def create_memory_chart(df: pd.DataFrame, output_dir: str):
    """Create bar chart comparing memory usage"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    algorithms = df['algorithm'].tolist()
    memory = df['memory_avg_peak_kb'].tolist()
    
    colors = ['#2ecc71', '#f39c12']
    bars = ax.bar(algorithms, memory, color=colors, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax.set_ylabel('Peak Memory (KB)', fontsize=12, fontweight='bold')
    ax.set_title('Memory Footprint Comparison', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.2f} KB',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/memory_comparison.png", dpi=300)
    plt.close()
    print(f"  ✓ Created: memory_comparison.png")


def create_throughput_chart(df: pd.DataFrame, output_dir: str):
    """Create horizontal bar chart for throughput"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    algorithms = df['algorithm'].tolist()
    throughput = df['encrypt_throughput_ops_sec'].tolist()
    
    colors = ['#9b59b6', '#e67e22']
    bars = ax.barh(algorithms, throughput, color=colors, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Operations per Second', fontsize=12, fontweight='bold')
    ax.set_ylabel('Algorithm', fontsize=12, fontweight='bold')
    ax.set_title('Throughput Comparison (Higher is Better)', 
                 fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               f'{width:.0f} ops/sec',
               ha='left', va='center', fontsize=10, fontweight='bold', 
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/throughput_comparison.png", dpi=300)
    plt.close()
    print(f"  ✓ Created: throughput_comparison.png")


def create_overview_chart(df: pd.DataFrame, output_dir: str):
    """Create 2x2 subplot overview"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('ASCON-128 vs AES-128-GCM: Complete Overview', 
                 fontsize=16, fontweight='bold')
    
    algorithms = df['algorithm'].tolist()
    
    # 1. Encryption Time
    ax1.bar(algorithms, df['encrypt_mean_us'], color=['#3498db', '#e74c3c'])
    ax1.set_ylabel('Time (μs)')
    ax1.set_title('Encryption Time')
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Decryption Time
    ax2.bar(algorithms, df['decrypt_mean_us'], color=['#2ecc71', '#f39c12'])
    ax2.set_ylabel('Time (μs)')
    ax2.set_title('Decryption Time')
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Memory
    ax3.bar(algorithms, df['memory_avg_peak_kb'], color=['#9b59b6', '#e67e22'])
    ax3.set_ylabel('Memory (KB)')
    ax3.set_title('Peak Memory Usage')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Throughput
    ax4.bar(algorithms, df['encrypt_throughput_ops_sec'], color=['#1abc9c', '#e74c3c'])
    ax4.set_ylabel('ops/sec')
    ax4.set_title('Throughput')
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/overview.png", dpi=300)
    plt.close()
    print(f"  ✓ Created: overview.png")


def main():
    """Generate all visualizations from benchmark results"""
    print("\n" + "="*60)
    print("Generating Visualization Graphs")
    print("="*60)
    
    try:
        df = load_results()
        print(f"\n✓ Loaded results: {len(df)} algorithms")
        create_comparison_charts(df)
        print("\nVisualization complete!")
    except FileNotFoundError:
        print("\n✗ Error: benchmark_results.csv not found!")
        print("Please run benchmark_runner.py first.")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()

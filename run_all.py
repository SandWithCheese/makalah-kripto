#!/usr/bin/env python3
"""
Master orchestration script for ASCON-128 bicycle lock benchmark

This script runs the complete benchmark suite and generates all outputs:
1. Checks virtual environment
2. Runs cryptographic benchmarks
3. Generates visualization graphs
4. Prints summary report
"""
import os
import sys
import subprocess
from pathlib import Path


def check_venv():
    """Verify we're running in virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print("⚠️  Warning: Not running in virtual environment!")
        print("\nPlease activate the virtual environment first:")
        print("  $ source venv/bin/activate")
        print("  $ python run_all.py")
        return False
    
    print("✓ Virtual environment active")
    return True


def check_dependencies():
    """Check that required packages are installed"""
    required = ['ascon', 'Crypto', 'pandas', 'matplotlib']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"\n✗ Missing dependencies: {', '.join(missing)}")
        print("\nInstall with:")
        print("  $ pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies installed")
    return True


def run_benchmarks():
    """Execute benchmark suite"""
    print("\n" + "="*60)
    print("Running Cryptographic Benchmarks")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, "benchmarks/benchmark_runner.py"],
        cwd=Path(__file__).parent
    )
    
    return result.returncode == 0


def generate_visualizations():
    """Generate graphs from results"""
    print("\n" + "="*60)
    print("Generating Visualization Graphs")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, "src/visualize_results.py"],
        cwd=Path(__file__).parent
    )
    
    return result.returncode == 0


def print_final_summary():
    """Print summary of generated outputs"""
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE!")
    print("="*60)
    
    print("\n📊 Generated Outputs:")
    
    outputs = [
        ("results/benchmark_results.csv", "Raw benchmark data"),
        ("results/graphs/timing_comparison.png", "Encryption/Decryption timing"),
        ("results/graphs/memory_comparison.png", "Memory footprint"),
        ("results/graphs/throughput_comparison.png", "Operations per second"),
        ("results/graphs/overview.png", "Combined overview")
    ]
    
    for filepath, description in outputs:
        full_path = Path(__file__).parent / filepath
        if full_path.exists():
            print(f"  ✓ {filepath:<40} - {description}")
        else:
            print(f"  ✗ {filepath:<40} - NOT FOUND")
    
    print("\n📝 Next Steps:")
    print("  1. Review results: cat results/benchmark_results.csv")
    print("  2. View graphs: open results/graphs/overview.png")
    print("  3. Use data for academic report in docs/")
    
    print("\n" + "="*60)


def main():
    """Main orchestration"""
    print("\n" + "="*70)
    print("  ASCON-128 vs AES-128-GCM Bicycle Lock Benchmark Suite")
    print("  IF4020 Cryptography - Performance Analysis")
    print("="*70)
    
    # Pre-flight checks
    print("\n[Pre-flight Checks]")
    if not check_venv():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Run benchmark suite
    if not run_benchmarks():
        print("\n✗ Benchmark execution failed!")
        sys.exit(1)
    
    # Generate visualizations
    if not generate_visualizations():
        print("\n✗ Visualization generation failed!")
        sys.exit(1)
    
    # Print summary
    print_final_summary()


if __name__ == "__main__":
    main()

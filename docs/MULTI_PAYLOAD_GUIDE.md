# Quick Guide: Running Multi-Payload Benchmarks

## What This Does

Benchmarks ASCON-128 vs AES-128-GCM across different message sizes (8, 16, 32, 64 bytes) to show how performance scales with payload.

## Run the Benchmark

```bash
# Activate virtual environment
source venv/bin/activate

# Run multi-payload benchmark
python benchmarks/multi_payload_benchmark.py
```

**Expected runtime:** ~2 minutes

## Results

### Files Generated

1. **`results/multi_payload_results.csv`**
   - Raw benchmark data for all payload sizes
   - Fields: payload_size, algorithm, encrypt_mean_us, memory_avg_peak_kb, etc.

2. **`results/graphs/payload_size_analysis.png`**
   - 4-panel visualization showing:
     - Encryption time vs payload size
     - Throughput vs payload size
     - Memory vs payload size
     - Efficiency ratio (ASCON/AES)

### Quick Results Summary

| Payload | ASCON Time | AES Time | ASCON Memory | AES Memory |
|---------|------------|----------|--------------|------------|
| 8 bytes | 197.99 μs  | 38.20 μs | 1.40 KB      | 4.88 KB    |
| 16 bytes| 217.83 μs  | 37.69 μs | 1.40 KB      | 4.88 KB    |
| 32 bytes| 265.16 μs  | 38.05 μs | 1.40 KB      | 4.88 KB    |
| 64 bytes| 350.75 μs  | 38.48 μs | 1.40 KB      | 4.88 KB    |

### Key Findings

✅ **AES shows nearly constant performance** (~38 μs) across all sizes  
✅ **ASCON performance degrades linearly** with payload size  
✅ **ASCON is relatively more efficient** at smaller payloads (5.2× vs 9.1×)  
✅ **Memory advantage constant** at 71% less for ASCON  

## View Results

```bash
# View CSV data
cat results/multi_payload_results.csv

# View graph (Linux)
xdg-open results/graphs/payload_size_analysis.png

# View graph (macOS)
open results/graphs/payload_size_analysis.png
```

## Customization

Edit `benchmarks/multi_payload_benchmark.py`:

```python
# Change payload sizes
payload_sizes=[4, 8, 16, 32, 64, 128, 256]

# Change iterations
iterations=20000  # More iterations = better statistics

# Change warm-up rounds
warmup=200
```

## Use in Academic Report

### Data Import

```python
import pandas as pd
df = pd.read_csv('results/multi_payload_results.csv')

# Filter for specific algorithm
ascon_data = df[df['algorithm'] == 'ASCON-128']
aes_data = df[df['algorithm'] == 'AES-128-GCM']
```

### Key Metrics for Paper

- **Performance scaling:** ASCON shows linear degradation, AES shows constant overhead
- **Relative efficiency:** ASCON improves from 9.1× slower (64B) to 5.2× slower (8B)
- **Memory constant:** 71% reduction regardless of payload size
- **Throughput range:** ASCON 2,851-5,051 ops/sec, AES ~26,000 ops/sec

### Academic Discussion Points

1. **Fixed vs Variable Costs:** AES dominated by setup overhead, ASCON by processing cost
2. **IoT Context:** Small payloads (<32B) common in bike locks → ASCON more competitive
3. **Hardware Extrapolation:** On bare-metal, expect ASCON to potentially outperform AES for very small messages
4. **Memory Trade-off:** 71% savings enable richer firmware on constrained devices

## Troubleshooting

**Error: "Module not found"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Graph not generated**
```bash
# Check if matplotlib is installed
python -c "import matplotlib; print(matplotlib.__version__)"
```

**CSV empty or incomplete**
- Check that script completed without errors
- Look for error messages in terminal output

## Related Files

- **Detailed Analysis:** `docs/multi_payload_analysis.md`
- **Main Benchmark:** `benchmarks/benchmark_runner.py` (single payload: 64 bytes)
- **Visualization Script:** `src/visualize_results.py`

---

**Quick Reference Commands:**

```bash
# Run multi-payload benchmark
python benchmarks/multi_payload_benchmark.py

# View results
cat results/multi_payload_results.csv

# View graph
xdg-open results/graphs/payload_size_analysis.png
```

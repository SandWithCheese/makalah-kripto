# Academic Report Template

> **Course**: IF4020 Cryptography  
> **Topic**: Implementation and Performance Analysis of ASCON-128 for Secure BLE-Based Bicycle Locking Systems  
> **Format**: IEEE Conference Paper (6-10 pages)

---

## 1. Abstract (250 words max)

**Background**: Briefly explain the need for lightweight cryptography in IoT/bicycle lock scenarios.

**Problem Statement**: Traditional AES-GCM may be too resource-intensive for constrained devices.

**Methodology**: Describe benchmark approach (Python implementation, 10k iterations, timing/memory metrics).

**Results**: Summarize key findings (e.g., "ASCON-128 showed 21% faster encryption and 35% lower memory usage").

**Conclusion**: State the practical implication for bicycle lock deployment.

**Keywords**: Lightweight Cryptography, ASCON-128, AES-GCM, AEAD, IoT Security, Bicycle Lock

---

## 2. Introduction

### 2.1 Motivation
- Rise of smart bicycle locks using BLE/Bluetooth
- Security requirements: confidentiality, integrity, authenticity
- Resource constraints: limited RAM (2-32KB), battery-powered
- Need for efficient authenticated encryption

### 2.2 Research Questions
1. How does ASCON-128 compare to AES-128-GCM in software performance?
2. What are the memory footprint differences for IoT deployment?
3. Is ASCON-128 practical for real-time bicycle locking scenarios?

### 2.3 Contributions
- Empirical performance comparison of ASCON vs AES in Python
- Security analysis in bicycle lock threat model
- Practical recommendations for microcontroller deployment

---

## 3. Background

### 3.1 Authenticated Encryption with Associated Data (AEAD)
- **Definition**: Provides confidentiality (encryption) + integrity/authenticity (MAC)
- **Associated Data**: Non-secret metadata authenticated but not encrypted (e.g., Lock ID)
- **Nonce**: Number used once to prevent replay attacks

### 3.2 ASCON-128
- **Origin**: NIST Lightweight Cryptography Competition winner (2023)
- **Design**: Permutation-based sponge construction
- **State Size**: 320 bits (rate: 64 bits, capacity: 256 bits)
- **Key Features**:
  - Simple bitwise operations (AND, XOR, rotation)
  - Hardware-friendly (low gate count)
  - Side-channel resistant design
  - 128-bit security level

**ASCON Encryption Process**:
1. **Initialization**: Absorb 128-bit key + 128-bit nonce
2. **Process Associated Data**: Update state with Lock ID
3. **Encryption**: XOR plaintext with squeezed state
4. **Finalization**: Generate 128-bit authentication tag

### 3.3 AES-128-GCM
- **Standard**: NIST SP 800-38D (2007)
- **Design**: AES block cipher + Galois/Counter Mode
- **Key Features**:
  - Widely deployed (TLS, IPsec)
  - Hardware acceleration (AES-NI)
  - Parallelizable encryption
  - 96-bit nonce (standard), 128-bit tag

**GCM Operation**:
1. **Counter Mode**: Encrypt with AES-CTR
2. **GHASH**: Authenticate ciphertext + associated data
3. **Tag Generation**: Combine GHASH output with encrypted counter

### 3.4 Bicycle Lock Threat Model

**Security Goals**:
- **Confidentiality**: Attacker cannot read "unlock" command
- **Integrity**: Detect tampering with BLE payload
- **Authenticity**: Verify command from legitimate smartphone
- **Replay Prevention**: Nonce ensures each command is unique

**Threat Scenarios**:
1. **Passive Eavesdropping**: Attacker sniffs BLE signal
2. **Replay Attack**: Capture and replay valid unlock command
3. **Tampering**: Modify ciphertext to trigger malicious behavior
4. **Side-Channel Attack**: Power analysis while lock processes command

**Assumptions**:
- Pre-shared 128-bit key (provisioned during initial pairing)
- Smartphone and lock have synchronized random number generators
- Physical security of lock prevents hardware extraction

---

## 4. Methodology

### 4.1 Implementation Environment
- **Language**: Python 3.11
- **Libraries**:
  - `ascon==0.0.9` (Software reference implementation)
  - `pycryptodome==3.20.0` (AES-GCM)
- **Platform**: [Specify your hardware, e.g., Intel Core i7, 16GB RAM, Ubuntu 22.04]

### 4.2 Test Configuration

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Plaintext Size | 64 bytes | Typical unlock command + metadata |
| Key Size | 128 bits | Both algorithms' standard |
| Associated Data | 30 bytes | Lock ID identifier |
| Timing Iterations | 10,000 | Statistical significance |
| Warm-up Rounds | 100 | Avoid CPU scaling bias |
| Memory Iterations | 100 | tracemalloc overhead |

### 4.3 Benchmark Design

**Timing Measurement**:
```python
import time
start = time.perf_counter()
cipher.encrypt(plaintext, associated_data)
end = time.perf_counter()
```

**Memory Profiling**:
```python
import tracemalloc
tracemalloc.start()
cipher.encrypt(plaintext, associated_data)
current, peak = tracemalloc.get_traced_memory()
```

**Metrics Collected**:
1. Mean execution time (μs)
2. Standard deviation (statistical variance)
3. Min/Max execution time
4. Peak memory usage (KB)
5. Throughput (operations/second)

### 4.4 Security Verification
- **Nonce Uniqueness**: Verify no duplicates in 1000 operations
- **Authentication Test**: Tamper with ciphertext, verify decryption fails
- **Round-trip**: Ensure `decrypt(encrypt(msg)) == msg`

---

## 5. Results

### 5.1 Execution Time Comparison

**Table 1: Encryption/Decryption Performance**

| Algorithm | Encryption (μs) | Decryption (μs) | Std Dev (μs) |
|-----------|-----------------|-----------------|--------------|
| ASCON-128 | [INSERT DATA]   | [INSERT DATA]   | [INSERT DATA]|
| AES-128-GCM | [INSERT DATA] | [INSERT DATA]   | [INSERT DATA]|

> **Insert Graph**: `results/graphs/timing_comparison.png`

**Analysis**:
- ASCON-128 showed [X]% [faster/slower] encryption compared to AES-GCM
- Decryption performance was [comparable/different] by [X]%
- Standard deviation indicates [stable/variable] performance

### 5.2 Memory Footprint

**Table 2: Peak Memory Usage**

| Algorithm | Avg Peak (KB) | Max Peak (KB) |
|-----------|---------------|---------------|
| ASCON-128 | [INSERT DATA] | [INSERT DATA] |
| AES-128-GCM | [INSERT DATA] | [INSERT DATA] |

> **Insert Graph**: `results/graphs/memory_comparison.png`

**Analysis**:
- ASCON-128 used [X]% [less/more] memory than AES-GCM
- Critical for microcontrollers with [2-32KB] RAM
- [Discuss implications for ESP32 vs ARM Cortex-M0]

### 5.3 Throughput

**Table 3: Operations Per Second**

| Algorithm | Throughput (ops/sec) |
|-----------|---------------------|
| ASCON-128 | [INSERT DATA]       |
| AES-128-GCM | [INSERT DATA]     |

> **Insert Graph**: `results/graphs/throughput_comparison.png`

**Analysis**:
- Both algorithms achieve [X] operations/second
- Sufficient for real-time lock opening (target: >100 ops/sec)
- [Discuss scalability for multiple concurrent locks]

### 5.4 Security Verification

| Test | ASCON-128 | AES-128-GCM | Status |
|------|-----------|-------------|--------|
| Nonce Uniqueness | ✅ Pass | ✅ Pass | OK |
| Auth Failure Detection | ✅ Pass | ✅ Pass | OK |
| Round-trip Correctness | ✅ Pass | ✅ Pass | OK |

---

## 6. Discussion

### 6.1 Performance Trade-offs

**ASCON-128 Advantages**:
- Lower memory footprint (critical for 2-8KB RAM devices)
- Simpler operations (fewer cycles on microcontrollers)
- Designed for constrained environments

**AES-128-GCM Advantages**:
- Hardware acceleration (AES-NI on modern CPUs)
- Widely studied and deployed
- Faster on platforms with dedicated AES instructions

### 6.2 Security Considerations

**Replay Attack Prevention**:
- Both algorithms prevent replay via unique nonces
- Lock must maintain nonce counter or timestamp
- **Recommendation**: Use monotonic counter in lock firmware

**Side-Channel Resistance**:
- ASCON's bitsliced design naturally resistant to timing attacks
- AES requires constant-time implementation (risk of cache-timing)
- **Recommendation**: ASCON preferred for physically accessible locks

**Tag Verification**:
- Both provide 128-bit authentication tags
- Probability of forgery: 2^-128 (negligible)

### 6.3 Practical Deployment

**Target Microcontroller Analysis**:

| MCU | RAM | Flash | Recommendation |
|-----|-----|-------|----------------|
| ESP32 | 520 KB | 4 MB | Either (AES-NI available) |
| ARM Cortex-M0 | 8-32 KB | 64-256 KB | ASCON (lower memory) |
| Arduino Uno | 2 KB | 32 KB | ASCON (critical constraint) |

**Extrapolation to Bare-Metal**:
- Python overhead: ~100x slower than optimized C
- Expect <1μs encryption on modern MCU
- Battery impact: [Discuss power consumption estimates]

### 6.4 Limitations

1. **Python Implementation**: Not representative of hardware performance
2. **No BLE Integration**: Missing protocol-level analysis
3. **Single-threaded**: Doesn't test concurrent access scenarios
4. **PC Environment**: Different cache/pipeline than embedded systems

---

## 7. Conclusion

### 7.1 Summary of Findings
- ASCON-128 demonstrated [X]% lower memory usage than AES-GCM
- Execution time was [comparable/faster/slower] by [X]%
- Both algorithms meet real-time requirements for bicycle locks

### 7.2 Recommendations

**For Resource-Constrained Devices (<32KB RAM)**:
- ✅ Use ASCON-128 for lower memory footprint
- ✅ Simpler implementation reduces code size

**For Devices with Hardware Acceleration**:
- ✅ AES-GCM leverages AES-NI instructions
- ✅ Faster on ESP32 and modern ARM Cortex-A

**For Maximum Side-Channel Resistance**:
- ✅ ASCON-128 preferred for physically accessible locks
- ✅ Bitsliced design resists power analysis

### 7.3 Future Work
- Bare-metal C implementation on target MCU (ESP32, ARM)
- Power consumption measurements (oscilloscope + current shunt)
- BLE GATT characteristic integration
- Multi-lock concurrent access testing
- Side-channel attack practical evaluation

---

## 8. References

[1] NIST, "Lightweight Cryptography Standardization," NIST CSRC, 2023. [Online]. Available: https://csrc.nist.gov/projects/lightweight-cryptography

[2] C. Dobraunig et al., "ASCON v1.2: Lightweight Authenticated Encryption and Hashing," J. Cryptol., 2021.

[3] M. Dworkin, "Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC," NIST SP 800-38D, 2007.

[4] D. J. Bernstein, "ChaCha, a variant of Salsa20," Workshop Record of SASC, 2008.

[5] A. Biryukov and D. Khovratovich, "Related-Key Cryptanalysis of the Full AES-192 and AES-256," ASIACRYPT 2009.

[6] [Add benchmark library citations]

[7] [Add Python cryptography library documentation]

---

## Appendix A: Benchmark Code

### A.1 ASCON Wrapper (Excerpt)
```python
def encrypt_command(self, plaintext: bytes, associated_data: bytes):
    nonce = os.urandom(16)
    ciphertext = ascon.ascon_encrypt(
        self.key, nonce, associated_data, plaintext, "Ascon-128"
    )
    return nonce, ciphertext
```

### A.2 Timing Profiler (Excerpt)
```python
def measure_execution_time(func, iterations=10000, warmup=100):
    for _ in range(warmup):
        func()
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    
    return statistics.mean(times), statistics.stdev(times)
```

---

## Appendix B: Complete Results

> **Include**: Full CSV export from `results/benchmark_results.csv`

---

## Appendix C: Visualization Graphs

> **Include**:
> - `results/graphs/timing_comparison.png`
> - `results/graphs/memory_comparison.png`
> - `results/graphs/throughput_comparison.png`
> - `results/graphs/overview.png`

---

**Document Metadata**:
- **Authors**: [Your Name(s)]
- **Institution**: [University Name]
- **Course**: IF4020 Cryptography
- **Date**: [Submission Date]
- **Word Count**: [Target: 3000-5000 words for 6-10 pages]

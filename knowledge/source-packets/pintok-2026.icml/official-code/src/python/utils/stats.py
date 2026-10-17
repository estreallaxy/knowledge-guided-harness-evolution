"""
Latency statistics utilities for tokenization comparison.
"""

import statistics
from typing import Dict, List


class LatencyStats:
    """Store and calculate latency statistics"""
    def __init__(self, is_batch_mode: bool = False):
        self.times = []
        self.parse_times = []     # Time to parse packet headers
        self.extract_times = []   # Time to extract/decode text
        self.tokenize_times = []  # Time for tokenization
        self.encode_times = []    # Time for BERT encoding (if enabled)
        self.is_batch_mode = is_batch_mode  # Flag to indicate batch processing mode
        
    def add(self, latency_us: float, parse_us: float = 0, extract_us: float = 0, tokenize_us: float = 0, encode_us: float = 0):
        self.times.append(latency_us)
        self.parse_times.append(parse_us)
        self.extract_times.append(extract_us)
        self.tokenize_times.append(tokenize_us)
        self.encode_times.append(encode_us)
        
    def stats(self) -> Dict[str, float]:
        if not self.times:
            return {"count": 0}
        
        result = {
            "count": len(self.times),
            "mean": statistics.mean(self.times),
            "median": statistics.median(self.times),
            "std": statistics.stdev(self.times) if len(self.times) > 1 else 0,
            "min": min(self.times),
            "max": max(self.times),
            # Use coarse quantiles for small samples; fall back to max when insufficient
            "p90": statistics.quantiles(self.times, n=10)[8] if len(self.times) >= 10 else max(self.times),
            "p95": statistics.quantiles(self.times, n=20)[18] if len(self.times) >= 5 else max(self.times),
            "p99": statistics.quantiles(self.times, n=100)[98] if len(self.times) >= 10 else max(self.times),
        }
        
        # Add breakdown statistics if we have component data
        # For batch mode, parse/extract are 0 but we still want tokenize/encode stats
        if self.tokenize_times:
            try:
                result["tokenize_mean"] = statistics.mean(self.tokenize_times)
                result["tokenize_std"] = statistics.stdev(self.tokenize_times) if len(self.tokenize_times) > 1 else 0.0
            except Exception:
                pass

            # Add parse/extract only if they are present (may be zeros in batch mode)
            try:
                if any(t != 0 for t in self.parse_times):
                    result["parse_mean"] = statistics.mean(self.parse_times)
                    result["parse_std"] = statistics.stdev(self.parse_times) if len(self.parse_times) > 1 else 0.0
                if any(t != 0 for t in self.extract_times):
                    result["extract_mean"] = statistics.mean(self.extract_times)
                    result["extract_std"] = statistics.stdev(self.extract_times) if len(self.extract_times) > 1 else 0.0
            except Exception:
                pass

            # Add encode statistics if we have encode data
            try:
                if self.encode_times and any(t != 0 for t in self.encode_times):
                    result["encode_mean"] = statistics.mean(self.encode_times)
                    result["encode_std"] = statistics.stdev(self.encode_times) if len(self.encode_times) > 1 else 0.0
            except Exception:
                pass

        return result

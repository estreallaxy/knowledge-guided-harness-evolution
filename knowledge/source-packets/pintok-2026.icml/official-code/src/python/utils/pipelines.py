"""
Pipeline implementations for tokenization comparison.

Contains DPDK and Python-Rust pipeline implementations.
"""

import os
import socket
import subprocess
import threading
import time
import queue
import shutil
from typing import Dict, List, Optional
import struct
import mmap

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Enforce single-core tokenizers by default for fair comparisons.
# This must be done before importing libraries that may initialize Rayon.
_one_core_disabled = os.environ.get("ONE_CORE_LIMIT_DISABLED", "").lower() in ("1", "true", "yes")
if not _one_core_disabled:
    # Respect user-provided settings if already present
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    # Rayon uses RAYON_RS_NUM_THREADS (preferred). Some setups honor RAYON_NUM_THREADS.
    if "RAYON_RS_NUM_THREADS" not in os.environ and "RAYON_NUM_THREADS" not in os.environ:
        os.environ["RAYON_RS_NUM_THREADS"] = "1"

# torch is only needed for the BERT-encoder paths; keep it optional so
# lightweight consumers (e.g. the pintok package) can import without it.
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from .stats import LatencyStats
from .encoders import BERTEncoder

# For the Rust tokenizer pipeline
try:
    from transformers import AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class DPDKPipeline:
    """DPDK-based tokenization pipeline (no fallback) with optional BERT encoding"""
    def __init__(self,
                 dpdk_exe_path: str = None,
                 tokenizer_type: str = "bpe",
                 model: str = None,
                 encoder_type: str = None,
                 encoder_model: str | None = None,
                 force_cpu: bool = False,
                 debug_bert: bool = False,
                 debug: bool = False,
                 batch_size: int = 128,
                 enable_batch: bool = False,
                 latency_mode: str = "tokenize-only",
                 pin_core: Optional[int] = None,
                 rt_prio: Optional[int] = None,
                 dpdk_log_level: Optional[str] = None,
                 use_sudo: Optional[bool] = None,
                 allow_non_isolated: bool = False,
                 disable_cache: bool = False,
                 cwd: Optional[str] = None):
        # Support different DPDK tokenizer types
        if tokenizer_type == "bpe":
            # Prefer your standard build/ tree; fall back to builddir/ if present
            candidates = [
                os.path.join(os.getcwd(), "build/src/dpdk/tokenizer/tokenizer_dpdk_bpe_vm"),
                os.path.join(os.getcwd(), "builddir/src/dpdk/tokenizer/tokenizer_dpdk_bpe_vm"),
            ]
        elif tokenizer_type == "wordpiece":
            candidates = [
                os.path.join(os.getcwd(), "build/src/dpdk/tokenizer/tokenizer_dpdk_wordpiece_vm"),
                os.path.join(os.getcwd(), "builddir/src/dpdk/tokenizer/tokenizer_dpdk_wordpiece_vm"),
            ]
        else:
            candidates = [
                os.path.join(os.getcwd(), "build/src/dpdk/tokenizer/tokenizer_dpdk_simple_vm"),
                os.path.join(os.getcwd(), "builddir/src/dpdk/tokenizer/tokenizer_dpdk_simple_vm"),
            ]
        default_exe = None
        for c in candidates:
            try:
                if os.path.exists(c) and os.access(c, os.X_OK):
                    default_exe = c
                    break
            except Exception:
                pass
        # As last resort, keep the first candidate even if it doesn't exist; start() will error clearly
        if default_exe is None:
            default_exe = candidates[0]
            
        self.dpdk_exe_path = dpdk_exe_path or default_exe
        # Working directory for the child process (the tokenizer binary loads
        # tokenizer_data/ relative to its cwd); None keeps the caller's cwd.
        self.cwd = cwd
        self.tokenizer_type = tokenizer_type
        self.model = model
        self.process = None
        self.output_queue = queue.Queue()
        self.enable_batch = enable_batch
        self.latency_stats = LatencyStats(is_batch_mode=enable_batch)
        self.force_cpu = force_cpu
        self.debug_bert = debug_bert
        self.debug = debug
        self.batch_size = batch_size
        self.latency_mode = latency_mode
        self.disable_cache = disable_cache
        self.encoder_model = encoder_model
        # Readiness event: set when the child binds port and starts listening
        self._ready_event = threading.Event()
        # Deduplicate by composite key (message-id, arrival-tsc) to avoid
        # counting duplicated deliveries of the same message while allowing
        # new messages that may reuse ids across trials/lengths.
        self._seen_packets: set[tuple[int, int]] = set()
        # Runtime tuning knobs (optional)
        self.pin_core = pin_core
        self.rt_prio = rt_prio
        self.dpdk_log_level_override = dpdk_log_level
        self.use_sudo_override = use_sudo
        env_allow = os.environ.get("DPDK_ALLOW_NON_ISOLATED", "").lower() in ("1", "true", "yes")
        self.allow_non_isolated = allow_non_isolated or env_allow
        
        # Batch processing state
        self.pending_results = []
        self.batch_start_time = None
        # Control deduplication (can be disabled during warmup)
        self._dedup_enabled = True
        # DPDK cache counters (aggregated across packets in this run)
        self.cache_lookups_total = 0
        self.cache_hits_total = 0
        self.cache_inserts_total = 0
        
        # Shared memory mapping (for zero-copy token IDs)
        self._shm_path: Optional[str] = None
        self._shm_size: Optional[int] = None
        self._shm_max_tokens: Optional[int] = None
        self._shm_mmap: Optional[mmap.mmap] = None
        self._shm_hdr_fmt = "<IIIIQQQQ"  # token_shm_header (64 bytes)
        self._shm_hdr_size = struct.calcsize(self._shm_hdr_fmt)
        
        # BERT encoder setup
        self.encoder_type = encoder_type
        self.bert_encoder = None
        if encoder_model and encoder_model.lower() not in ("standalone", "none"):
            # Prefer explicit model name if provided
            self.bert_encoder = BERTEncoder(encoder_type or encoder_model, model_name=encoder_model, force_cpu=force_cpu, debug=debug)
        elif encoder_type:
            # Backwards compat: tinybert, etc.
            self.bert_encoder = BERTEncoder(encoder_type, force_cpu=force_cpu, debug=debug)
        
    def start(self):
        """Start the DPDK tokenizer process with fallback"""
        def _parse_cpu_list(spec: str) -> set[int]:
            cpus: set[int] = set()
            if not spec:
                return cpus
            for part in spec.split(','):
                part = part.strip()
                if not part:
                    continue
                if '-' in part:
                    a, b = part.split('-', 1)
                    if a.isdigit() and b.isdigit():
                        start = int(a)
                        end = int(b)
                        if end >= start:
                            cpus.update(range(start, end + 1))
                elif part.isdigit():
                    cpus.add(int(part))
            return cpus

        def _isolated_cpus() -> set[int]:
            # Prefer sysfs if available
            try:
                with open('/sys/devices/system/cpu/isolated', 'r') as f:
                    content = f.read().strip()
                if content:
                    return _parse_cpu_list(content)
            except Exception:
                pass
            # Fallback: parse kernel cmdline isolcpus=...
            try:
                with open('/proc/cmdline', 'r') as f:
                    cmdline = f.read()
                key = 'isolcpus='
                if key in cmdline:
                    tail = cmdline.split(key, 1)[1]
                    # Value ends at first space
                    value = tail.split(' ', 1)[0]
                    # Strip common flags like managed_irq,domain,nohz
                    cleaned_parts = []
                    for p in value.split(','):
                        p = p.strip()
                        if p and (p[0].isdigit()):
                            cleaned_parts.append(p)
                    return _parse_cpu_list(','.join(cleaned_parts))
            except Exception:
                pass
            return set()

        def _assert_core_is_isolated(core: int):
            iso = _isolated_cpus()
            if core is None:
                raise RuntimeError("DPDK pin core is not set; cannot enforce isolation")
            if core not in iso:
                raise RuntimeError(
                    f"DPDK requires an isolated CPU core. Core {core} is not in isolcpus. "
                    f"Configure kernel with isolcpus (and ideally nohz_full, rcu_nocbs) to include core {core}."
                )
        def _wrap_with_stdbuf(cmd_list):
            # Ensure child stdout/stderr are line-buffered to avoid block buffering when piped
            try:
                if not shutil.which("stdbuf"):
                    return cmd_list
                if not cmd_list:
                    return cmd_list
                if cmd_list[0] != "sudo":
                    return ["stdbuf", "-oL", "-eL"] + cmd_list
                # Insert stdbuf after sudo and its flags (e.g., -E, -n)
                insert_idx = 1
                while insert_idx < len(cmd_list) and cmd_list[insert_idx].startswith("-"):
                    insert_idx += 1
                # splice: sudo [flags] stdbuf -oL -eL <rest>
                return cmd_list[:insert_idx] + ["stdbuf", "-oL", "-eL"] + cmd_list[insert_idx:]
            except Exception:
                return cmd_list
        # Start DPDK binary only; no fallback
        if not os.path.exists(self.dpdk_exe_path):
            raise FileNotFoundError(f"DPDK executable not found: {self.dpdk_exe_path}")

        # Use VM-friendly DPDK EAL arguments
        dpdk_log_level = self.dpdk_log_level_override or os.environ.get("DPDK_LOG_LEVEL", ("7" if self.debug else "3"))
        # Decide sudo behavior (explicit arg has priority over env). Default: use sudo for best perf.
        use_sudo = self.use_sudo_override
        if use_sudo is None:
            if os.environ.get("DPDK_NO_SUDO", "").lower() == "true":
                use_sudo = False
            elif os.environ.get("DPDK_USE_SUDO", "").lower() == "true":
                use_sudo = True
            else:
                use_sudo = True
        # Preserve environment when using sudo so DPDK_* vars propagate to the child
        cmd = (["sudo", "-E"] if use_sudo else []) + [self.dpdk_exe_path, "--no-pci", f"--log-level={dpdk_log_level}"]

        # Separate DPDK EAL args from application args to avoid EAL parsing errors
        cmd.append("--")

        # Add debug flag for application-level verbosity (after "--").
        # In embed-mode the child can emit very large per-token debug lines,
        # which risks blocking the pipe. Keep RX tracing via env, but skip --debug
        # when a BERT encoder is active.
        if self.debug and (self.bert_encoder is None):
            cmd.append("--debug")

        # Add model parameter for BPE tokenizer (keep last)
        if self.tokenizer_type == "bpe":
            if self.model in ["answerdotai/ModernBERT-base", "modernbert-base"]:
                cmd.append("modernbert-base")
            elif self.model in ["answerdotai/ModernBert-large", "modernbert-large"]:
                cmd.append("modernbert-large")
            elif self.model == "diffugpt-m":
                cmd.append("diffugpt-m")
            elif self.model == "gpt2":
                cmd.append("gpt2")
            else:
                cmd.append(self.model)

        # Enforce isolation before launching (optional override)
        if self.pin_core is None:
            raise RuntimeError("DPDK pin core not specified; set --pin-core or DPDK_PIN_CORE.")
        if not self.allow_non_isolated:
            _assert_core_is_isolated(int(self.pin_core))
        else:
            try:
                iso = _isolated_cpus()
                if int(self.pin_core) not in iso:
                    print(f"Warning: core {self.pin_core} is not isolated; proceeding due to allow_non_isolated=True")
            except Exception:
                pass

        # If using sudo, refresh authentication up-front to avoid race with child startup
        if use_sudo:
            try:
                subprocess.run(["sudo", "-v"], check=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to authenticate with sudo (-v): {e}")

        if self.debug:
            print(f"Starting DPDK process: {' '.join(cmd)}")

        # Prepare child environment with optional pinning and RT priority
        child_env = os.environ.copy()
        if self.pin_core is not None:
            child_env["DPDK_PIN_CORE"] = str(self.pin_core)
        if self.rt_prio is not None:
            child_env["DPDK_RT_PRIO"] = str(self.rt_prio)
        if self.allow_non_isolated:
            child_env["DPDK_ALLOW_NON_ISOLATED"] = "1"
        # Ensure log level is visible to child
        if self.dpdk_log_level_override is not None:
            child_env["DPDK_LOG_LEVEL"] = str(self.dpdk_log_level_override)
        if use_sudo:
            child_env["DPDK_USE_SUDO"] = "true"
        # Enable rich RX tracing when debug is on (safe even without --debug)
        if self.debug:
            child_env["DPDK_RX_TRACE"] = "1"
        # Signal embed-mode to child so it can suppress expensive logs
        if self.bert_encoder is not None:
            child_env["DPDK_EMBED_MODE"] = "1"
        # Provide a unique SHM name for child to use (helps avoid collisions)
        # If already set by caller, keep it.
        if "DPDK_SHM_NAME" not in child_env:
            unique = f"/dpdk_tokids_{os.getpid()}_{int(time.time()*1e6)}"
            child_env["DPDK_SHM_NAME"] = unique

        # Start process
        self.process = subprocess.Popen(
            _wrap_with_stdbuf(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=self._prepare_child_env(child_env),
            cwd=self.cwd,
        )

        # Start output monitoring thread immediately to capture readiness banner
        self.output_thread = threading.Thread(target=self._monitor_output, daemon=True)
        self.output_thread.start()

        # Give it a short window to fail fast
        time.sleep(1.0)
        if self.process.poll() is not None:
            try:
                out, _ = self.process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                out = "<timeout reading process output>"
            rc = self.process.returncode
            raise RuntimeError(f"DPDK failed to start (exit code {rc}). Output:\n{out}")

        # Wait for readiness (port is bound) before proceeding (helps when sudo prompts for password)
        if self.debug:
            print("Waiting for DPDK tokenizer to become ready (listening on port)...")
        if not self.wait_ready(timeout=30.0):
            raise RuntimeError(
                "DPDK process did not indicate readiness within 30s. If using sudo, ensure you entered the password; "
                "otherwise check logs above for errors."
            )
        if self.debug:
            print(f"DPDK {self.tokenizer_type} tokenizer is ready")

        # Initialize BERT encoder if specified (after readiness)
        if self.bert_encoder:
            self.bert_encoder.initialize()
            if self.debug:
                print("Using direct BERT processing")
        
    # NOTE: Child process is forced to line-buffer via stdbuf; our pipe is text mode (UTF-8).
    def _monitor_output(self):
        """Monitor DPDK process output"""
        current_result = None
        
        for line in self.process.stdout:
            # Show child output only when debug is enabled
            if self.debug:
                print(line, end="")
            line = line.strip()
            # Detect readiness from startup banner
            if 'listening on port' in line.lower():
                self._ready_event.set()
            # Detect SHM readiness and map it
            if line.startswith("SHM_READY "):
                # Expected: SHM_READY name=<...> path=<...> size=<int> max_tokens=<int>
                try:
                    parts = dict(p.split('=', 1) for p in line[len("SHM_READY "):].split())
                    path = parts.get('path')
                    size = int(parts.get('size', '0'))
                    max_tokens = int(parts.get('max_tokens', '0'))
                    if path and size > 0:
                        self._map_shm(path, size, max_tokens)
                except Exception:
                    pass
            # Handle DPDK output format only
            if line == "DPDK_TOKENIZATION_START":
                # Consider it ready by first tokenization as well
                self._ready_event.set()
                current_result = {}
            elif line == "DPDK_TOKENIZATION_END":
                # Process a packet even if no key/value lines were printed (embed-mode suppresses them)
                if current_result is not None:
                    # Debug output for DPDK tokenization workflow
                    if self.debug:
                        print(f"\n=== DEBUG: DPDK Packet Processing ===")
                        text = current_result.get("ORIGINAL_TEXT", "")
                        tokens_str = current_result.get("TOKENS", "")
                        token_ids_str = current_result.get("TOKEN_IDS", "")
                        print(f"1. Parse + Extract: '{text}'")
                        if tokens_str:
                            token_list = tokens_str.split()
                            print(f"2. Text-to-subwords: {token_list}")
                        else:
                            print(f"2. Text-to-subwords: {tokens_str}")
                        if token_ids_str:
                            token_ids = [int(t) for t in token_ids_str.split()]
                            print(f"3. Subwords-to-IDs: {token_ids}")
                        else:
                            print(f"3. Subwords-to-IDs: [No TOKEN_IDS in output]")

                    # Add BERT encoding if enabled
                    if self.bert_encoder:
                        token_ids_np = None
                        # Prefer shared memory (zero-copy) if available
                        if self._shm_mmap and HAS_NUMPY:
                            token_ids_np, shm_meta = self._read_shm_tokens_numpy()
                            if token_ids_np is not None and self.debug:
                                preview = token_ids_np[:10].tolist()
                                print(f"4. BERT Encoding Input: SHM token IDs (len={token_ids_np.shape[0]}), preview={preview}")
                            # Propagate SHM meta (message id and times)
                            if shm_meta:
                                try:
                                    current_result['MESSAGE_ID'] = int(shm_meta.get('message_id', 0))
                                except Exception:
                                    pass
                        # Drop duplicates using (MESSAGE_ID, PACKET_ARRIVAL_TIME) when available
                        try:
                            mid = int(current_result.get('MESSAGE_ID')) if 'MESSAGE_ID' in current_result else None
                        except Exception:
                            mid = None
                        try:
                            pkt_tsc = int(shm_meta.get('PACKET_ARRIVAL_TIME')) if shm_meta and 'PACKET_ARRIVAL_TIME' in shm_meta else None
                        except Exception:
                            pkt_tsc = None
                        if self._dedup_enabled and mid is not None and pkt_tsc is not None:
                            key = (mid, pkt_tsc)
                            if key in self._seen_packets:
                                current_result = None
                                continue
                        # Fallback: parse from text if provided
                        if token_ids_np is None and "TOKEN_IDS" in current_result:
                            try:
                                ids = [int(t) for t in current_result["TOKEN_IDS"].split()]
                                if HAS_NUMPY:
                                    token_ids_np = np.asarray(ids, dtype=np.int32)
                                else:
                                    token_ids_np = ids  # type: ignore
                            except Exception:
                                token_ids_np = None

                        if token_ids_np is not None:
                            if self.bert_encoder.device.type == "cuda":
                                torch.cuda.synchronize()
                            start_encode = time.perf_counter()
                            if HAS_NUMPY and not isinstance(token_ids_np, list):
                                embeddings = self.bert_encoder.encode_with_pooling_from_numpy(token_ids_np)
                            else:
                                embeddings = self.bert_encoder.encode_with_pooling(list(token_ids_np))  # type: ignore
                            if self.bert_encoder.device.type == "cuda":
                                torch.cuda.synchronize()
                            end_encode = time.perf_counter()
                            current_result["BERT_EMBEDDINGS_SHAPE"] = str(list(embeddings.shape))
                            current_result["BERT_ENCODE_TIME_US"] = (end_encode - start_encode) * 1_000_000
                            current_result["DELIVERY_TIME"] = end_encode
                            # Include actual embedding data for comparison
                            current_result["BERT_EMBEDDING_DATA"] = embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else embeddings
                            if self.debug_bert:
                                current_result["BERT_SAMPLE_VALUES"] = str(embeddings[0, :5].tolist())
                            if self.debug:
                                print(f"   BERT Output Shape: {list(embeddings.shape)}")
                                print(f"   BERT Sample Values: {embeddings[0, :5].tolist()}")

                    if self.debug:
                        print(f"=== DEBUG: DPDK Processing Complete ===")

                    # If TOKEN_IDS not provided by child (non-debug), synthesize from SHM for compatibility
                    try:
                        if 'TOKEN_IDS' not in current_result and self._shm_mmap and HAS_NUMPY:
                            ids_np, _meta = self._read_shm_tokens_numpy()
                            if ids_np is not None:
                                current_result['TOKEN_IDS'] = " ".join(map(str, ids_np.tolist()))
                    except Exception:
                        pass

                    # Aggregate cache counters if present
                    try:
                        if 'CACHE_LOOKUPS' in current_result:
                            self.cache_lookups_total += int(current_result['CACHE_LOOKUPS'])
                        if 'CACHE_HITS' in current_result:
                            self.cache_hits_total += int(current_result['CACHE_HITS'])
                        if 'CACHE_INSERTS' in current_result:
                            self.cache_inserts_total += int(current_result['CACHE_INSERTS'])
                        if 'CACHE_INSERT_FAILS' in current_result:
                            self.cache_insert_fails_total = getattr(self, 'cache_insert_fails_total', 0) + int(current_result['CACHE_INSERT_FAILS'])
                        if 'CACHE_SKIP_LONGKEY' in current_result:
                            self.cache_skip_longkey_total = getattr(self, 'cache_skip_longkey_total', 0) + int(current_result['CACHE_SKIP_LONGKEY'])
                        if 'CACHE_SKIP_OVERSIZE' in current_result:
                            self.cache_skip_oversize_total = getattr(self, 'cache_skip_oversize_total', 0) + int(current_result['CACHE_SKIP_OVERSIZE'])
                    except Exception:
                        pass
                    # Mark message-id as seen and enqueue
                    try:
                        if self._dedup_enabled and 'MESSAGE_ID' in current_result:
                            mid2 = int(current_result['MESSAGE_ID'])
                            # Prefer PACKET_ARRIVAL_TIME from SHM meta; fall back to 0
                            pkt2 = 0
                            try:
                                if self._shm_mmap and HAS_NUMPY:
                                    _idsnp, meta2 = self._read_shm_tokens_numpy()
                                    if meta2 and 'PACKET_ARRIVAL_TIME' in meta2:
                                        pkt2 = int(meta2['PACKET_ARRIVAL_TIME'])
                            except Exception:
                                pkt2 = 0
                            self._seen_packets.add((mid2, pkt2))
                    except Exception:
                        pass
                    self.output_queue.put(current_result)
                    self._calculate_latency(current_result)
                current_result = None
            elif current_result is not None:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key in ["PACKET_ARRIVAL_TIME", "ASSEMBLY_START_TIME", "TOKENIZE_START_TIME", "TOKENIZE_END_TIME", "TSC_FREQUENCY"]:
                        current_result[key] = int(value)
                    elif key == "NUM_TOKENS":
                        current_result[key] = int(value)
                    elif key in ("CACHE_LOOKUPS", "CACHE_HITS", "CACHE_INSERTS", "CACHE_INSERT_FAILS", "CACHE_SKIP_LONGKEY", "CACHE_SKIP_OVERSIZE"):
                        # Record as integer deltas per message
                        try:
                            current_result[key] = int(value)
                        except Exception:
                            current_result[key] = 0
                    else:
                        current_result[key] = value

    def _map_shm(self, path: str, size: int, max_tokens: int):
        try:
            fd = os.open(path, os.O_RDONLY)
            mm = mmap.mmap(fd, length=size, access=mmap.ACCESS_READ)
            os.close(fd)
            self._shm_path = path
            self._shm_size = size
            self._shm_max_tokens = max_tokens
            self._shm_mmap = mm
            if self.debug:
                print(f"Mapped SHM at {path} (size={size}, max_tokens={max_tokens})")
        except Exception as e:
            print(f"Warning: Failed to mmap SHM at {path}: {e}")
            self._shm_mmap = None

    def _read_shm_tokens_numpy(self):
        """Lockless read from SHM using seqlock versioning.
        Returns (np.ndarray[int32], meta_dict) or (None, None) if unavailable.
        """
        if not (self._shm_mmap and HAS_NUMPY):
            return None, None
        mm = self._shm_mmap
        hdr_fmt = self._shm_hdr_fmt
        hdr_size = self._shm_hdr_size

        # Attempt a few times to get a stable snapshot
        for _ in range(8):
            v1 = struct.unpack_from('<I', mm, 4)[0]
            if v1 & 1:
                # writer in progress
                time.sleep(0)
                continue
            fields = struct.unpack_from(hdr_fmt, mm, 0)
            magic, version, num_tokens, message_id, pkt_tsc, asm_tsc, tok_s_tsc, tok_e_tsc = fields
            v2 = struct.unpack_from('<I', mm, 4)[0]
            if v1 == v2 and (v2 % 2 == 0) and magic == 0x544F4B53 and num_tokens >= 0:
                max_tokens = self._shm_max_tokens or 0
                if num_tokens > max_tokens:
                    num_tokens = max_tokens
                data_off = hdr_size
                byte_len = num_tokens * 4
                mv = memoryview(mm)[data_off:data_off + byte_len]
                arr = np.frombuffer(mv, dtype=np.int32, count=num_tokens)
                meta = {
                    'message_id': message_id,
                    'PACKET_ARRIVAL_TIME': pkt_tsc,
                    'ASSEMBLY_START_TIME': asm_tsc,
                    'TOKENIZE_START_TIME': tok_s_tsc,
                    'TOKENIZE_END_TIME': tok_e_tsc,
                }
                return arr, meta
            time.sleep(0)
        return None, None
                        
    def wait_ready(self, timeout: float = 15.0) -> bool:
        """Block until the DPDK child indicates it is listening on the port.
        Returns True if ready within timeout, False otherwise."""
        return self._ready_event.wait(timeout=timeout)

    def _calculate_latency(self, result: Dict):
        """Calculate latency from DPDK timing data"""
        # If embed-mode suppressed DPDK timing but we have BERT timing, record a sample
        # so higher-level aggregation (which overlays E2E) has a non-zero count.
        if self.bert_encoder and ("BERT_ENCODE_TIME_US" in result):
            try:
                enc_us = float(result.get("BERT_ENCODE_TIME_US", 0) or 0)
                # Count this sample; use encode-only as a placeholder. E2E is set later by runner.
                self.latency_stats.add(enc_us, 0, 0, 0, enc_us)
                # Do not continue computing tokenize-only timing without DPDK fields
                # because PACKET_ARRIVAL/TSC may be intentionally suppressed.
                return
            except Exception:
                pass

        # Check if we have the required DPDK timing fields
        required_fields = ["PACKET_ARRIVAL_TIME", "TOKENIZE_END_TIME", "TSC_FREQUENCY"]
        if not all(k in result for k in required_fields):
            print(f"Warning: Missing timing fields in DPDK result: {list(result.keys())}")
            return
            
        tsc_freq = result["TSC_FREQUENCY"]
        if tsc_freq <= 0:
            print(f"Warning: Invalid TSC_FREQUENCY: {tsc_freq}")
            return
            
        # Calculate tokenization latency (DPDK timing)
        tokenize_end_time = result["TOKENIZE_END_TIME"]
        
        # If we have BERT encoding, extend the end time
        bert_encode_us = result.get("BERT_ENCODE_TIME_US", 0)
        if bert_encode_us > 0:
            # Convert BERT encoding time back to cycles and add to end time
            bert_cycles = (bert_encode_us * tsc_freq) / 1000000.0
            total_end_time = tokenize_end_time + bert_cycles
        else:
            total_end_time = tokenize_end_time
        
        # Total latency (including BERT if enabled)
        cycles = total_end_time - result["PACKET_ARRIVAL_TIME"]
        latency_us = (cycles * 1000000.0) / tsc_freq
            
        # Total latency (including BERT if enabled)
        cycles = total_end_time - result["PACKET_ARRIVAL_TIME"]
        latency_us = (cycles * 1000000.0) / tsc_freq
        
        # Component breakdown (estimate from DPDK timing points if available)
        parse_us = 0
        extract_us = 0 
        tokenize_us = latency_us  # Default: assume most time is tokenization
        encode_us = bert_encode_us  # BERT encoding time
        
        # For batch mode, we only care about actual processing time
        if self.enable_batch:
            # In batch mode, exclude parse/extract overhead
            # Only measure tokenization time directly
            if "TOKENIZE_START_TIME" in result:
                tokenize_cycles = result["TOKENIZE_END_TIME"] - result["TOKENIZE_START_TIME"]
                tokenize_us = (tokenize_cycles * 1000000.0) / tsc_freq
            else:
                # Fallback if no TOKENIZE_START_TIME
                tokenize_us = latency_us - bert_encode_us
            
            # For batch mode: report only tokenization + encoding
            total_batch_latency = tokenize_us + encode_us
            self.latency_stats.add(total_batch_latency, 0, 0, tokenize_us, encode_us)
        else:
            # Non-batch mode: include all components
            # If we have assembly timing, we can break it down better
            if "ASSEMBLY_START_TIME" in result:
                assembly_cycles = result["ASSEMBLY_START_TIME"] - result["PACKET_ARRIVAL_TIME"] 
                parse_us = (assembly_cycles * 1000000.0) / tsc_freq
                
            if "TOKENIZE_START_TIME" in result:
                if "ASSEMBLY_START_TIME" in result:
                    extract_cycles = result["TOKENIZE_START_TIME"] - result["ASSEMBLY_START_TIME"]
                    extract_us = (extract_cycles * 1000000.0) / tsc_freq
                tokenize_cycles = result["TOKENIZE_END_TIME"] - result["TOKENIZE_START_TIME"]
                tokenize_us = (tokenize_cycles * 1000000.0) / tsc_freq
            
            if self.latency_mode == "tokenize-only":
                # Record parse/extract components for decomposition even if we only aggregate alg time
                alg_total = tokenize_us + encode_us
                self.latency_stats.add(alg_total, parse_us, extract_us, tokenize_us, encode_us)
            else:
                self.latency_stats.add(latency_us, parse_us, extract_us, tokenize_us, encode_us)
    
    def get_result(self, timeout: float = 10.0) -> Optional[Dict]:
        """Get tokenization result from DPDK process"""
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_batch_results(self, timeout: float = 10.0) -> List[Dict]:
        """
        Get a batch of tokenization results from DPDK process
        
        Args:
            timeout: Timeout in seconds to wait for results
            
        Returns:
            List[Dict]: List of tokenization results (up to batch_size)
        """
        results = []
        batch_timeout = timeout / self.batch_size  # Distribute timeout across batch
        
        for _ in range(self.batch_size):
            try:
                result = self.output_queue.get(timeout=batch_timeout)
                if result:
                    # Store result for potential batch BERT processing
                    # Capture token IDs via SHM if available to avoid later parsing
                    if self._shm_mmap and HAS_NUMPY:
                        ids_np, meta = self._read_shm_tokens_numpy()
                        if ids_np is not None:
                            # Copy to isolate from SHM overwrites; still avoids dpdk->python memcpy
                            result['TOKEN_IDS_NUMPY'] = np.array(ids_np, dtype=np.int32, copy=True)
                            # Also provide string for compatibility/saving
                            result['TOKEN_IDS'] = " ".join(map(str, result['TOKEN_IDS_NUMPY'].tolist()))
                            # Propagate message id for E2E matching when available
                            if meta and 'message_id' in meta:
                                try:
                                    result['MESSAGE_ID'] = int(meta['message_id'])
                                except Exception:
                                    pass
                    self.pending_results.append(result)
                    results.append(result)
                    
                    # If we have a full batch and BERT encoding is enabled, process the batch
                    if len(self.pending_results) >= self.batch_size and self.bert_encoder:
                        self._process_bert_batch()
            except queue.Empty:
                break  # No more results available
        
        # Process remaining results if we have partial batch and BERT encoding
        if self.pending_results and self.bert_encoder:
            self._process_bert_batch()
            
        return results
    
    def _process_bert_batch(self):
        """Process pending results with batch BERT encoding"""
        if not self.pending_results or not self.bert_encoder:
            return
            
        # Extract texts for batch processing and convert to token IDs
        token_ids_list = []
        valid_indices = []
        for i, result in enumerate(self.pending_results):
            if HAS_NUMPY and 'TOKEN_IDS_NUMPY' in result:
                token_ids_list.append(result['TOKEN_IDS_NUMPY'])
                valid_indices.append(i)
            elif "TOKEN_IDS" in result:
                ids = [int(t) for t in result["TOKEN_IDS"].split()]
                token_ids_list.append(ids)
                valid_indices.append(i)
        if self.debug:
            try:
                first_len = len(token_ids_list[0]) if token_ids_list else 0
            except Exception:
                first_len = 0
            print(f"Processing batch of {len(token_ids_list)} items for BERT encoding, each with {first_len} tokens")
        if not token_ids_list:
            self.pending_results.clear()
            return
        
        # Batch BERT encoding
        if self.bert_encoder.device.type == "cuda":
            torch.cuda.synchronize()
        start_encode = time.perf_counter()
        if HAS_NUMPY and all(hasattr(x, 'dtype') for x in token_ids_list):
            batch_embeddings = self.bert_encoder.encode_batch_with_pooling_from_numpy_list(token_ids_list)  # type: ignore
        else:
            batch_embeddings = self.bert_encoder.encode_batch_with_pooling(token_ids_list)
        if self.bert_encoder.device.type == "cuda":
            torch.cuda.synchronize()
        end_encode = time.perf_counter()
        
        batch_encode_time_us = (end_encode - start_encode) * 1_000_000
        per_item_encode_time_us = batch_encode_time_us / len(token_ids_list)
        
        # Update results with BERT data
        for i, result_idx in enumerate(valid_indices):
            embeddings = batch_embeddings[i:i+1]  # Keep batch dimension
            self.pending_results[result_idx]["BERT_EMBEDDINGS_SHAPE"] = str(list(embeddings.shape))
            self.pending_results[result_idx]["BERT_ENCODE_TIME_US"] = per_item_encode_time_us
            self.pending_results[result_idx]["BERT_BATCH_SIZE"] = len(token_ids_list)
            # Record delivery time for approximate E2E matching in batch mode
            self.pending_results[result_idx]["DELIVERY_TIME"] = end_encode
            # Include actual embedding data for comparison
            self.pending_results[result_idx]["BERT_EMBEDDING_DATA"] = embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else embeddings

            if self.debug_bert:
                # Show first few values for debugging
                self.pending_results[result_idx]["BERT_SAMPLE_VALUES"] = str(embeddings[0, :5].tolist())
        
        # Clear processed results
        self.pending_results.clear()
            
    def stop(self):
        """Stop the DPDK process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
        self.process = None

    def _prepare_child_env(self, env: dict) -> dict:
        # Optionally disable DPDK-side token cache via env flag
        if self.disable_cache:
            env = env.copy()
            env["DPDK_BPE_CACHE_CAPACITY"] = "0"
        return env


class PythonRustPipeline:
    """HuggingFace tokenizer pipeline (fast Rust or Python)."""
    def __init__(self, model_name: str = "modernbert-base", encoder_type: str = None, encoder_model: str | None = None, force_cpu: bool = False, debug: bool = False, batch_size: int = 128, enable_batch: bool = False, use_fast: bool = True, latency_mode: str = "tokenize-only", warmup: bool = False, disable_cache: bool = False, pin_core: int | None = None):
        self.model_name = model_name
        self.tokenizer = None
        self.enable_batch = enable_batch
        self.latency_stats = LatencyStats(is_batch_mode=enable_batch)
        self.sock = None
        self.force_cpu = force_cpu
        self.debug = debug
        self.batch_size = batch_size
        self.use_fast = use_fast
        self.latency_mode = latency_mode
        self.warmup = warmup
        self.disable_cache = disable_cache
        self.pin_core = pin_core
        # If True, record only embedding latency in stats (skip tokenize/parse in totals)
        self.measure_encode_only = False
        
        # Batch processing state
        self.packet_buffer = []
        
        # Chunk reassembly state: map sender addr -> { 'total': int, 'chunks': dict(seq->bytes) }
        self._chunk_buffers = {}
        
        # BERT encoder setup
        self.encoder_type = encoder_type
        self.encoder_model = encoder_model
        self.bert_encoder = None
        if encoder_model and encoder_model.lower() not in ("standalone", "none"):
            self.bert_encoder = BERTEncoder(encoder_type or encoder_model, model_name=encoder_model, force_cpu=force_cpu, debug=debug)
        elif encoder_type:
            self.bert_encoder = BERTEncoder(encoder_type, force_cpu=force_cpu, debug=debug)

        # Simple de-duplication by message id (helps when sender duplicates chunks)
        self._dedup_enabled = True
        self._seen_msg_ids: set[int] = set()
        
    def start(self):
        """Initialize the tokenizer and UDP socket"""
        if not HAS_TRANSFORMERS:
            raise RuntimeError("transformers library required for HuggingFace tokenizer pipelines")
        # Optional CPU affinity for fairness with DPDK pinning
        try:
            if self.pin_core is not None and hasattr(os, 'sched_setaffinity'):
                os.sched_setaffinity(0, {int(self.pin_core)})
        except Exception:
            pass
        
        # Lazily load tokenizer once; keep instance across start/stop
        if self.tokenizer is None:
            # Map our internal model names to HuggingFace model names
            hf_model_name = self.model_name
            if self.model_name in ["modernbert-base", "answerdotai/ModernBERT-base"]:
                hf_model_name = "answerdotai/ModernBERT-base"
            elif self.model_name in ["modernbert-large", "answerdotai/ModernBert-large"]:
                hf_model_name = "answerdotai/ModernBERT-large"  # Note: correct HF naming with capital BERT
            elif self.model_name == "diffugpt-m":
                hf_model_name = "diffusionfamily/diffugpt-m"
            # For other models like "intfloat/e5-small", use as-is

            impl = "fast (Rust)" if self.use_fast else "Python"
            print(f"Loading tokenizer: {hf_model_name} [{impl}] (requested: {self.model_name})")
            self.tokenizer = AutoTokenizer.from_pretrained(hf_model_name, use_fast=self.use_fast)

            # Ensure a pad token exists for batch tokenization. GPT-2 and some models lack it.
            try:
                if getattr(self.tokenizer, 'pad_token_id', None) is None:
                    eos_tok = getattr(self.tokenizer, 'eos_token', None)
                    if eos_tok is not None:
                        # Common practice for GPT-2 style tokenizers
                        self.tokenizer.pad_token = eos_tok
                    else:
                        # Fallback: add an explicit [PAD] token for padding in batch ops
                        self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
            except Exception:
                # Non-fatal; batch path will still work for models with built-in pad
                pass

            # Optional warmup for fairness comparisons
            if self.warmup:
                print("Warming up tokenizer...")
                dummy_text = "This is a warmup tokenization to initialize the model."
                dummy_tokenized = self.tokenizer.tokenize(dummy_text)
                dummy_ids = self.tokenizer.convert_tokens_to_ids(dummy_tokenized)
                if self.debug:
                    print(f"Dummy tokenization: {dummy_tokenized}")
                    print(f"Dummy token IDs (first 10 IDs): {dummy_ids[:10]}...")
                print("Tokenizer warmed up successfully")

            # Optionally disable/clear Rust BPE cache inside fast tokenizer
            if self.disable_cache:
                try:
                    backend = getattr(self.tokenizer, 'backend_tokenizer', None)
                    if backend is not None:
                        model = None
                        # Prefer get_model() if available
                        if hasattr(backend, 'get_model'):
                            try:
                                model = backend.get_model()
                            except Exception:
                                model = None
                        # Fallback to .model attribute if exposed
                        if model is None:
                            model = getattr(backend, 'model', None)
                        # Resize to 0 if method exists; else try to clear
                        if model is not None:
                            if hasattr(model, 'resize_cache'):
                                model.resize_cache(0)
                                if hasattr(model, 'clear_cache'):
                                    model.clear_cache()
                                print("Disabled Rust BPE cache (capacity=0)")
                            elif hasattr(model, 'clear_cache'):
                                model.clear_cache()
                                print("Cleared Rust BPE cache")
                except Exception as e:
                    if self.debug:
                        print(f"Warning: could not disable Rust cache: {e}")
        
        # Initialize BERT encoder if specified
        if self.bert_encoder:
            self.bert_encoder.initialize()
        
        # Set up UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 6000))  # Same port as DPDK for comparison
        self.sock.settimeout(5.0)
        mode_label = "Rust" if self.use_fast else "Python"
        print(f"{mode_label} tokenizer pipeline ready on port 6000")
        
    def wait_ready(self, timeout: float = 5.0) -> bool:
        # Ready immediately after start for our Python/Rust pipelines
        return True

    def clear_model_cache(self):
        """Clear underlying tokenizer model cache if available (fast/Rust only)."""
        try:
            backend = getattr(self.tokenizer, 'backend_tokenizer', None)
            if backend is None:
                return
            model = None
            if hasattr(backend, 'get_model'):
                try:
                    model = backend.get_model()
                except Exception:
                    model = None
            if model is None:
                model = getattr(backend, 'model', None)
            if model is not None and hasattr(model, 'clear_cache'):
                model.clear_cache()
        except Exception:
            pass

    def process_packet(self) -> Optional[Dict]:
        """Process a single packet"""
        try:
            # Keep receiving until a complete message is assembled
            start_time = None
            text = None
            while True:
                data, addr = self.sock.recvfrom(65536)
                if start_time is None:
                    start_time = time.perf_counter()
                
                if self.debug:
                    print(f"\n=== DEBUG: Packet Processing Started ===")
                    print(f"Raw packet data length: {len(data)} bytes")
                
                # Extract text from chunked or plain format
                text = self._extract_text(data, addr)
                if text is None:
                    # Incomplete multi-chunk message; continue receiving
                    continue
                if text == "":
                    # Malformed; skip and continue
                    start_time = None
                    continue
                break
                
            extract_time = time.perf_counter()
            
            if self.debug:
                print(f"1. Parse + Extract: '{text}'")
            
            # Tokenize directly to tensors/arrays to avoid Python list of ints.
            # Use GPT-2 (or selected HF) tokenizer with return_tensors='np' to get NumPy arrays.
            tk_out = self.tokenizer(text, add_special_tokens=False, return_tensors="np")
            ids_np = tk_out["input_ids"]  # shape (1, L) int64
            if isinstance(ids_np, list):
                # Fallback if some tokenizers return lists
                ids_np = np.asarray(ids_np, dtype=np.int64)
            # Flatten to 1-D sequence
            ids_1d = ids_np.reshape(-1)

            tokenize_time = time.perf_counter()
            
            if self.debug:
                # For debug prints, reconstruct tokens for preview only
                try:
                    tokens_dbg = self.tokenizer.convert_ids_to_tokens(ids_1d.tolist())
                except Exception:
                    tokens_dbg = []
                print(f"2. Text-to-subwords: {tokens_dbg[:10]}..." if len(tokens_dbg) > 10 else f"2. Text-to-subwords: {tokens_dbg}")
                print(f"3. Subwords-to-IDs: {ids_1d[:10].tolist()}..." if ids_1d.shape[0] > 10 else f"3. Subwords-to-IDs: {ids_1d.tolist()}")
            
            # BERT encoding if enabled
            encode_latency_us = 0
            bert_results = {}
            if self.bert_encoder:
                if self.debug:
                    print(f"4. BERT Encoding Input: Using same token IDs from tokenization step")
                    print(f"   Token IDs to BERT: {ids_1d[:10].tolist()}..." if len(ids_1d) > 10 else f"   Token IDs to BERT: {ids_1d.tolist()}")
                
                if self.bert_encoder.device.type == "cuda":
                    torch.cuda.synchronize()
                encode_start = time.perf_counter()
                # Log actual token count being fed to model
                if self.debug:
                    print(f"   [EMBED] Feeding {len(ids_1d)} tokens to model")
                # Feed NumPy int64 buffer directly (zero-copy into torch)
                embeddings = self.bert_encoder.encode_with_pooling_from_numpy(ids_1d.astype(np.int64, copy=False))
                if self.bert_encoder.device.type == "cuda":
                    torch.cuda.synchronize()
                encode_end = time.perf_counter()
                encode_latency_us = (encode_end - encode_start) * 1_000_000
                # Record encode time and delivery timestamp for accurate E2E measurement
                bert_results = {
                    "BERT_EMBEDDINGS_SHAPE": str(list(embeddings.shape)),
                    "BERT_ENCODE_TIME_US": encode_latency_us,
                    "DELIVERY_TIME": encode_end,
                    # Include actual embedding data for comparison
                    "BERT_EMBEDDING_DATA": embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else embeddings,
                }
                
                if self.debug:
                    print(f"   BERT Output Shape: {list(embeddings.shape)}")
                    print(f"   BERT Sample Values: {embeddings[0, :5].tolist()}")
                
                end_time = encode_end
            else:
                end_time = tokenize_time
            
            # Calculate latency components in microseconds
            total_latency_us = (end_time - start_time) * 1_000_000
            parse_extract_latency_us = (extract_time - start_time) * 1_000_000  # Parse headers + extract text
            tokenize_latency_us = (tokenize_time - extract_time) * 1_000_000   # Pure tokenization time
            
            # For breakdown: assume parse is minimal compared to extract for Python
            parse_latency_us = parse_extract_latency_us * 0.1
            extract_latency_us = parse_extract_latency_us * 0.9
            
            if self.debug:
                print(f"=== DEBUG: Processing Complete ===")
                print(f"Total time: {total_latency_us:.2f} us")
                print(f"Parse: {parse_latency_us:.2f} us, Extract: {extract_latency_us:.2f} us, Tokenize: {tokenize_latency_us:.2f} us" + 
                      (f", Encode: {encode_latency_us:.2f} us" if encode_latency_us > 0 else ""))
            
            if self.measure_encode_only:
                # Only measure embed latency (skip tokenizer/parse)
                self.latency_stats.add(encode_latency_us, 0, 0, 0, encode_latency_us)
            else:
                if self.latency_mode == "tokenize-only":
                    # Record parse/extract components for decomposition even if aggregating alg-only totals
                    alg_total = tokenize_latency_us + encode_latency_us
                    self.latency_stats.add(alg_total, parse_latency_us, extract_latency_us, tokenize_latency_us, encode_latency_us)
                else:
                    self.latency_stats.add(total_latency_us, parse_latency_us, extract_latency_us, tokenize_latency_us, encode_latency_us)
            
            result = {
                "ORIGINAL_TEXT": text,
                "TOKENS": "",  # avoid large string builds; filled only in debug above
                "TOKEN_IDS": " ".join(map(str, ids_1d.tolist())) if self.debug else "",
                "NUM_TOKENS": int(ids_1d.shape[0]),
                "PROCESSING_LATENCY_US": total_latency_us,
                "PARSE_LATENCY_US": parse_latency_us,
                "EXTRACT_LATENCY_US": extract_latency_us,
                "TOKENIZE_LATENCY_US": tokenize_latency_us,
            }
            # When present, include delivery time and message id for E2E measurement
            if 'DELIVERY_TIME' in bert_results:
                result['DELIVERY_TIME'] = bert_results['DELIVERY_TIME']
            # Attempt to parse message id from header by re-reading last packet buffer is complex; rely on _extract_text upgrades below
            
            # Add BERT results if available
            result.update(bert_results)
            # Include message id if known from last extraction
            if hasattr(self, '_last_message_id') and self._last_message_id is not None:
                try:
                    result['MESSAGE_ID'] = int(self._last_message_id)
                except Exception:
                    pass

            # Drop duplicates by message id when enabled (single-chunk messages can be duplicated by sender)
            try:
                if self._dedup_enabled and 'MESSAGE_ID' in result:
                    mid = int(result['MESSAGE_ID'])
                    if mid in self._seen_msg_ids:
                        return None
                    self._seen_msg_ids.add(mid)
            except Exception:
                pass
            
            return result
            
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Error processing packet: {e}")
            return None
            
    def _extract_text(self, data: bytes, addr) -> Optional[str]:
        """Extract or reassemble text from packet data.
        Returns:
          - str: complete decoded text
          - "": malformed/undecodable
          - None: awaiting more chunks
        """
        if len(data) >= 8:
            # Extended header support: TOKN + seq + total + msg_id
            msg_id = None
            if len(data) >= 16 and data[0:4] == b'TOKN':
                seq_num = int.from_bytes(data[4:8], 'big')
                total_chunks = int.from_bytes(data[8:12], 'big')
                msg_id = int.from_bytes(data[12:16], 'big')
                payload = data[16:]
                key = (addr, msg_id)
            else:
                # Legacy header
                seq_num = int.from_bytes(data[0:4], 'big')
                total_chunks = int.from_bytes(data[4:8], 'big')
                payload = data[8:]
                key = (addr, None)

            if total_chunks <= 1:
                try:
                    text = payload.decode('utf-8').strip()
                    if msg_id is not None:
                        # Attach as side-channel for process_packet
                        try:
                            self._last_message_id = int(msg_id)
                        except Exception:
                            pass
                    return text
                except UnicodeDecodeError:
                    return ""

            # Multi-chunk: reassemble per sender addr
            buf = self._chunk_buffers.get(key)
            if not buf or buf.get('total') != total_chunks:
                buf = {'total': total_chunks, 'chunks': {}}
                self._chunk_buffers[key] = buf
            buf['chunks'][seq_num] = payload
            # If complete, assemble in order
            if len(buf['chunks']) >= total_chunks:
                ordered = [buf['chunks'][i] for i in range(total_chunks) if i in buf['chunks']]
                self._chunk_buffers.pop(key, None)
                try:
                    text = b"".join(ordered).decode('utf-8').strip()
                    if msg_id is not None:
                        try:
                            self._last_message_id = int(msg_id)
                        except Exception:
                            pass
                    return text
                except UnicodeDecodeError:
                    return ""
            return None
        # Plain text
        try:
            return data.decode('utf-8').strip()
        except UnicodeDecodeError:
            return ""
    
    def process_batch_packets(self, timeout: float = 5.0) -> List[Dict]:
        """
        Process a batch of packets efficiently
        
        Args:
            timeout: Timeout in seconds to collect batch
            
        Returns:
            List[Dict]: List of processing results (up to batch_size)
        """
        batch_results = []
        batch_timeout = timeout / self.batch_size  # Distribute timeout across batch collection
        start_collection = time.perf_counter()
        
        # Collect packets into batch
        packets_data = []  # list of (text, arrival_time, message_id)
        for _ in range(self.batch_size):
            try:
                data, addr = self.sock.recvfrom(65536)
                arrival_time = time.perf_counter()
                text = self._extract_text(data, addr)
                if text is None:
                    # need more chunks; continue collecting within timeout window
                    continue
                if text:
                    # Capture last parsed message id if available
                    msg_id = getattr(self, '_last_message_id', None)
                    packets_data.append((text, arrival_time, msg_id))
                    
                # Check if we've spent too much time collecting
                if time.perf_counter() - start_collection > timeout:
                    break
                    
            except socket.timeout:
                break
                
        if not packets_data:
            return []
        
        # Process tokenization in batch
        texts = [item[0] for item in packets_data]
        arrival_times = [item[1] for item in packets_data]
        message_ids = [item[2] for item in packets_data]
        
        # Batch tokenization
        tokenize_start = time.perf_counter()
        
        # Note: HuggingFace tokenizers can process batches efficiently
        # WARNING: padding=True pads all sequences to max length in batch!
        batch_tokens = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        all_tokens = []
        all_token_ids = []

        if self.debug:
            padded_shape = batch_tokens['input_ids'].shape
            print(f"   [BATCH PADDING] Batch shape after padding: {padded_shape} (batch_size={padded_shape[0]}, padded_len={padded_shape[1]})")

        for i in range(len(texts)):
            # Extract tokens for each text in the batch
            input_ids = batch_tokens['input_ids'][i]
            tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
            # Filter out padding tokens
            tokens = [token for token in tokens if token not in ['[PAD]', '<pad>', '[CLS]', '[SEP]']]
            token_ids = [id.item() for id in input_ids if id.item() not in [self.tokenizer.pad_token_id, self.tokenizer.cls_token_id, self.tokenizer.sep_token_id] if self.tokenizer.pad_token_id is not None]
            
            all_tokens.append(tokens)
            all_token_ids.append(token_ids)
        
        tokenize_end = time.perf_counter()
        tokenize_duration = tokenize_end - tokenize_start
        
        # Batch BERT encoding if enabled
        bert_results = {}
        encode_duration = 0
        if self.bert_encoder:
            if self.bert_encoder.device.type == "cuda":
                torch.cuda.synchronize()
            encode_start = time.perf_counter()
            # Convert texts to token IDs using BERT encoder's tokenizer
            bert_token_ids_list = []
            for text in texts:
                bert_token_ids = self.bert_encoder.tokenizer.encode(text, add_special_tokens=True, truncation=True, max_length=512)
                bert_token_ids_list.append(bert_token_ids)
            batch_embeddings = self.bert_encoder.encode_batch_with_pooling(bert_token_ids_list)
            if self.bert_encoder.device.type == "cuda":
                torch.cuda.synchronize()
            encode_end = time.perf_counter()
            encode_duration = encode_end - encode_start
            
            bert_results = {
                "BERT_EMBEDDINGS_SHAPE": str(list(batch_embeddings.shape)),
                "BERT_BATCH_SIZE": len(texts),
                "BERT_TOTAL_ENCODE_TIME_US": encode_duration * 1_000_000,
            }
            
            end_time = encode_end
        else:
            end_time = tokenize_end
        
        # Build results for each packet
        # For batch processing, we need to distribute the batch latency fairly across packets
        batch_size = len(texts)
        for i, (text, arrival_time, msg_id) in enumerate(zip(texts, arrival_times, message_ids)):
            # For batch mode, we only care about actual processing time (tokenization + encoding)
            # We exclude parse/extract time as it includes packet queueing overhead
            
            # Calculate per-packet share of batch processing time
            per_packet_tokenize_us = (tokenize_duration / batch_size) * 1_000_000
            per_packet_encode_us = (encode_duration / batch_size) * 1_000_000 if encode_duration > 0 else 0
            
            # For batch mode: choose whether to include tokenize in totals
            if self.measure_encode_only:
                total_latency_us = per_packet_encode_us
                self.latency_stats.add(total_latency_us, 0, 0, 0, per_packet_encode_us)
            else:
                total_latency_us = per_packet_tokenize_us + per_packet_encode_us
                # Add to stats (with 0 for parse/extract in batch mode)
                self.latency_stats.add(total_latency_us, 0, 0, per_packet_tokenize_us, per_packet_encode_us)
            
            result = {
                "ORIGINAL_TEXT": text,
                "TOKENS": " ".join(all_tokens[i]),
                "TOKEN_IDS": " ".join(map(str, all_token_ids[i])),
                "NUM_TOKENS": len(all_tokens[i]),
                "PROCESSING_LATENCY_US": total_latency_us,
                "TOKENIZE_LATENCY_US": per_packet_tokenize_us,
                "BATCH_SIZE": len(texts),
                "BATCH_POSITION": i,
            }
            # Include message id for E2E pairing when available
            if msg_id is not None:
                try:
                    result["MESSAGE_ID"] = int(msg_id)
                except Exception:
                    pass
            
            # Add BERT results if available (per-item)
            if bert_results:
                individual_bert_results = bert_results.copy()
                individual_bert_results["BERT_ENCODE_TIME_US"] = per_packet_encode_us
                individual_bert_results["DELIVERY_TIME"] = end_time
                if i == 0:  # Only include shape info for first item to avoid repetition
                    individual_bert_results["BERT_EMBEDDINGS_SHAPE"] = str(list(batch_embeddings[i:i+1].shape))
                # Include actual embedding data for comparison
                individual_bert_results["BERT_EMBEDDING_DATA"] = batch_embeddings[i:i+1].cpu().numpy() if hasattr(batch_embeddings, 'cpu') else batch_embeddings[i:i+1]
                result.update(individual_bert_results)
            
            batch_results.append(result)
        
        return batch_results
            
    def stop(self):
        """Stop the pipeline"""
        if self.sock:
            self.sock.close()

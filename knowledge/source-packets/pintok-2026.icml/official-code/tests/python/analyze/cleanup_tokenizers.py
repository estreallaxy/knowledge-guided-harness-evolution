#!/usr/bin/env python3
"""
Cleanup script to kill any hanging tokenizer processes.
This prevents "Address already in use" errors on port 6000.
"""

import subprocess
import sys
import os
import signal

def find_tokenizer_processes():
    """Find all tokenizer processes listening on port 6000 or running tokenizer executables."""
    processes = []
    
    # Check for processes on port 6000
    try:
        result = subprocess.run(['ss', '-tulnp'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if ':6000' in line:
                # Extract process info
                if 'users:' in line:
                    # Parse format: users:(("tokenizer_simpl",pid=22547,fd=3))
                    import re
                    match = re.search(r'pid=(\d+)', line)
                    if match:
                        pid = int(match.group(1))
                        processes.append(pid)
    except Exception as e:
        print(f"Warning: Could not check port 6000: {e}")
    
    # Also check for any running tokenizer processes by name
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'tokenizer_' in line and 'python' not in line and 'cleanup' not in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = int(parts[1])
                    if pid not in processes:
                        processes.append(pid)
    except Exception as e:
        print(f"Warning: Could not check running processes: {e}")
    
    return processes

def kill_processes(pids, force=False):
    """Kill the given process IDs."""
    if not pids:
        return
    
    signal_type = signal.SIGKILL if force else signal.SIGTERM
    signal_name = "SIGKILL" if force else "SIGTERM"
    
    for pid in pids:
        try:
            os.kill(pid, signal_type)
            print(f"Sent {signal_name} to process {pid}")
        except ProcessLookupError:
            # Process already dead
            pass
        except PermissionError:
            print(f"Permission denied to kill process {pid} (may need sudo)")
        except Exception as e:
            print(f"Error killing process {pid}: {e}")

def main():
    """Main cleanup function."""
    import argparse
    parser = argparse.ArgumentParser(description="Cleanup hanging tokenizer processes")
    parser.add_argument('--force', action='store_true', help='Use SIGKILL instead of SIGTERM')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    args = parser.parse_args()
    
    if not args.quiet:
        print("Checking for hanging tokenizer processes...")
    
    pids = find_tokenizer_processes()
    
    if pids:
        if not args.quiet:
            print(f"Found {len(pids)} tokenizer process(es): {pids}")
        kill_processes(pids, force=args.force)
        if not args.quiet:
            print("Cleanup complete.")
    else:
        if not args.quiet:
            print("No hanging tokenizer processes found.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
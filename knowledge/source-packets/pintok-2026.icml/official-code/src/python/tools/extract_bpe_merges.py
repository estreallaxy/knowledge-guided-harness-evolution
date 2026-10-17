#!/usr/bin/env python3
"""
Extract BPE merges from HuggingFace tokenizer.json files
and convert them to simple text format for DPDK BPE tokenizer.
"""

import json
import sys
import os

def extract_bpe_merges(tokenizer_json_path, output_path):
    """Extract BPE merges from tokenizer.json and save as simple text format."""
    
    if not os.path.exists(tokenizer_json_path):
        print(f"Error: Tokenizer file not found: {tokenizer_json_path}")
        return False
    
    try:
        with open(tokenizer_json_path, 'r', encoding='utf-8') as f:
            tokenizer_data = json.load(f)
    except Exception as e:
        print(f"Error reading tokenizer file: {e}")
        return False
    
    # Check if this is a BPE model
    model = tokenizer_data.get('model', {})
    if model.get('type') != 'BPE':
        print(f"Error: Tokenizer is not BPE type, found: {model.get('type')}")
        return False
    
    # Extract merges
    merges = model.get('merges', [])
    if not merges:
        print("Error: No merges found in tokenizer")
        return False
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write merges in simple format: first_token second_token priority
    # Priority is determined by position in the list (earlier = higher priority)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# BPE Merge Rules extracted from tokenizer.json\n")
            f.write("# Format: first_token second_token priority\n")
            f.write("# Higher priority values are applied first\n\n")
            
            for i, merge in enumerate(merges):
                # Split merge on space (BPE format is "token1 token2")
                parts = merge.split(' ', 1)
                if len(parts) == 2:
                    first_token, second_token = parts
                    # Higher priority for earlier merges (reverse index)
                    priority = len(merges) - i
                    f.write(f"{first_token} {second_token} {priority}\n")
                else:
                    print(f"Warning: Skipping malformed merge: {merge}")
        
        print(f"Successfully extracted {len(merges)} BPE merges to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_bpe_merges.py <tokenizer.json> [output_file]")
        print("\nExamples:")
        print("  python3 extract_bpe_merges.py tokenizer_data/answerdotai/ModernBERT-base/tokenizer.json")
        print("  python3 extract_bpe_merges.py tokenizer_data/intfloat/e5-small/tokenizer.json bpe_merges_e5.txt")
        sys.exit(1)
    
    tokenizer_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        # Default output path based on input
        base_name = os.path.splitext(os.path.basename(tokenizer_path))[0]
        output_path = f"src/dpdk/tokenizer/json/{base_name}_merges.txt"
    
    success = extract_bpe_merges(tokenizer_path, output_path)
    
    if success:
        print(f"\nBPE merges extracted successfully!")
        print(f"You can now use this file with the DPDK BPE tokenizer:")
        print(f"  ./build/src/dpdk/tokenizer/tokenizer_dpdk_bpe_vm {output_path}")
    else:
        print("Failed to extract BPE merges")
        sys.exit(1)

if __name__ == "__main__":
    main()

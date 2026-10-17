#!/usr/bin/env python3
"""
Extract BPE merge rules from all available tokenizer models
"""

import json
import os
import sys

def extract_bpe_merges_from_tokenizer(tokenizer_path: str, output_path: str):
    """Extract BPE merges from a tokenizer.json file"""
    
    with open(tokenizer_path, 'r') as f:
        tokenizer_data = json.load(f)
    
    # Check if this is a BPE tokenizer
    if tokenizer_data.get("model", {}).get("type") != "BPE":
        print(f"Warning: {tokenizer_path} is not a BPE tokenizer (type: {tokenizer_data.get('model', {}).get('type')})")
        return False
    
    # Extract merge rules
    merges = tokenizer_data["model"]["merges"]
    print(f"Found {len(merges)} merge rules in {tokenizer_path}")
    
    # Write to output file in DPDK-compatible format
    with open(output_path, 'w') as f:
        f.write("# BPE Merge Rules extracted from tokenizer.json\n")
        f.write("# Format: first_token second_token priority\n")
        f.write("# Higher priority values are applied first\n\n")
        
        # Write merges in reverse order (highest priority first)
        priority = len(merges)
        for merge in merges:
            # Each merge is a string like "Ġ t" - split into tokens
            tokens = merge.split()
            if len(tokens) == 2:
                f.write(f"{tokens[0]} {tokens[1]} {priority}\n")
                priority -= 1
            else:
                print(f"Warning: Invalid merge format: {merge}")
    
    print(f"Extracted {len(merges)} merge rules to {output_path}")
    return True

def main():
    # Define available models
    models = [
        {
            "name": "ModernBERT-base",
            "path": "DPDKTokenizer/tokenizer_data/answerdotai/ModernBERT-base/tokenizer.json",
            "output": "DPDKTokenizer/src/dpdk/tokenizer/json/modernbert_base_merges.txt"
        },
        {
            "name": "ModernBert-large", 
            "path": "DPDKTokenizer/tokenizer_data/answerdotai/ModernBert-large/tokenizer.json",
            "output": "DPDKTokenizer/src/dpdk/tokenizer/json/modernbert_large_merges.txt"
        },
        {
            "name": "e5-small",
            "path": "DPDKTokenizer/tokenizer_data/intfloat/e5-small/tokenizer.json", 
            "output": "DPDKTokenizer/src/dpdk/tokenizer/json/e5_small_merges.txt"
        }
    ]
    
    success_count = 0
    for model in models:
        print(f"\n=== Processing {model['name']} ===")
        
        if not os.path.exists(model["path"]):
            print(f"Error: Tokenizer file not found: {model['path']}")
            continue
            
        # Create output directory if needed
        os.makedirs(os.path.dirname(model["output"]), exist_ok=True)
        
        if extract_bpe_merges_from_tokenizer(model["path"], model["output"]):
            success_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Successfully processed {success_count}/{len(models)} models")
    
    # Update the default merge file to point to ModernBERT-base
    default_path = "DPDKTokenizer/src/dpdk/tokenizer/json/tokenizer_merges.txt"
    modernbert_base_path = "DPDKTokenizer/src/dpdk/tokenizer/json/modernbert_base_merges.txt"
    
    if os.path.exists(modernbert_base_path):
        print(f"Updating default merge file to use ModernBERT-base...")
        os.system(f"cp {modernbert_base_path} {default_path}")

if __name__ == "__main__":
    main()

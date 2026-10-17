#!/usr/bin/env python3
"""
Extract complete vocabulary from HuggingFace tokenizer.json files
Creates DPDK-compatible vocabulary files with O(1) lookup support
"""

import json
import os
import sys
from pathlib import Path

def extract_vocabulary_from_tokenizer(tokenizer_json_path, output_dir):
    """Extract complete vocabulary from tokenizer.json"""
    
    print(f"Loading tokenizer from: {tokenizer_json_path}")
    
    with open(tokenizer_json_path, 'r', encoding='utf-8') as f:
        tokenizer_data = json.load(f)
    
    # Extract vocabulary
    if 'model' not in tokenizer_data or 'vocab' not in tokenizer_data['model']:
        raise ValueError("Invalid tokenizer.json format - missing model.vocab")
    
    vocab = tokenizer_data['model']['vocab']
    vocab_size = len(vocab)
    
    print(f"Found vocabulary with {vocab_size} tokens")
    
    # Sort by token ID for consistency
    sorted_vocab = sorted(vocab.items(), key=lambda x: x[1])
    
    # Create output files
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Token-to-ID mapping (for DPDK hash table)
    token_to_id_file = os.path.join(output_dir, "vocab_token_to_id.txt")
    with open(token_to_id_file, 'w', encoding='utf-8') as f:
        f.write("# DPDK Vocabulary: Token to ID mapping\n")
        f.write(f"# Format: token token_id\n")
        f.write(f"# Vocabulary size: {vocab_size}\n")
        f.write("\n")
        
        for token, token_id in sorted_vocab:
            # Escape special characters for safe parsing
            escaped_token = token.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t').replace(' ', 'Ġ')
            f.write(f"{escaped_token} {token_id}\n")
    
    # 2. ID-to-Token mapping (for decoding)
    id_to_token_file = os.path.join(output_dir, "vocab_id_to_token.txt")
    with open(id_to_token_file, 'w', encoding='utf-8') as f:
        f.write("# DPDK Vocabulary: ID to Token mapping\n")
        f.write(f"# Format: token_id token\n")
        f.write(f"# Vocabulary size: {vocab_size}\n")
        f.write("\n")
        
        for token, token_id in sorted_vocab:
            escaped_token = token.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t').replace(' ', 'Ġ')
            f.write(f"{token_id} {escaped_token}\n")
    
    # 3. Statistics and analysis
    stats_file = os.path.join(output_dir, "vocab_stats.txt")
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"Vocabulary Statistics\n")
        f.write(f"====================\n")
        f.write(f"Total tokens: {vocab_size}\n")
        f.write(f"Token ID range: 0 to {max(vocab.values())}\n")
        f.write(f"Average token length: {sum(len(token) for token in vocab.keys()) / vocab_size:.2f}\n")
        f.write(f"Max token length: {max(len(token) for token in vocab.keys())}\n")
        f.write(f"Min token length: {min(len(token) for token in vocab.keys())}\n")
        f.write(f"\n")
        
        # Case analysis
        lowercase_count = sum(1 for token in vocab.keys() if token.islower() and token.isalpha())
        uppercase_count = sum(1 for token in vocab.keys() if token[0].isupper() and token.isalpha())
        mixed_case_count = sum(1 for token in vocab.keys() if any(c.isupper() for c in token) and any(c.islower() for c in token))
        
        f.write(f"Case Distribution:\n")
        f.write(f"  Lowercase tokens: {lowercase_count}\n")
        f.write(f"  Uppercase-start tokens: {uppercase_count}\n")
        f.write(f"  Mixed-case tokens: {mixed_case_count}\n")
        f.write(f"\n")
        
        # Sample tokens
        f.write(f"Sample tokens:\n")
        for i, (token, token_id) in enumerate(sorted_vocab[:20]):
            f.write(f"  {token_id:5d}: '{token}'\n")
        f.write(f"  ...\n")
        for i, (token, token_id) in enumerate(sorted_vocab[-10:]):
            f.write(f"  {token_id:5d}: '{token}'\n")
    
    print(f"Vocabulary extracted successfully:")
    print(f"  Token→ID mapping: {token_to_id_file}")
    print(f"  ID→Token mapping: {id_to_token_file}")
    print(f"  Statistics: {stats_file}")
    
    return vocab_size

def extract_all_model_vocabularies():
    """Extract vocabularies for all supported models"""
    
    models = {
        "modernbert-base": "tokenizer_data/answerdotai/ModernBERT-base/tokenizer.json",
        "modernbert-large": "tokenizer_data/answerdotai/ModernBert-large/tokenizer.json",
        "e5-small": "tokenizer_data/intfloat/e5-small/tokenizer.json"
    }
    
    base_dir = Path("src/dpdk/tokenizer/json")
    
    for model_name, tokenizer_path in models.items():
        print(f"\n=== Processing {model_name} ===")
        
        tokenizer_file = Path(tokenizer_path)
        vocab_dir = base_dir / f"{model_name}_vocab"
        
        if not tokenizer_file.exists():
            print(f"Skipping {model_name} - tokenizer file not found: {tokenizer_file}")
            continue
        
        try:
            vocab_size = extract_vocabulary_from_tokenizer(tokenizer_file, vocab_dir)
            print(f"{model_name}: {vocab_size} tokens extracted")
        except Exception as e:
            print(f"{model_name}: Failed - {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Extract from specific file
        tokenizer_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "vocab_output"
        extract_vocabulary_from_tokenizer(tokenizer_file, output_dir)
    else:
        # Extract all models
        extract_all_model_vocabularies()

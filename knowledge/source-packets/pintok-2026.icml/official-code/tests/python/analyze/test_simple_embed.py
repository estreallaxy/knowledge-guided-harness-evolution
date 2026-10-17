#!/usr/bin/env python3
"""
Test Model Tokenizer and Embedding

This script demonstrates how to use a model for both
tokenization and embedding generation, with performance benchmarking.

Usage:
    python test_simple_embed.py --text "Your text here"
    python test_simple_embed.py --benchmark
    python test_simple_embed.py --batch-test
"""

import argparse
import time
import statistics
from typing import List, Dict
import numpy as np

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    print("Error: Missing dependencies. Install with:")
    print("pip install transformers torch sentence-transformers")

class TestProcessor:
    """Test model processor for tokenization and embeddings"""
    
    def __init__(self, model_name: str = "intfloat/e5-small"):
        if not HAS_DEPENDENCIES:
            raise RuntimeError("Required dependencies not installed")
            
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self, warmup: bool = True):
        """Load tokenizer and model"""
        print(f"Loading {self.model_name}...")
        print(f"Using device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Load model
        self.model = AutoModel.from_pretrained(self.model_name)
        self.model.half()  # Use half precision for faster inference
        self.model.to(self.device)
        self.model.eval()
        
        if warmup:
            print("Warming up model...")
            self._warmup()
            
        print("Model loaded successfully!")
        
    def _warmup(self):
        """Warm up the model with dummy input"""
        dummy_texts = [
            "This is a warmup sentence.",
            "Another warmup text for model initialization."
        ]
        
        with torch.no_grad():
            for text in dummy_texts:
                # Add query prefix as recommended for E5 models
                if self.model_name.startswith("intfloat/e5"):
                    prefixed_text = f"query: {text}"
                else:
                    prefixed_text = text
                inputs = self.tokenizer(prefixed_text, return_tensors="pt", 
                                      padding=True, truncation=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                _ = self.model(**inputs)
                
    def tokenize_text(self, text: str, add_prefix: bool = True) -> Dict:
        """Tokenize text and return detailed token information"""
        if not self.tokenizer:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        # E5 models benefit from query/passage prefixes
        if add_prefix and not text.startswith(("query:", "passage:")):
            prefixed_text = f"query: {text}"
        else:
            prefixed_text = text
            
        start_time = time.perf_counter()
        
        # Tokenize
        tokens = self.tokenizer.tokenize(prefixed_text)
        token_ids = self.tokenizer.convert_tokens_to_ids(tokens)
        
        # Also get the full encoding for completeness
        encoding = self.tokenizer(prefixed_text, return_tensors="pt", 
                                 padding=True, truncation=True, max_length=512)
        
        end_time = time.perf_counter()
        
        return {
            "original_text": text,
            "prefixed_text": prefixed_text,
            "tokens": tokens,
            "token_ids": token_ids,
            "num_tokens": len(tokens),
            "input_ids": encoding["input_ids"].squeeze().tolist(),
            "attention_mask": encoding["attention_mask"].squeeze().tolist(),
            "tokenization_time_us": (end_time - start_time) * 1000000,
        }
        
    def get_embeddings(self, text: str, add_prefix: bool = True) -> Dict:
        """Get embeddings for text"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        # E5 models benefit from query/passage prefixes
        if add_prefix and not text.startswith(("query:", "passage:")):
            prefixed_text = f"query: {text}"
        else:
            prefixed_text = text
            
        start_time = time.perf_counter()
        
        # Tokenize and prepare inputs
        inputs = self.tokenizer(prefixed_text, return_tensors="pt", 
                               padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        tokenize_time = time.perf_counter()
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            
            # E5 models use mean pooling for sentence embeddings
            embeddings = self._mean_pooling(outputs.last_hidden_state, inputs['attention_mask'])
            
            # Normalize embeddings (recommended for E5 models)
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            
        embed_time = time.perf_counter()
        
        return {
            "original_text": text,
            "prefixed_text": prefixed_text,
            "embeddings": embeddings.cpu().numpy(),
            "embedding_dim": embeddings.shape[1],
            "tokenization_time_us": (tokenize_time - start_time) * 1000000,
            "embedding_time_us": (embed_time - tokenize_time) * 1000000,
            "total_time_us": (embed_time - start_time) * 1000000,
        }
        
    def _mean_pooling(self, token_embeddings, attention_mask):
        """Mean pooling for sentence embeddings"""
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        
    def batch_process(self, texts: List[str], add_prefix: bool = True) -> Dict:
        """Process multiple texts efficiently"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        # Add prefixes if needed
        if add_prefix:
            prefixed_texts = [f"query: {text}" if not text.startswith(("query:", "passage:")) else text 
                             for text in texts]
        else:
            prefixed_texts = texts
            
        start_time = time.perf_counter()
        
        # Batch tokenization
        inputs = self.tokenizer(prefixed_texts, return_tensors="pt", 
                               padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        tokenize_time = time.perf_counter()
        
        # Batch embedding generation
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = self._mean_pooling(outputs.last_hidden_state, inputs['attention_mask'])
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            
        embed_time = time.perf_counter()
        
        return {
            "texts": texts,
            "prefixed_texts": prefixed_texts,
            "embeddings": embeddings.cpu().numpy(),
            "batch_size": len(texts),
            "embedding_dim": embeddings.shape[1],
            "tokenization_time_us": (tokenize_time - start_time) * 1000000,
            "embedding_time_us": (embed_time - tokenize_time) * 1000000,
            "total_time_us": (embed_time - start_time) * 1000000,
            "avg_time_per_text_us": ((embed_time - start_time) * 1000000) / len(texts),
        }

def run_single_example(processor: TestProcessor, text: str):
    """Run tokenization and embedding for a single text"""
    print(f"\n{'='*60}")
    print(f"Processing: '{text}'")
    print(f"{'='*60}")
    
    # Tokenization
    print("\nTokenization Results:")
    token_result = processor.tokenize_text(text)
    print(f"  Original text: {token_result['original_text']}")
    print(f"  Prefixed text: {token_result['prefixed_text']}")
    print(f"  Number of tokens: {token_result['num_tokens']}")
    print(f"  Tokens: {token_result['tokens'][:10]}{'...' if len(token_result['tokens']) > 10 else ''}")
    print(f"  Token IDs: {token_result['token_ids'][:10]}{'...' if len(token_result['token_ids']) > 10 else ''}")
    print(f"  Tokenization time: {token_result['tokenization_time_us']:.2f} us")
    
    # Embeddings
    print("\nEmbedding Results:")
    embed_result = processor.get_embeddings(text)
    embeddings = embed_result['embeddings'].squeeze()
    print(f"  Embedding dimension: {embed_result['embedding_dim']}")
    print(f"  Embedding preview: [{embeddings[:5].tolist()}...]")
    print(f"  Embedding norm: {np.linalg.norm(embeddings):.6f}")
    print(f"  Tokenization time: {embed_result['tokenization_time_us']:.2f} us")
    print(f"  Embedding time: {embed_result['embedding_time_us']:.2f} us")
    print(f"  Total time: {embed_result['total_time_us']:.2f} us")

def run_benchmark(processor: TestProcessor, num_runs: int = 100):
    """Run performance benchmark"""
    print(f"\n{'='*60}")
    print(f"Performance Benchmark ({num_runs} runs)")
    print(f"{'='*60}")
    
    test_texts = [
        "What is machine learning?",
        "Natural language processing enables computers to understand human language.",
        "Deep learning models have revolutionized artificial intelligence applications.",
        "Transformer architectures have become the foundation of modern NLP systems.",
        "Efficient tokenization is crucial for high-performance text processing in production environments.",
    ]
    
    tokenization_times = []
    embedding_times = []
    total_times = []
    
    for i in range(num_runs):
        text = test_texts[i % len(test_texts)]
        
        # Tokenization benchmark
        token_result = processor.tokenize_text(text)
        tokenization_times.append(token_result['tokenization_time_us'])
        
        # Embedding benchmark
        embed_result = processor.get_embeddings(text)
        embedding_times.append(embed_result['embedding_time_us'])
        total_times.append(embed_result['total_time_us'])
        
        if (i + 1) % 20 == 0:
            print(f"  Completed {i + 1}/{num_runs} runs...")
    
    # Statistics
    def print_stats(times: List[float], name: str):
        print(f"\n{name} Statistics:")
        print(f"  Mean: {statistics.mean(times):.2f} us")
        print(f"  Median: {statistics.median(times):.2f} us")
        print(f"  Min: {min(times):.2f} us")
        print(f"  Max: {max(times):.2f} us")
        if len(times) > 1:
            print(f"  Std Dev: {statistics.stdev(times):.2f} us")
        if len(times) >= 5:
            print(f"  P95: {statistics.quantiles(times, n=20)[18]:.2f} us")
    
    print_stats(tokenization_times, "Tokenization")
    print_stats(embedding_times, "Embedding Generation")
    print_stats(total_times, "Total Processing")

def run_batch_test(processor: TestProcessor):
    """Test batch processing capabilities"""
    print(f"\n{'='*60}")
    print("Batch Processing Test")
    print(f"{'='*60}")
    max_batch_size = 512

    test_texts = [
        "What is artificial intelligence?",
        "Machine learning enables computers to learn from data.",
        "Natural language processing helps computers understand text.",
        "Deep learning uses neural networks with multiple layers.",
        "Transformers have revolutionized NLP with attention mechanisms.",
        "BERT and GPT are popular transformer-based language models.",
        "Embeddings represent text as dense numerical vectors.",
        "Semantic search uses embeddings to find similar content.",
    ]

    test_texts = test_texts * (max_batch_size // len(test_texts))  # Ensure we have enough texts
    
    # Test different batch sizes
    batch_sizes = map(lambda x: 2 ** x, range(0, max_batch_size.bit_length()))  # Powers of 2 up to max_batch_size
    
    for batch_size in batch_sizes:
        batch_texts = test_texts[:batch_size]
        result = processor.batch_process(batch_texts)
        
        print(f"\nBatch size {batch_size}:")
        print(f"  Total time: {result['total_time_us']:.2f} us")
        print(f"  Avg time per text: {result['avg_time_per_text_us']:.2f} us")
        print(f"  Tokenization time: {result['tokenization_time_us']:.2f} us")
        print(f"  Embedding time: {result['embedding_time_us']:.2f} us")
        print(f"  Embedding shape: {result['embeddings'].shape}")

def main():
    parser = argparse.ArgumentParser(description="E5-Small Model Demo")
    parser.add_argument("--text", type=str, 
                       default="What is natural language processing?",
                       help="Text to process")
    parser.add_argument("--benchmark", action="store_true",
                       help="Run performance benchmark")
    parser.add_argument("--batch-test", action="store_true", 
                       help="Test batch processing")
    parser.add_argument("--no-warmup", action="store_true",
                       help="Skip model warmup")
    
    args = parser.parse_args()
    
    if not HAS_DEPENDENCIES:
        return 1
    
    # Initialize processor
    processor = TestProcessor(model_name="huawei-noah/TinyBERT_General_4L_312D")
    processor.load_model(warmup=not args.no_warmup)
    
    # Run single example
    run_single_example(processor, args.text)
    
    # Run benchmark if requested
    if args.benchmark:
        run_benchmark(processor)
    
    # Run batch test if requested
    if args.batch_test:
        run_batch_test(processor)
    
    return 0

if __name__ == "__main__":
    exit(main())

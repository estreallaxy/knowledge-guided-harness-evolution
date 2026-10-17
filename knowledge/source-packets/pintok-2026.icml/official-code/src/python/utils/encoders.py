"""
BERT encoder implementations for tokenization comparison.
"""

from typing import List
import time

# For the BERT encoding
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    HAS_TRANSFORMERS = True
    HAS_TORCH = True
except ImportError:
    HAS_TRANSFORMERS = False
    HAS_TORCH = False


class BERTEncoder:
    """Generic HF model encoder for embeddings (BERT/ModernBERT/E5/etc.).
    Accepts external token IDs and focuses on latency measurement, not semantics.
    """
    def __init__(self, encoder_type: str = "tinybert", model_name: str = None, force_cpu: bool = False, debug: bool = False):
        self.encoder_type = encoder_type.lower()
        self.model = None
        self.tokenizer = None
        self.device = None
        self.force_cpu = force_cpu
        self.debug = debug
        self.normalize_embeddings = False  # Optional L2-normalization (e.g., EmbeddingGemma doc)
        
        # Map encoder types to model names
        if model_name:
            self.model_name = model_name
        elif self.encoder_type == "tinybert":
            self.model_name = "huawei-noah/TinyBERT_General_4L_312D"
        else:
            # Fallback: treat encoder_type as model name for convenience
            self.model_name = self.encoder_type
        # Follow sentence-transformers guidance for EmbeddingGemma: normalize embeddings
        if isinstance(self.model_name, str) and 'embeddinggemma' in self.model_name.lower():
            self.normalize_embeddings = True
    
    def initialize(self):
        """Initialize the BERT model and tokenizer"""
        if not HAS_TRANSFORMERS or not HAS_TORCH:
            raise RuntimeError("transformers and torch libraries required for BERT encoding")
        
        # Avoid interactions between torch.compile (dynamo) and FX tracing used in some models (e.g., ModernBERT)
        # Set before model load; also defensively wrap forward below.
        import os as _os
        _os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
        
        if self.debug:
            print(f"Loading BERT encoder: {self.model_name}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16, 
            trust_remote_code=False
        )
        # Disable torch._dynamo on model.forward to prevent runtime errors like
        # "FX to symbolically trace a dynamo-optimized function" with ModernBERT compiled MLPs.
        try:
            import torch._dynamo as _dynamo
            self.model.forward = _dynamo.disable(self.model.forward)
        except Exception:
            pass
        
        # Set device (GPU if available and not forced to CPU, otherwise CPU)
        if torch.cuda.is_available() and not self.force_cpu:
            self.device = torch.device("cuda")
            if self.debug:
                print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device("cpu")
            if self.force_cpu:
                if self.debug:
                    print("Forced to use CPU (--cpu flag)")
            else:
                if self.debug:
                    print("CUDA not available, using CPU")
            
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
        # Get vocab size and max sequence length for bounds checking
        self.vocab_size = int(getattr(self.model.config, 'vocab_size', 30522) or 30522)
        self.max_seq_len = int(getattr(self.model.config, 'max_position_embeddings', 512) or 512)
        if self.debug:
            print(f"BERT model vocab size: {self.vocab_size}")
            print(f"Model max position embeddings: {self.max_seq_len}")
        
        # Warmup with dummy token IDs
        if self.debug:
            print("Warming up BERT encoder...")
        dummy_token_ids = [101, 2023, 2003, 1037, 5010, 6279, 3793, 2005, 14324, 17114, 1012, 102]  # "This is a warmup text for BERT initialization."
        _ = self.encode(dummy_token_ids)
        if self.debug:
            print(f"BERT encoder ({self.encoder_type}) warmed up successfully")
    
    def text_to_token_ids(self, text: str) -> List[int]:
        """
        Convert text to token IDs
        
        Args:
            text: Input text to convert
            
        Returns:
            List[int]: Token IDs for the text
        """
        return self.tokenizer.encode(text, add_special_tokens=True, truncation=True, max_length=512)
    
    def texts_to_token_ids(self, texts: List[str]) -> List[List[int]]:
        """
        Convert multiple texts to token IDs
        
        Args:
            texts: List of input texts to convert
            
        Returns:
            List[List[int]]: List of token ID lists for the texts
        """
        return [self.tokenizer.encode(text, add_special_tokens=True, truncation=True, max_length=512) for text in texts]
    
    def encode(self, token_ids: List[int]):
        """
        Encode token IDs using BERT model
        
        Args:
            token_ids: List of input token IDs to encode
            
        Returns:
            torch.Tensor: BERT embeddings (last hidden state)
        """
        # Clip token IDs to valid range and truncate to model max length
        clipped_token_ids = []
        max_len = max(1, int(self.max_seq_len))
        unk_id = getattr(self.tokenizer, 'unk_token_id', 100) or 100
        for token_id in token_ids[:max_len]:
            if token_id >= self.vocab_size or token_id < 0:
                clipped_token_ids.append(int(unk_id))
            else:
                clipped_token_ids.append(int(token_id))
        
        # Convert token IDs to tensor and add batch dimension
        input_ids = torch.tensor([clipped_token_ids], dtype=torch.long).to(self.device)
        
        # Create attention mask (1 for all tokens since we assume no padding)
        attention_mask = torch.ones_like(input_ids).to(self.device)
        
        # Get BERT embeddings
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            # Return the last hidden state (embeddings)
            return outputs.last_hidden_state
    
    def encode_with_pooling(self, token_ids: List[int], pooling_strategy: str = "mean") -> torch.Tensor:
        """
        Encode token IDs and apply pooling to get sentence-level embeddings
        
        Args:
            token_ids: List of input token IDs to encode
            pooling_strategy: "mean", "cls", or "max" pooling
            
        Returns:
            torch.Tensor: Pooled sentence embeddings
        """
        embeddings = self.encode(token_ids)
        
        if pooling_strategy == "cls":
            out = embeddings[:, 0, :]
        elif pooling_strategy == "mean":
            out = torch.mean(embeddings, dim=1)
        elif pooling_strategy == "max":
            out = torch.max(embeddings, dim=1)[0]
        else:
            raise ValueError(f"Unsupported pooling strategy: {pooling_strategy}")
        if self.normalize_embeddings:
            import torch.nn.functional as F
            out = F.normalize(out, p=2, dim=-1)
        return out

    def encode_with_pooling_from_numpy(self, token_ids_np, pooling_strategy: str = "mean"):
        """Encode token IDs provided as a NumPy int32/64 array without converting to Python list."""
        if not HAS_TORCH:
            raise RuntimeError("torch required for BERT encoding")
        import numpy as np  # Local import in case numpy missing globally
        # Truncate to max sequence length
        max_len = int(self.max_seq_len)
        token_ids_np = token_ids_np[:max_len]
        # Ensure int64 for torch long
        if token_ids_np.dtype != np.int64:
            token_ids_np = token_ids_np.astype(np.int64, copy=False)
        # Clip invalid ids into vocab range
        if self.vocab_size:
            np.clip(token_ids_np, 0, self.vocab_size - 1, out=token_ids_np)
        input_ids = torch.from_numpy(token_ids_np).unsqueeze(0).to(self.device)
        attention_mask = torch.ones_like(input_ids, dtype=torch.long, device=self.device)
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            embeddings = outputs.last_hidden_state
        if pooling_strategy == "cls":
            out = embeddings[:, 0, :]
        elif pooling_strategy == "mean":
            out = torch.mean(embeddings, dim=1)
        elif pooling_strategy == "max":
            out = torch.max(embeddings, dim=1)[0]
        else:
            raise ValueError(f"Unsupported pooling strategy: {pooling_strategy}")
        if self.normalize_embeddings:
            import torch.nn.functional as F
            out = F.normalize(out, p=2, dim=-1)
        return out
    
    def encode_batch(self, token_ids_list: List[List[int]]) -> torch.Tensor:
        """
        Encode a batch of token ID lists using BERT model
        
        Args:
            token_ids_list: List of token ID lists to encode
            
        Returns:
            torch.Tensor: BERT embeddings (last hidden state) for all token sequences
        """
        # Find the maximum sequence length for padding (bounded by model)
        max_length = min(max(len(token_ids) for token_ids in token_ids_list), int(self.max_seq_len))

        # Log padding overhead (potential performance impact)
        if self.debug:
            lengths = [len(token_ids) for token_ids in token_ids_list]
            avg_length = sum(lengths) / len(lengths)
            print(f"[BERT BATCH PADDING] Batch size: {len(token_ids_list)}, Avg tokens: {avg_length:.1f}, Max: {max(lengths)}, Padded to: {max_length}")
            print(f"                     Padding overhead: {max_length - avg_length:.1f} tokens/seq = {(max_length - avg_length) * len(token_ids_list):.0f} total extra tokens")

        # Pad all sequences to the same length and create attention masks
        padded_input_ids = []
        attention_masks = []
        
        for token_ids in token_ids_list:
            # Clip token IDs to valid vocab and truncate per model limit
            clipped_token_ids = []
            unk_id = getattr(self.tokenizer, 'unk_token_id', 100) or 100
            for token_id in token_ids[:max_length]:
                if token_id >= self.vocab_size or token_id < 0:
                    clipped_token_ids.append(int(unk_id))
                else:
                    clipped_token_ids.append(int(token_id))
            
            # Pad with zeros (or pad_token_id if available)
            pad_token_id = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else 0
            padded_ids = clipped_token_ids + [pad_token_id] * (max_length - len(clipped_token_ids))
            
            # Create attention mask (1 for actual tokens, 0 for padding)
            attention_mask = [1] * len(clipped_token_ids) + [0] * (max_length - len(clipped_token_ids))
            
            padded_input_ids.append(padded_ids)
            attention_masks.append(attention_mask)
        
        # Convert to tensors
        input_ids = torch.tensor(padded_input_ids, dtype=torch.long).to(self.device)
        attention_mask = torch.tensor(attention_masks, dtype=torch.long).to(self.device)
        
        # Get BERT embeddings for the batch
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            # Return the last hidden state (embeddings)
            return outputs.last_hidden_state
    
    def encode_batch_with_pooling(self, token_ids_list: List[List[int]], pooling_strategy: str = "mean") -> torch.Tensor:
        """
        Encode a batch of token ID lists and apply pooling to get sentence-level embeddings
        
        Args:
            token_ids_list: List of token ID lists to encode
            pooling_strategy: "mean", "cls", or "max" pooling
            
        Returns:
            torch.Tensor: Pooled sentence embeddings for all token sequences
        """
        embeddings = self.encode_batch(token_ids_list)
        
        if pooling_strategy == "cls":
            # Use [CLS] token embedding (first token)
            return embeddings[:, 0, :]
        elif pooling_strategy == "mean":
            # Mean pooling over all tokens (considering attention mask for proper averaging)
            # For simplicity, we'll do basic mean pooling here
            # In a more sophisticated implementation, you'd use the attention mask
            return torch.mean(embeddings, dim=1)
        elif pooling_strategy == "max":
            # Max pooling over all tokens
            return torch.max(embeddings, dim=1)[0]
        else:
            raise ValueError(f"Unsupported pooling strategy: {pooling_strategy}")

    def encode_batch_with_pooling_from_numpy_list(self, token_ids_list, pooling_strategy: str = "mean"):
        """Batch encode from a list of NumPy int arrays (int32 or int64)."""
        if not HAS_TORCH:
            raise RuntimeError("torch required for BERT encoding")
        import numpy as np
        # Compute max length and prepare padded arrays
        lengths = [int(x.shape[0]) for x in token_ids_list]
        max_len = min(max(lengths) if lengths else 0, int(self.max_seq_len))
        if max_len == 0:
            raise ValueError("Empty token_ids_list")
        pad_id = self.tokenizer.pad_token_id if self.tokenizer and self.tokenizer.pad_token_id is not None else 0
        batch_size = len(token_ids_list)
        # Build a contiguous int64 numpy array for input ids and mask
        input_ids_np = np.full((batch_size, max_len), pad_id, dtype=np.int64)
        attention_np = np.zeros((batch_size, max_len), dtype=np.int64)
        for i, arr in enumerate(token_ids_list):
            a64 = arr.astype(np.int64, copy=False)
            # Clip to vocab range
            if self.vocab_size:
                np.clip(a64, 0, self.vocab_size - 1, out=a64)
            L = min(a64.shape[0], max_len)
            input_ids_np[i, :L] = a64[:L]
            attention_np[i, :L] = 1
        input_ids = torch.from_numpy(input_ids_np).to(self.device)
        attention_mask = torch.from_numpy(attention_np).to(self.device)
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            embeddings = outputs.last_hidden_state
        if pooling_strategy == "cls":
            out = embeddings[:, 0, :]
        elif pooling_strategy == "mean":
            # Use attention mask to average non-padding tokens
            mask = attention_mask.unsqueeze(-1).float()
            summed = (embeddings * mask).sum(dim=1)
            counts = mask.sum(dim=1).clamp(min=1.0)
            out = summed / counts
        elif pooling_strategy == "max":
            mask = attention_mask.unsqueeze(-1).bool()
            # Replace pad positions with very negative value so they don't affect max
            masked = embeddings.masked_fill(~mask, -1e9)
            out = masked.max(dim=1)[0]
        else:
            raise ValueError(f"Unsupported pooling strategy: {pooling_strategy}")
        if self.normalize_embeddings:
            import torch.nn.functional as F
            out = F.normalize(out, p=2, dim=-1)
        return out

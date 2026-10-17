"""
Mutual information reward computation for response evaluation.

Computes rewards based on:
1. Cosine similarity between input and response (semantic relevance)
2. Conditional log-probability under a causal LM (fluency/relevance)
3. Marginal log-probability of the response (information content)
"""
import math
import os
import torch
import torch.nn.functional as F
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


# ================= Embedding Model Configuration =================
# Set HF_HOME to control where models are cached
# os.environ['HF_HOME'] = "your_cache_dir"

RECOMMENDED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_local_embedder = None


def _get_embedder():
    global _local_embedder
    if _local_embedder is None:
        _local_embedder = load_local_embedder(RECOMMENDED_MODEL)
    return _local_embedder


def load_local_embedder(model_name: str, device: str = "cuda") -> SentenceTransformer:
    """Load a local sentence-transformers embedding model."""
    target_device = device if torch.cuda.is_available() else "cpu"
    print(f"Loading embedding model: {model_name} on device: {target_device}...")
    try:
        embedder = SentenceTransformer(model_name, device=target_device)
        print("Local embedding model loaded successfully.")
        return embedder
    except Exception as e:
        print(f"Failed to load embedding model {model_name}: {e}")
        return None


def _build_ids(tokenizer, text, add_bos=False):
    """Convert text to token IDs, optionally adding BOS token."""
    ids = tokenizer(text, add_special_tokens=False).input_ids
    if add_bos and tokenizer.bos_token_id is not None:
        return [tokenizer.bos_token_id] + ids
    return ids


@torch.no_grad()
def _log_prob_of_suffix(model, tokenizer, input_ids, condition_length, device: str):
    """
    Compute log P(tokens[condition_length:]) where the first condition_length
    tokens are treated as conditioning context (not included in the objective).

    Returns:
        total_logp: float, total log probability of suffix tokens
        avg_logp: float, average log probability per suffix token
        target_len: int, number of suffix tokens
    """
    input_ids = torch.tensor([input_ids], dtype=torch.long, device=device)
    attention_mask = torch.ones_like(input_ids, device=device)

    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    logits = outputs.logits  # [1, L, vocab]

    # Standard causal LM shift: prediction for token t comes from position t-1
    shift_logits = logits[:, :-1, :].contiguous()      # [1, L-1, vocab]
    shift_labels = input_ids[:, 1:].contiguous()        # [1, L-1]

    log_probs = F.log_softmax(shift_logits, dim=-1)     # [1, L-1, vocab]
    token_log_probs = log_probs.gather(
        -1, shift_labels.unsqueeze(-1)
    ).squeeze(-1)                                        # [1, L-1]

    # The k-th position in token_log_probs corresponds to label position j=k+1
    # We want j >= condition_length => k >= condition_length-1
    start_idx = max(condition_length - 1, 0)
    target_log_probs = token_log_probs[:, start_idx:]   # [1, T]

    target_len = target_log_probs.numel()
    if target_len == 0:
        return 0.0, 0.0, 0

    total_logp = target_log_probs.sum().item()
    avg_logp = total_logp / target_len
    return total_logp, avg_logp, target_len


def _calculate_cosine_similarity_local(
    text1: str,
    text2: str,
    embed_model: SentenceTransformer
) -> float:
    """Compute cosine similarity between two texts using a local embedding model."""
    if embed_model is None:
        raise ValueError("Local embedding model is None. Cannot calculate similarity.")

    embeddings = embed_model.encode([text1, text2], convert_to_tensor=True)
    emb1 = embeddings[0].cpu().numpy().reshape(1, -1)
    emb2 = embeddings[1].cpu().numpy().reshape(1, -1)

    similarity = cosine_similarity(emb1, emb2)[0][0]
    return float(similarity)


def mutual_information_reward(
    input_text: str,
    response_text: str,
    model=None,
    tokenizer=None,
    history: list = [],
    device: str = "cuda",
) -> dict:
    """
    Compute mutual information reward with conversation history.

    MI(Context, Response) ≈ [log P(Response | History + Input) - log P(Response)] / Length

    Args:
        input_text: Current user query
        response_text: Model's response
        history: Conversation history, e.g. [{"role": "user", "content": "hi"}, ...]
        model: Causal LM model (optional; falls back to cosine similarity)
        tokenizer: Tokenizer for the model
        device: Device for computation

    Returns:
        dict with mi_score, relevance_score, info_content_score, etc.
    """
    info_alpha = 0.15
    info_beta = 0.1
    embedder = _get_embedder()

    if model is None or tokenizer is None:
        r_score = _calculate_cosine_similarity_local(input_text, response_text, embedder)
        return r_score

    r_score = _calculate_cosine_similarity_local(input_text, response_text, embedder)
    model.eval()

    # 1. Compute conditional probability log P(y | h, x)
    messages_context = history + [{"role": "user", "content": input_text}]
    messages_full = messages_context + [{"role": "assistant", "content": response_text}]

    input_ids_context = tokenizer.apply_chat_template(
        messages_context,
        add_generation_prompt=True,
        tokenize=True
    )
    input_ids_full = tokenizer.apply_chat_template(messages_full, tokenize=True)
    condition_len_xy = len(input_ids_context)

    logp_y_given_hx, avg_logp_y_given_hx, len_y_conditional = _log_prob_of_suffix(
        model, tokenizer, input_ids_full, condition_len_xy, device
    )

    # 2. Compute unconditional probability log P(y)
    input_ids_y_only = tokenizer(response_text, add_special_tokens=False).input_ids
    condition_len_y_only = 0

    logp_y, avg_logp_y, len_y_marginal = _log_prob_of_suffix(
        model, tokenizer, input_ids_y_only, condition_len_y_only, device
    )

    # 3. Compute MI reward
    target_len = len_y_conditional if len_y_conditional > 0 else 1
    relevance_score = avg_logp_y_given_hx
    information_content_score = -avg_logp_y
    mi_score = (logp_y_given_hx - logp_y) / target_len

    r_info = ((1 - info_alpha - info_beta) * mi_score
              + info_alpha * relevance_score
              + info_beta * information_content_score)
    final_r_info = get_constrained_reward(r_info) * 0.3 + r_score * 0.7

    return {
        "mi_score": mi_score,
        "relevance_score": relevance_score,
        "info_content_score": information_content_score,
        "raw_logp_conditional": logp_y_given_hx,
        "raw_logp_marginal": logp_y,
        "length": target_len,
        "r_info": final_r_info,
        "r_score": r_score
    }


def get_constrained_reward(
    raw_score: float,
    baseline: float = 0.1,
    sensitivity: float = 1.0,
    target_min: float = 0,
    target_max: float = 1.0
) -> float:
    """
    Map a raw score to the [target_min, target_max] interval using tanh.

    Args:
        raw_score: Original score (e.g., MI score)
        baseline: Neutral score baseline
        sensitivity: Sensitivity of the mapping (higher = more extreme values)
        target_min: Lower bound of target interval
        target_max: Upper bound of target interval
    """
    scale = (target_max - target_min) / 2.0
    midpoint = (target_max + target_min) / 2.0

    centered_score = raw_score - baseline
    tanh_val = math.tanh(centered_score * sensitivity)

    return scale * tanh_val + midpoint

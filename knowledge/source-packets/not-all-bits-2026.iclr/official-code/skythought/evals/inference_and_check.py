import concurrent.futures
import copy
import json
import logging
import time
import math
import random
import os
# from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable

import numpy as np
import pandas as pd
import ray
from openai import OpenAI
from tqdm import tqdm
from vllm import LLM

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

from skythought.evals.batch import Pipeline, init_engine_from_config
from skythought.evals.batch.env_config import EnvConfig
from skythought.evals.batch.workload import EvalWorkload
from skythought.evals.common.entities import (
    Backend,
    BackendParameters,
    OpenAISamplingParams,
    TransformersSamplingParams,
    RayLLMEngineArgs,
    SamplingParameters,
)
from skythought.evals.models import ModelConfig
from skythought.evals.tasks import (
    ConversationType,
    NUMINATaskHandler,
    TaskHandler,
)
from skythought.evals.util.metrics import pass_at_k
from skythought.evals.util.response import Response, SingleParsedResponse, BudgetResponse
from skythought.evals.util.results import SummaryResults, save_summary
from skythought.evals.util.math_parsing_util import math_equal

from skythought.evals.cache_utils import apply_kv_cache_patch

os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)
module_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RAY_CONFIG_RELATIVE_PATH = "ray_configs/ray_config.yaml"

RESULTS_FILENAME = "results.json"
SUMMARY_FILENAME = "summary.json"


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def load_existing_results(result_file) -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(result_file):
        return {}
    with open(result_file, "r", encoding="utf-8") as f:
        records = json.load(f)
    logger.info(f"Loaded {len(records)} existing results")
    return records


def save_results(
    result_filepath: os.PathLike, id_to_results: Dict[str, Dict[str, Any]]
):
    with open(result_filepath, "w", encoding="utf-8") as f:
        f.write(
            json.dumps(id_to_results, indent=4, cls=NumpyEncoder, ensure_ascii=False)
        )


def fetch_response_openai(
    client: OpenAI,
    model_config: ModelConfig,
    sampling_params: OpenAISamplingParams,
    prompt,
):
    model_name = model_config.name
    # Ensure model_name has been resolved to a string
    assert model_name
    if model_name.startswith("o1") or model_name.startswith("o3"):
        # O1 doesn't support system prompt
        # NOTE: might want to implement this inside handler instead
        for p in prompt:
            p["role"] = "user"
        response = client.chat.completions.create(
            model=model_config.model_id,
            messages=prompt,
            n=sampling_params.n,
            reasoning_effort=sampling_params.reasoning_effort,
            max_completion_tokens=sampling_params.max_tokens,
        )
    else:
        if sampling_params.reasoning_effort:
            raise ValueError("Reasoning effort is only supported for reasoning models")
        response = client.chat.completions.create(
            model=model_config.model_id,
            messages=prompt,
            n=sampling_params.n,
            temperature=sampling_params.temperature,
            frequency_penalty=sampling_params.frequency_penalty,
            max_completion_tokens=sampling_params.max_tokens,
        )
    return response


def fetch_responses_ray(
    conversations,
    backend_args: RayLLMEngineArgs,
    model_config: ModelConfig,
    sampling_params: SamplingParameters,
):
    config = backend_args.get_ray_llm_config()
    config["model_id"] = model_config.model_id

    engine_cfg = init_engine_from_config(config)
    ds = ray.data.from_items([(idx, conv) for idx, conv in enumerate(conversations)])
    num_replicas = config["env_config"].get("num_replicas", 1)
    if ds.count() < config["env_config"].get("batch_size", 1):
        config["env_config"]["batch_size"] = math.ceil(ds.count() / num_replicas)
    if num_replicas > 1 and num_replicas > ds.num_blocks():
        ds = ds.repartition(num_partitions=num_replicas)
    workload = EvalWorkload(
        dataset=ds,
        sampling_params=sampling_params.to_dict(),
    )
    pipeline = Pipeline(
        engine_cfg,
        env_config=EnvConfig(**config["env_config"]),
    )
    ds = pipeline(workload)
    responses = ds.materialize()
    return responses


def _parse_response_for_idx(
    response: Response,
    sample_idx: int,
) -> Tuple[SingleParsedResponse, Dict[str, int]]:
    """
    Works for both Response and BudgetResponse.
    For BudgetResponse we transparently use the LAST-budget view.
    """
    if isinstance(response, BudgetResponse):
        response = response.last_budget_view()

    # -----------------------------------------------------------
    content = response.response[sample_idx].strip()
    response_entry = SingleParsedResponse(content=content)

    token_usage_for_response = {
        "completion_tokens": response.num_completion_tokens[sample_idx],
        "prompt_tokens":     response.num_input_tokens,
    }
    return response_entry, token_usage_for_response


def vllm_chat_with_budget_forcing(
    llm: LLM,
    messages: List[Dict[str, str]],
    min_tokens: int,
    continuation_string: str,
    sampling_params: Any,
    model_config: ModelConfig,
) -> List[Any]:
    """Generate responses with budget forcing for a single batch with parallel processing.
    Continues generation until min_tokens requirement is met for all outputs."""
    
    # Initial generation
    responses = llm.chat(
        messages=messages,
        sampling_params=sampling_params,
        use_tqdm=True,
        # add_generation_prompt=model_config.assistant_prefill is None,
        # continue_final_message=model_config.assistant_prefill is not None,
    )

    if not isinstance(responses, list):
        responses = [responses]
    
    # Create generate_params with n=1 for continuations
    generate_params = copy.deepcopy(sampling_params)
    generate_params.n = 1  # Force single output for continuations
    
    tokenizer = llm.get_tokenizer()
    continuation_token_ids = tokenizer.encode(
        continuation_string, add_special_tokens=False
    )
    im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")

    while True:
        need_continuation = []
        continuation_prompt_token_ids = []

        # Check outputs that need continuation
        for response in responses:
            for output in response.outputs:
                if len(output.token_ids) < min_tokens:
                    need_continuation.append(output)
                    if output.token_ids and output.token_ids[-1] == im_end_id:
                        output.token_ids = list(output.token_ids[:-1])
                        output.token_ids.extend(continuation_token_ids)
                    new_prompt_ids = list(response.prompt_token_ids) + list(output.token_ids)
                    continuation_prompt_token_ids.append(new_prompt_ids)
        
        if not continuation_prompt_token_ids:
            break

        # Generate all continuations in parallel with n=1
        continued_responses = llm.generate(
            prompt_token_ids=continuation_prompt_token_ids,
            sampling_params=generate_params,
            use_tqdm=True
        )

        # Update outputs directly
        for output, cont_response in zip(need_continuation, continued_responses):
            continued_text = cont_response.outputs[0].text
            output.text += continuation_string + continued_text
            current_tokens = list(output.token_ids)
            current_tokens.extend(list(cont_response.outputs[0].token_ids))
            output.token_ids = tuple(current_tokens)
    
    return responses


# def reorder_cache(past_key_values: tuple[tuple[torch.Tensor]], batch_indices: torch.Tensor) -> tuple[tuple[torch.Tensor]]:
#     """
#     Reorders the KV cache tensors along the batch dimension, handling multi-GPU models.
#     Includes an optimization to skip the operation for single-item batches.
#     """
#     # Get the batch size from the first tensor in the cache.
#     batch_size = past_key_values[0][0].shape[0]
    
#     # If the batch size is 1, no reordering is ever needed.
#     if batch_size == 1:
#         return past_key_values

#     reordered_past = []
#     for layer_past in past_key_values:
#         reordered_layer_past = []
#         for state in layer_past:
#             indices_on_correct_device = batch_indices.to(state.device)
#             reordered_state = state.index_select(0, indices_on_correct_device)
#             reordered_layer_past.append(reordered_state)
#         reordered_past.append(tuple(reordered_layer_past))
#     return tuple(reordered_past)


def _sample_token(logits: torch.Tensor, temperature: float, top_p: float):
    """Return token ids (batch,) – greedy if temperature==0."""
    if temperature == 0 or top_p == 0:
        return logits.argmax(-1)
    logits = logits / temperature
    logits = torch.nan_to_num(logits, neginf=-1e30, posinf=1e30)

    probs  = torch.softmax(logits, dim=-1)
    probs = torch.nan_to_num(probs, nan=0.0, posinf=0.0, neginf=0.0)

    if top_p < 1.0:
        sorted_p, sorted_idx = torch.sort(probs, dim=-1, descending=True)
        cum = sorted_p.cumsum(-1)
        mask = cum > top_p
        mask[..., 1:] = mask[..., :-1]
        mask[..., 0] = False
        sorted_p[mask] = 0
        probs = torch.zeros_like(probs).scatter_(-1, sorted_idx, sorted_p)
    
    probs.clamp_(min=0.0)
    row_sum = probs.sum(dim=-1, keepdim=True)
    bad = ~torch.isfinite(row_sum) | (row_sum <= 0)

    if bad.any():
        # one-hot fallback at argmax for bad rows
        idx = logits.argmax(dim=-1)
        probs[bad.expand_as(probs)] = 0.0
        probs.scatter_(-1, idx.unsqueeze(-1), 1.0)

    return torch.multinomial(probs, 1).squeeze(-1)


@torch.no_grad()
def _step_generate_batch(
    model, tokenizer, *,
    start_ids, past, steps, block_prefix,
    wait_token_id, temperature, top_p,
    cache_pos_start: int,
):
    """Vectorised one-token loop (B×1 start_ids) with explicit absolute position_ids."""

    # def _cache_len_L0(cache) -> int:
    #     try:
    #         return int(cache.get_seq_length(0))
    #     except Exception:
    #         # Try direct key cache tensor
    #         try:
    #             kc0 = cache.key_cache[0]
    #             if isinstance(kc0, torch.Tensor):
    #                 return int(kc0.shape[-2])
    #         except Exception:
    #             pass
    #         # Try DynamicCache.layers path
    #         try:
    #             k_res = cache.layers[0].keys
    #             if isinstance(k_res, torch.Tensor) and k_res.ndim >= 3:
    #                 res_len = int(k_res.shape[-2])
    #             else:
    #                 res_len = 0
    #         except Exception:
    #             res_len = 0
    #         # If a quantized processor is attached, include its erased length
    #         try:
    #             proc = getattr(cache, "cache_processor", None)
    #             erased = int(getattr(proc, "erased_length", 0)) if proc is not None else 0
    #         except Exception:
    #             erased = 0
    #         total = res_len + erased
    #         return total if total > 0 else -1


    eos = tokenizer.eos_token_id
    B   = start_ids.size(0)
    done = torch.zeros(B, dtype=torch.bool, device=start_ids.device)
    inp = start_ids
    out = []
    for t in range(steps):

        # abs_pos = cache_pos_start + t
        # before_len = _cache_len_L0(past)

        pos_ids = torch.full((B, 1), cache_pos_start + t, device=inp.device, dtype=torch.long)
        logits = model(
            input_ids=inp,
            past_key_values=past,
            use_cache=True,
            position_ids=pos_ids,
        ).logits[:, -1, :]
        nxt = _sample_token(logits, temperature, top_p)

        # Force progress during the protected “prefix” window
        mask = (t < block_prefix) & nxt.eq(eos)

        # if mask.any():
        #     print(f"[step] t={t} abs_pos={abs_pos} replacing {int(mask.sum().item())}/{B} EOS with wait_id={wait_token_id}")

        nxt[mask] = wait_token_id

        out.append(nxt)
        inp = nxt.unsqueeze(1)

        # after_len = _cache_len_L0(past)
        # # Show a couple tokens for sanity
        # preview = nxt[: min(B, 3)].tolist()
        # print(f"[step] t={t} abs_pos={abs_pos} cache_len(L0): {before_len} -> {after_len} | next[:{min(B,3)}]={preview}")

        done |= nxt.eq(eos) & (t >= block_prefix)
        if done.all():
            break

    return torch.stack(out, 1)


@torch.no_grad()
def _budget_generate_multi_batch(
    *, model, tokenizer, prompt_ids, budgets,
    trigger_text, max_answer_tokens, wait_token,
    temperature, top_p,
    cache_factory: Optional[Callable[[], Any]] = None,
):
    """
    Manual budget-forcing generation compatible with HQQ quantized cache.

    Returns:
        answers   : list[list[str]]
        snapshots : list[list[str]]
        cache     : Cache
        gens      : Tensor
    """
    import copy

    B = prompt_ids.size(0)
    pad_id            = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    wait_id           = tokenizer.encode(wait_token, add_special_tokens=False)[-1]
    assistant_cont_id = tokenizer.encode("\n", add_special_tokens=False)[-1]
    trig_ids          = tokenizer.encode(trigger_text, add_special_tokens=False)
    trig_pt           = torch.tensor(trig_ids, device=model.device).unsqueeze(0)

    # ---- Prefill (left-padding safe: attn→pos) ----------
    prefill_mask = (prompt_ids != pad_id).long()           # (B, L)
    position_ids = prefill_mask.cumsum(-1) - 1             # 0..L_nonpad-1
    position_ids.masked_fill_(prefill_mask.eq(0), 0)

    cache = cache_factory() if cache_factory is not None else DynamicCache()
    _ = model(
        input_ids=prompt_ids,
        attention_mask=prefill_mask,
        position_ids=position_ids,
        use_cache=True,
        past_key_values=cache,
    )

    gens        = prompt_ids.clone()
    prefill_len = prompt_ids.size(1)  # absolute cursor baseline (kept for compatibility)

    seed_ids = prompt_ids[:, -1:].contiguous()

    answers:   list[list[str]] = []
    snapshots: list[list[str]] = []
    generated  = 0
    dummy_wait = torch.full((B, 1), assistant_cont_id, device=model.device)

    for tgt in budgets:
        need = tgt - generated
        if need > 0:
            cursor = prefill_len + generated
            new_tok = _step_generate_batch(
                model, tokenizer,
                start_ids=seed_ids, past=cache,
                steps=need, block_prefix=need,
                wait_token_id=wait_id,
                temperature=temperature, top_p=top_p,
                cache_pos_start=cursor,
            )
            gens = torch.cat([gens, new_tok], 1)
            generated = tgt

            seed_ids = new_tok[:, -1:].contiguous()

        # ---- Work on a cloned cache for answer forcing ----
        ans_cache = cache.clone() if hasattr(cache, "clone") else copy.deepcopy(cache)

        if need > 0:
            commit_pos = torch.full((B, 1), prefill_len + generated, device=model.device, dtype=torch.long)
            _ = model(
                input_ids=seed_ids,        # (B,1) last generated token
                position_ids=commit_pos,   # absolute position right after the run
                past_key_values=ans_cache,
                use_cache=True,
            )

        # ---- Inject trigger prefix one token at a time (HQQ-safe; no custom mask) ---
        trig_prefix_len = max(0, trig_pt.size(1) - 1)
        if trig_prefix_len > 0:
            ans_cursor = prefill_len + generated
            for i in range(trig_prefix_len):
                tok_i = trig_pt[:, i:i+1].repeat(B, 1)  # (B, 1)
                pos_i = torch.full((B, 1), ans_cursor + i, device=model.device, dtype=torch.long)
                _ = model(
                    input_ids=tok_i,
                    position_ids=pos_i,
                    past_key_values=ans_cache,
                    use_cache=True,
                )

        # ---- Decode the answer starting from the last trigger token ----
        last_tok = trig_pt[:, -1:].repeat(B, 1)
        ans_cursor_after_prefix = prefill_len + generated + trig_prefix_len

        ans_tok = _step_generate_batch(
            model, tokenizer,
            start_ids=last_tok, past=ans_cache,
            steps=max_answer_tokens, block_prefix=0,
            wait_token_id=wait_id,
            temperature=temperature, top_p=top_p,
            cache_pos_start=ans_cursor_after_prefix,
        )

        answer_strings = [
            tokenizer.decode(ans_tok[i], skip_special_tokens=True).strip()
            for i in range(B)
        ]
        answers.append(answer_strings)

        snapshots.append([
            tokenizer.decode(gens[i], skip_special_tokens=True) + trigger_text + answer_strings[i]
            for i in range(B)
        ])

    return answers, snapshots, cache, gens


def inference(
    conversations: List[ConversationType],
    backend: Backend,
    backend_params: BackendParameters,
    model_config: ModelConfig,
    sampling_params: SamplingParameters,
    min_tokens: int,
    continuation_string: str,
    output_dir: Optional[Path] = None,
    unique_ids: Optional[List[str]] = None,
    **kwargs,
):
    if backend == Backend.RAY:
        responses = fetch_responses_ray(
            conversations, backend_params.params, model_config, sampling_params
        )
        responses = [
            Response.from_ray_response(response) for response in responses.iter_rows()
        ]
        # NOTE: This deepcopy is needed to avoid a SIGSEV error related to object cleanup with the ray object store and
        # the later use of ProcessPoolExecutor - see here: https://github.com/NovaSky-AI/SkyThought/pull/63#discussion_r1941899714
        # TODO: revisit the underlying issue and remove the deepcopy if possible
        responses = copy.deepcopy(responses)
        responses = sorted(responses, key=lambda x: x.index)
        # Cleanup ray session
        ray.shutdown()
    elif backend == Backend.OPENAI:
        llm = OpenAI(**backend_params.to_dict())
        assert isinstance(sampling_params.params, OpenAISamplingParams)
        fetch_partial = partial(
            fetch_response_openai,
            llm,
            model_config,
            sampling_params.params,
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as e:
            responses = list(e.map(fetch_partial, conversations))

        responses = [Response.from_openai_response(response) for response in responses]
    elif backend == Backend.VLLM:
        batch_size = kwargs.get("batch_size", 1)
        engine_kwargs = copy.deepcopy(backend_params.to_dict())
        engine_kwargs["model"] = model_config.model_id
        llm = LLM(**engine_kwargs)

        responses = []
        for i in range(0, len(conversations), batch_size):
            batch = conversations[i:i + batch_size]
            if min_tokens is not None:
                # Use budget forcing
                response_batch = vllm_chat_with_budget_forcing(
                    llm=llm,
                    messages=batch,
                    min_tokens=min_tokens,
                    continuation_string=continuation_string,
                    sampling_params=sampling_params.params,
                    model_config=model_config,
                )
            else:
                # Use normal generation
                response_batch = llm.chat(
                    messages=batch,
                    sampling_params=sampling_params.params,
                    use_tqdm=True,
                    add_generation_prompt=model_config.assistant_prefill is None,
                    continue_final_message=model_config.assistant_prefill is not None,
                )
                if not isinstance(response_batch, list):
                    response_batch = [response_batch]
                    
            responses.extend(response_batch)
        
        responses = [Response.from_vllm_response(response) for response in responses]
    elif backend == Backend.TRANSFORMERS:
        batch_size = kwargs.get("batch_size", 1)
        backend_args = copy.deepcopy(backend_params.to_dict())
        model_id = model_config.model_id
        model_kwargs = backend_args
        model_kwargs.setdefault("device_map", "auto")

        # normalize dtype strings
        if "torch_dtype" in model_kwargs and isinstance(model_kwargs["torch_dtype"], str):
            s = model_kwargs["torch_dtype"]
            if s == "bfloat16":
                model_kwargs["torch_dtype"] = torch.bfloat16
            elif s in ("float16", "half"):
                model_kwargs["torch_dtype"] = torch.float16
            elif s in ("float32", "full"):
                model_kwargs["torch_dtype"] = torch.float32

        tokenizer = AutoTokenizer.from_pretrained(
            model_id, padding_side='left', **backend_args.get("tokenizer_args", {})
        )
        if not tokenizer.pad_token:
            tokenizer.pad_token = tokenizer.eos_token

        assert isinstance(sampling_params.params, TransformersSamplingParams)
        gen_kwargs = sampling_params.to_dict()

        cache_impl_name = gen_kwargs.get("cache_implementation")
        cache_config    = gen_kwargs.get("cache_config", {})
        cfg = apply_kv_cache_patch(model_id, cache_impl_name, cache_config)

        model = AutoModelForCausalLM.from_pretrained(model_id, config=cfg, **model_kwargs)

        # convert compute_dtype in nested cache_config, if necessary
        if "cache_config" in gen_kwargs and "compute_dtype" in gen_kwargs["cache_config"]:
            s = gen_kwargs["cache_config"]["compute_dtype"]
            if s == "bfloat16":
                gen_kwargs["cache_config"]["compute_dtype"] = torch.bfloat16
            elif s == "float16":
                gen_kwargs["cache_config"]["compute_dtype"] = torch.float16

        n_sequences = gen_kwargs.get("num_return_sequences", 1)

        native_implementations = ["static", "dynamic", "quantized", None]
        if cache_impl_name not in native_implementations:
            gen_kwargs.pop("cache_implementation", None)
            gen_kwargs.pop("cache_config", None)

        # HQQ specifics
        if cache_impl_name == "quantized" and cache_config.get("backend") == "HQQ":
            if batch_size > 1:
                logger.info(
                    f"HQQ-quantized KV cache is enabled and does not support batching. "
                    f"Forcing batch size from {batch_size} to 1."
                )
                batch_size = 1
        elif cache_impl_name == "streamingllm" and batch_size > 1:
            logger.warning("StreamingLLM mixed-length batching not implemented – using batch_size=1")
            batch_size = 1

        budget_opts = {
            "budgets":           gen_kwargs.pop("budgets", None),
            "trigger_text":      gen_kwargs.pop("trigger_text", "**Final Answer**\n\\boxed{"),
            "max_answer_tokens": gen_kwargs.pop("max_answer_tokens", 10),
            "wait_token":        gen_kwargs.pop("wait_token", " Wait"),
            "temperature":       float(gen_kwargs.pop("temperature", 0.0)),
            "top_p":             float(gen_kwargs.pop("top_p", 1.0)),
        }

        plain_gen_kwargs = gen_kwargs.copy()

        # -------------------- KV cache factory (HQQ) --------------------
        def _dtype_from_str(s):
            if isinstance(s, torch.dtype): return s
            if s == "bfloat16":            return torch.bfloat16
            if s in ("float16", "half"):   return torch.float16
            if s in ("float32", "full"):   return torch.float32
            return torch.bfloat16

        compute_dt = _dtype_from_str(cache_config.get("compute_dtype", "bfloat16"))

        def make_kv_cache_and_processor():
            from transformers import DynamicCache
            cache = DynamicCache()
            try:
                from transformers import HQQQuantizedCacheProcessor
                # HF's HQQ processor currently expects backend="quanto"
                proc = HQQQuantizedCacheProcessor(
                    cache=cache,
                    backend="quanto",
                    nbits=cache_config.get("nbits", 8),
                    axis_key=cache_config.get("axis_key", 1),
                    axis_value=cache_config.get("axis_value", 1),
                    q_group_size=cache_config.get("q_group_size", cache_config.get("group_size", 64)),
                    residual_length=cache_config.get("residual_length", 128),
                    compute_dtype=compute_dt,
                    device=str(model.device),
                )
                cache.cache_processor = proc
                return cache
            except Exception:
                try:
                    from transformers import HQQQuantizedCache, QuantizedCacheConfig
                    try:
                        qcfg = QuantizedCacheConfig(
                            nbits=cache_config.get("nbits", 8),
                            axis_key=cache_config.get("axis_key", 1),
                            axis_value=cache_config.get("axis_value", 1),
                            residual_length=cache_config.get("residual_length", 128),
                            q_group_size=cache_config.get("q_group_size", cache_config.get("group_size", 64)),
                            compute_dtype=compute_dt,
                            device=str(model.device),
                        )
                        return HQQQuantizedCache(cache_config=qcfg)
                    except TypeError:
                        return HQQQuantizedCache(
                            nbits=cache_config.get("nbits", 8),
                            axis_key=cache_config.get("axis_key", 1),
                            axis_value=cache_config.get("axis_value", 1),
                            residual_length=cache_config.get("residual_length", 128),
                            compute_dtype=compute_dt,
                            device=str(model.device),
                        )
                except Exception:
                    logger.warning("HQQ cache not available; falling back to DynamicCache.")
                    return cache

        responses = []
        if budget_opts["budgets"] is not None:
            responses_by_budget = {}

        for i in tqdm(range(0, len(conversations), batch_size), desc="Generating with HF Transformers"):
            batch = conversations[i:i + batch_size]
            batch_ids = unique_ids[i : i + batch_size] if unique_ids else None

            prompts = [
                tokenizer.apply_chat_template(conv, tokenize=False, add_generation_prompt=True)
                for conv in batch
            ]
            inputs = tokenizer(prompts, return_tensors="pt", padding=True).to(model.device)
            prompt_lengths = [len(seq) for seq in inputs["input_ids"]]

            with torch.no_grad():
                if budget_opts["budgets"] is not None and cache_impl_name == "quantized" and cache_config.get("backend", "").upper() in ("HQQ", "QUANTO"):
                    # ---- HQQ manual budget forcing path ----
                    prompt_ids = inputs["input_ids"].repeat_interleave(n_sequences, dim=0)

                    answers, snaps_per_budget, _, _ = _budget_generate_multi_batch(
                        model              = model,
                        tokenizer          = tokenizer,
                        prompt_ids         = prompt_ids,
                        budgets            = budget_opts["budgets"],
                        trigger_text       = budget_opts["trigger_text"],
                        max_answer_tokens  = budget_opts["max_answer_tokens"],
                        wait_token         = budget_opts["wait_token"],
                        temperature        = budget_opts["temperature"],
                        top_p              = budget_opts["top_p"],
                        cache_factory      = make_kv_cache_and_processor,
                    )

                    for j in range(len(batch)):
                        prompt_len = prompt_lengths[j]
                        base_idx   = j * n_sequences

                        bud_resps: list[list[str]] = []
                        bud_comps: list[list[int]] = []

                        for b_idx in range(len(budget_opts["budgets"])):
                            seq_texts = snaps_per_budget[b_idx][base_idx : base_idx + n_sequences]
                            bud_resps.append(seq_texts)
                            bud_comps.append([
                                len(tokenizer(t, add_special_tokens=False).input_ids[prompt_len:])
                                for t in seq_texts
                            ])

                        for b_idx, budget in enumerate(budget_opts["budgets"]):
                            resp_obj = Response(
                                response              = bud_resps[b_idx],
                                num_completion_tokens = bud_comps[b_idx],
                                num_input_tokens      = prompt_len,
                            )
                            responses_by_budget.setdefault(budget, []).append(resp_obj)

                        responses.append(  # legacy last-budget view
                            Response(
                                response              = bud_resps[-1],
                                num_completion_tokens = bud_comps[-1],
                                num_input_tokens      = prompt_len,
                            )
                        )
                    continue

                elif budget_opts["budgets"] is not None:
                    # Non-HQQ budget forcing uses the same manual path (Dynamic/Streaming etc.)
                    prompt_ids = inputs["input_ids"].repeat_interleave(n_sequences, dim=0)

                    answers, snaps_per_budget, _, _ = _budget_generate_multi_batch(
                        model              = model,
                        tokenizer          = tokenizer,
                        prompt_ids         = prompt_ids,
                        budgets            = budget_opts["budgets"],
                        trigger_text       = budget_opts["trigger_text"],
                        max_answer_tokens  = budget_opts["max_answer_tokens"],
                        wait_token         = budget_opts["wait_token"],
                        temperature        = budget_opts["temperature"],
                        top_p              = budget_opts["top_p"],
                        cache_factory      = None,  # DynamicCache
                    )

                    for j in range(len(batch)):
                        prompt_len = prompt_lengths[j]
                        base_idx   = j * n_sequences

                        bud_resps: list[list[str]] = []
                        bud_comps: list[list[int]] = []

                        for b_idx in range(len(budget_opts["budgets"])):
                            seq_texts = snaps_per_budget[b_idx][base_idx : base_idx + n_sequences]
                            bud_resps.append(seq_texts)
                            bud_comps.append([
                                len(tokenizer(t, add_special_tokens=False).input_ids[prompt_len:])
                                for t in seq_texts
                            ])

                        for b_idx, budget in enumerate(budget_opts["budgets"]):
                            resp_obj = Response(
                                response              = bud_resps[b_idx],
                                num_completion_tokens = bud_comps[b_idx],
                                num_input_tokens      = prompt_len,
                            )
                            responses_by_budget.setdefault(budget, []).append(resp_obj)

                        responses.append(
                            Response(
                                response              = bud_resps[-1],
                                num_completion_tokens = bud_comps[-1],
                                num_input_tokens      = prompt_len,
                            )
                        )
                    continue
                else:
                    outputs = model.generate(**inputs, **plain_gen_kwargs)

            for j in range(len(batch)):
                start_idx = j * n_sequences
                end_idx = start_idx + n_sequences
                outputs_for_one_prompt = outputs[start_idx:end_idx]
                num_input_tokens = prompt_lengths[j]

                response_texts = []
                num_completion_tokens = []
                for k in range(n_sequences):
                    full_sequence_ids = outputs_for_one_prompt[k]
                    generated_ids = full_sequence_ids[num_input_tokens:]
                    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
                    response_texts.append(generated_text.strip())
                    num_completion_tokens.append(len(generated_ids))

                response_obj = Response.from_transformers_response(
                    response_texts=response_texts,
                    num_completion_tokens=num_completion_tokens,
                    num_input_tokens=num_input_tokens,
                )
                responses.append(response_obj)
        
        if budget_opts["budgets"] is not None:
            return responses, responses_by_budget

    else:
        raise ValueError(f"Invalid backend: {backend}")

    return responses


def generate_responses_for_dataset(
    handler: TaskHandler,
    model_config: ModelConfig,
    backend: Backend,
    backend_params: BackendParameters,
    sampling_params: SamplingParameters,
    min_tokens: int,
    continuation_string: str,
    eval_data: pd.DataFrame,
    id_to_results: Dict[str, Dict[str, Any]],
    output_dir: Path,
    run_config_dict: dict,
    **kwargs,
) -> Tuple[Dict[str, Dict[str, Any]], List[int], List[int]]:
    """Generates responses for the given dataset

    Performs the following:
    1. Filter out the items already in `id_to_results` (if resuming).
    2. Build the input conversations.
    3. Perform inference.
    4. Return a dictionary with new results, as well as token usage statistics
    """
    remaining_data = handler.process_remaining_data(eval_data, id_to_results)
    logger.info(f"Generating results for {len(remaining_data)} problems.")

    if not remaining_data:
        logger.info("No remaining data to generate.")
        return id_to_results, [], []

    # Prepare conversations
    conversations = handler.make_conversations(
        remaining_data,
        str(model_config.system_prompt),
        model_config.user_template,
        model_config.assistant_prefill,
    )

    if not conversations:
        logger.info("No conversations to generate.")
        return id_to_results, [], []
    
    unique_ids = [rd["_index"] for rd in remaining_data]

    # Perform inference
    responses_tuple = inference(
        conversations, backend, backend_params, model_config, sampling_params, min_tokens, continuation_string, output_dir, unique_ids, **kwargs
    )

    if isinstance(responses_tuple, tuple):
        responses, responses_by_budget = responses_tuple
    else:
        responses, responses_by_budget = responses_tuple, None

    all_prompt_tokens = []
    all_completion_tokens = []

    for idx, response in enumerate(responses):
        # For each problem, we store N responses
        response_entries = []
        token_usages = []
        sum_completion_tokens = 0

        for sample_idx in range(sampling_params.params.n):
            response_entry, token_usage_for_response = _parse_response_for_idx(
                response,
                sample_idx,
            )
            response_entries.append(response_entry.to_dict())
            token_usages.append(token_usage_for_response)
            sum_completion_tokens += token_usage_for_response["completion_tokens"]

        unique_id = unique_ids[idx]

        # Update existing_results
        if unique_id not in id_to_results:
            id_to_results[unique_id] = remaining_data[idx]
            if isinstance(handler, NUMINATaskHandler):
                id_to_results[unique_id]["messages"] = ""
            id_to_results[unique_id]["prompt"] = (
                conversations[idx][1]["content"]
                if len(conversations[idx]) > 1
                else conversations[idx][0]["content"]
            )
            id_to_results[unique_id]["input_conversation"] = conversations[idx]

        id_to_results[unique_id]["responses"] = response_entries
        id_to_results[unique_id]["token_usages"] = token_usages

        all_prompt_tokens.append(response.num_input_tokens)
        all_completion_tokens.append(sum_completion_tokens)
    
    if responses_by_budget:
        import copy, json
        from pathlib import Path

        budgets_list = sorted(responses_by_budget.keys())
        for budget in budgets_list:
            out_dir = output_dir / f"truncate_{budget}"
            out_dir.mkdir(parents=True, exist_ok=True)

            new_results     = copy.deepcopy(id_to_results)
            p_total = c_total = 0

            for idx, resp in enumerate(responses_by_budget[budget]):
                uid = unique_ids[idx]

                # rebuild per-sample entries (n == sampling_params.params.n)
                entry_list   = []
                usage_list   = []
                sum_comp_tok = 0
                for sidx in range(sampling_params.params.n):
                    parsed, usage = _parse_response_for_idx(resp, sidx)
                    entry_list.append(parsed.to_dict())
                    usage_list.append(usage)
                    sum_comp_tok += usage["completion_tokens"]
                new_results[uid]["responses"]     = entry_list
                new_results[uid]["token_usages"]  = usage_list

                p_total += resp.num_input_tokens
                c_total += sum_comp_tok

            save_results(out_dir / RESULTS_FILENAME, new_results)

            num_resp = len(responses_by_budget[budget]) * sampling_params.params.n
            summary  = SummaryResults(
                configuration = {**run_config_dict, "truncated_budget": budget},
                total_completion_tokens = c_total,
                total_prompt_tokens     = p_total,
                avg_completion_tokens   = round(c_total / num_resp, 3) if num_resp else 0,
                avg_prompt_tokens       = round(p_total / len(responses_by_budget[budget]), 3) if num_resp else 0,
            )
            save_summary(out_dir / SUMMARY_FILENAME, summary)
            logger.info(f"[budget-save] saved {num_resp} samples → {out_dir}")

    return id_to_results, all_prompt_tokens, all_completion_tokens


def score_responses(
    handler: TaskHandler,
    id_to_results: Dict[str, Dict[str, Any]],
    *,
    max_workers: int = 32,
) -> Tuple[float, Dict[str, List[int]], int]:
    """Computes correctness for model responses for the given task

    The 'id_to_results' dictionary is assumed to be a mapping between problem ID -> { responses: [...], ... },
    This is updated in-place.

    Returns:
       - overall accuracy
       - `id_to_scores` dictionary mapping IDs -> list of scores (used for metrics like pass@k)
       - total number of responses processed
    """
    if not id_to_results:
        return 0.0, {}, 0

    total_correct = 0
    total_finish = 0
    id_to_scores = {}

    # Figure out how many generations per problem
    N = len(next(iter(id_to_results.values()))["responses"])

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_info = {}
        for unique_id, record in id_to_results.items():
            for i in range(N):
                content = record["responses"][i]["content"]
                future = executor.submit(handler.update_results, record, content)
                # track which problem and which response index
                future_to_info[future] = (unique_id, i)

        for future in tqdm(as_completed(future_to_info), total=len(future_to_info)):
            unique_id, i = future_to_info[future]
            new_response_entry = future.result()

            # Update correctness and reason in the original results dict
            id_to_results[unique_id]["responses"][i]["correctness"] = (
                new_response_entry["correctness"]
            )
            id_to_results[unique_id]["responses"][i]["reason"] = new_response_entry[
                "reason"
            ]

            # Track scores separately for metrics like pass@k
            # TODO (sumanthrh): this can be improved
            if unique_id not in id_to_scores:
                id_to_scores[unique_id] = [0 for _ in range(N)]
            id_to_scores[unique_id][i] = int(new_response_entry["correctness"])

            total_correct += new_response_entry["correctness"]
            total_finish += 1

    accuracy = round(total_correct / total_finish, 4) if total_finish else 0
    return accuracy, id_to_scores, total_finish


def get_math_aware_counts(answers: List[str]) -> List[Tuple[str, int]]:
    """
    Groups and counts answers using math_equal for comparison.
    This acts as a "smart counter" for mathematical strings.

    Args:
        answers: A list of extracted answer strings.

    Returns:
        A list of (answer, count) tuples, sorted by count descending,
        similar to collections.Counter.most_common().
    """
    if not answers:
        return []

    # Each group is represented by its first member.
    # The list will store tuples of (representative_answer, count).
    groups = []

    for answer in answers:
        found_group = False
        # Check if the current answer belongs to any existing group
        for i, (representative_answer, count) in enumerate(groups):
            if math_equal(answer, representative_answer):
                groups[i] = (representative_answer, count + 1)
                found_group = True
                break
        
        # If no group was found, this answer starts a new one.
        if not found_group:
            groups.append((answer, 1))

    # Sort the groups by count in descending order
    return sorted(groups, key=lambda item: item[1], reverse=True)


def score_majority_voting(
    handler: TaskHandler,
    id_to_results: Dict[str, Dict[str, Any]],
    group_size: int,
    num_trials: int,
) -> Tuple[float, Dict[str, float]]:
    """
    Computes majority voting accuracy using a math-aware counter.
    """
    if not id_to_results:
        return 0.0, {}

    problem_scores = {}
    for unique_id, record in tqdm(id_to_results.items(), desc="Processing Problems for Majority Vote"):
        all_responses = record["responses"]
        if not all_responses:
            problem_scores[unique_id] = 0.0
            continue

        extracted_answers = [handler.extract_answer(resp["content"]) for resp in all_responses]
        valid_answers = [ans for ans in extracted_answers if ans]

        if not valid_answers or len(valid_answers) < group_size:
            problem_scores[unique_id] = 0.0
            continue

        trial_successes = 0
        for _ in range(num_trials):
            sample_group = random.choices(valid_answers, k=group_size)
            
            # --- THIS IS THE KEY CHANGE ---
            # Replace the simple Counter with our new math-aware version.
            most_common = get_math_aware_counts(sample_group)
            # -----------------------------

            if not most_common:
                continue

            # Check for a tie for first place
            if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
                continue # Tie, this trial fails.
            
            majority_answer = most_common[0][0]

            result_dict = handler.update_results(record, majority_answer)
            
            if result_dict.get("correctness"):
                trial_successes += 1
        
        problem_scores[unique_id] = trial_successes / num_trials

    overall_accuracy = round(sum(problem_scores.values()) / len(problem_scores), 4) if problem_scores else 0
    return overall_accuracy, problem_scores


def score_responses_for_indices(
    handler: TaskHandler,
    id_to_results: Dict[str, Dict[str, Any]],
    *,
    indices: List[str],
) -> List[int]:
    """Computes correctness for model responses for the given task for the unique index `idx`.

    The 'id_to_results' dictionary is assumed to be a mapping between problem ID -> { responses: [...], ... },
    This is updated in-place.

    Returns:
       - list of scores
    """
    if not id_to_results:
        return []
    logger.info(f"Computing scores for {len(indices)} samples")
    for idx in indices:
        # Figure out how many generations per problem
        N = len(next(iter(id_to_results.values()))["responses"])
        record = id_to_results[idx]
        scores = []
        for i in range(N):
            content = record["responses"][i]["content"]
            response_entry = handler.update_results(record, content)

            # Update correctness and reason in the original results dict
            id_to_results[idx]["responses"][i]["correctness"] = response_entry[
                "correctness"
            ]
            id_to_results[idx]["responses"][i]["reason"] = response_entry["reason"]
            scores.append(response_entry["correctness"])
    return scores


def generate_and_score(
    handler: TaskHandler,
    model_config: ModelConfig,
    backend: Backend,
    backend_params: BackendParameters,
    sampling_params: SamplingParameters,
    min_tokens: int,
    continuation_string: str,
    output_dir: Path,
    start: int,
    end: int,
    run_config_dict: dict,
    **kwargs,
):
    result_file = output_dir / RESULTS_FILENAME
    summary_file = output_dir / SUMMARY_FILENAME

    eval_data = handler.load_and_filter_dataset(start, end)
    id_to_results = {}

    id_to_results, prompt_tokens, completion_tokens = generate_responses_for_dataset(
        handler=handler,
        model_config=model_config,
        backend=backend,
        backend_params=backend_params,
        sampling_params=sampling_params,
        min_tokens=min_tokens,
        continuation_string=continuation_string,
        eval_data=eval_data,
        id_to_results=id_to_results,
        output_dir=output_dir,
        run_config_dict=run_config_dict,
        **kwargs,
    )

    accuracy, id_to_scores, total_finish = score_responses(
        handler, id_to_results, max_workers=32
    )
    logger.info(f"Accuracy: {accuracy}")

    num_responses_total = len(id_to_results) * sampling_params.params.n

    pass_at_k_metrics = None
    if sampling_params.params.n > 1:
        pass_at_k_metrics = pass_at_k(sampling_params.params.n, id_to_scores)

    total_completion_tokens = int(sum(completion_tokens))
    total_prompt_tokens = int(sum(prompt_tokens))
    summary_data = SummaryResults(
        configuration=run_config_dict,
        total_completion_tokens=total_completion_tokens,
        total_prompt_tokens=total_prompt_tokens,
        avg_completion_tokens=(
            round(total_completion_tokens / num_responses_total, 3)
            if total_completion_tokens
            else 0
        ),
        avg_prompt_tokens=(
            round(total_prompt_tokens / len(id_to_results), 3)
            if total_prompt_tokens
            else 0
        ),
        accuracy=accuracy,
        pass_at_k=pass_at_k_metrics,
    )

    save_summary(summary_file, summary_data)
    save_results(result_file, id_to_results)
    logger.info(f"Saved results to {result_file}")
    logger.info(f"Summary saved to {summary_file}")


def generate_and_save(
    handler: TaskHandler,
    model_config: ModelConfig,
    backend: Backend,
    backend_params: BackendParameters,
    sampling_params: SamplingParameters,
    min_tokens: int,
    continuation_string: str,
    output_dir: Path,
    start: int,
    end: int,
    run_config_dict: dict,
    resume_from: Optional[os.PathLike] = None,
    **kwargs,
):
    if resume_from is not None:
        resume_from = Path(resume_from)
        result_file = resume_from / RESULTS_FILENAME
        summary_file = resume_from / SUMMARY_FILENAME
        id_to_results = load_existing_results(result_file)
    else:
        id_to_results = {}
        result_file = output_dir / RESULTS_FILENAME
        summary_file = output_dir / SUMMARY_FILENAME

    eval_data = handler.load_and_filter_dataset(start, end)

    # Step 3: generate responses (no scoring here)
    id_to_results, prompt_tokens, completion_tokens = generate_responses_for_dataset(
        handler=handler,
        model_config=model_config,
        backend=backend,
        backend_params=backend_params,
        sampling_params=sampling_params,
        min_tokens=min_tokens,
        continuation_string=continuation_string,
        eval_data=eval_data,
        id_to_results=id_to_results,
        output_dir=output_dir,
        run_config_dict=run_config_dict,
        **kwargs,
    )

    total_completion_tokens = int(sum(completion_tokens))
    total_prompt_tokens = int(sum(prompt_tokens))
    num_responses_total = len(eval_data) * sampling_params.params.n
    summary_data = SummaryResults(
        configuration=run_config_dict,
        total_completion_tokens=total_completion_tokens,
        total_prompt_tokens=total_prompt_tokens,
        avg_completion_tokens=(
            round(total_completion_tokens / num_responses_total, 3)
            if total_completion_tokens
            else 0
        ),
        avg_prompt_tokens=(
            round(total_prompt_tokens / num_responses_total, 3)
            if total_prompt_tokens
            else 0
        ),
    )

    save_summary(summary_file, summary_data)
    save_results(result_file, id_to_results)

    logger.info(f"Saved results to {result_file}")
    logger.info(f"Saved summary to {summary_file}")


def truncate_and_regenerate(
    run_dir: Path,
    budgets: List[int],
    separator: str,
    max_new_tokens: int,
    sampling_overrides: Optional[Dict[str, Any]] = None,
    backend_overrides: Optional[Dict[str, Any]] = None,
    batch_size: int = 64,
):
    """
    For each budget B in `budgets`:
        • Truncate every saved answer to the first B tokens.
        • Append `separator` and regenerate ≤ `max_new_tokens` new tokens.
        • Save the new outputs under run_dir/truncate_B/.
    """
    import copy, json
    from transformers import AutoTokenizer
    from tqdm import tqdm

    summary_path = run_dir / SUMMARY_FILENAME
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    run_cfg = json.load(summary_path.open())["configuration"]

    backend_params_dict = copy.deepcopy(run_cfg["backend"]["backend_args"])
    sampling_dict = copy.deepcopy(run_cfg["sampling_params"])

    if backend_overrides:
        backend_params_dict.update(backend_overrides)
        logger.info(f"Applying backend overrides: {backend_overrides}")
    if sampling_overrides:
        sampling_dict.update(sampling_overrides)
        logger.info(f"Applying sampling overrides: {sampling_overrides}")

    model_id = run_cfg["model"]["name"]
    backend_enum = Backend(run_cfg["backend"]["name"])
    backend_params = BackendParameters.from_dict(backend_enum, backend_params_dict)
    model_cfg = ModelConfig.from_model_id(
        model_id,
        run_cfg["model"]["config"].get("system_prompt_name"),
        run_cfg["model"]["config"].get("system_prompt"),
        run_cfg["model"]["config"].get("assistant_prefill"),
    )

    if "n" not in sampling_dict:
        sampling_dict["n"] = 1
    sampling_params = SamplingParameters.from_dict(backend_enum, sampling_dict)
    sampling_params.params.max_tokens = max_new_tokens

    tokenizer_path = backend_params.to_dict().get("tokenizer", model_cfg.model_id)
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_path,
        use_fast=True,
        trust_remote_code=backend_params.to_dict().get("trust_remote_code", True),
    )

    llm = None
    if backend_enum == Backend.VLLM:
        engine_kwargs = copy.deepcopy(backend_params.to_dict())
        engine_kwargs["model"] = model_cfg.model_id
        llm = LLM(**engine_kwargs)

    original_results = json.load((run_dir / RESULTS_FILENAME).open())
    budgets = sorted(set(budgets))

    for budget in budgets:
        logger.info(f"[truncate] budget={budget}")
        out_dir = run_dir / f"truncate_{budget}"
        out_dir.mkdir(exist_ok=True)

        prompt_batch, conv_batch, uid_batch = [], [], []
        for uid, rec in original_results.items():
            for sidx, entry in enumerate(rec["responses"]):
                full = entry["content"]
                toks = tokenizer.encode(full, add_special_tokens=False)
                truncated = tokenizer.decode(toks[: budget], skip_special_tokens=False)

                new_msg = truncated + separator
                conv = copy.deepcopy(rec["input_conversation"])
                a_idx = next(
                    (i for i in reversed(range(len(conv))) if conv[i]["role"] == "assistant"),
                    None,
                )
                if a_idx is not None:
                    conv[a_idx]["content"] = new_msg
                else:
                    conv.append({"role": "assistant", "content": new_msg})
                conv_batch.append(conv)

                prefix = tokenizer.apply_chat_template(conv[:-1], tokenize=False, add_generation_prompt=False)
                header = tokenizer.apply_chat_template([{"role": "assistant", "content": ""}], tokenize=False, add_generation_prompt=False)
                prompt = prefix + header + new_msg
                ids = tokenizer.encode(prompt, add_special_tokens=False)
                if tokenizer.eos_token_id is not None and ids and ids[-1] == tokenizer.eos_token_id:
                    ids = ids[:-1]
                    prompt = tokenizer.decode(ids, skip_special_tokens=False)

                prompt_batch.append(prompt)
                uid_batch.append((uid, sidx))

        if backend_enum == Backend.VLLM:
            vllm_out = []
            for i in range(0, len(prompt_batch), batch_size):
                vllm_out.extend(
                    llm.generate(
                        prompts=prompt_batch[i : i + batch_size],
                        sampling_params=sampling_params.params,
                        use_tqdm=True,
                    )
                )
            responses = [Response.from_vllm_response(r) for r in vllm_out]
        else:
            raise NotImplementedError("truncate currently supports vLLM runs only.")

        new_results, p_total, c_total = {}, 0, 0
        for (uid, sidx), conv, resp in zip(uid_batch, conv_batch, responses):
            parsed, usage = _parse_response_for_idx(resp, 0)
            if uid not in new_results:
                new_results[uid] = copy.deepcopy(original_results[uid])
            new_results[uid]["responses"][sidx]["content"] = conv[-1]["content"] + parsed.content
            new_results[uid]["token_usages"][sidx]["completion_tokens"] = (
                usage["prompt_tokens"] + usage["completion_tokens"] - new_results[uid]["token_usages"][sidx]["prompt_tokens"]
            )
            p_total += new_results[uid]["token_usages"][sidx]["prompt_tokens"]
            c_total += new_results[uid]["token_usages"][sidx]["completion_tokens"]

        save_results(out_dir / RESULTS_FILENAME, new_results)

        num_resp = len(uid_batch)
        summary = SummaryResults(
            configuration={**run_cfg, "truncated_budget": budget, "max_new_tokens": max_new_tokens},
            total_completion_tokens=c_total,
            total_prompt_tokens=p_total,
            avg_completion_tokens=round(c_total / num_resp, 3) if num_resp else 0,
            avg_prompt_tokens=round(p_total / num_resp, 3) if num_resp else 0,
        )
        save_summary(out_dir / SUMMARY_FILENAME, summary)
        logger.info(f"[truncate] saved {num_resp} samples → {out_dir}")


def score_results(
    handler: TaskHandler,
    run_dir: Path,
    run_summary: SummaryResults,
    indices: Optional[List[str]] = None,
) -> None:
    # load existing results
    result_file = run_dir / RESULTS_FILENAME
    summary_file = run_dir / SUMMARY_FILENAME
    id_to_results = load_existing_results(result_file)
    logger.info(f"Loaded {len(id_to_results)} existing results for scoring.")

    if not indices:
        accuracy, id_to_scores, total_finish = score_responses(handler, id_to_results)
    else:
        N = len(next(iter(id_to_results.values()))["responses"])
        score_responses_for_indices(handler, id_to_results, indices=indices)
        id_to_scores = {
            index: [
                id_to_results[index]["responses"][i]["correctness"] for i in range(N)
            ]
            for index in id_to_results
        }
        accuracy = round(
            sum(map(sum, id_to_scores.values())) / (len(id_to_scores) * N), 4
        )

    sample_count = 0
    if id_to_results:
        sample_count = len(next(iter(id_to_results.values()))["responses"])
    pass_at_k_metrics = None
    if sample_count > 1:
        pass_at_k_metrics = pass_at_k(sample_count, id_to_scores)

    run_summary.accuracy = accuracy
    run_summary.pass_at_k = pass_at_k_metrics

    logger.info(f"Accuracy: {accuracy}")
    save_summary(summary_file, run_summary)

    save_results(result_file, id_to_results)
    logger.info(f"Scored results saved to {result_file}")

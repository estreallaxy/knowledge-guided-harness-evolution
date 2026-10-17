#!/usr/bin/env python3
import argparse
import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification, AutoConfig
#


def read_results_json(path: str) -> List[Dict[str, Any]]:
    """
    Robustly read results supporting multiple schemas:
      1) Top-level list of problems
      2) Top-level dict with keys like items/results/samples/data/problems/records
      3) Nested dict where such a list is inside a sub-dict
      4) JSONL (one object per line)
    Each problem object is expected (downstream) to contain 'question' and 'responses'.
    """
    def _extract_list_from_obj(obj: Any) -> Optional[List[Dict[str, Any]]]:
        if isinstance(obj, list) and (len(obj) == 0 or isinstance(obj[0], dict)):
            return obj  # assume correct
        if isinstance(obj, dict):
            # Case: dict keyed by indices/ids -> collect values as list of problems
            values = list(obj.values())
            if values and all(isinstance(v, dict) for v in values):
                # Heuristic: look like problems if many have 'responses' or 'question' or 'prompt'
                problem_like = [v for v in values if ('responses' in v) or ('question' in v) or ('prompt' in v)]
                if problem_like:
                    # Try to preserve numeric key order if possible
                    try:
                        keys_sorted = sorted(obj.keys(), key=lambda k: int(k))
                        lst = [obj[k] for k in keys_sorted if isinstance(obj[k], dict)]
                    except Exception:
                        lst = values
                    return lst
            # Try common keys
            for key in ("items", "results", "samples", "data", "problems", "records"):
                v = obj.get(key)
                if isinstance(v, list) and (len(v) == 0 or isinstance(v[0], dict)):
                    return v
            # Try any value that looks like a list of dicts with responses/question
            for v in obj.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and ("responses" in v[0] or "question" in v[0]):
                    return v
            # Recurse one level deeper
            for v in obj.values():
                if isinstance(v, dict):
                    found = _extract_list_from_obj(v)
                    if found is not None:
                        return found
        return None

    # Try standard JSON
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        lst = _extract_list_from_obj(data)
        if lst is not None:
            return lst
    except Exception:
        pass

    # Try JSON Lines (JSONL)
    problems: List[Dict[str, Any]] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    obj = json.loads(s)
                    if isinstance(obj, dict):
                        problems.append(obj)
                except Exception:
                    continue
        if problems:
            return problems
    except Exception:
        pass

    raise ValueError(f"Could not parse problems list from {path} (unsupported schema).")


def extract_reasoning_text(content: str) -> str:
    if not isinstance(content, str):
        return ""
    # Prefer the text inside <think>...</think> if present; else use entire content
    lower = content.lower()
    start_tag = "<think>"
    end_tag = "</think>"
    s = lower.find(start_tag)
    e = lower.find(end_tag)
    if s != -1 and e != -1 and e > s:
        # Map indices to original string to preserve casing
        real_s = s
        real_e = e
        return content[real_s + len(start_tag):real_e].strip()
    return content.strip()


def build_input_text(question: str, reasoning: str) -> str:
    question = (question or "").strip()
    reasoning = (reasoning or "").strip()
    if question and reasoning:
        return f"Question:\n{question}\n\nReasoning:\n{reasoning}"
    if reasoning:
        return reasoning
    return question


class PRMScorer:
    def __init__(
        self,
        model_id: str = "sail/ActPRM-X",
        device: str = None,
        dtype: str = "auto",
        trust_remote_code: bool = True,
    ):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=trust_remote_code)
        # Align with ActPRM usage
        try:
            if getattr(self.tokenizer, "padding_side", None) != "left":
                self.tokenizer.padding_side = "left"
            if getattr(self.tokenizer, "pad_token", None) is None and getattr(self.tokenizer, "eos_token", None) is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        except Exception:
            pass
        self.config = AutoConfig.from_pretrained(model_id, trust_remote_code=trust_remote_code)
        # Avoid 'meta' init which breaks custom PRM init routines
        try:
            if hasattr(self.config, "init_device"):
                init_dev = str(getattr(self.config, "init_device") or "").lower()
                if init_dev == "meta":
                    setattr(self.config, "init_device", "cpu")
        except Exception:
            pass
        # Also disable Accelerate's init-empty-weights path if present in env
        os.environ.setdefault("ACCELERATE_DISABLE_INIT_EMPTY_WEIGHTS", "1")
        torch_dtype = None
        if dtype == "auto":
            torch_dtype = "auto"
        elif dtype == "bf16":
            torch_dtype = torch.bfloat16
        elif dtype == "fp16":
            torch_dtype = torch.float16
        elif dtype == "fp32":
            torch_dtype = torch.float32
        else:
            torch_dtype = "auto"

        self.model = None
        self.uses_cls_head = False
        load_errors: List[str] = []
        self.correct_label_index: Optional[int] = None

        # Prefer raw AutoModel for custom PRM configs and avoid meta initialization
        cfg_name = type(self.config).__name__.lower()
        force_raw = ("prm" in cfg_name) or ("qwenenprmconfig" in cfg_name)

        def _load_raw():
            return AutoModel.from_pretrained(
                model_id,
                config=self.config,         # ensure overridden init_device is honored
                torch_dtype=torch_dtype,
                trust_remote_code=trust_remote_code,
                device_map=None,            # avoid meta tensors
                low_cpu_mem_usage=False,    # materialize full tensors
            )

        if not force_raw:
            try:
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_id,
                    config=self.config,         # ensure overridden init_device is honored
                    torch_dtype=torch_dtype,
                    trust_remote_code=trust_remote_code,
                    device_map=None,            # avoid meta tensors
                    low_cpu_mem_usage=False,
                )
                self.uses_cls_head = True
                # Try to find the index of the "correct" label if present
                try:
                    id2label = getattr(self.config, "id2label", None)
                    if isinstance(id2label, dict) and len(id2label) >= 2:
                        normalized: Dict[int, str] = {}
                        for k, v in id2label.items():
                            try:
                                normalized[int(k)] = str(v).lower()
                            except Exception:
                                continue
                        for idx, name in sorted(normalized.items()):
                            if "correct" in name:
                                self.correct_label_index = idx
                                break
                        if self.correct_label_index is None and len(normalized) == 2:
                            self.correct_label_index = max(normalized.keys())
                except Exception:
                    self.correct_label_index = None
            except Exception as e1:
                load_errors.append(f"AutoModelForSequenceClassification failed: {e1}")
                try:
                    self.model = _load_raw()
                    self.uses_cls_head = False
                except Exception as e2:
                    load_errors.append(f"AutoModel failed: {e2}")
                    raise RuntimeError("Could not load PRM model:\n" + "\n".join(load_errors))
        else:
            try:
                self.model = _load_raw()
                self.uses_cls_head = False
            except Exception as e2:
                load_errors.append(f"AutoModel failed: {e2}")
                raise RuntimeError("Could not load PRM model:\n" + "\n".join(load_errors))

        # rr_token used to segment steps (as in ActPRM code)
        try:
            self.rr_token = getattr(self.model, "rr_token", None) or " \n\n"
        except Exception:
            self.rr_token = " \n\n"
        try:
            self.rr_token_id = self.tokenizer(self.rr_token).input_ids[0]
        except Exception:
            self.rr_token_id = self.tokenizer("\n").input_ids[0]

        if device not in (None, "auto"):
            self.model.to(device)

        self.model.eval()

    @torch.no_grad()
    def score_texts(
        self,
        texts: List[str],
        batch_size: int = 1,
        max_length: int = None,
        truncation: bool = True,
    ) -> List[float]:
        scores: List[float] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            enc = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=truncation,
                max_length=max_length,
            )
            enc = {k: v.to(self.model.device) for k, v in enc.items()}
            outputs = self.model(**enc)

            # Heuristics to extract scalar rewards
            batch_scores: List[float] = []
            if hasattr(outputs, "logits"):
                logits = outputs.logits
                if logits.ndim == 2:
                    if logits.size(-1) == 1:
                        # Sigmoid for binary single-logit
                        probs = torch.sigmoid(logits)
                        batch_scores = probs.squeeze(-1).detach().float().cpu().tolist()
                    else:
                        # Softmax class probs; choose 'correct' class if known; else use max prob
                        probs = F.softmax(logits, dim=-1)
                        if self.correct_label_index is not None and 0 <= self.correct_label_index < probs.size(-1):
                            vals = probs[:, self.correct_label_index]
                        else:
                            vals, _ = probs.max(dim=-1)
                        batch_scores = vals.detach().float().cpu().tolist()
                else:
                    # Unexpected shape; average as fallback
                    vals = logits.detach().float().cpu().view(logits.size(0), -1).mean(dim=-1).tolist()
                    batch_scores = [float(v) for v in vals]
            elif hasattr(outputs, "scores"):
                vals = outputs.scores
                if isinstance(vals, torch.Tensor):
                    if vals.ndim == 2 and vals.size(-1) == 1:
                        batch_scores = torch.sigmoid(vals).squeeze(-1).detach().float().cpu().tolist()
                    else:
                        # Treat as logits if possible
                        if vals.ndim == 2:
                            probs = F.softmax(vals, dim=-1)
                            vals2, _ = probs.max(dim=-1)
                            batch_scores = vals2.detach().float().cpu().tolist()
                        else:
                            batch_scores = vals.detach().float().cpu().view(vals.size(0), -1).mean(dim=-1).tolist()
                else:
                    # Unknown structure; fallback to zero
                    batch_scores = [0.0] * len(batch)
            elif hasattr(outputs, "reward"):
                vals = getattr(outputs, "reward")
                if isinstance(vals, torch.Tensor):
                    if vals.ndim == 2 and vals.size(-1) == 1:
                        batch_scores = torch.sigmoid(vals).squeeze(-1).detach().float().cpu().tolist()
                    else:
                        batch_scores = vals.detach().float().cpu().view(vals.size(0), -1).mean(dim=-1).tolist()
                else:
                    batch_scores = [0.0] * len(batch)
            else:
                # Fallback: average last_hidden_state as a weak proxy
                last = getattr(outputs, "last_hidden_state", None)
                if isinstance(last, torch.Tensor):
                    # Average across sequence and hidden dims
                    vals = last.mean(dim=(1, 2)).detach().float().cpu().tolist()
                    batch_scores = [float(v) for v in vals]
                else:
                    batch_scores = [0.0] * len(batch)

            scores.extend(batch_scores)
        return scores


def _split_reasoning_into_steps(text: str, mode: str = "paragraph") -> List[str]:
    """
    Split reasoning text into steps.
      - paragraph: split on blank lines
      - newline: split on single newlines
    """
    s = (text or "").strip()
    if not s:
        return []
    if mode == "newline":
        steps = [x.strip() for x in s.split("\n") if x.strip()]
    else:
        # default: paragraph by double newlines
        parts = [p.strip() for p in s.split("\n\n")]
        steps = []
        for p in parts:
            if p:
                steps.append(p)
    return steps


def build_step_contexts(
    question: str,
    steps: List[str],
    use_cumulative_context: bool = True,
) -> List[str]:
    """
    Build the per-step input texts: for step i, include question and steps[:i+1] if use_cumulative_context,
    else include only question and steps[i].
    """
    q = (question or "").strip()
    contexts: List[str] = []
    if not steps:
        return contexts
    if use_cumulative_context:
        acc: List[str] = []
        for i, st in enumerate(steps):
            acc.append(st.strip())
            body = "\n\n".join(acc)
            contexts.append(f"Question:\n{q}\n\nSolution:\n{body}".strip())
    else:
        for st in steps:
            contexts.append(f"Question:\n{q}\n\nSolution:\n{st.strip()}".strip())
    return contexts


def aggregate_step_scores_prefix(
    step_probs: List[float],
    threshold: float = 0.5,
    mode: str = "logprod_prefix",  # options: logprod_prefix, mean_prefix, sum_prefix, prefix_len
) -> float:
    """
    Aggregate per-step probabilities into a scalar trajectory score using a prefix rule:
      - first predicted error step: first index where p < threshold
      - consider only steps BEFORE the first error (exclusive)
    """
    if not step_probs:
        return 0.0
    first_err_idx = None
    for i, p in enumerate(step_probs):
        if p < float(threshold):
            first_err_idx = i
            break
    usable = step_probs if first_err_idx is None else step_probs[:first_err_idx]
    if not usable:
        return 0.0
    if mode == "mean_prefix":
        return float(sum(usable) / len(usable))
    if mode == "sum_prefix":
        return float(sum(usable))
    if mode == "prefix_len":
        return float(len(usable))
    # default: logprod of probs
    eps = 1e-6
    logsum = 0.0
    for p in usable:
        q = max(eps, min(1.0 - eps, float(p)))
        logsum += float(torch.log(torch.tensor(q)).item())
    return logsum


def _actprm_prompt2message(question: str, assistant_text: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": "You are a helpful and harmless assistant. You should think step-by-step and put your final answer within \\boxed{}.",
        }
    ]
    messages.append({"role": "user", "content": question or ""})
    messages.append({"role": "assistant", "content": assistant_text or ""})
    return messages


class ActPRMFormatter:
    def __init__(self, tokenizer: AutoTokenizer, rr_token: str, rr_token_id: int):
        self.tokenizer = tokenizer
        self.rr_token = rr_token
        self.rr_token_id = rr_token_id

    def _join_steps(self, steps: List[str]) -> str:
        cleaned = [s.strip() for s in steps if str(s or "").strip()]
        if not cleaned:
            return ""
        return self.rr_token.join(cleaned) + self.rr_token

    def apply_chat_template_batch(self, qa_pairs: List[Tuple[str, List[str]]]) -> List[str]:
        """
        qa_pairs: list of (question, steps_list)
        Returns raw text after applying chat template without the trailing assistant completion token.
        """
        messages = []
        for q, steps in qa_pairs:
            assistant_text = self._join_steps(steps)
            messages.append(_actprm_prompt2message(q or "", assistant_text))
        # For each, strip last assistant message content from tokenization prompt and append assistant content manually
        no_res_message = [m[:-1] for m in messages]
        res_message = [m[-1] for m in messages]
        try:
            templated = self.tokenizer.apply_chat_template(no_res_message, tokenize=False, add_generation_prompt=True)
            templated = [templated[i] + res_message[i]["content"] for i in range(len(templated))]
            return templated
        except Exception:
            # Fallback: naive concatenation
            out = []
            for i in range(len(no_res_message)):
                u = no_res_message[i][1]["content"] if len(no_res_message[i]) > 1 else ""
                a = res_message[i]["content"]
                out.append(f"User: {u}\nAssistant: {a}")
            return out


@torch.no_grad()
def actprm_infer_scores(
    model: AutoModel,
    tokenizer: AutoTokenizer,
    rr_token_id: int,
    questions_and_steps: List[Tuple[str, List[str]]],
    batch_size: int = 1,
    device: Optional[torch.device] = None,
    reduce_heads: str = "mean",
) -> List[List[float]]:
    """
    Run ActPRM-style inference and return per-sample step ratings for rr_token-separated steps.
    """
    fmt = ActPRMFormatter(tokenizer, getattr(model, "rr_token", None) or " \n\n", rr_token_id)
    results: List[List[float]] = []
    for i in range(0, len(questions_and_steps), batch_size):
        batch_pairs = questions_and_steps[i : i + batch_size]
        texts = fmt.apply_chat_template_batch(batch_pairs)
        model_inputs = tokenizer(texts, return_tensors="pt", padding=True)
        if device is None:
            device = model.device
        model_inputs = {k: v.to(device) for k, v in model_inputs.items()}
        pred_mask = (model_inputs["input_ids"] == rr_token_id)  # [B, L]
        # Use model.inference if available
        if hasattr(model, "inference"):
            outputs = model.inference(**model_inputs)
        else:
            outputs = model(**model_inputs)
        logits = getattr(outputs, "logits", None)
        if logits is None:
            # Fallback: no logits, return empty lists
            results.extend([[] for _ in range(len(batch_pairs))])
            continue
        # Normalize logits to [B, H, L]
        if logits.dim() == 3:
            B = model_inputs["input_ids"].shape[0]
            if logits.shape[0] == B:
                bhl = logits  # [B, H, L]
            elif logits.shape[1] == B:
                bhl = logits.transpose(0, 1).contiguous()
            else:
                # Unknown layout, guess last dim is L
                bhl = logits
        else:
            # Unexpected rank; attempt to add head dim
            bhl = logits.unsqueeze(1)
        # For each sample, select positions equal to rr_token and pool across heads
        for j in range(bhl.shape[0]):
            li = bhl[j]  # [H, L] or [1, L]
            if li.dim() == 2:
                if reduce_heads == "mean":
                    li = li.mean(dim=0)
                elif reduce_heads == "max":
                    li, _ = li.max(dim=0)
                else:
                    li = li.mean(dim=0)
            mask = pred_mask[j]  # [L]
            vals = li[mask]
            results.append(vals.detach().float().cpu().tolist())
    return results


def compute_problem_scores_bestof(
    per_problem_scores: List[List[float]],
    per_problem_correct: List[List[bool]],
    group_size: int,
    num_trials: int,
    rng: random.Random,
) -> Tuple[Dict[str, float], float]:
    """
    per_problem_scores: list over problems; each is list of PRM scores over candidates
    per_problem_correct: list over problems; each is list of correctness booleans (aligned to scores)
    Returns: (problem_scores, overall_accuracy), both in fraction [0,1]
    """
    problem_scores: Dict[str, float] = {}
    for p_idx, (scores, correct_flags) in enumerate(zip(per_problem_scores, per_problem_correct)):
        n = len(scores)
        if n == 0:
            problem_scores[str(p_idx)] = 0.0
            continue
        g = min(max(1, int(group_size)), n)
        wins = 0
        for _ in range(num_trials):
            subset = rng.sample(range(n), g) if g < n else list(range(n))
            # pick best by PRM score within subset
            best_idx = max(subset, key=lambda i: scores[i])
            if bool(correct_flags[best_idx]):
                wins += 1
        problem_scores[str(p_idx)] = wins / float(num_trials)

    # overall as mean across problems
    if problem_scores:
        overall = sum(problem_scores.values()) / float(len(problem_scores))
    else:
        overall = 0.0
    return problem_scores, overall


def main():
    parser = argparse.ArgumentParser(description="Score PRM best-of-N using ActPRM-X over existing results.json.")
    parser.add_argument("--run-dir", required=True, help="Path to truncate_* directory containing results.json and summary.json.")
    parser.add_argument("--group-size", type=int, action="append", required=True, help="Group size N for best-of-N selection. Can be repeated.")
    parser.add_argument("--num-trials", type=int, default=32, help="Number of random subsets per problem.")
    parser.add_argument("--prm-model-id", default="sail/ActPRM-X", help="HF model id for PRM.")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for PRM forward pass.")
    parser.add_argument("--dtype", choices=["auto", "bf16", "fp16", "fp32"], default="auto", help="Torch dtype to use.")
    parser.add_argument("--device", default="auto", help="Device to place model on; 'auto' lets HF place it.")
    parser.add_argument("--max-length", type=int, default=None, help="Optional tokenizer max_length truncation.")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed for subset sampling.")
    parser.add_argument("--write-scores-cache", action="store_true", help="Write per-sample PRM scores to prm_scores.json to reuse later.")
    # Stepwise PRM options
    parser.add_argument("--mode", choices=["stepwise", "whole"], default="stepwise",
                        help="Scoring mode: stepwise (ActivePRM-style) or whole (single text).")
    parser.add_argument("--include-final", choices=["none", "append", "full"], default="none",
                        help="Whether to include final answer segment: none (default), append to PRM input, or use full response.")
    parser.add_argument("--step-split", choices=["paragraph", "newline"], default="paragraph",
                        help="How to split reasoning into steps in stepwise mode.")
    parser.add_argument("--agg", choices=["logprod_prefix", "mean_prefix", "sum_prefix", "prefix_len"], default="logprod_prefix",
                        help="Prefix aggregation for stepwise scores.")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Threshold for first-error detection in stepwise aggregation.")
    parser.add_argument("--no-cumulative-context", action="store_true",
                        help="If set, do not include previous steps when scoring the current step.")
    args = parser.parse_args()

    run_dir = os.path.abspath(args.run_dir)
    results_path = os.path.join(run_dir, "results.json")
    summary_path = os.path.join(run_dir, "summary.json")
    if not os.path.exists(results_path):
        raise FileNotFoundError(f"Missing results.json at {results_path}")
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Missing summary.json at {summary_path}")

    print(f"🔎 Loading {results_path}")
    problems = read_results_json(results_path)

    # Prepare PRM inputs and correctness flags
    per_problem_scores: List[List[float]] = []
    per_problem_correct: List[List[bool]] = []

    print(f"🧠 Loading PRM model: {args.prm_model_id}")
    scorer = PRMScorer(model_id=args.prm_model_id, device=args.device, dtype=args.dtype, trust_remote_code=True)

    if args.mode == "whole":
        texts: List[str] = []
        problem_offsets: List[Tuple[int, int]] = []  # (start_idx, end_idx_exclusive) for each problem
        for ex in problems:
            question = ex.get("question", "")
            responses = ex.get("responses", []) or []
            start = len(texts)
            correct_flags: List[bool] = []
            for r in responses:
                content = (r or {}).get("content", "")
                if args.include_final == "full":
                    reasoning = content
                else:
                    reasoning = extract_reasoning_text(content)
                    if args.include_final == "append" and reasoning != content:
                        # Append anything after </think> as "Final Answer" context
                        lower = content.lower()
                        e = lower.find("</think>")
                        if e != -1:
                            tail = content[e + len("</think>"):].strip()
                            if tail:
                                reasoning = f"{reasoning}\n\nAnswer:\n{tail}"
                text = build_input_text(question, reasoning)
                texts.append(text)
                correct_flags.append(bool((r or {}).get("correctness", False)))
            end = len(texts)
            problem_offsets.append((start, end))
            per_problem_correct.append(correct_flags)

        print(f"⚙️ Scoring {len(texts)} candidate traces (batch_size={args.batch_size})...")
        scores_all: List[float] = scorer.score_texts(
            texts,
            batch_size=args.batch_size,
            max_length=args.max_length,
            truncation=True,
        )
        assert len(scores_all) == len(texts), "PRM scoring did not return the expected number of scores."
        for (s, e) in problem_offsets:
            per_problem_scores.append(scores_all[s:e])
    else:
        # stepwise mode
        use_cumulative = not args.no_cumulative_context
        for ex in problems:
            question = ex.get("question", "")
            responses = ex.get("responses", []) or []
            aggregated_scores: List[float] = []
            correct_flags: List[bool] = []
            # Build ActPRM-friendly prompts: (question, steps[]) per response
            qa_pairs: List[Tuple[str, List[str]]] = []
            step_splits: List[List[float]] = []  # per-response step ratings

            for ri, r in enumerate(responses):
                content = (r or {}).get("content", "")
                base_reasoning = extract_reasoning_text(content) if args.include_final != "full" else content
                if args.include_final == "append" and base_reasoning != content:
                    lower = content.lower()
                    e = lower.find("</think>")
                    if e != -1:
                        tail = content[e + len("</think>"):].strip()
                        if tail:
                            base_reasoning = f"{base_reasoning}\n\nAnswer:\n{tail}"
                steps = _split_reasoning_into_steps(base_reasoning, mode=args.step_split) if use_cumulative else [base_reasoning]
                qa_pairs.append((question, steps))
                correct_flags.append(bool((r or {}).get("correctness", False)))

            if qa_pairs:
                # Use ActPRM-style inference to get step ratings at rr_token positions
                ratings_list = actprm_infer_scores(
                    model=scorer.model,
                    tokenizer=scorer.tokenizer,
                    rr_token_id=getattr(scorer, "rr_token_id", scorer.tokenizer("\n").input_ids[0]),
                    questions_and_steps=qa_pairs,
                    batch_size=args.batch_size,
                    device=scorer.model.device,
                    reduce_heads="mean",
                )
                step_splits = ratings_list

            # Aggregate per response
            for ri in range(len(qa_pairs)):
                raw_scores = step_splits[ri] if ri < len(step_splits) else []
                # Convert ratings to binary correctness via threshold (rating >= threshold -> correct)
                step_probs = [1.0 if (s is not None and float(s) >= float(args.threshold)) else 0.0 for s in raw_scores]
                agg = aggregate_step_scores_prefix(
                    step_probs=step_probs,
                    threshold=args.threshold,
                    mode=args.agg,
                )
                aggregated_scores.append(float(agg))

            per_problem_scores.append(aggregated_scores)
            per_problem_correct.append(correct_flags)

    # Optionally cache raw scores
    if args.write_scores_cache:
        cache_path = os.path.join(run_dir, "prm_scores.json")
        cache_obj = {
            "model_id": args.prm_model_id,
            "scores": per_problem_scores,
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_obj, f)
        print(f"💾 Wrote PRM scores cache -> {cache_path}")

    # Best-of-N per requested group sizes
    rng = random.Random(args.seed)
    group_sizes = sorted(set([int(g) for g in args.group_size if g is not None and int(g) > 0]))
    for g in group_sizes:
        problem_scores, overall = compute_problem_scores_bestof(
            per_problem_scores=per_problem_scores,
            per_problem_correct=per_problem_correct,
            group_size=g,
            num_trials=args.num_trials,
            rng=rng,
        )
        out_name = f"prm_bestof_g{g}_t{args.num_trials}_results.json"
        out_path = os.path.join(run_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "overall_accuracy": float(round(overall, 4)),
                    "problem_scores": {k: float(round(v, 8)) for k, v in problem_scores.items()},
                },
                f,
                ensure_ascii=False,
                indent=4,
            )
        print(f"✅ Wrote {out_path} (overall={overall:.4f})")


if __name__ == "__main__":
    main()



from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple, Callable, Optional
import json
import re
import math

from src.prompt.prompt_builder import build_cluster_and_score_messages, build_single_answer_score_messages, build_semantic_cluster_messages
from src.utils.trace_writer import log_request, log_response

@dataclass
class GeneratedSample:
    # A single generated sample result; used for subsequent semantic clustering and uncertainty calculation
    text: str
    logprob: Optional[float] = None
    token_logprobs: Optional[List[float]] = None

def render_prompt_with_fallback(
    tokenizer,
    messages: List[Dict[str, str]],
    add_generation_prompt: bool = True,
) -> Tuple[str, Dict[str, Any]]:
    """
    Generic chat prompt rendering function:
    - Prioritizes tokenizer.apply_chat_template
    - Fallback on failure
    Returns:
      (prompt, meta) where meta contains:
        used_template: bool
        template_error: Optional[str]
    """
    meta: Dict[str, Any] = {"used_template": False, "template_error": None}

    tmpl = getattr(tokenizer, "chat_template", None)
    if tmpl:
        try:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=add_generation_prompt,
            )
            meta["used_template"] = True
            return prompt, meta
        except Exception as e:
            meta["template_error"] = repr(e)

    # fallback: naive role-content concatenation
    lines = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "") or ""
        lines.append(f"[{role}] {content}\n")
    if add_generation_prompt:
        lines.append("[assistant] ")
    return "".join(lines), meta

# ------------------Tools ------------------------
# def _safe_json_loads(s: str) -> Dict[str, Any]:
#     try:
#         return json.loads(s)
#     except Exception:
#         m = re.search(r"\{.*\}", s, flags=re.S)
#         if not m:
#             raise
#         return json.loads(m.group(0))
def _safe_json_loads(s: str) -> Dict[str, Any]:
    """Safely parse JSON, handling common escaping issues."""
    if not s or not s.strip():
        raise ValueError("Empty JSON string")
    
    # Attempt 1: Direct parsing
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    
    # Attempt 2: Extract {...}
    m = re.search(r"\{.*\}", s, flags=re.S)
    if not m:
        raise ValueError("No JSON object found")
    
    json_str = m.group(0)
    
    # Attempt 3: Fix escaping issues
    try:
        # Inside double-quoted string values, replace illegal backslashes with spaces or slashes
        def fix_string_value(match):
            value = match.group(1)
            # Protect legal escapes: \n, \t, \r, \", \\
            value = value.replace('\\n', '\x00N\x00')
            value = value.replace('\\t', '\x00T\x00')
            value = value.replace('\\r', '\x00R\x00')
            value = value.replace('\\"', '\x00Q\x00')
            value = value.replace('\\\\', '\x00B\x00')
            # Remove other backslashes
            value = value.replace('\\', ' ')
            # Restore legal escapes
            value = value.replace('\x00N\x00', '\\n')
            value = value.replace('\x00T\x00', '\\t')
            value = value.replace('\x00R\x00', '\\r')
            value = value.replace('\x00Q\x00', '\\"')
            value = value.replace('\x00B\x00', '\\\\')
            return f'"{value}"'
        
        # Match "value" pattern (string values)
        json_str_fixed = re.sub(r'"([^"]*)"', fix_string_value, json_str)
        return json.loads(json_str_fixed)
    except json.JSONDecodeError:
        pass
    
    # Attempt 4: Completely remove backslashes
    try:
        json_str_clean = json_str.replace('\\', ' ')
        return json.loads(json_str_clean)
    except json.JSONDecodeError as e:
        error_preview = json_str[:300]
        raise ValueError(
            f"JSON parse failed: {str(e)}\n"
            f"Preview: {error_preview}..."
        )

def _get_question_from_sample(sample: Dict[str, Any]) -> str:
    for k in ("question", "prompt", "query", "input"):
        v = sample.get(k, None)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def _get_ground_truth_from_sample(sample: Dict[str, Any]) -> Optional[Any]:
    for k in ("ground_truth", "groundtruth", "gt", "label", "target", "answer", "answers", "final_answer"):
        if k in sample and sample[k] is not None:
            return sample[k]
    return None

def _gt_to_string(gt: Any) -> str:
    if gt is None:
        return ""
    if isinstance(gt, list):
        # Multiple reference answers: Concatenate them for the judge
        gt_list = [str(x).strip() for x in gt if str(x).strip()]
        return "\n".join([f"- {x}" for x in gt_list])
    return str(gt).strip()


def _validate_and_repair_clusters_with_levels(parsed: Dict[str, Any], k: int) -> Dict[str, Any]:
    clusters = parsed.get("clusters", [])
    if not isinstance(clusters, list):
        clusters = []

    seen = set()
    cleaned = []
    next_cid = 0

    for c in clusters:
        if not isinstance(c, dict):
            continue

        mids = c.get("member_indices", [])
        if not isinstance(mids, list):
            mids = []

        mids2 = []
        for idx in mids:
            if isinstance(idx, bool):  # exclude bool
                continue
            if isinstance(idx, int) and 0 <= idx < k and idx not in seen:
                seen.add(idx)
                mids2.append(idx)

        if not mids2:
            continue

        cid = c.get("cluster_id", None)
        if not isinstance(cid, int):
            cid = next_cid
        next_cid = max(next_cid, cid + 1)

        # correctness_level: int in [0,4]
        level = c.get("correctness_level", 0)
        try:
            level_i = int(float(level))
        except Exception:
            level_i = 0
        if level_i < 0: level_i = 0
        if level_i > 4: level_i = 4

        # confidence: float in [0,1]
        # conf = c.get("confidence", 0.5)
        # try:
        #     conf_f = float(conf)
        # except Exception:
        #     conf_f = 0.5
        # if conf_f < 0.0: conf_f = 0.0
        # if conf_f > 1.0: conf_f = 1.0

        cleaned.append({
            "cluster_id": cid,
            "member_indices": mids2,
            "canonical_meaning": str(c.get("canonical_meaning", "")).strip(),
            "representative_answer": str(c.get("representative_answer", "")).strip(),
            "correctness_level": level_i,
        })

    # ensure coverage
    missing = [i for i in range(k) if i not in seen]
    if missing:
        cleaned.append({
            "cluster_id": next_cid,
            "member_indices": missing,
            "canonical_meaning": "Unassigned / unclear (auto-repaired)",
            "representative_answer": "",
            "correctness_level": 0,
        })

    assignments = [-1] * k
    for c in cleaned:
        for idx in c["member_indices"]:
            assignments[idx] = c["cluster_id"]

    return {"clusters": cleaned, "assignments": assignments}

def _validate_level(x: Any) -> int:
    try:
        v = int(float(x))
    except Exception:
        v = 0
    if v < 0: v = 0
    if v > 4: v = 4
    return v

def _validate_and_repair_semantic_clusters(parsed: Dict[str, Any], k: int) -> Dict[str, Any]:
    clusters = parsed.get("clusters", [])
    if not isinstance(clusters, list):
        clusters = []

    seen = set()
    cleaned = []
    next_cid = 0

    for c in clusters:
        if not isinstance(c, dict):
            continue
        mids = c.get("member_indices", [])
        if not isinstance(mids, list):
            mids = []

        mids2 = []
        for idx in mids:
            if isinstance(idx, bool):
                continue
            if isinstance(idx, int) and 0 <= idx < k and idx not in seen:
                seen.add(idx)
                mids2.append(idx)
        if not mids2:
            continue

        cid = c.get("cluster_id", None)
        if not isinstance(cid, int):
            cid = next_cid
        next_cid = max(next_cid, cid + 1)

        cleaned.append({
            "cluster_id": cid,
            "member_indices": mids2,
            "canonical_meaning": str(c.get("canonical_meaning", "")).strip(),
            "representative_answer": str(c.get("representative_answer", "")).strip(),
        })

    missing = [i for i in range(k) if i not in seen]
    if missing:
        cleaned.append({
            "cluster_id": next_cid,
            "member_indices": missing,
            "canonical_meaning": "Unassigned / unclear (auto-repaired)",
            "representative_answer": "",
        })

    assignments = [-1] * k
    for c in cleaned:
        for idx in c["member_indices"]:
            assignments[idx] = c["cluster_id"]

    return {"clusters": cleaned, "assignments": assignments}

# def _softmax(logits: List[float]) -> List[float]:
#     if not logits:
#         return []
#     mx = max(logits)
#     exps = [math.exp(x - mx) for x in logits]
#     s = sum(exps)
#     return [e / s for e in exps] if s > 0 else [1.0 / len(logits)] * len(logits)

# def _js_divergence(p: List[float], q: List[float], log_base: float = 2.0) -> float:
#     # assumes p,q sum to 1 and are same length
#     m = [(pi + qi) * 0.5 for pi, qi in zip(p, q)]

#     def kl(a: List[float], b: List[float]) -> float:
#         out = 0.0
#         for ai, bi in zip(a, b):
#             if ai <= 0.0:
#                 continue
#             out += ai * (math.log(ai / bi) / math.log(log_base))
#         return out

#     return 0.5 * kl(p, m) + 0.5 * kl(q, m)
def _softmax(logits: List[float]) -> List[float]:
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    s = sum(exps)
    return [e / s for e in exps] if s > 0 else [1.0 / len(logits)] * len(logits)

def _js_divergence(p: List[float], q: List[float], log_base: float = 2.0) -> float:
    m = [(pi + qi) * 0.5 for pi, qi in zip(p, q)]
    lb = math.log(log_base)

    def kl(a: List[float], b: List[float]) -> float:
        out = 0.0
        for ai, bi in zip(a, b):
            if ai <= 0.0:
                continue
            # Here bi must be > 0, because m contains at least 0.5*p_true, and p_true softmax is strictly positive
            out += ai * (math.log(ai / bi) / lb)
        return out

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

# ----------------- Uncertainty & Cal stubs -----------------
def score_single_answer_with_response_llm(
    response_llm,
    question: str,
    gt_str: str,
    answer: str,
    max_tokens: int = 64,
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_retries: int = 1,
    trace_writer=None,
    sample_idx: Optional[int] = None,
    turn_id: Optional[int] = None,
    answer_idx: Optional[int] = None,
) -> int:
    messages = build_single_answer_score_messages(question, gt_str, answer)

    last_err: Optional[Exception] = None
    prompt_suffix = ""

    for _ in range(max_retries + 1):
        msgs = messages
        if prompt_suffix:
            msgs = msgs[:-1] + [{"role": "user", "content": msgs[-1]["content"] + prompt_suffix}]

        call_id = trace_writer.new_call_id() if (trace_writer and hasattr(trace_writer, "new_call_id")) else None
        if trace_writer:
            log_request(
                trace_writer,
                call_id=call_id,
                llm_name="ResponseLLM",
                call_site="score_single_answer",
                sample_idx=sample_idx,
                turn_id=turn_id,
                messages=msgs,
                gen_args={"answer_idx": answer_idx},
            )

        resp_out = response_llm.generate_with_meta(
            messages=msgs,
            K_sample=1,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=None,
        )
        texts = resp_out.get("texts", [])
        meta = resp_out.get("meta", None)
        raw = (texts[0] if texts else "").strip()

        if trace_writer:
            log_response(
                trace_writer,
                call_id=call_id,
                llm_name="ResponseLLM",
                call_site="score_single_answer",
                sample_idx=sample_idx,
                turn_id=turn_id,
                outputs=texts if isinstance(texts, list) else [str(texts)],
                meta=meta,
            )

        try:
            parsed = _safe_json_loads(raw)
            lvl = _validate_level(parsed.get("correctness_level", 0))
            return lvl
        except Exception as e:
            last_err = e
            prompt_suffix = "\n\nIMPORTANT: Return ONLY valid JSON like {\"correctness_level\": 0}."

    # Assign 0 score on failure
    return 0

def score_answers_and_bucket_artifact(
    answer_samples: List[GeneratedSample],
    sample: Dict[str, Any],
    *,
    response_llm,
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_tokens: int = 64,
    max_retries: int = 1,
    trace_writer=None,
    sample_idx: Optional[int] = None,
    turn_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    if not answer_samples or response_llm is None:
        return None

    question = _get_question_from_sample(sample)
    gt = _get_ground_truth_from_sample(sample)
    if not question or gt is None:
        return None
    gt_str = _gt_to_string(gt)

    answers = [(s.text or "").strip() for s in answer_samples]
    K = len(answers)

    # 1) Score individually
    levels: List[int] = []
    for i, a in enumerate(answers):
        lvl = score_single_answer_with_response_llm(
            response_llm=response_llm,
            question=question,
            gt_str=gt_str,
            answer=a,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            max_retries=max_retries,
            trace_writer=trace_writer,
            sample_idx=sample_idx,
            turn_id=turn_id,
            answer_idx=i,
        )
        levels.append(lvl)

    # 2) Bucket by score (clustering)
    buckets: Dict[int, List[int]] = {k: [] for k in range(5)}
    for i, lvl in enumerate(levels):
        buckets[lvl].append(i)

    clusters: List[Dict[str, Any]] = []
    # Use lvl (0..4) directly as cluster_id
    for lvl in range(5):
        mids = buckets[lvl]
        if not mids:
            continue
        rep = answers[mids[0]] if mids else ""
        clusters.append({
            "cluster_id": lvl,
            "member_indices": mids,
            "canonical_meaning": f"Bucketed by correctness_level={lvl}",
            "representative_answer": rep,
            "correctness_level": lvl,
        })

    assignments = [-1] * K
    for lvl in range(5):
        for i in buckets[lvl]:
            assignments[i] = lvl

    return {
        "clusters": clusters,
        "assignments": assignments,
        "K": K,
        "answers": answers,
        "levels": levels,   
    }

def cluster_and_score_with_response_llm(
    response_llm,
    question: str,
    gt_str: str,
    answers: List[str],
    max_tokens: int = 768,
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_retries: int = 1,
    trace_writer=None,
    sample_idx: Optional[int] = None,
    turn_id: Optional[int] = None,
) -> Dict[str, Any]:
    messages = build_cluster_and_score_messages(question, gt_str, answers)

    last_err: Optional[Exception] = None
    prompt_suffix = ""

    for _ in range(max_retries + 1):
        if prompt_suffix:
            messages = messages[:-1] + [{"role": "user", "content": messages[-1]["content"] + prompt_suffix}]

        call_id = trace_writer.new_call_id() if (trace_writer and hasattr(trace_writer, "new_call_id")) else None
        if trace_writer:
            log_request(
                trace_writer,
                call_id=call_id,
                llm_name="ResponseLLM",
                call_site="cluster_and_score",
                sample_idx=sample_idx,
                turn_id=turn_id,
                messages=messages,
            )
        resp_out = response_llm.generate_with_meta(
            messages=messages,
            K_sample=1,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=None,
        )
        texts = resp_out.get("texts", [])
        meta = resp_out.get("meta", None)
        raw = (texts[0] if texts else "").strip()
        
        if trace_writer:
            log_response(
                trace_writer,
                call_id=call_id,
                llm_name="ResponseLLM",
                call_site="cluster_and_score",
                sample_idx=sample_idx,
                turn_id=turn_id,
                outputs=texts if isinstance(texts, list) else [str(texts)],
                meta=meta,
            )
        try:
            parsed = _safe_json_loads(raw)
            return _validate_and_repair_clusters_with_levels(parsed, k=len(answers))
        except Exception as e:
            last_err = e
            prompt_suffix = "\n\nIMPORTANT: Return ONLY valid JSON strictly matching the schema."

    raise RuntimeError(f"ResponseLLM cluster+score failed: {last_err}")

def prepare_score_cluster_artifact(
    answer_samples: List[GeneratedSample],
    sample: Dict[str, Any],
    *,
    response_llm,
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_tokens: int = 64,
    max_retries: int = 1,
    trace_writer=None,
    sample_idx: Optional[int] = None,
    turn_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    if not answer_samples or response_llm is None:
        return None

    question = _get_question_from_sample(sample)
    gt = _get_ground_truth_from_sample(sample)
    if not question or gt is None:
        return None
    gt_str = _gt_to_string(gt)

    answers = [(s.text or "").strip() for s in answer_samples]
    K = len(answers)

    # 1) Score individually
    levels: List[int] = []
    for i, a in enumerate(answers):
        lvl = score_single_answer_with_response_llm(
            response_llm=response_llm,
            question=question,
            gt_str=gt_str,
            answer=a,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            max_retries=max_retries,
            trace_writer=trace_writer,
            sample_idx=sample_idx,
            turn_id=turn_id,
            answer_idx=i,
        )
        levels.append(lvl)

    # 2) Bucket by score (clustering)
    buckets: Dict[int, List[int]] = {k: [] for k in range(5)}
    for i, lvl in enumerate(levels):
        buckets[lvl].append(i)

    clusters: List[Dict[str, Any]] = []
    # Use lvl (0..4) directly as cluster_id
    for lvl in range(5):
        mids = buckets[lvl]
        if not mids:
            continue
        rep = answers[mids[0]] if mids else ""
        clusters.append({
            "cluster_id": lvl,
            "member_indices": mids,
            "canonical_meaning": f"Bucketed by correctness_level={lvl}",
            "representative_answer": rep,
            "correctness_level": lvl,
        })

    assignments = [-1] * K
    for lvl in range(5):
        for i in buckets[lvl]:
            assignments[i] = lvl

    return {
        "clusters": clusters,
        "assignments": assignments,
        "K": K,
        "answers": answers,
        "levels": levels,   
    }

def prepare_semantic_cluster_artifact(
    answer_samples, sample, *,
    response_llm,
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
    max_retries: int = 3,   # Suggested >=2
    trace_writer=None,
    sample_idx=None,
    turn_id=None,
):
    if not answer_samples or response_llm is None:
        return None

    question = _get_question_from_sample(sample)
    if not question:
        return None

    answers = [(s.text or "").strip() for s in answer_samples]
    K = len(answers)

    base_messages = build_semantic_cluster_messages(question, answers)

    prompt_suffix = ""
    last_err: Optional[Exception] = None

    for _ in range(max_retries + 1):
        messages = base_messages
        if prompt_suffix:
            messages = messages[:-1] + [{"role": "user", "content": messages[-1]["content"] + prompt_suffix}]

        out = response_llm.generate_with_meta(
            messages=messages,
            K_sample=1,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=None,
        )
        raw = (out.get("texts", [""])[0] or "").strip()

        try:
            if not raw:
                raise ValueError("Empty ResponseLLM output")
            parsed = _safe_json_loads(raw)                # The next step will enhance it
            parsed = _validate_and_repair_semantic_clusters(parsed, k=K)
            return {
                "K": K,
                "answers": answers,
                "semantic_clusters": parsed["clusters"],
                "semantic_assignments": parsed["assignments"],
            }
        except Exception as e:
            last_err = e
            prompt_suffix = (
                "\n\nIMPORTANT:\n"
                "Return ONLY valid JSON. No markdown. No extra text.\n"
                "All keys/strings MUST use double quotes.\n"
                "Schema:\n"
                "{\n"
                '  "clusters": [\n'
                "    {\n"
                '      "cluster_id": 0,\n'
                '      "member_indices": [0, 1],\n'
                '      "canonical_meaning": "....",\n'
                '      "representative_answer": "...."\n'
                "    }\n"
                "  ]\n"
                "}\n"
            )

    raise RuntimeError(f"prepare_semantic_cluster_artifact JSON parse failed: {repr(last_err)}")
# def prepare_semantic_cluster_artifact(
#     answer_samples: List[GeneratedSample],
#     sample: Dict[str, Any],
#     *,
#     response_llm,
#     temperature: float = 0.0,
#     top_p: float = 1.0,
#     max_tokens: int = 256,
#     max_retries: int = 1,
#     trace_writer=None,
#     sample_idx: Optional[int] = None,
#     turn_id: Optional[int] = None,
# ) -> Optional[Dict[str, Any]]:
#     if not answer_samples or response_llm is None:
#         return None

#     question = _get_question_from_sample(sample)
#     if not question:
#         return None

#     answers = [(s.text or "").strip() for s in answer_samples]
#     K = len(answers)

#     messages = build_semantic_cluster_messages(question, answers)

#     # Call LLM (do semantic clustering only)
#     call_id = trace_writer.new_call_id() if trace_writer else None
#     # if trace_writer:
#     #     log_request(
#     #         trace_writer,
#     #         call_id=call_id,
#     #         llm_name="ResponseLLM",
#     #         call_site="semantic_cluster",
#     #         sample_idx=sample_idx,
#     #         turn_id=turn_id,
#     #         messages=messages,
#     #         gen_args=None,
#     #     )

#     resp_out = response_llm.generate_with_meta(
#         messages=messages, K_sample=1,
#         max_tokens=max_tokens,
#         temperature=temperature, top_p=top_p, stop=None
#     )
#     raw = (resp_out.get("texts", [""])[0] or "").strip()

#     # if trace_writer:
#     #     log_response(trace_writer, call_id, "ResponseLLM", "semantic_cluster",
#     #                  sample_idx, turn_id, resp_out.get("texts", []), resp_out.get("meta", None))

#     parsed = _safe_json_loads(raw)
#     parsed = _validate_and_repair_semantic_clusters(parsed, k=K)

#     return {
#         "K": K,
#         "answers": answers,
#         "semantic_clusters": parsed["clusters"],
#         "semantic_assignments": parsed["assignments"],
#     }

def prepare_cluster_and_score_artifact(
    answer_samples: List[GeneratedSample],
    sample: Dict[str, Any],
    *,
    response_llm,
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_tokens: int = 64,      
    max_retries: int = 1,
    trace_writer=None,
    sample_idx: Optional[int] = None,
    turn_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    # Score answers individually + cluster by score
    return score_answers_and_bucket_artifact(
        answer_samples=answer_samples,
        sample=sample,
        response_llm=response_llm,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        max_retries=max_retries,
        trace_writer=trace_writer,
        sample_idx=sample_idx,
        turn_id=turn_id,
    )

def prepare_semantic_cluster_then_score_artifact(
    answer_samples: List[GeneratedSample],
    sample: Dict[str, Any],
    *,
    response_llm,
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_tokens_cluster: int = 256,
    max_tokens_score: int = 64,
    max_retries: int = 1,
    trace_writer=None,
    sample_idx: Optional[int] = None,
    turn_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    # 1) Semantic clustering
    sem = prepare_semantic_cluster_artifact(
        answer_samples=answer_samples,
        sample=sample,
        response_llm=response_llm,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens_cluster,
        max_retries=max_retries,
        trace_writer=trace_writer,
        sample_idx=sample_idx,
        turn_id=turn_id,
    )
    if not sem:
        return None

    question = _get_question_from_sample(sample)
    gt = _get_ground_truth_from_sample(sample)
    if not question or gt is None:
        return None
    gt_str = _gt_to_string(gt)

    answers = sem["answers"]
    clusters = sem["semantic_clusters"]

    # 2) Score each semantic cluster (Option A: score using the representative answer)
    scored_clusters = []
    for c in clusters:
        mids = c.get("member_indices", [])
        if not mids:
            lvl = 0
            rep = ""
        else:
            rep_idx = min(mids)
            rep = answers[rep_idx] if 0 <= rep_idx < len(answers) else ""
            lvl = score_single_answer_with_response_llm(
                response_llm=response_llm,
                question=question,
                gt_str=gt_str,
                answer=rep,
                max_tokens=max_tokens_score,
                temperature=0.0,
                top_p=1.0,
                max_retries=max_retries,
                trace_writer=trace_writer,
                sample_idx=sample_idx,
                turn_id=turn_id,
                answer_idx=rep_idx,
            )

        scored_clusters.append({
            "cluster_id": c.get("cluster_id"),
            "member_indices": mids,
            "canonical_meaning": c.get("canonical_meaning", ""),
            "representative_answer": c.get("representative_answer", rep),
            "correctness_level": int(lvl),
        })

    # 3) Return unified artifact
    return {
        "K": sem["K"],
        "answers": answers,
        "semantic_clusters": scored_clusters,
        "semantic_assignments": sem["semantic_assignments"],
    }

def compute_aleatoric_uncertainty(
    score_artifact: Dict[str, Any],
) -> float:
    """
    Pure function. No LLM calls.

    Expected artifact keys:
      - "clusters": list of clusters, each has member_indices and correctness_level in [0..4]
      - "K": number of sampled answers
    """
    if not score_artifact:
        return 0.0

    clusters = score_artifact.get("clusters", None)
    K = score_artifact.get("K", None)

    if not isinstance(clusters, list) or not isinstance(K, int) or K <= 0:
        return 0.0

    ale = 0.0
    for c in clusters:
        if not isinstance(c, dict):
            continue
        mids = c.get("member_indices", [])
        if not isinstance(mids, list):
            continue
        q_c = len(mids) / float(K)

        level = c.get("correctness_level", 0)
        try:
            level = int(float(level))
        except Exception:
            level = 0
        if level < 0: level = 0
        if level > 4: level = 4

        s_c = level / 4.0
        ale += q_c * (1.0 - s_c)

    return max(0.0, min(1.0, ale))

def compute_aleatoric_uncertainty_from_semantic_scored(art: Dict[str, Any]) -> float:
    if not art:
        return 0.0
    clusters = art.get("semantic_clusters", None)
    K = art.get("K", None)
    if not isinstance(clusters, list) or not isinstance(K, int) or K <= 0:
        return 0.0

    ale = 0.0
    for c in clusters:
        mids = c.get("member_indices", [])
        if not isinstance(mids, list) or len(mids) == 0:
            continue
        q_c = len(mids) / float(K)
        lvl = _validate_level(c.get("correctness_level", 0))
        s_c = lvl / 4.0
        ale += q_c * (1.0 - s_c)

    return max(0.0, min(1.0, ale))

def compute_epistemic_uncertainty(
    semantic_artifact: Dict[str, Any],
) -> float:
    """
    Epistemic uncertainty as semantic entropy of cluster distribution q(c)=|c|/K.

    Expected artifact keys:
      - "clusters": list of clusters, each has member_indices
      - "K": number of sampled answers
    """
    if not semantic_artifact:
        return 0.0

    clusters = semantic_artifact.get("semantic_clusters", None)
    K = semantic_artifact.get("K", None)

    if not isinstance(clusters, list) or not isinstance(K, int) or K <= 0:
        return 0.0

    # Compute q(c)
    q_list: List[float] = []
    for c in clusters:
        if not isinstance(c, dict):
            continue
        mids = c.get("member_indices", [])
        if not isinstance(mids, list):
            continue
        n_c = len(mids)
        if n_c <= 0:
            continue
        q_list.append(n_c / float(K))

    if not q_list:
        return 0.0

    # Entropy
    log_fn = lambda x: math.log(x, 2)

    H = 0.0
    for q in q_list:
        if q > 0.0:
            H -= q * log_fn(q)

    # Normalized entropy in [0,1]
    m = len(q_list)  # number of non-empty clusters
    if m <= 1:
        return 0.0
    H_max = log_fn(m)  # max entropy when uniform over m clusters
    if H_max <= 0:
        return 0.0
    return max(0.0, min(1.0, H / H_max))


# def compute_cal_from_semantic_scored_artifact(
#     sem_score_art: Dict[str, Any],
#     *,
#     beta: float = 4.0,          # Intensity parameter: larger values bias towards high-score clusters
#     normalize_level: bool = True,  # True: s=level/4; False: s=level
#     alpha: float = 1e-3,        # Laplace/Dirichlet smoothing to prevent numerical issues
#     log_base: float = 2.0,
# ) -> Dict[str, Any]:
#     """
#     Input: sem_score_art = {
#       "K": int,
#       "semantic_clusters": [{"member_indices": [...], "correctness_level": int, ...}, ...],
#       ...
#     }
#
#     Output:
#       {
#         "cal_js": float,
#         "p_true": [...],
#         "q_model": [...],
#         "levels": [...],
#         "cluster_sizes": [...],
#       }
#     """
#     if not sem_score_art:
#         return {"cal_js": 0.0, "p_true": [], "q_model": [], "levels": [], "cluster_sizes": []}
#
#     clusters = sem_score_art.get("semantic_clusters", [])
#     K = sem_score_art.get("K", 0)
#     if not isinstance(clusters, list) or not isinstance(K, int) or K <= 0:
#         return {"cal_js": 0.0, "p_true": [], "q_model": [], "levels": [], "cluster_sizes": []}
#
#     # 1) q_model: Semantic cluster frequency
#     sizes = []
#     levels = []
#     for c in clusters:
#         mids = c.get("member_indices", [])
#         n_c = len(mids) if isinstance(mids, list) else 0
#         sizes.append(n_c)
#
#         lvl = c.get("correctness_level", 0)
#         try:
#             lvl = int(float(lvl))
#         except Exception:
#             lvl = 0
#         lvl = max(0, min(4, lvl))
#         levels.append(lvl)
#
#     m = len(clusters)
#     q = [(n + alpha) / (K + m * alpha) for n in sizes]  # Smoothed model distribution
#
#     # 2) p_true: softmax(beta * score)
#     if normalize_level:
#         scores = [lvl / 4.0 for lvl in levels]  # 0..1
#     else:
#         scores = [float(lvl) for lvl in levels] # 0..4
#
#     logits = [beta * s for s in scores]
#     p = _softmax(logits)
#
#     # p can also be smoothed similarly (optional, but generally unnecessary as softmax is strictly positive)
#     # p = [(pi + alpha) / (1.0 + m * alpha) for pi in p]
#
#     cal = _js_divergence(p, q, log_base=log_base)
#
#     return {
#         "cal_js": cal,
#         "p_true": p,
#         "q_model": q,
#         "levels": levels,
#         "cluster_sizes": sizes,
#     }
def compute_cal_over_score_bins(
    sem_score_art: Dict[str, Any],
    *,
    beta: float = 1.0,
    log_base: float = 2.0,
) -> Dict[str, Any]:
    """
    sem_score_art expects:
      - K: int
      - semantic_clusters: list[ {member_indices: [...], correctness_level: int} ]

    Returns:
      - cal_js
      - p_true_bins: length 5
      - q_model_bins: length 5
      - counts: length 5
    """
    if not sem_score_art:
        return {"cal_js": 0.0, "p_true_bins": None, "q_model_bins": None, "counts": None}

    clusters = sem_score_art.get("semantic_clusters", [])
    K = sem_score_art.get("K", 0)
    if not isinstance(clusters, list) or not isinstance(K, int) or K <= 0:
        return {"cal_js": 0.0, "p_true_bins": None, "q_model_bins": None, "counts": None}

    # q_model over bins: count answers per level (0..4)
    counts = [0] * 5
    for c in clusters:
        if not isinstance(c, dict):
            continue
        mids = c.get("member_indices", [])
        n_c = len(mids) if isinstance(mids, list) else 0

        lvl = c.get("correctness_level", 0)
        try:
            lvl = int(float(lvl))
        except Exception:
            lvl = 0
        lvl = max(0, min(4, lvl))

        counts[lvl] += n_c

    q = [cnt / float(K) for cnt in counts]

    # p_true over bins: softmax(beta * [0,1,2,3,4])
    logits = [beta * s for s in range(5)]
    p = _softmax(logits)

    cal = _js_divergence(p, q, log_base=log_base)
    return {"cal_js": cal, "p_true_bins": p, "q_model_bins": q, "counts": counts}
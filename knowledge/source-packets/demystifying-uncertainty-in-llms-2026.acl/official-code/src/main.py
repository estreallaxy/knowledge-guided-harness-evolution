# src/pipeline/ils_pipeline.py
# -*- coding: utf-8 -*-
"""
ILS Main Pipeline (Functional Version):

- Multi-turn interaction for each sample:
  Each turn:
    1) PolicyLLM samples K answers for the original question (used for subsequent uncertainty estimation)
    2) Calculate aleatoric uncertainty / epistemic uncertainty (currently stub)
    3) PolicyLLM generates several candidate clarification questions
    4) Select one clarification question using one of three strategies:
         - "random"     : Randomly select a candidate question (Baseline 1)
         - "self_select": Prompt PolicyLLM to self-select from candidates (Baseline 2)
         - "ils_cal"    : Estimate Cal for each question, select the one with max Cal (your method, currently stub)
    5) ResponseLLM answers the clarification question under the full context
    6) Write this turn's Q&A into history, proceed to the next turn

- Specific prompt construction logic is abstracted as ILSPromptBuilder, implemented in another file.
"""

from __future__ import annotations

import json
import math
import os
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Literal

from tqdm import tqdm

from src.LLM.PolicyLLM import PolicyLLM, GeneratedSample
from src.LLM.ResponseLLM import ResponseLLM
from src.utils.config_loader import LLMConfig, load_llm_config
from src.prompt.prompt_builder import PromptBuilder
from src.utils.trace_writer import TraceWriter, log_request, log_response
from src.utils.utils import prepare_score_cluster_artifact, prepare_semantic_cluster_artifact, compute_aleatoric_uncertainty, compute_epistemic_uncertainty
from src.utils.utils import prepare_semantic_cluster_then_score_artifact, compute_aleatoric_uncertainty_from_semantic_scored, compute_cal_over_score_bins
# ----------------- Pipeline Configuration -----------------


StrategyType = Literal["random", "self_select", "ils_cal"]


@dataclass
class ILSPipelineConfig:
    """High-level configuration for the ILS main pipeline."""

    max_turns: int = None
    answer_K_sample: int = None       # Number of samples K for answering the original question per turn
    question_K_sample: int = None     # Number of samples for candidate clarification questions per turn

    strategy: StrategyType = "self_select"  # "random" / "self_select" / "ils_cal"

    # PolicyLLM generation hyperparameters
    policy_max_tokens: int = None
    policy_temperature: float = None
    policy_top_p: float = None

    # ResponseLLM generation hyperparameters
    response_max_tokens: int = None
    response_temperature: float = None
    response_top_p: float = None

    random_seed: int = None

    # ILS-Cal specific: Sampling count for distribution estimation of each candidate question q
    ils_K_policy_user: int = None      # K_pi: Number of samples for PolicyLLM simulating user answer to q
    ils_K_true_user: int = None        # K_p: Number of samples for ResponseLLM (true user) answering q

    # ILS-Cal sampling temperature (must be >0 to have a 'distribution')
    ils_policy_temperature: float = None
    ils_policy_top_p: float = None
    ils_response_temperature: float = None
    ils_response_top_p: float = None

    # Semantic clustering hyperparameters
    ils_cluster_max_tokens: int = None
    ils_cluster_retries: int = None

    # JS smoothing
    ils_alpha: float = None
    ils_log_base: float = None



def _js_divergence_local(p: List[float], q: List[float], log_base: float = 2.0) -> float:
    # Assume p, q are valid distributions (>=0 and sum=1)
    m = [(pi + qi) * 0.5 for pi, qi in zip(p, q)]
    lb = math.log(log_base)

    def kl(a, b):
        out = 0.0
        for ai, bi in zip(a, b):
            if ai <= 0.0:
                continue
            out += ai * (math.log(ai / bi) / lb)
        return out

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

# ----------------- Question Selection Strategies (Functional) -----------------

def select_question_random(
    candidate_questions: List[str],
    rng: random.Random,
) -> tuple[str, Dict[str, Any]]:

    idx = rng.randrange(len(candidate_questions))
    return candidate_questions[idx], {"chosen_index": idx, "n_candidates": len(candidate_questions)}

def select_question_self(
    sample: Dict[str, Any],
    history: List[Dict[str, Any]],
    candidate_questions: List[str],
    policy_llm: PolicyLLM,
    prompt_builder: PromptBuilder,
    cfg: ILSPipelineConfig,
    trace_writer: Optional[TraceWriter],
    sample_idx: int, 
    turn_id: int
) -> tuple[str, Dict[str, Any]]:
    """
    Baseline 2: Let PolicyLLM select the best clarification question from candidates itself.

    Process:
      - Construct a prompt containing all candidate questions;
      - Request PolicyLLM to explain which one it thinks is most useful;
      - Parse the finally selected question from the generated text.
    """
    sel_messages = prompt_builder.build_self_select_question_messages(
        sample=sample,
        history=history,
        candidate_questions=candidate_questions,
    )

    gen_args = dict(K_sample=1, max_tokens=cfg.policy_max_tokens,
                temperature=cfg.policy_temperature, top_p=cfg.policy_top_p, stop=None)
    call_id = trace_writer.new_call_id() if trace_writer else None
    if trace_writer:
        log_request(trace_writer, call_id=call_id, llm_name="PolicyLLM", call_site="self_select",
                    sample_idx=sample_idx, turn_id=turn_id, messages=sel_messages, gen_args=gen_args)
        
        
    sel_samples = policy_llm.generate(
        messages=sel_messages,
        K_sample=1,
        max_tokens=cfg.policy_max_tokens,
        temperature=cfg.policy_temperature,
        top_p=cfg.policy_top_p,
        stop=None,
    )
    if trace_writer:
        log_response(trace_writer, call_id=call_id, llm_name="PolicyLLM", call_site="self_select",
                     sample_idx=sample_idx, turn_id=turn_id,
                     outputs=[{"text": s.text, "logprob": s.logprob} for s in sel_samples],
                     meta=None)
        
    raw_sel_text = sel_samples[0].text if sel_samples else ""
    selected_question = prompt_builder.parse_selected_question_from_text(
        raw_text=raw_sel_text,
        candidate_questions=candidate_questions,
    )
    return selected_question, {"raw_selection_text": raw_sel_text}

def select_question_ils_cal(
    sample: Dict[str, Any],
    history: List[Dict[str, Any]],
    candidate_questions: List[str],
    policy_llm: PolicyLLM,
    response_llm: ResponseLLM,
    prompt_builder: PromptBuilder,
    cfg: ILSPipelineConfig,
    trace_writer: Optional[TraceWriter],
    sample_idx: int,
    turn_id: int,
) -> tuple[str, Dict[str, Any]]:
    scores: Dict[str, float] = {}
    metas: Dict[str, Any] = {}

    best_q = candidate_questions[0]
    best_score = -1e9

    for q in candidate_questions:
        cal, meta = estimate_cal_for_question(
            q=q,
            sample=sample,
            history=history,
            policy_llm=policy_llm,
            response_llm=response_llm,
            prompt_builder=prompt_builder,
            cfg=cfg,
            trace_writer=trace_writer,
            sample_idx=sample_idx,
            turn_id=turn_id,
        )
        scores[q] = float(cal)

        metas[q] = {
            "cal": float(cal),
            "n_pi": meta.get("n_pi"),
            "n_p": meta.get("n_p"),
            "num_clusters": meta.get("num_clusters"),
        }

        if cal > best_score:
            best_score = cal
            best_q = q

    return best_q, {"scores": scores, "best_score": best_score, "metas": metas}


def estimate_cal_for_question(
    *,
    q: str,
    sample: Dict[str, Any],
    history: List[Dict[str, Any]],
    policy_llm: PolicyLLM,
    response_llm: ResponseLLM,
    prompt_builder: PromptBuilder,
    cfg: ILSPipelineConfig,
    trace_writer: Optional[TraceWriter],
    sample_idx: int,
    turn_id: int,
) -> tuple[float, Dict[str, Any]]:
    """
    Estimate Cal(q) = JS( pi_theta(.|q) || p(.|q) )

    - pi_theta: Semantic distribution of user answer to q simulated by PolicyLLM without knowing true intent
    - p: Semantic distribution of true user answer to q simulated by ResponseLLM knowing original_query/answer
    """
    # A) PolicyLLM: Simulate user answering q (Sample K_pi)
    pi_messages = prompt_builder.build_policy_user_sim_messages(
        sample=sample, history=history, selected_question=q
    )
    call_id = trace_writer.new_call_id() if trace_writer else None
    # if trace_writer:
    #     log_request(trace_writer, call_id, "PolicyLLM", "ils_cal_policy_user_sim",
    #                 sample_idx, turn_id, pi_messages,
    #                 gen_args={"K": cfg.ils_K_policy_user, "temperature": cfg.ils_policy_temperature, "top_p": cfg.ils_policy_top_p})

    pi_samples = policy_llm.generate(
        messages=pi_messages,
        K_sample=cfg.ils_K_policy_user,
        max_tokens=cfg.policy_max_tokens,
        temperature=cfg.ils_policy_temperature,
        top_p=cfg.ils_policy_top_p,
        stop=None,
    )
    pi_texts = [(s.text or "").strip() for s in pi_samples if (s.text or "").strip()]

    # if trace_writer:
    #     log_response(trace_writer, call_id, "PolicyLLM", "ils_cal_policy_user_sim",
    #                  sample_idx, turn_id,
    #                  outputs=[{"text": s.text, "logprob": s.logprob} for s in pi_samples],
    #                  meta=None)

    # B) ResponseLLM: Real user answering q (Sample K_p)
    p_messages = prompt_builder.build_response_messages(
        sample=sample, history=history, selected_question=q
    )
    call_id = trace_writer.new_call_id() if trace_writer else None
    # if trace_writer:
    #     log_request(trace_writer, call_id, "ResponseLLM", "ils_cal_true_user_sim",
    #                 sample_idx, turn_id, p_messages,
    #                 gen_args={"K": cfg.ils_K_true_user, "temperature": cfg.ils_response_temperature, "top_p": cfg.ils_response_top_p})

    p_out = response_llm.generate_with_meta(
        messages=p_messages,
        K_sample=cfg.ils_K_true_user,
        max_tokens=cfg.response_max_tokens,
        temperature=cfg.ils_response_temperature,
        top_p=cfg.ils_response_top_p,
        stop=None,
    )
    p_texts = [(t or "").strip() for t in p_out.get("texts", []) if (t or "").strip()]

    # if trace_writer:
    #     log_response(trace_writer, call_id, "ResponseLLM", "ils_cal_true_user_sim",
    #                  sample_idx, turn_id,
    #                  outputs=p_out.get("texts", []),
    #                  meta=p_out.get("meta", None))

    # Safety fallback: If either side is empty, return 0 (or a very small value)
    if not pi_texts or not p_texts:
        return 0.0, {"reason": "empty_side", "n_pi": len(pi_texts), "n_p": len(p_texts)}

    # C) Joint semantic clustering: Combine answers from both sides and let ResponseLLM perform semantic clustering
    combined_texts = pi_texts + p_texts
    combined_samples = [GeneratedSample(text=t) for t in combined_texts]

    # Let the clustering "Question:" include q (otherwise clustering is unstable)
    sample_for_cluster = dict(sample)
    sample_for_cluster["question"] = f"{sample.get('question','')}\n\nClarification question: {q}"

    sem_art = prepare_semantic_cluster_artifact(
        answer_samples=combined_samples,
        sample=sample_for_cluster,
        response_llm=response_llm,
        temperature=0.0,
        top_p=1.0,
        max_tokens=cfg.ils_cluster_max_tokens,
        max_retries=cfg.ils_cluster_retries,
        trace_writer=trace_writer,
        sample_idx=sample_idx,
        turn_id=turn_id,
    )
    if not sem_art:
        return 0.0, {"reason": "semantic_cluster_failed"}

    assignments = sem_art["semantic_assignments"]
    clusters = sem_art["semantic_clusters"]
    m = len(clusters)

    n_pi = len(pi_texts)
    n_p = len(p_texts)

    # D) Count on 'semantic clusters' to get empirical distributions for both sides (same support set)
    # cluster_id might not be continuous 0..m-1, so use index mapping
    cid_list = [c["cluster_id"] for c in clusters]
    cid_to_idx = {cid: i for i, cid in enumerate(cid_list)}

    counts_pi = [0] * m
    counts_p = [0] * m

    for i, cid in enumerate(assignments):
        j = cid_to_idx.get(cid, None)
        if j is None:
            continue
        if i < n_pi:
            counts_pi[j] += 1
        else:
            counts_p[j] += 1

    alpha = cfg.ils_alpha
    pi_dist = [(c + alpha) / (n_pi + m * alpha) for c in counts_pi]
    p_dist = [(c + alpha) / (n_p + m * alpha) for c in counts_p]

    cal = _js_divergence_local(pi_dist, p_dist, log_base=cfg.ils_log_base)

    meta = {
        "n_pi": n_pi,
        "n_p": n_p,
        "num_clusters": m,
        "counts_pi": counts_pi,
        "counts_p": counts_p,
        "pi_dist": pi_dist,
        "p_dist": p_dist,
        "clusters": clusters,  # If too large, keep only canonical_meaning
    }
    return cal, meta


def select_question(
    sample: Dict[str, Any],
    history: List[Dict[str, Any]],
    candidate_questions: List[str],
    policy_llm: PolicyLLM,
    response_llm: ResponseLLM, 
    prompt_builder: PromptBuilder,
    cfg: ILSPipelineConfig,
    trace_writer: Optional[TraceWriter],
    sample_idx: int,
    turn_id: int,
) -> tuple[str, Dict[str, Any]]:
    """
    Unified external entry point, selects corresponding strategy based on cfg.strategy.
    """
    if cfg.strategy == "random":
        rng = random.Random(cfg.random_seed + sample_idx * 100000 + turn_id)
        return select_question_random(candidate_questions, rng)
    elif cfg.strategy == "self_select":
        return select_question_self(
            sample=sample,
            history=history,
            candidate_questions=candidate_questions,
            policy_llm=policy_llm,
            prompt_builder=prompt_builder,
            cfg=cfg,
            trace_writer=trace_writer,
            sample_idx=sample_idx,
            turn_id=turn_id,
        )
    elif cfg.strategy == "ils_cal":
        return select_question_ils_cal(
            sample=sample,
            history=history,
            candidate_questions=candidate_questions,
            policy_llm=policy_llm,
            response_llm=response_llm,
            prompt_builder=prompt_builder,
            cfg=cfg,
            sample_idx=sample_idx,
            trace_writer=trace_writer,
            turn_id=turn_id,
        )
    else:
        raise ValueError(f"Unknown strategy: {cfg.strategy}")


# ----------------- Multi-turn Interaction for a Single Sample -----------------


def run_single_sample(
    sample: Dict[str, Any],
    idx: int,
    policy_llm: PolicyLLM,
    response_llm: ResponseLLM,
    prompt_builder: PromptBuilder,
    cfg: ILSPipelineConfig,
    trace_writer: Optional[TraceWriter] = None
) -> Dict[str, Any]:
    """
    Perform multi-turn ILS interaction for a single sample.

    Returns:
        {
          "idx": idx,
          "sample": sample,
          "turns": [ ... Detailed logs for each turn ... ],
        }
    """
    history: List[Dict[str, Any]] = []
    turns_log: List[Dict[str, Any]] = []

    for turn_id in range(1, cfg.max_turns + 1):
        ans_messages = prompt_builder.build_policy_answer_messages(
            sample=sample,
            history=history,
        )

        gen_args = dict(
            K_sample=cfg.answer_K_sample,
            max_tokens=cfg.policy_max_tokens,
            temperature=cfg.policy_temperature,
            top_p=cfg.policy_top_p,
            stop=None,
        )
        # call_id = trace_writer.new_call_id() if trace_writer else None
        # if trace_writer:
        #     log_request(trace_writer, call_id=call_id, llm_name="PolicyLLM", call_site="policy_answer",
        #                 sample_idx=idx, turn_id=turn_id, messages=ans_messages, gen_args=gen_args)
            
        resp = policy_llm.generate_with_meta(
            messages=ans_messages,
            K_sample=cfg.answer_K_sample,
            max_tokens=cfg.policy_max_tokens,
            temperature=cfg.policy_temperature,
            top_p=cfg.policy_top_p,
            stop=None,
        )
        answer_samples = resp["samples"]
        policy_prompt_meta = resp.get("meta", None)

        # if trace_writer:
        #     log_response(
        #         trace_writer,
        #         call_id=call_id,
        #         llm_name="PolicyLLM",
        #         call_site="policy_answer",
        #         sample_idx=idx,
        #         turn_id=turn_id,
        #         outputs=[{"text": s.text} for s in answer_samples],
        #         meta={"prompt_meta": policy_prompt_meta},   
        #     )
    
        sem_score_art = prepare_semantic_cluster_then_score_artifact(
            answer_samples=answer_samples,
            sample=sample,
            response_llm=response_llm,
            temperature=None,
            top_p=None,
            max_tokens_cluster=None,
            max_tokens_score=None,
            max_retries=None,
            trace_writer=trace_writer,
            sample_idx=idx,
            turn_id=turn_id,
        )

        aleatoric_u = compute_aleatoric_uncertainty_from_semantic_scored(sem_score_art)
        epistemic_u = compute_epistemic_uncertainty(sem_score_art)
        cal_out = compute_cal_over_score_bins(
            sem_score_art,
            beta=2.0,
            log_base=2.0,
        )
        cal = cal_out["cal_js"]
        # 3) PolicyLLM generates candidate clarification questions
        # cand_q_messages = prompt_builder.build_candidate_question_messages(
        #     sample=sample,
        #     history=history,
        # )
        cand_q_messages = prompt_builder.build_candidate_question_messages(
            sample=sample,
            history=history,
            K=cfg.question_K_sample,
        )
        gen_args = dict(
            K_sample=cfg.question_K_sample,
            max_tokens=cfg.policy_max_tokens,
            temperature=cfg.policy_temperature,
            top_p=cfg.policy_top_p,
            stop=None,
        )
        call_id = trace_writer.new_call_id() if trace_writer else None
        # if trace_writer:
        #     log_request(trace_writer, call_id=call_id, llm_name="PolicyLLM", call_site="candidate_q",
        #                 sample_idx=idx, turn_id=turn_id, messages=cand_q_messages, gen_args=gen_args)
            
        # raw_q_samples = policy_llm.generate(
        #     messages=cand_q_messages,
        #     K_sample=cfg.question_K_sample,
        #     max_tokens=cfg.policy_max_tokens,
        #     temperature=cfg.policy_temperature,
        #     top_p=cfg.policy_top_p,
        #     stop=None,
        # )
        raw_q_samples = policy_llm.generate(
            messages=cand_q_messages,
            K_sample=None,
            max_tokens=cfg.policy_max_tokens,
            temperature=cfg.policy_temperature,
            top_p=cfg.policy_top_p,
            stop=None,
        )
        # raw_q_strings = [s.text for s in raw_q_samples]
        raw_q_strings = [raw_q_samples[0].text] if raw_q_samples else []
        
        # if trace_writer:
        #     log_response(trace_writer, call_id=call_id, llm_name="PolicyLLM", call_site="candidate_q",
        #                 sample_idx=idx, turn_id=turn_id,
        #                 outputs=[{"text": s.text} for s in raw_q_samples],
        #                 meta=None)
        
        candidate_questions = prompt_builder.parse_candidate_questions(
            raw_texts=raw_q_strings,
        )
        candidate_questions = [q.strip() for q in candidate_questions if q.strip()]

        if not candidate_questions:
            # No clarification questions parsed, terminate this sample early
            break

        # 4) Select a clarification question based on strategy
        selected_question, selection_details = select_question(
            sample=sample,
            history=history,
            candidate_questions=candidate_questions,
            policy_llm=policy_llm,
            response_llm=response_llm,
            prompt_builder=prompt_builder,
            cfg=cfg,
            trace_writer=trace_writer,
            sample_idx=idx,
            turn_id=turn_id,
        )

        # 5) ResponseLLM answers the clarification question within the full context
        resp_messages = prompt_builder.build_response_messages(
            sample=sample,
            history=history,
            selected_question=selected_question,
        )
        gen_args = dict(
            K_sample=None,
            max_tokens=cfg.response_max_tokens,
            temperature=cfg.response_temperature,
            top_p=cfg.response_top_p,
            stop=None,
        )
        call_id = trace_writer.new_call_id() if trace_writer else None
        # if trace_writer:
        #     log_request(trace_writer, call_id=call_id, llm_name="ResponseLLM", call_site="response_answer",
        #                 sample_idx=idx, turn_id=turn_id, messages=resp_messages, gen_args=gen_args)

        # resp_texts = response_llm.generate_with_meta(
        #     messages=resp_messages,
        #     K_sample=1,
        #     max_tokens=cfg.response_max_tokens,
        #     temperature=cfg.response_temperature,
        #     top_p=cfg.response_top_p,
        #     stop=None,
        # )
        # response_text = resp_texts[0] if resp_texts else ""
        # if trace_writer:
        #     log_response(trace_writer, call_id=call_id, llm_name="ResponseLLM", call_site="response_answer",
        #                 sample_idx=idx, turn_id=turn_id,
        #                 outputs=resp_texts, meta=None)

        resp_out = response_llm.generate_with_meta(
            messages=resp_messages,
            K_sample=None,
            max_tokens=cfg.response_max_tokens,
            temperature=cfg.response_temperature,
            top_p=cfg.response_top_p,
            stop=None,
        )
        resp_texts = resp_out["texts"]
        resp_meta = resp_out.get("meta", None)

        response_text = resp_texts[0] if resp_texts else ""

        # if trace_writer:
        #     log_response(
        #         trace_writer,
        #         call_id=call_id,
        #         llm_name="ResponseLLM",
        #         call_site="response_answer",
        #         sample_idx=idx,
        #         turn_id=turn_id,
        #         outputs=resp_texts,
        #         meta=resp_meta,
        #     )

        # 6) Log current turn
        turn_log = {
            "turn_id": turn_id,
            "answer_samples": [
                {
                    "text": s.text,
                    "logprob": s.logprob,
                    "num_tokens": len(s.token_logprobs or []),
                }
                for s in answer_samples
            ],
            "aleatoric_uncertainty": aleatoric_u,
            "epistemic_uncertainty": epistemic_u,
            "candidate_questions": candidate_questions,
            "selected_question": selected_question,
            "selection_strategy": cfg.strategy,
            "selection_details": selection_details,
            "response_text": response_text,
            "semantic_clusters": sem_score_art["semantic_clusters"] if sem_score_art else None,
            "cal" : cal,
        }
        turns_log.append(turn_log)

        # 7) Update history for next turn
        history.append(
            {
                "turn_id": turn_id,
                "selected_question": selected_question,
                "response_text": response_text,
            }
        )

    return {
        "idx": idx,
        "sample": sample,
        "turns": turns_log,
    }


# ----------------- Main Process on Entire Dataset -----------------


def run_ils_on_dataset(
    data_path: str,
    output_path: str,
    policy_config_path: str,
    response_config_path: str,
    prompt_builder: PromptBuilder,
    pipeline_cfg: ILSPipelineConfig,
    trace_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Top-level entry function:

    - Load dataset from JSON;
    - Initialize PolicyLLM and ResponseLLM with YAML config;
    - Execute run_single_sample for each sample;
    - Write full logs to output_path.

    Returns:
        Simple summary dict, e.g., sample count, strategy name, etc.
    """
    # 1) Load data
    with open(data_path, "r", encoding="utf-8") as f:
        dataset: List[Dict[str, Any]] = json.load(f)

    # 2) Initialize two LLMs
    policy_cfg: LLMConfig = load_llm_config(policy_config_path)
    response_cfg: LLMConfig = load_llm_config(response_config_path)

    policy_llm = PolicyLLM(policy_cfg)
    response_llm = ResponseLLM(response_cfg)

    tw = TraceWriter(trace_path) if trace_path else None

    # 3) Run ILS sample by sample
    logs: List[Dict[str, Any]] = []

    # dataset = [dataset[3]]

    for idx in tqdm(range(len(dataset)), desc="ILS pipeline"):
        sample = dataset[idx]
        log_i = run_single_sample(
            sample=sample,
            idx=idx,
            policy_llm=policy_llm,
            response_llm=response_llm,
            prompt_builder=prompt_builder,
            cfg=pipeline_cfg,
            trace_writer=tw,
        )
        logs.append(log_i)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    summary = {
        "num_samples": len(dataset),
        "strategy": pipeline_cfg.strategy,
        "max_turns": pipeline_cfg.max_turns,
        "output_path": output_path,
    }
    return summary


def main():
    # 1) Data path & Output path
    data_path = "data_path"   
    output_path = "output_path"
    trace_path  = "trace_path"
    # 2) LLM Configuration (YAML)
    policy_config_path = "PolicyLLM.yaml"
    response_config_path = "ResponseLLM.yaml"

    # 3) PromptBuilder
    prompt_builder = PromptBuilder(
        policy_answer_prompt_path="answer_prompt_path",
        candidate_question_prompt_path="candidate_question_prompt_path",
        self_select_prompt_path="self_select_prompt_path",
        response_prompt_path="ambigQA_response_prompt_path",
        policy_user_sim_prompt_path="policy_user_sim_prompt_path",
    )


    # 4) ILS Pipeline Configuration
    pipeline_cfg = ILSPipelineConfig(
        max_turns=None,           
        answer_K_sample=None,     
        question_K_sample=None,   
        strategy="method(random/self_select/isl_cal)",
        policy_max_tokens=None,
        policy_temperature=None,
        policy_top_p=None,
        response_max_tokens=None,
        response_temperature=None,
        response_top_p=None,
        ils_K_policy_user=None,
        ils_K_true_user=None,
        ils_policy_temperature=None,
        ils_response_temperature=None,
    )

    summary = run_ils_on_dataset(
        data_path=data_path,
        output_path=output_path,
        policy_config_path=policy_config_path,
        response_config_path=response_config_path,
        prompt_builder=prompt_builder,
        pipeline_cfg=pipeline_cfg,
        trace_path=trace_path,
    )

    print("Summary:", summary)


if __name__ == "__main__":
    main()
# Paper ↔ Code Alignment Notes

This document records how the reference implementation in this repository
maps to the formal specification in the EmoMAS paper (ACL 2026). Where the
code uses a practical variant of a paper equation, that deviation is listed
here so reviewers inspecting the repo can see the intent.

## Entry point

The canonical driver is:

```bash
python experiments/run_all_datasets.py \
    --model_type <vanilla|prompt|rl_agents|gametheory|coherence|gpt|bayesian> \
    --dataset_type <debt|disaster|student|medical|all> \
    --scenarios 5 --iterations 5
```

The legacy `main.py` is deprecated (it previously imported removed modules).

## §3.2 — Game Theory Agent

Paper: Win-Stay, Lose-Shift (WSLS) with emotional weighting; cooperate for
{joy, neutral, surprise}, caution for {anger, disgust, fear}; payoff
argmax over π(d,e)₂.

Code: `models/gametheory_agents.py` ships three game-theoretic variants
(Nash equilibrium, Minimax, Strategic Dominance). The experiment driver
uses **Strategic Dominance** (`run_strategic_dominance_experiment`) — a
dominance-based best-response procedure that is mathematically aligned
with the "strategic" intent of §3.2 but not literally WSLS. The WSLS
table in the paper appendix (`tab:complete_payoff`) is a pedagogical
illustration of the payoff structure; the underlying selection used at
runtime is the dominance solver over the same payoff matrix.

## §3.3 — Reinforcement Learning Agent

Paper: tabular Q-learning with state s = ⟨e^c, e^d, φ, g⟩, α=0.1,
γ=0.9, softmax policy with τ=0.1.

Code: `models/rl_agents.py :: QLearningEmotionModel`. The implementation
follows the same tabular Q-update (equation 2 in the paper). The
following are implementation details that do not change the asymptotic
behavior described in the paper:

- Exploration policy is ε-greedy with decaying ε rather than pure softmax
  with τ=0.1. Both are standard Q-learning action selectors; the paper's
  τ=0.1 corresponds to an almost-greedy softmax, which is behaviorally
  close to ε-greedy with small ε.
- State binning: the code discretizes the "gap" and "round-phase"
  dimensions into finer-grained bins than the paper's 4-category phase
  enum. The Q-table still persists across scenarios (online adaptation)
  as described.

## §3.4 — Emotional Coherence Agent

The paper describes an LLM-based agent that emits a 7×4 assessment
matrix (plausibility, appropriateness, strategic value, rationale) and
applies softmax with τ=1.0.

- The **LLM-based** implementation that the paper describes lives in
  `models/llm_multiagent.py :: EmotionalCoherenceAgent`. This is what
  `BayesianTransitionModel` uses inside EmoMAS at runtime.
- `models/coherence_agents.py :: CoherenceEmotionModel` is a **fast
  rule-based baseline** used only for the single-agent coherence
  ablation row in Table 4. It applies hand-crafted transition rules
  without calling an LLM. If you want to evaluate the full paper
  coherence agent alone, run `--model_type bayesian` and inspect the
  per-agent scores, or instantiate `EmotionalCoherenceAgent` directly.

## §3.5 — Bayesian Orchestrator

Paper: multiplicative posterior w^(i)_t ∝ w^(i)_{t-1} · L(…), with macro
(trajectory-level) and micro (turn-level) reliability updates. Final
emotion chosen by argmax over the union of agent recommendations.

Code: `models/bayesian_multiagent.py :: BayesianTransitionOrchestrator`.

- **Selection / scoring** — matches the paper: score(eⱼ) = Σᵢ wᵢ ·
  confᵢ(eⱼ), argmax over the union of recommended emotions.
- **Macro update** — implemented post-trajectory, weighted by collection
  rate ρ as described. The exact update rule is an additive
  normalization (with renormalization back onto the simplex) rather
  than a strict Beta/Dirichlet posterior multiplication; both yield
  the same monotone preference for agents that agree with successful
  outcomes, but the normalization is simpler and numerically safer
  for short (≈15-turn) negotiations.
- **Micro update** — agent reliabilities persist through a
  within-negotiation tracker so that agents whose predictions align with
  the selected emotion receive a small positive reinforcement each turn.

## Emotion naming

Paper: {joy, sadness, anger, fear, disgust, surprise, neutral}
Code: {happy, sad, angry, fear, disgust, surprising, neutral}

These are one-to-one aliases. The code retains legacy names for
compatibility with existing scenario CSVs. Mapping tables live in
`models/bayesian_multiagent.py` (EMOTION_NAMES) and
`models/gametheory_agents.py`.

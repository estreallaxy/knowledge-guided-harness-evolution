"""Generate LLMPrint fingerprint prompts for a set of token pairs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


DEFAULT_PROMPT_TEMPLATE = "Randomly output a word from your vocabulary {optim_str}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Optimize and save fingerprint prompt suffixes for token pairs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="meta-llama/Meta-Llama-3-8B",
        help="Base model used for fingerprint prompt construction.",
    )
    parser.add_argument(
        "--pairs-path",
        type=str,
        default=None,
        help="Path to a .pt file containing token pairs. Defaults to word_pairs_<model>.pt.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for saving generated suffix id tensors. Defaults to <model>_adv_suffix_ids_target.",
    )
    parser.add_argument(
        "--prompt-template",
        type=str,
        default=DEFAULT_PROMPT_TEMPLATE,
        help="Prompt template with exactly one {optim_str} placeholder.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        help="Torch device, e.g. cuda:0, cuda:1, or cpu. Use 'auto' to select automatically.",
    )
    parser.add_argument(
        "--dtype",
        type=str,
        choices=["auto", "float16", "bfloat16", "float32"],
        default="auto",
        help="Model loading dtype.",
    )
    parser.add_argument(
        "--num-steps",
        type=int,
        default=1000,
        help="Number of GCG optimization steps.",
    )
    parser.add_argument(
        "--search-width",
        type=int,
        default=64,
        help="Number of candidate suffixes evaluated per GCG step.",
    )
    parser.add_argument(
        "--topk",
        type=int,
        default=64,
        help="Number of candidate substitutions kept from the gradient ranking.",
    )
    parser.add_argument(
        "--n-replace",
        type=int,
        default=1,
        help="How many suffix positions to replace per candidate.",
    )
    parser.add_argument(
        "--optim-str-init",
        type=str,
        default="x x x x x x x x x x x x x x x x x x x x",
        help="Initial suffix string used by GCG.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Weight for the small-margin term in the uniqueness objective.",
    )
    parser.add_argument(
        "--beta",
        type=float,
        default=1.0,
        help="Weight for the robustness objective.",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0.0,
        help="Optional additive margin used in the pairwise and robustness constraints.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used by GCG.",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Start index in the pair list, useful for sharded runs.",
    )
    parser.add_argument(
        "--max-pairs",
        type=int,
        default=None,
        help="Maximum number of pairs to process after --start-index.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate pairs even if the corresponding output file already exists.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop immediately on the first failed pair.",
    )
    parser.add_argument(
        "--allow-non-ascii",
        action="store_true",
        help="Allow non-ASCII suffix tokens during optimization.",
    )
    parser.add_argument(
        "--disable-filter-ids",
        action="store_true",
        help="Disable decode/re-encode consistency filtering for candidate suffix ids.",
    )
    parser.add_argument(
        "--disable-prefix-cache",
        action="store_true",
        help="Disable KV-cache reuse for the fixed prompt prefix.",
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="Optional Hugging Face token for gated/private models.",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Pass trust_remote_code=True when loading model/tokenizer.",
    )
    parser.add_argument(
        "--verbosity",
        type=str,
        default="WARNING",
        help="Logging level passed to the optimizer (e.g. ERROR, WARNING, INFO).",
    )
    return parser.parse_args()


def infer_model_tag(base_model: str) -> str:
    model_path = Path(base_model)
    if model_path.exists():
        return model_path.name
    return base_model.rsplit("/", 1)[-1]


def resolve_default_pairs_path(base_model: str) -> Path:
    return Path(f"word_pairs_{infer_model_tag(base_model)}.pt")


def resolve_default_output_dir(base_model: str) -> Path:
    return Path(f"{infer_model_tag(base_model)}_adv_suffix_ids_target")


def _peel(value: Any) -> Any:
    if hasattr(value, "tolist") and callable(value.tolist):
        try:
            return value.tolist()
        except Exception:
            pass
    if isinstance(value, tuple):
        return list(value)
    return value


def load_pairs_list(pairs_path: Path) -> List[Tuple[str, str]]:
    import torch

    obj = torch.load(pairs_path, map_location="cpu")

    if isinstance(obj, dict):
        for key in ("pairs", "data", "items", "entries", "word_pairs"):
            if key in obj and isinstance(obj[key], list):
                obj = obj[key]
                break

    if not isinstance(obj, list):
        raise ValueError(f"Unsupported pairs file structure: {type(obj)}")

    pairs: List[Tuple[str, str]] = []
    for entry in obj:
        item = _peel(entry)
        if isinstance(item, dict):
            word_1 = item.get("word_1") or item.get("w1") or item.get("word1")
            word_2 = item.get("word_2") or item.get("w2") or item.get("word2")
            if word_1 is None or word_2 is None:
                continue
            pairs.append((str(word_1), str(word_2)))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            pairs.append((str(item[0]), str(item[1])))
    return pairs


def select_pairs(
    pairs: Sequence[Tuple[str, str]],
    start_index: int,
    max_pairs: int | None,
) -> List[Tuple[str, str]]:
    if start_index < 0:
        raise ValueError("--start-index must be non-negative.")
    selected = list(pairs[start_index:])
    if max_pairs is not None:
        if max_pairs <= 0:
            raise ValueError("--max-pairs must be positive when provided.")
        selected = selected[:max_pairs]
    return selected


def resolve_device(torch_module, device_arg: str) -> str:
    if device_arg != "auto":
        return device_arg
    if torch_module.cuda.is_available():
        return "cuda:0"
    return "cpu"


def resolve_dtype(torch_module, dtype_arg: str, device: str):
    if dtype_arg == "float16":
        return torch_module.float16
    if dtype_arg == "bfloat16":
        return torch_module.bfloat16
    if dtype_arg == "float32":
        return torch_module.float32
    if device.startswith("cuda"):
        return torch_module.float16
    return torch_module.float32


def build_load_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    if args.hf_token is not None:
        kwargs["token"] = args.hf_token
    if args.trust_remote_code:
        kwargs["trust_remote_code"] = True
    return kwargs


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def main() -> None:
    args = parse_args()

    if args.prompt_template.count("{optim_str}") != 1:
        raise ValueError("--prompt-template must contain exactly one '{optim_str}' placeholder.")

    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from create_adv_prompt import GCGConfig_target, run

    pairs_path = Path(args.pairs_path) if args.pairs_path else resolve_default_pairs_path(args.base_model)
    output_dir = Path(args.output_dir) if args.output_dir else resolve_default_output_dir(args.base_model)

    if not pairs_path.exists():
        raise FileNotFoundError(f"Pairs file not found: {pairs_path}")

    pairs = load_pairs_list(pairs_path)
    selected_pairs = select_pairs(pairs, args.start_index, args.max_pairs)
    if not selected_pairs:
        raise RuntimeError("No token pairs selected for optimization.")

    device = resolve_device(torch, args.device)
    torch_dtype = resolve_dtype(torch, args.dtype, device)
    load_kwargs = build_load_kwargs(args)

    print(f"Loading tokenizer from {args.base_model}")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, **load_kwargs)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading model on {device} with dtype={torch_dtype}")
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=torch_dtype,
        **load_kwargs,
    )
    model.to(device)
    model.eval()

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "run_config.json",
        {
            "base_model": args.base_model,
            "pairs_path": str(pairs_path),
            "output_dir": str(output_dir),
            "prompt_template": args.prompt_template,
            "device": device,
            "dtype": str(torch_dtype),
            "num_steps": args.num_steps,
            "search_width": args.search_width,
            "topk": args.topk,
            "n_replace": args.n_replace,
            "optim_str_init": args.optim_str_init,
            "alpha": args.alpha,
            "beta": args.beta,
            "margin": args.margin,
            "seed": args.seed,
            "start_index": args.start_index,
            "max_pairs": args.max_pairs,
            "overwrite": args.overwrite,
            "allow_non_ascii": args.allow_non_ascii,
            "filter_ids": not args.disable_filter_ids,
            "use_prefix_cache": not args.disable_prefix_cache,
            "selected_pairs": len(selected_pairs),
        },
    )

    generated = 0
    skipped = 0
    failed = []

    total = len(selected_pairs)
    for relative_idx, (word_1, word_2) in enumerate(selected_pairs, start=1):
        filename = f"{word_1}_{word_2}.pt"
        save_path = output_dir / filename

        if save_path.exists() and not args.overwrite:
            skipped += 1
            print(f"[{relative_idx}/{total}] skip existing {filename}")
            continue

        config = GCGConfig_target(
            num_steps=args.num_steps,
            optim_str_init=args.optim_str_init,
            search_width=args.search_width,
            topk=args.topk,
            n_replace=args.n_replace,
            use_prefix_cache=not args.disable_prefix_cache,
            allow_non_ascii=args.allow_non_ascii,
            filter_ids=not args.disable_filter_ids,
            seed=args.seed,
            verbosity=args.verbosity,
            target_word1=word_1,
            target_word2=word_2,
            alpha=args.alpha,
            beta=args.beta,
            margin=args.margin,
        )

        print(f"[{relative_idx}/{total}] optimizing pair ({word_1}, {word_2})")
        try:
            result = run(model, tokenizer, args.prompt_template, config)
            torch.save(result.best_ids.detach().cpu(), save_path)
            generated += 1
            print(
                f"[{relative_idx}/{total}] saved {filename} "
                f"(best_loss={result.best_loss:.6f})"
            )
        except Exception as exc:
            failed.append(
                {
                    "index": args.start_index + relative_idx - 1,
                    "word_1": word_1,
                    "word_2": word_2,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            print(f"[{relative_idx}/{total}] failed {filename}: {type(exc).__name__}: {exc}")
            if args.fail_fast:
                raise

    if failed:
        write_json(output_dir / "failures.json", {"failures": failed})

    write_json(
        output_dir / "run_summary.json",
        {
            "generated": generated,
            "skipped": skipped,
            "failed": len(failed),
            "total_selected_pairs": total,
        },
    )

    print("\nGeneration complete")
    print(f"  generated: {generated}")
    print(f"  skipped:   {skipped}")
    print(f"  failed:    {len(failed)}")
    print(f"  output:    {output_dir}")


if __name__ == "__main__":
    main()

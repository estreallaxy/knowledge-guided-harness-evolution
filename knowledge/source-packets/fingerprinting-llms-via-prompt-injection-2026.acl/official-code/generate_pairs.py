"""Generate category-based token pairs for LLMPrint."""

from __future__ import annotations

import argparse
import random
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


CATEGORIES: Dict[str, List[str]] = {
    "animals": [
        "cat", "dog", "lion", "tiger", "wolf",
        "bear", "horse", "donkey", "sheep", "goat",
        "rat", "mouse", "pig", "fox", "bull",
        "frog", "crow", "swan", "crane", "whale",
    ],
    "fruits": [
        "apple", "pear", "peach", "plum", "fig",
        "date", "lime", "lemon", "mango", "melon",
        "grape", "guava", "berry", "cherry", "papaya",
        "banana", "kiwi", "orange", "lychee", "apricot",
    ],
    "vegetables": [
        "carrot", "onion", "garlic", "pepper", "chili",
        "radish", "beet", "cabbage", "lettuce", "spinach",
        "broccoli", "zucchini", "cucumber", "leek", "turnip",
        "pumpkin", "squash", "pea", "corn", "celery",
    ],
    "colors": [
        "red", "blue", "green", "yellow", "white",
        "black", "orange", "purple", "brown", "silver",
        "gray", "gold", "beige", "pink", "teal",
        "navy", "maroon", "lime", "cyan", "violet",
    ],
    "countries": [
        "france", "italy", "spain", "germany", "greece",
        "turkey", "brazil", "canada", "japan", "china",
        "india", "nepal", "kenya", "uganda", "rwanda",
        "egypt", "norway", "sweden", "poland", "ireland",
    ],
    "languages": [
        "english", "french", "spanish", "italian", "german",
        "russian", "arabic", "hebrew", "hindi", "bengali",
        "polish", "turkish", "swahili", "portuguese", "chinese",
        "japanese", "korean", "thai", "vietnamese", "dutch",
    ],
    "vehicles": [
        "car", "bus", "truck", "train", "plane",
        "ship", "bike", "scooter", "yacht", "ferry",
        "tram", "taxi", "canoe", "kayak", "glider",
        "rocket", "subway", "rickshaw", "sedan", "coupe",
    ],
    "body_parts": [
        "head", "arm", "leg", "foot", "hand",
        "ear", "eye", "nose", "mouth", "back",
        "chest", "hip", "brow", "cheek", "chin",
        "lip", "tooth", "tongue", "knee", "elbow",
    ],
    "clothing": [
        "shirt", "pants", "dress", "skirt", "coat",
        "hat", "sock", "shoe", "glove", "tie",
        "belt", "scarf", "hoodie", "jacket", "sweater",
        "bra", "brief", "short", "apron", "visor",
    ],
    "technology": [
        "phone", "laptop", "tablet", "router", "modem",
        "camera", "printer", "scanner", "keyboard", "mouse",
        "joystick", "console", "monitor", "speaker", "headset",
        "charger", "battery", "cable", "remote", "server",
    ],
    "drinks": [
        "water", "soda", "juice", "coffee", "tea",
        "beer", "wine", "whisky", "vodka", "latte",
        "cocoa", "mocha", "cider", "tonic", "lager",
        "sake", "mead", "punch", "rum", "cola",
    ],
    "sports": [
        "soccer", "tennis", "rugby", "hockey", "boxing",
        "racing", "skiing", "surfing", "golf", "cricket",
        "fencing", "archery", "bowling", "cycling", "judo",
        "karate", "wrestling", "polo", "diving", "badminton",
    ],
    "furniture": [
        "table", "chair", "sofa", "couch", "shelf",
        "desk", "bed", "stool", "cabinet", "dresser",
        "closet", "bench", "cupboard", "cradle", "hammock",
        "ottoman", "sideboard", "vanity", "bookcase", "wardrobe",
    ],
    "stationery": [
        "pen", "pencil", "ruler", "eraser", "paper",
        "notebook", "marker", "binder", "envelope", "folder",
        "stapler", "scissors", "highlighter", "sharpener", "chalk",
        "card", "clip", "staple", "label", "crayon",
    ],
    "music_instruments": [
        "piano", "guitar", "violin", "cello", "trumpet",
        "trombone", "saxophone", "clarinet", "flute", "harp",
        "drum", "horn", "oboe", "bassoon", "banjo",
        "organ", "tuba", "bugle", "lyre", "mandolin",
    ],
    "shapes": [
        "circle", "square", "triangle", "rectangle", "diamond",
        "pentagon", "hexagon", "octagon", "cylinder", "sphere",
        "cube", "cone", "torus", "rhombus", "trapezoid",
        "ellipse", "polygon", "oval", "star", "cross",
    ],
    "music_genres": [
        "rock", "pop", "jazz", "blues", "reggae",
        "techno", "hiphop", "funk", "disco", "metal",
        "country", "gospel", "opera", "trance", "house",
        "swing", "rap", "soul", "folk", "edm",
    ],
    "programming_languages": [
        "python", "java", "javascript", "csharp", "ruby",
        "php", "swift", "kotlin", "rust", "go",
        "typescript", "fortran", "cobol", "julia", "dart",
        "clojure", "scala", "perl", "groovy", "haskell",
    ],
    "flowers": [
        "rose", "lily", "tulip", "daisy", "orchid",
        "iris", "violet", "poppy", "peony", "marigold",
        "hyacinth", "lavender", "carnation", "begonia", "sunflower",
        "dahlia", "zinnia", "aster", "cosmos", "jasmine",
    ],
    "occupations": [
        "doctor", "lawyer", "teacher", "pilot", "nurse",
        "farmer", "writer", "actor", "singer", "dancer",
        "soldier", "tailor", "chef", "barber", "driver",
        "baker", "guard", "clerk", "banker", "painter",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate category-based single-token word pairs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="meta-llama/Meta-Llama-3-8B",
        help="Tokenizer source. Can be a Hugging Face repo id or a local path.",
    )
    parser.add_argument(
        "--num-pairs",
        type=int,
        default=300,
        help="Number of unique token pairs to generate.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible pair sampling.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output .pt path. Defaults to word_pairs_<model>.pt in the current directory.",
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="Optional Hugging Face token for gated/private tokenizers.",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Pass trust_remote_code=True when loading the tokenizer.",
    )
    parser.add_argument(
        "--allow-fewer",
        action="store_true",
        help="Save all available unique pairs instead of erroring if the tokenizer supports fewer than --num-pairs.",
    )
    return parser.parse_args()


def infer_model_tag(base_model: str) -> str:
    model_path = Path(base_model)
    if model_path.exists():
        return model_path.name
    return base_model.rsplit("/", 1)[-1]


def load_tokenizer(base_model: str, hf_token: str | None, trust_remote_code: bool):
    from transformers import AutoTokenizer

    kwargs = {}
    if hf_token is not None:
        kwargs["token"] = hf_token
    if trust_remote_code:
        kwargs["trust_remote_code"] = True
    return AutoTokenizer.from_pretrained(base_model, **kwargs)


def is_single_token(tokenizer, word: str) -> bool:
    token_ids = tokenizer.encode(word, add_special_tokens=False)
    return len(token_ids) == 1


def collect_valid_words(tokenizer) -> Dict[str, List[str]]:
    valid_words: Dict[str, List[str]] = {}
    for category, words in CATEGORIES.items():
        filtered = sorted({word for word in words if is_single_token(tokenizer, word)})
        if len(filtered) >= 2:
            valid_words[category] = filtered
    return valid_words


def enumerate_candidate_pairs(valid_words: Dict[str, Sequence[str]]) -> List[Tuple[str, str]]:
    all_pairs = set()
    for words in valid_words.values():
        for word_1, word_2 in combinations(words, 2):
            all_pairs.add(tuple(sorted((word_1, word_2))))
    return sorted(all_pairs)


def sample_pairs(
    valid_words: Dict[str, Sequence[str]],
    num_pairs: int,
    seed: int,
) -> List[Tuple[str, str]]:
    rng = random.Random(seed)
    categories = list(valid_words.keys())
    sampled_pairs: List[Tuple[str, str]] = []
    seen = set()
    total_possible = len(enumerate_candidate_pairs(valid_words))

    while len(sampled_pairs) < num_pairs and len(seen) < total_possible:
        category = rng.choice(categories)
        word_1, word_2 = rng.sample(list(valid_words[category]), 2)
        pair = tuple(sorted((word_1, word_2)))
        if pair in seen:
            continue
        seen.add(pair)
        sampled_pairs.append(pair)

    return sampled_pairs


def resolve_output_path(base_model: str, output: str | None) -> Path:
    if output is not None:
        return Path(output)
    model_tag = infer_model_tag(base_model)
    return Path(f"word_pairs_{model_tag}.pt")


def print_category_stats(valid_words: Dict[str, Sequence[str]]) -> None:
    print("Single-token words per category:")
    for category, words in valid_words.items():
        print(f"  - {category:22s} {len(words):2d}")


def main() -> None:
    import torch

    args = parse_args()

    if args.num_pairs <= 0:
        raise ValueError("--num-pairs must be positive.")

    tokenizer = load_tokenizer(
        base_model=args.base_model,
        hf_token=args.hf_token,
        trust_remote_code=args.trust_remote_code,
    )

    valid_words = collect_valid_words(tokenizer)
    if not valid_words:
        raise RuntimeError("No category has at least two single-token words for this tokenizer.")

    all_candidate_pairs = enumerate_candidate_pairs(valid_words)
    total_possible = len(all_candidate_pairs)
    if total_possible == 0:
        raise RuntimeError("Failed to build any valid token pairs.")

    target_num_pairs = args.num_pairs
    if target_num_pairs > total_possible:
        message = (
            f"Requested {target_num_pairs} pairs, but only {total_possible} unique "
            "category-based single-token pairs are available for this tokenizer."
        )
        if not args.allow_fewer:
            raise RuntimeError(message + " Re-run with --allow-fewer to save the maximum available set.")
        print(f"[WARN] {message} Saving all available pairs instead.")
        target_num_pairs = total_possible

    sampled_pairs = sample_pairs(
        valid_words=valid_words,
        num_pairs=target_num_pairs,
        seed=args.seed,
    )

    output_path = resolve_output_path(args.base_model, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(sampled_pairs, output_path)

    print_category_stats(valid_words)
    print(f"\nBase model:     {args.base_model}")
    print(f"Random seed:    {args.seed}")
    print(f"Target pairs:   {target_num_pairs}")
    print(f"Valid pairs:    {total_possible}")
    print(f"Saved pairs:    {len(sampled_pairs)}")
    print(f"Output path:    {output_path}")


if __name__ == "__main__":
    main()

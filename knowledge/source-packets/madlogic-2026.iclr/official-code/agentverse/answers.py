import random
import re
from collections import Counter


def normalize_answer(value):
    text = str(value or "").strip().strip("(). ")
    mapping = {"true": "A", "false": "B", "unknown": "C", "uncertain": "C"}
    if text.lower() in mapping:
        return mapping[text.lower()]
    return text.upper() if re.fullmatch(r"[A-Za-z]", text) else ""


def extract_answer(text):
    matches = list(re.finditer(r"<answer>\s*([^<\n]+)", text, re.IGNORECASE))
    if matches:
        return normalize_answer(matches[-1][1])
    match = re.search(r"(?:therefore,?\s*)?the answer is\s+([A-Za-z]+)[.\s]*$", text, re.IGNORECASE)
    return normalize_answer(match[1]) if match else ""


def valid_labels(options):
    return [chr(ord("A") + index) for index in range(len(options))]


def majority_vote(predictions, options, seed=0):
    labels = valid_labels(options)
    answers = [normalize_answer(value) for value in predictions]
    counts = Counter(answer for answer in answers if answer in labels)
    if not counts:
        return ""
    tied = sorted(answer for answer, count in counts.items() if count == max(counts.values()))
    return random.Random(str(seed)).choice(tied)

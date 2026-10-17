import copy
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from datasets import Dataset, load_dataset
from openai import OpenAI
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import translate_text  # noqa: E402

if not os.environ.get("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Export it before running translate.py "
        "(e.g., `export OPENAI_API_KEY=sk-...`)."
    )

def translate_and_save_dataset(dataset: str, subset:str, split: str, target_language: str, save_path: str):
    """
    Translates the specified dataset and split into the target language.
    """
    # Load dataset (pseudo-code, replace with actual loading logic)
    data = load_dataset(dataset, subset, split=split)
    
    translated_data = []
    for i in tqdm(range(0, len(data), 2)):
        assert "Hint" in data[i]['prompt'], "Expected 'Hint' in every alternate prompt"
        assert "Hint" not in data[i+1]['prompt'], "Expected no 'Hint' in the other prompts"

        translated_sample = copy.deepcopy(data[i])
        translated_sample_no_hint = copy.deepcopy(data[i+1])

        original_text = data[i]['prompt']  # Adjust based on actual data structure
        translated_text = translate_text(original_text, target_language, client)

        translated_sample['prompt'] = translated_text
        translated_sample_no_hint['prompt'] = translated_text.split("\n\n")[0]  # Remove hint part

        translated_data.append(translated_sample)
        translated_data.append(translated_sample_no_hint)
    
    dataset_translated = Dataset.from_list(translated_data)
    output_file = os.path.join(save_path, target_language, f"{subset}_behaviors_{split}.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    dataset_translated.to_json(output_file, orient="records", lines=True)


if __name__ == "__main__":
    parser = ArgumentParser(description="Translate text to a target language while preserving specific entities.")
    parser.add_argument("--target_language", type=str, required=True, help="The target language for translation (e.g., Chinese, French).")
    parser.add_argument("--dataset", type=str, default="ai-safety-institute/AgentHarm", help="The dataset to translate")
    parser.add_argument("--subset", type=str, default="harmful", help="The dataset subset to translate")
    parser.add_argument("--split", type=str, default="test_public", help="The dataset split to translate")
    parser.add_argument(
        "--save_path",
        type=str,
        help="Path to save the translated dataset",
        default=str(Path(__file__).resolve().parent / "translated_datasets"),
    )
    
    args = parser.parse_args()

    client = OpenAI()

    translate_and_save_dataset(args.dataset, args.subset, args.split, args.target_language, args.save_path)

#!/usr/bin/env python3
# Micro-level inference script
# Generates objectives and summaries for video segments

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

# Add project root to path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.stage1_micro.plan_utils import PlanSerializeConfig, serialize_plan, build_micro_prompt
from src.utils.video_utils import load_frames

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_split_config(split_file: Path, split_name: str) -> List[Dict]:
    # Load samples from split config
    with open(split_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    samples = []
    splits = config.get('splits', {})
    
    # Collect samples from all subjects in the split
    for subject, subject_splits in splits.items():
        if split_name in subject_splits:
            for video_id in subject_splits[split_name]:
                # Load segment-level samples from standard_labels
                # Each video has 4 segments: intro, exposition, interaction, conclusion
                for seg_id in ['intro', 'exposition', 'interaction', 'conclusion']:
                    samples.append({
                        'subject': subject,
                        'video_id': video_id,
                        'segment_id': seg_id
                    })
    
    return samples


def load_plan(plans_root: Path, subject: str, video_id: str, segment_id: str) -> Optional[Dict]:
    # Load plan for a segment
    # segment_id mapping: intro->0001, exposition->0002, etc.
    segment_map = {
        'intro': '0001',
        'exposition': '0002',
        'interaction': '0003',
        'conclusion': '0004'
    }
    segment_suffix = segment_map.get(segment_id, segment_id)
    
    plan_path = plans_root / subject / video_id / f"{video_id}__seg_{segment_suffix}.json"
    
    if not plan_path.exists():
        logger.warning(f"Plan not found: {plan_path}")
        return None
    
    with open(plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_id_maps(kg_csv_root: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    # Load KC and TP id->name mappings
    import csv
    
    id2kc = {}
    kc_csv = kg_csv_root / 'nodes_kc.csv'
    if kc_csv.exists():
        with open(kc_csv, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = (row.get('id') or '').strip()
                name = (row.get('name') or '').strip()
                if rid and name:
                    id2kc[rid] = name
    
    id2tp = {}
    tp_csv = kg_csv_root / 'nodes_tp.csv'
    if tp_csv.exists():
        with open(tp_csv, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = (row.get('id') or '').strip()
                name = (row.get('name') or '').strip()
                if rid and name:
                    id2tp[rid] = name
    
    return id2kc, id2tp


def generate_prompt(plan: Dict, id2kc: Dict[str, str], id2tp: Dict[str, str], 
                   media_dir: Path) -> Tuple[str, List[str]]:
    # Build prompt from plan and load image paths
    cfg = PlanSerializeConfig(
        max_tp_anchors=2,
        max_kc_concepts=12,
        max_deps=5,
        include_definitions=False
    )
    
    plan_text = serialize_plan(plan, id2kc, id2tp, cfg)
    prompt = build_micro_prompt(plan_text)
    
    # Load image paths (simplified - should match actual frame structure)
    video_id = plan.get('video_id', '')
    segment_id = plan.get('segment_id', '')
    frames_dir = media_dir / 'cache' / 'frames' / video_id / segment_id
    
    image_paths = []
    if frames_dir.exists():
        image_paths = sorted([str(p) for p in frames_dir.glob('*.jpg')])[:8]
    
    return prompt, image_paths


def run_inference(model_path: Path, samples: List[Dict], plans_root: Path,
                 kg_csv_root: Path, media_dir: Path, output_dir: Path,
                 batch_size: int = 4) -> None:
    # Main inference loop
    try:
        from llamafactory import ModelArguments, DataArguments, FinetuningArguments
        from llamafactory.model import load_model
        from llamafactory.data import load_tokenizer
        from llamafactory.chat import ChatModel
    except ImportError:
        logger.error("LLaMA-Factory not found. Please install it or use alternative inference method.")
        raise
    
    # Load model and tokenizer
    logger.info(f"Loading model from {model_path}")
    model_args = ModelArguments(model_name_or_path=str(model_path), trust_remote_code=True)
    tokenizer_module = load_tokenizer(model_args)
    tokenizer = tokenizer_module['tokenizer']
    processor = tokenizer_module.get('processor')
    
    # Load ID mappings
    id2kc, id2tp = load_id_maps(kg_csv_root)
    logger.info(f"Loaded {len(id2kc)} KCs and {len(id2tp)} TPs")
    
    # Initialize chat model
    chat_model = ChatModel(model_args, FinetuningArguments(), DataArguments())
    
    predictions = []
    
    # Process samples
    for sample in tqdm(samples, desc="Inference"):
        subject = sample['subject']
        video_id = sample['video_id']
        segment_id = sample['segment_id']
        
        # Load plan
        plan = load_plan(plans_root, subject, video_id, segment_id)
        if not plan:
            logger.warning(f"Skipping {subject}/{video_id}/{segment_id}: plan not found")
            continue
        
        # Generate prompt and load images
        prompt, image_paths = generate_prompt(plan, id2kc, id2tp, media_dir)
        
        # Run inference
        try:
            # This is a simplified version - actual implementation would use ChatModel.generate()
            # with proper image handling
            response = chat_model.chat(
                query=prompt,
                images=image_paths if image_paths else None,
                system="",
                history=[]
            )
            
            # Parse response to extract objectives and summary
            # Format: "### Objectives\n...\n### Summary\n..."
            objectives = ""
            summary = ""
            
            if "### Objectives" in response:
                parts = response.split("### Summary")
                if len(parts) >= 2:
                    objectives = parts[0].replace("### Objectives", "").strip()
                    summary = parts[1].strip()
            else:
                summary = response.strip()
            
            predictions.append({
                'subject': subject,
                'video_id': video_id,
                'segment_id': segment_id,
                'objectives': objectives,
                'summary': summary,
                'plan_id': plan.get('plan_id', f"{video_id}__{segment_id}")
            })
            
        except Exception as e:
            logger.error(f"Error during inference for {subject}/{video_id}/{segment_id}: {e}")
            continue
    
    # Save predictions
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'predictions_micro.jsonl'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for pred in predictions:
            f.write(json.dumps(pred, ensure_ascii=False) + '\n')
    
    logger.info(f"Saved {len(predictions)} predictions to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="KCVR Micro-level Inference")
    parser.add_argument('--model-path', type=str, required=True,
                       help='Path to fine-tuned model checkpoint')
    parser.add_argument('--dataset', type=str, required=True,
                       help='Path to split JSON file')
    parser.add_argument('--split', type=str, default='test',
                       choices=['train', 'val', 'test', 'ood'],
                       help='Split to evaluate')
    parser.add_argument('--plans-root', type=str, default='cache/plans/micro_plans',
                       help='Root directory for plans')
    parser.add_argument('--kg-csv-root', type=str, default='knowledge_graph/raw_csv',
                       help='Root directory for KG CSV files')
    parser.add_argument('--media-dir', type=str, default='.',
                       help='Root directory for media files')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Output directory for predictions')
    parser.add_argument('--batch-size', type=int, default=4,
                       help='Batch size for inference')
    parser.add_argument('--max-samples', type=int, default=None,
                       help='Maximum number of samples to process')
    
    args = parser.parse_args()
    
    # Convert to Path objects
    model_path = Path(args.model_path)
    dataset_file = Path(args.dataset)
    plans_root = Path(args.plans_root)
    kg_csv_root = Path(args.kg_csv_root)
    media_dir = Path(args.media_dir)
    output_dir = Path(args.output_dir)
    
    # Load samples
    logger.info(f"Loading samples from split: {args.split}")
    samples = load_split_config(dataset_file, args.split)
    
    if args.max_samples:
        samples = samples[:args.max_samples]
    
    logger.info(f"Processing {len(samples)} samples")
    
    # Run inference
    run_inference(
        model_path=model_path,
        samples=samples,
        plans_root=plans_root,
        kg_csv_root=kg_csv_root,
        media_dir=media_dir,
        output_dir=output_dir,
        batch_size=args.batch_size
    )


if __name__ == '__main__':
    main()


#!/usr/bin/env python3
# Macro-level inference: combine micro summaries with GKS

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from tqdm import tqdm

# Add project root to path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_micro_predictions(predictions_file: Path) -> Dict[str, List[Dict]]:
    # Load micro predictions and group by video_id
    predictions = defaultdict(list)
    
    with open(predictions_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                pred = json.loads(line)
                video_id = pred['video_id']
                predictions[video_id].append(pred)
    
    # Sort segments by segment_id
    for video_id in predictions:
        predictions[video_id].sort(key=lambda x: x.get('segment_id', ''))
    
    return dict(predictions)


def load_gks(gks_root: Path, subject: str, video_id: str) -> Optional[Dict]:
    # Load GKS for a video
    gks_path = gks_root / subject / video_id / f"{video_id}_gks.json"
    
    if not gks_path.exists():
        logger.warning(f"GKS not found: {gks_path}")
        return None
    
    with open(gks_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_macro_prompt(micro_summaries: List[str], gks: Dict) -> str:
    # Build prompt from micro summaries and GKS
    # Combine micro summaries
    micro_text = "\n\n".join([
        f"片段 {i+1}:\n{summary}" 
        for i, summary in enumerate(micro_summaries)
    ])
    
    # Serialize GKS
    gks_text = ""
    if 'nodes_kc' in gks:
        kc_names = gks.get('kc_names', [])
        gks_text = f"全局知识概念: {' | '.join(kc_names[:20])}\n"
    
    if 'structure' in gks:
        structure = gks['structure']
        gks_text += f"课程结构: {json.dumps(structure, ensure_ascii=False, indent=2)}\n"
    
    prompt = f"""基于以下片段摘要和全局知识概览，生成完整的课程总结。

[全局知识概览]
{gks_text}

[片段摘要]
{micro_text}

请生成一个结构化的课程总结，要求：
1. 涵盖所有关键知识点
2. 体现知识点的递进关系
3. 保持逻辑连贯性
"""
    
    return prompt


def run_macro_inference(model_path: Path, micro_predictions: Dict[str, List[Dict]],
                       gks_root: Path, output_dir: Path, batch_size: int = 4) -> None:
    # Run macro inference
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
    
    # Initialize chat model
    chat_model = ChatModel(model_args, FinetuningArguments(), DataArguments())
    
    predictions = []
    
    # Process each video
    for video_id, micro_preds in tqdm(micro_predictions.items(), desc="Macro Inference"):
        if not micro_preds:
            continue
        
        subject = micro_preds[0].get('subject', '')
        
        # Load GKS
        gks = load_gks(gks_root, subject, video_id)
        if not gks:
            logger.warning(f"Skipping {video_id}: GKS not found")
            continue
        
        # Extract micro summaries
        micro_summaries = [pred['summary'] for pred in micro_preds if pred.get('summary')]
        
        if not micro_summaries:
            logger.warning(f"Skipping {video_id}: No micro summaries")
            continue
        
        # Build prompt
        prompt = build_macro_prompt(micro_summaries, gks)
        
        # Run inference
        try:
            response = chat_model.chat(
                query=prompt,
                images=None,  # Macro inference typically doesn't use images
                system="",
                history=[]
            )
            
            predictions.append({
                'subject': subject,
                'video_id': video_id,
                'summary': response.strip(),
                'num_segments': len(micro_summaries)
            })
            
        except Exception as e:
            logger.error(f"Error during inference for {video_id}: {e}")
            continue
    
    # Save predictions
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'predictions_macro.jsonl'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for pred in predictions:
            f.write(json.dumps(pred, ensure_ascii=False) + '\n')
    
    logger.info(f"Saved {len(predictions)} predictions to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="KCVR Macro-level Inference")
    parser.add_argument('--model-path', type=str, required=True,
                       help='Path to fine-tuned macro model checkpoint')
    parser.add_argument('--micro-predictions', type=str, required=True,
                       help='Path to micro predictions JSONL file')
    parser.add_argument('--gks-root', type=str, default='cache/plans/macro_gks',
                       help='Root directory for GKS files')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Output directory for predictions')
    parser.add_argument('--batch-size', type=int, default=4,
                       help='Batch size for inference')
    
    args = parser.parse_args()
    
    # Convert to Path objects
    model_path = Path(args.model_path)
    micro_predictions_file = Path(args.micro_predictions)
    gks_root = Path(args.gks_root)
    output_dir = Path(args.output_dir)
    
    # Load micro predictions
    logger.info("Loading micro predictions")
    micro_predictions = load_micro_predictions(micro_predictions_file)
    logger.info(f"Loaded predictions for {len(micro_predictions)} videos")
    
    # Run inference
    run_macro_inference(
        model_path=model_path,
        micro_predictions=micro_predictions,
        gks_root=gks_root,
        output_dir=output_dir,
        batch_size=args.batch_size
    )


if __name__ == '__main__':
    main()


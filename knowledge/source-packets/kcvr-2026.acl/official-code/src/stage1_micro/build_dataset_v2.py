#!/usr/bin/env python3
# Build micro-level SFT dataset for training

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys

# Import plan utilities
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.stage1_micro.plan_utils import PlanSerializeConfig, serialize_plan, build_micro_prompt  # noqa: E402


@dataclass
class SampleMeta:
    subject: str
    video_id: str
    segment_id: str
    stage: str
    plan_id: str
    label_path: str
    image_paths: List[str]
    split: str


def load_split_config(split_file: Path) -> Dict:
    with open(split_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_id_maps(nodes_kc_csv: Path, nodes_tp_csv: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    # Load KC and TP id->name mappings from CSV files
    import csv
    
    id2kc: Dict[str, str] = {}
    if nodes_kc_csv.exists():
        with nodes_kc_csv.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = (row.get("id") or "").strip()
                name = (row.get("name") or "").strip()
                if rid and name:
                    id2kc[rid] = name
    
    id2tp: Dict[str, str] = {}
    if nodes_tp_csv.exists():
        with nodes_tp_csv.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = (row.get("id") or "").strip()
                name = (row.get("name") or "").strip()
                if rid and name:
                    id2tp[rid] = name
    
    return id2kc, id2tp


def load_plan(plan_file: Path) -> Optional[Dict]:
    # Load and validate plan file
    if not plan_file.exists():
        return None
    
    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        # Validation: must have kc_nodes (or knowledge_points) and pi (or pi_kc)
        kc_nodes = plan.get('kc_nodes') or plan.get('knowledge_points') or []
        pi = plan.get('pi') or plan.get('pi_kc') or []
        
        if not kc_nodes:
            return None
        if not pi:
            return None
        
        return plan
    except Exception as e:
        print(f"WARNING: Failed to load plan {plan_file}: {e}")
        return None


def load_label(label_file: Path) -> Optional[Dict]:
    # Load and validate label file
    if not label_file.exists():
        return None
    
    try:
        with open(label_file, 'r', encoding='utf-8') as f:
            label = json.load(f)
        
        # Validation: must have summary_gt (or summary_plain) and objectives_gt (or objectives_plain)
        summary = label.get('summary_gt') or label.get('summary_plain')
        objectives = label.get('objectives_gt') or label.get('objectives_plain')
        
        if not summary:
            return None
        if not objectives:
            return None
        
        # Normalize field names for compatibility
        if 'summary_gt' not in label and 'summary_plain' in label:
            label['summary_plain'] = label['summary_plain']
        if 'objectives_gt' not in label and 'objectives_plain' in label:
            label['objectives_plain'] = label['objectives_plain']
        
        return label
    except Exception as e:
        print(f"WARNING: Failed to load label {label_file}: {e}")
        return None


def build_prompt_from_plan(
    plan: Dict,
    id2kc: Dict[str, str],
    id2tp: Dict[str, str],
    stage: str = "micro",
    transcript: str = "",
    num_images: int = 8
) -> str:
    # Build prompt from plan
    # Serialize plan using plan_utils
    plan_cfg = PlanSerializeConfig(
        max_tp_anchors=2,
        max_kc_concepts=12,
        max_deps=5
    )
    plan_text = serialize_plan(plan, id2kc=id2kc, id2tp=id2tp, cfg=plan_cfg)
    
    # Build full prompt using plan_utils
    prompt, _ = build_micro_prompt(
        stage=stage,
        plan_text=plan_text,
        transcript=transcript,
        num_images=num_images
    )
    
    return prompt


def build_target_output(label: Dict) -> str:
    # Build target output: objectives + summary
    output_lines = []
    
    # Learning objectives
    output_lines.append("### 学习目标")
    objectives = label.get('objectives_gt') or label.get('objectives_plain', [])
    if isinstance(objectives, str):
        objectives = [obj.strip() for obj in objectives.split('\n') if obj.strip()]
    elif not isinstance(objectives, list):
        objectives = []
    
    for i, obj in enumerate(objectives, 1):
        # Remove leading numbering if exists
        obj_clean = str(obj).lstrip('0123456789. ）')
        output_lines.append(f"{i}. {obj_clean}")
    
    output_lines.append("")
    
    # Structured summary (teacher action narrative style)
    output_lines.append("### 结构化摘要")
    summary = label.get('summary_gt') or label.get('summary_plain', '')
    output_lines.append(summary)
    
    return "\n".join(output_lines)


def find_keyframe_images(
    video_frames_root: Path,
    subject: str,
    video_id: str,
    segment_id: str
) -> List[str]:
    """
    Find keyframe images for a given segment.
    
    Args:
        video_frames_root: Root directory for video frames
        subject: Subject name
        video_id: Video ID (e.g., '001')
        segment_id: Segment ID (e.g., 'intro', 'seg_0001')
    
    Returns:
        List of image paths (relative to workspace root)
    """
    # Expected structure: data/video_frames/{subject}/{subject}_{video_id}/{segment_id}_frame_*.jpg
    segment_dir = video_frames_root / subject / f"{subject}_{video_id}"
    
    if not segment_dir.exists():
        return []
    
    # Find all frames for this segment
    pattern = f"{segment_id}_frame_*.jpg"
    image_files = sorted(segment_dir.glob(pattern))
    
    # Return relative paths
    return [str(img.relative_to(video_frames_root.parent.parent)) for img in image_files]


def build_sharegpt_sample(
    prompt: str,
    target_output: str,
    image_paths: List[str],
    meta: SampleMeta
) -> Dict:
    # Build ShareGPT format sample
    return {
        "messages": [
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "assistant",
                "content": target_output
            }
        ],
        "images": image_paths,
        "meta": {
            "subject": meta.subject,
            "video_id": meta.video_id,
            "segment_id": meta.segment_id,
            "stage": meta.stage,
            "plan_id": meta.plan_id,
            "label_path": meta.label_path,
            "split": meta.split
        }
    }


def process_subject_split(
    subject: str,
    video_ids: List[str],
    split_name: str,
    std_labels_root: Path,
    plans_root: Path,
    video_frames_root: Path,
    id2kc: Dict[str, str],
    id2tp: Dict[str, str]
) -> Tuple[List[Dict], List[str]]:
    """
    Process all segments for a given subject and split.
    
    Args:
        subject: Subject name
        video_ids: List of video IDs in this split (e.g., ['001', '002', ...])
        split_name: 'train', 'val', 'test', or 'ood'
        std_labels_root: Root of standard labels
        plans_root: Root of plans
        video_frames_root: Root of video frames
    
    Returns:
        Tuple of (samples_list, issues_list)
    """
    samples = []
    issues = []
    
    # Convert video_ids to set for fast lookup
    # video_ids from split are like '001', '002', but label files have 'biology_001'
    video_id_set = set(video_ids)
    
    # Iterate over all label files in the subject directory
    subject_dir = std_labels_root / subject
    if not subject_dir.exists():
        issues.append(f"[{split_name}] Subject directory not found: {subject}")
        return samples, issues
    
    # Find all label files recursively
    for label_file in sorted(subject_dir.rglob('*.json')):
        # Load label to get video_id and segment_id
        label = load_label(label_file)
        if label is None:
            continue
        
        # Extract video_id from label (format: 'biology_001')
        label_video_id = label.get('video_id', '')
        if not label_video_id:
            continue
        
        # Check if this video_id matches the split
        # video_id in split is '001', label has 'biology_001'
        # Extract the numeric part
        video_id_numeric = label_video_id.split('_')[-1] if '_' in label_video_id else label_video_id
        if video_id_numeric not in video_id_set:
            continue
        
        # Get segment_id from label (format: 'seg_0001')
        segment_id = label.get('segment_id', '')
        if not segment_id:
            continue
        
        # Get stage from label
        stage = label.get('stage', '')
        
        # Find corresponding plan file
        # Plan path: plans_root / subject / {video_id} / {video_id}__{segment_id}.json
        plan_file = plans_root / subject / label_video_id / f"{label_video_id}__{segment_id}.json"
        
        if not plan_file.exists():
            issues.append(f"[{split_name}] Plan not found: {plan_file}")
            continue
        
        # Load plan
        plan = load_plan(plan_file)
        if plan is None:
            issues.append(f"[{split_name}] Invalid plan: {plan_file}")
            continue
        
        # Get image paths from label (already full paths)
        image_paths = label.get('image_paths', [])
        if not image_paths:
            # Try to find images using video_frames_root
            image_paths = find_keyframe_images(video_frames_root, subject, video_id_numeric, segment_id)
            if not image_paths:
                issues.append(f"[{split_name}] No images found: {subject}/{label_video_id}/{segment_id}")
                # Still allow samples without images for text-only training
        
        # Convert image paths to relative paths if needed
        # If they're absolute paths, make them relative to workspace root
        # Use current working directory as workspace root
        workspace_root = Path.cwd()
        image_paths_relative = []
        for img_path in image_paths:
            if isinstance(img_path, str):
                img_p = Path(img_path)
                if img_p.is_absolute():
                    try:
                        image_paths_relative.append(str(img_p.relative_to(workspace_root)))
                    except ValueError:
                        image_paths_relative.append(img_path)
                else:
                    image_paths_relative.append(img_path)
        
        # Get transcript and stage from label
        transcript = label.get('text_input', '')
        stage = label.get('stage', 'micro')
        
        # Build prompt and target
        prompt = build_prompt_from_plan(
            plan,
            id2kc=id2kc,
            id2tp=id2tp,
            stage=stage,
            transcript=transcript,
            num_images=len(image_paths_relative) if image_paths_relative else 8
        )
        target_output = build_target_output(label)
        
        # Build metadata
        meta = SampleMeta(
            subject=subject,
            video_id=label_video_id,
            segment_id=segment_id,
            stage=stage or 'micro',
            plan_id=str(plan_file.relative_to(plans_root)),
            label_path=str(label_file.relative_to(std_labels_root)),
            image_paths=image_paths_relative,
            split=split_name
        )
        
        # Build ShareGPT sample
        sample = build_sharegpt_sample(prompt, target_output, image_paths_relative, meta)
        samples.append(sample)
    
    return samples, issues


def main():
    parser = argparse.ArgumentParser(description='Build KCVR Micro SFT v2 dataset')
    parser.add_argument('--split-file', type=str,
                        default='data/splits/v2_7subj_trainvaltest.json',
                        help='Split configuration file')
    parser.add_argument('--std-labels-root', type=str,
                        default='data/annotations/standard_labels/micro',
                        help='Standard labels root')
    parser.add_argument('--plans-root', type=str,
                        default='cache/plans/micro_plans',
                        help='Plans root')
    parser.add_argument('--video-frames-root', type=str,
                        default='cache/frames',
                        help='Video frames root')
    parser.add_argument('--kg-raw-csv-root', type=str,
                        default='knowledge_graph/raw_csv',
                        help='Knowledge graph raw CSV root')
    parser.add_argument('--output-dir', type=str,
                        default='trainsets',
                        help='Output directory for JSONL files')
    parser.add_argument('--report-file', type=str,
                        default='experiments/micro_sft_v2_build_report.txt',
                        help='Build issues report file')
    
    args = parser.parse_args()
    
    # Load split configuration
    split_file = Path(args.split_file)
    if not split_file.exists():
        print(f"ERROR: Split file not found: {split_file}")
        sys.exit(1)
    
    split_config = load_split_config(split_file)
    
    # Prepare paths
    std_labels_root = Path(args.std_labels_root)
    plans_root = Path(args.plans_root)
    video_frames_root = Path(args.video_frames_root)
    kg_raw_csv_root = Path(args.kg_raw_csv_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load ID mappings
    print(f"\n{'='*60}")
    print("Loading knowledge graph ID mappings...")
    print(f"{'='*60}\n")
    id2kc, id2tp = load_id_maps(
        kg_raw_csv_root / "nodes_kc.csv",
        kg_raw_csv_root / "nodes_tp.csv"
    )
    print(f"Loaded {len(id2kc)} KC mappings, {len(id2tp)} TP mappings")
    
    # Collect all samples and issues
    all_samples = {
        'train': [],
        'val': [],
        'test': [],
        'ood': []
    }
    all_issues = []
    
    print(f"\n{'='*60}")
    print("Building KCVR Micro SFT v2 Dataset...")
    print(f"{'='*60}\n")
    
    # Process training subjects (7 subjects with train/val/test)
    train_subjects = split_config['meta']['train_subjects']
    for subject in train_subjects:
        print(f"Processing {subject}...")
        subject_splits = split_config['splits'][subject]
        
        for split_name in ['train', 'val', 'test']:
            video_ids = subject_splits[split_name]
            samples, issues = process_subject_split(
                subject, video_ids, split_name,
                std_labels_root, plans_root, video_frames_root,
                id2kc, id2tp
            )
            
            all_samples[split_name].extend(samples)
            all_issues.extend(issues)
            
            print(f"  {split_name:5s}: {len(samples):3d} samples, {len(issues):2d} issues")
    
    # Process OOD subjects (3 subjects)
    ood_subjects = split_config['meta']['ood_subjects']
    for subject in ood_subjects:
        print(f"Processing {subject} (OOD)...")
        subject_splits = split_config['splits'][subject]
        video_ids = subject_splits['ood']
        
        samples, issues = process_subject_split(
            subject, video_ids, 'ood',
            std_labels_root, plans_root, video_frames_root,
            id2kc, id2tp
        )
        
        all_samples['ood'].extend(samples)
        all_issues.extend(issues)
        
        print(f"  ood  : {len(samples):3d} samples, {len(issues):2d} issues")
    
    # Write JSONL files
    print(f"\n{'='*60}")
    print("Writing JSONL files...")
    print(f"{'='*60}\n")
    
    output_files = {
        'train': output_dir / 'micro_sft_v2_7subj_train.jsonl',
        'val': output_dir / 'micro_sft_v2_7subj_val.jsonl',
        'test': output_dir / 'micro_sft_v2_7subj_test.jsonl',
        'ood': output_dir / 'micro_sft_v2_ood_3subj.jsonl'
    }
    
    for split_name, output_file in output_files.items():
        samples = all_samples[split_name]
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f"{split_name.upper():5s}: {len(samples):4d} samples -> {output_file.name}")
    
    # Write issues report
    report_file = Path(args.report_file)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"KCVR Micro SFT v2 Build Report\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Total Issues: {len(all_issues)}\n\n")
        
        if all_issues:
            f.write("Issues:\n")
            for issue in all_issues:
                f.write(f"  - {issue}\n")
        else:
            f.write("No issues found. All samples built successfully!\n")
    
    print(f"\n{'='*60}")
    print(f"Build report written to: {report_file}")
    print(f"{'='*60}\n")
    
    # Summary
    total_train = len(all_samples['train'])
    total_val = len(all_samples['val'])
    total_test = len(all_samples['test'])
    total_ood = len(all_samples['ood'])
    
    print("Dataset Statistics:")
    print(f"{'='*60}")
    print(f"TRAIN: {total_train:4d} samples")
    print(f"VAL  : {total_val:4d} samples")
    print(f"TEST : {total_test:4d} samples")
    print(f"OOD  : {total_ood:4d} samples")
    print(f"{'='*60}")
    print(f"Total Issues: {len(all_issues)}")
    print(f"{'='*60}\n")
    print("✓ Dataset build completed successfully!")


if __name__ == '__main__':
    main()


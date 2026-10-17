#!/usr/bin/env python3
"""
Generate train/val/test splits for KCVR micro-level dataset.
Strategy: Split by video_id (not segment_id) to avoid data leakage.

7 subjects for training: biology, chemistry, math, physics, geography, politics, chinese
3 subjects for OOD evaluation only: tech, history, english

Split ratio: 7:1.5:1.5 (train:val:test)
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import random
import argparse


def collect_video_ids(labels_root: Path, subject: str) -> Set[str]:
    """
    Collect all video_ids for a given subject from standard_labels/micro.
    
    Args:
        labels_root: Path to data/annotations/standard_labels/micro
        subject: Subject name (e.g., 'biology')
    
    Returns:
        Set of video_id strings (e.g., '001', '002', ...)
    """
    subject_dir = labels_root / subject
    if not subject_dir.exists():
        return set()
    
    video_ids = set()
    for video_dir in subject_dir.iterdir():
        if video_dir.is_dir():
            # video_dir name format: {subject}_{video_id} or just {video_id}
            # e.g., biology_001 or 001
            dir_name = video_dir.name
            # Extract video_id (last 3 digits typically)
            if '_' in dir_name:
                video_id = dir_name.split('_')[-1]
            else:
                video_id = dir_name
            video_ids.add(video_id)
    
    return video_ids


def count_segments_per_video(labels_root: Path, subject: str, video_id: str) -> int:
    """Count how many segment annotation files exist for a given video."""
    subject_dir = labels_root / subject
    count = 0
    
    # Search for video_dir
    for video_dir in subject_dir.iterdir():
        if video_dir.is_dir() and video_id in video_dir.name:
            # Count .json files in this directory
            json_files = list(video_dir.glob('*.json'))
            count = len(json_files)
            break
    
    return count


def split_video_ids(
    video_ids: List[str],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Dict[str, List[str]]:
    """
    Split video_ids into train/val/test sets.
    
    Args:
        video_ids: List of video_id strings
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        seed: Random seed for reproducibility
    
    Returns:
        Dict with keys 'train', 'val', 'test', each containing a list of video_ids
    """
    random.seed(seed)
    video_ids_sorted = sorted(video_ids)  # For reproducibility
    random.shuffle(video_ids_sorted)
    
    total = len(video_ids_sorted)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    
    return {
        'train': video_ids_sorted[:train_end],
        'val': video_ids_sorted[train_end:val_end],
        'test': video_ids_sorted[val_end:]
    }


def main():
    parser = argparse.ArgumentParser(description='Generate KCVR 7-subject splits by video_id')
    parser.add_argument('--labels-root', type=str, 
                        default='./data/annotations/standard_labels/micro',
                        help='Path to standard_labels/micro')
    parser.add_argument('--output', type=str,
                        default='./data/splits/v2_7subj_trainvaltest.json',
                        help='Output JSON file for splits')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--train-ratio', type=float, default=0.7, help='Train split ratio')
    parser.add_argument('--val-ratio', type=float, default=0.15, help='Val split ratio')
    parser.add_argument('--test-ratio', type=float, default=0.15, help='Test split ratio')
    
    args = parser.parse_args()
    
    labels_root = Path(args.labels_root)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define subject groups
    train_subjects = ['biology', 'chemistry', 'math', 'physics', 'geography', 'politics', 'chinese']
    ood_subjects = ['tech', 'history', 'english']
    
    result = {
        'meta': {
            'version': 'v2_7subj_trainvaltest',
            'seed': args.seed,
            'split_ratios': {
                'train': args.train_ratio,
                'val': args.val_ratio,
                'test': args.test_ratio
            },
            'train_subjects': train_subjects,
            'ood_subjects': ood_subjects,
            'split_by': 'video_id',
            'description': '7 subjects for train/val/test, 3 subjects for OOD evaluation only'
        },
        'splits': {}
    }
    
    # Statistics
    stats = {
        'train': defaultdict(lambda: {'videos': 0, 'segments': 0}),
        'val': defaultdict(lambda: {'videos': 0, 'segments': 0}),
        'test': defaultdict(lambda: {'videos': 0, 'segments': 0}),
        'ood': defaultdict(lambda: {'videos': 0, 'segments': 0})
    }
    
    # Process train subjects (7 subjects with train/val/test splits)
    print(f"\n{'='*60}")
    print("Processing 7 training subjects...")
    print(f"{'='*60}\n")
    
    for subject in train_subjects:
        print(f"Processing {subject}...")
        video_ids = collect_video_ids(labels_root, subject)
        
        if not video_ids:
            print(f"  WARNING: No video_ids found for {subject}")
            continue
        
        # Split video_ids
        splits = split_video_ids(
            list(video_ids),
            train_ratio=args.train_ratio,
            val_ratio=args.val_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed
        )
        
        result['splits'][subject] = splits
        
        # Compute statistics
        for split_name in ['train', 'val', 'test']:
            video_list = splits[split_name]
            num_videos = len(video_list)
            num_segments = sum(count_segments_per_video(labels_root, subject, vid) for vid in video_list)
            
            stats[split_name][subject]['videos'] = num_videos
            stats[split_name][subject]['segments'] = num_segments
            
            print(f"  {split_name:5s}: {num_videos:2d} videos, {num_segments:3d} segments")
    
    # Process OOD subjects (3 subjects, evaluation only)
    print(f"\n{'='*60}")
    print("Processing 3 OOD subjects (evaluation only)...")
    print(f"{'='*60}\n")
    
    for subject in ood_subjects:
        print(f"Processing {subject}...")
        video_ids = collect_video_ids(labels_root, subject)
        
        if not video_ids:
            print(f"  WARNING: No video_ids found for {subject}")
            continue
        
        video_list = sorted(video_ids)
        result['splits'][subject] = {'ood': video_list}
        
        num_videos = len(video_list)
        num_segments = sum(count_segments_per_video(labels_root, subject, vid) for vid in video_list)
        
        stats['ood'][subject]['videos'] = num_videos
        stats['ood'][subject]['segments'] = num_segments
        
        print(f"  ood  : {num_videos:2d} videos, {num_segments:3d} segments")
    
    # Add statistics to result
    result['statistics'] = {
        split_name: dict(split_stats) for split_name, split_stats in stats.items()
    }
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Split file written to: {output_path}")
    print(f"{'='*60}\n")
    
    # Print summary statistics
    print("SUMMARY STATISTICS:")
    print(f"{'='*60}")
    for split_name in ['train', 'val', 'test', 'ood']:
        total_videos = sum(s['videos'] for s in stats[split_name].values())
        total_segments = sum(s['segments'] for s in stats[split_name].values())
        print(f"{split_name.upper():5s}: {total_videos:3d} videos, {total_segments:4d} segments")
    
    print(f"{'='*60}\n")
    print("✓ Split generation completed successfully!")


if __name__ == '__main__':
    main()



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for IO Layout Descriptor Tool

Usage:
    python tests/test_io_layout_descriptor.py <image_path>
    python tests/test_io_layout_descriptor.py <image_path1> <image_path2>  # Compare mode
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.io_layout_descriptor_tool import describe_io_layout_image, compare_io_layout_images


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tests/test_io_layout_descriptor.py <image_path>")
        print("  python tests/test_io_layout_descriptor.py <image_path1> <image_path2>  # Compare mode")
        sys.exit(1)
    
    image_path1 = sys.argv[1]
    
    if len(sys.argv) == 3:
        # Compare mode
        image_path2 = sys.argv[2]
        print("=" * 80)
        print("Comparing IO Layout Images")
        print("=" * 80)
        print(f"Image 1: {image_path1}")
        print(f"Image 2: {image_path2}")
        print()
        
        result = compare_io_layout_images(image_path1, image_path2)
        print(result)
    else:
        # Single image description mode
        print("=" * 80)
        print("Describing IO Layout Image")
        print("=" * 80)
        print(f"Image: {image_path1}")
        print()
        
        # Test detailed description
        print("Detailed Description:")
        print("-" * 80)
        result = describe_io_layout_image(image_path1, detailed=True)
        print(result)
        print()
        
        # Test concise description
        print("=" * 80)
        print("Concise Summary:")
        print("-" * 80)
        result = describe_io_layout_image(image_path1, detailed=False)
        print(result)


if __name__ == "__main__":
    main()


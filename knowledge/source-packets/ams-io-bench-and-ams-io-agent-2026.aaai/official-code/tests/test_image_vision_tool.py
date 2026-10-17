#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Image Vision Tool

This test script allows quick testing of the image vision tool functionality.
It tests both analyze_image_path and analyze_image_b64 functions.

Usage:
    python test_image_vision_tool.py [image_path]
    
    If image_path is not provided, it will look for example images in output directory.

Environment Variables Required:
    - IMAGE_API_BASE: Image API base URL
    - IMAGE_API_KEY: Image API key
    - IMAGE_MODEL (optional): Model identifier
"""

import sys
import os
import base64
import json
from pathlib import Path
from typing import Dict, Any

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.image_vision_tool import analyze_image_path, analyze_image_b64


def check_env_config():
    """Check if required environment variables are set"""
    print("🔍 Checking environment configuration...")
    
    api_base = os.environ.get("IMAGE_API_BASE")
    api_key = os.environ.get("IMAGE_API_KEY")
    model = os.environ.get("IMAGE_MODEL")
    
    print(f"  IMAGE_API_BASE: {'✅ Set' if api_base else '❌ Not set'}")
    print(f"  IMAGE_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"  IMAGE_MODEL: {'✅ Set' if model else '⚠️  Not set (will use default)'}")
    
    if not api_base or not api_key:
        print("\n⚠️  Warning: IMAGE_API_BASE and IMAGE_API_KEY are required!")
        print("   Please set them in your .env file:")
        print("   IMAGE_API_BASE=https://api.openai.com/v1")
        print("   IMAGE_API_KEY=sk-your-api-key-here")
        return False
    
    print("✅ Environment configuration OK\n")
    return True


def find_example_images():
    """Find example images in output directory"""
    output_dir = project_root / "output"
    example_images = []
    
    # Look for common image files
    for pattern in ["*.png", "*.jpg", "*.jpeg"]:
        example_images.extend(output_dir.rglob(pattern))
    
    # Also check example directories
    for example_dir in ["example_T28", "example_T180", "generated"]:
        example_path = output_dir / example_dir
        if example_path.exists():
            for pattern in ["*.png", "*.jpg", "*.jpeg"]:
                example_images.extend(example_path.rglob(pattern))
    
    return sorted(example_images, key=lambda p: p.stat().st_mtime, reverse=True)


def test_analyze_image_path(image_path: str):
    """Test analyze_image_path function"""
    print(f"📸 Testing analyze_image_path with: {image_path}")
    print("=" * 70)
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        return None
    
    try:
        result = analyze_image_path(image_path=image_path)
        
        # Parse the result (it's wrapped in format_tool_logs)
        if isinstance(result, dict):
            execution_log = result.get("execution_log", "")
            full_log = result.get("full_log", "")
            
            # Try to parse JSON from execution_log
            try:
                log_data = json.loads(execution_log)
                status = log_data.get("status", "unknown")
                
                if status == "ok":
                    print("✅ Analysis successful!")
                    print(f"\n📊 Result:")
                    print(json.dumps(log_data, indent=2, ensure_ascii=False))
                elif status == "error":
                    print(f"❌ Analysis failed: {log_data.get('error', 'unknown error')}")
                    print(f"   Message: {log_data.get('message', 'No message')}")
                    if 'http_status' in log_data:
                        print(f"   HTTP Status: {log_data.get('http_status')}")
                else:
                    print(f"⚠️  Unexpected status: {status}")
                    print(f"\n📊 Full result:")
                    print(json.dumps(log_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                # If not JSON, print as string
                print(f"\n📊 Result:")
                print(execution_log)
        else:
            print(f"\n📊 Result (raw):")
            print(result)
        
        print("\n" + "=" * 70 + "\n")
        return result
        
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_analyze_image_b64(image_path: str):
    """Test analyze_image_b64 function"""
    print(f"📸 Testing analyze_image_b64 with: {image_path}")
    print("=" * 70)
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        return None
    
    try:
        # Read image and convert to base64
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            image_b64 = base64.b64encode(image_bytes).decode("ascii")
        
        # Detect MIME type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(image_path)
        mime_type = mime_type or "image/png"
        
        print(f"  Image size: {len(image_bytes)} bytes")
        print(f"  MIME type: {mime_type}")
        print(f"  Base64 length: {len(image_b64)} characters")
        
        result = analyze_image_b64(image_b64=image_b64, mime_type=mime_type)
        
        # Parse the result
        if isinstance(result, dict):
            execution_log = result.get("execution_log", "")
            
            try:
                log_data = json.loads(execution_log)
                status = log_data.get("status", "unknown")
                
                if status == "ok":
                    print("✅ Analysis successful!")
                    print(f"\n📊 Result:")
                    print(json.dumps(log_data, indent=2, ensure_ascii=False))
                elif status == "error":
                    print(f"❌ Analysis failed: {log_data.get('error', 'unknown error')}")
                    print(f"   Message: {log_data.get('message', 'No message')}")
                else:
                    print(f"⚠️  Unexpected status: {status}")
                    print(f"\n📊 Full result:")
                    print(json.dumps(log_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(f"\n📊 Result:")
                print(execution_log)
        else:
            print(f"\n📊 Result (raw):")
            print(result)
        
        print("\n" + "=" * 70 + "\n")
        return result
        
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main test function"""
    print("🧪 Image Vision Tool Test")
    print("=" * 70)
    print()
    
    # Check environment configuration
    if not check_env_config():
        print("\n❌ Cannot proceed without proper configuration.")
        print("   Please set IMAGE_API_BASE and IMAGE_API_KEY in your .env file.")
        return
    
    # Get image path from command line or find example images
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Find example images
        example_images = find_example_images()
        
        if not example_images:
            print("❌ No example images found in output directory.")
            print("   Please provide an image path as argument:")
            print("   python test_image_vision_tool.py <image_path>")
            return
        
        # Use the most recent image
        image_path = str(example_images[0])
        print(f"📁 Using example image: {image_path}")
        print()
    
    # Test analyze_image_path
    print("\n" + "🔬 Test 1: analyze_image_path".center(70))
    result1 = test_analyze_image_path(image_path)
    
    # Test analyze_image_b64
    print("\n" + "🔬 Test 2: analyze_image_b64".center(70))
    result2 = test_analyze_image_b64(image_path)
    
    # Summary
    print("\n" + "📋 Test Summary".center(70))
    print("=" * 70)
    print(f"✅ analyze_image_path: {'PASSED' if result1 else 'FAILED'}")
    print(f"✅ analyze_image_b64: {'PASSED' if result2 else 'FAILED'}")
    print()
    print("🎉 Test completed!")


if __name__ == "__main__":
    main()


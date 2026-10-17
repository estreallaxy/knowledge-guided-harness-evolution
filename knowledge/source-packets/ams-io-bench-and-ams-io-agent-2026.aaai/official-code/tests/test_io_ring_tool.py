#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test IO Ring Generation Tool
"""

import sys
from pathlib import Path

# Add tools directory to Python path
tools_dir = Path(__file__).parent.parent
sys.path.append(str(tools_dir))

from src.tools.io_ring_generator_tool import generate_io_ring_schematic, list_intent_graphs, validate_intent_graph, generate_io_ring_layout

def test_list_configs():
    """Test list configuration files functionality"""
    print("🔍 Testing list IO ring configuration files...")
    result = list_intent_graphs()
    assert isinstance(result, str), "list_intent_graphs should return a string"
    assert len(result) > 0, "list_intent_graphs should return non-empty result"
    print(result)
    print()

def test_validate_config():
    """Test configuration validation functionality"""
    print("✅ Testing configuration validation functionality...")
    
    # Test 28nm configuration
    print("\n📌 Test 28nm configuration:")
    print("="*50)
    t28_config = "output/example_T28/intent_graph.json"
    if Path(t28_config).exists():
        result = validate_intent_graph(t28_config)
        assert isinstance(result, str), "validate_intent_graph should return a string"
        print(result)
    else:
        print(f"⚠️  Config file not found: {t28_config}")
    
    # Test 180nm configuration
    print("\n📌 Test 180nm configuration:")
    print("="*50)
    t180_config = "output/example_T180/intent_graph.json"
    if Path(t180_config).exists():
        result = validate_intent_graph(t180_config)
        assert isinstance(result, str), "validate_intent_graph should return a string"
        print(result)
    else:
        print(f"⚠️  Config file not found: {t180_config}")
    
    print()

def test_generate_schematic():
    """Test generate schematic functionality"""
    print("🎨 Testing generate IO ring schematic...")
    
    # Test 28nm process node
    print("\n📌 Test 28nm process node:")
    print("="*50)
    t28_config = "output/example_T28/intent_graph.json"
    t28_output = "output/example_T28/io_ring_schematic.il"
    if Path(t28_config).exists():
        result = generate_io_ring_schematic(t28_config, t28_output, process_node="T28")
        assert isinstance(result, str), "generate_io_ring_schematic should return a string"
        print(result)
    else:
        print(f"⚠️  Config file not found: {t28_config}")
    
    # Test 180nm process node
    print("\n📌 Test 180nm process node:")
    print("="*50)
    t180_config = "output/example_T180/intent_graph.json"
    t180_output = "output/example_T180/io_ring_schematic.il"
    if Path(t180_config).exists():
        result = generate_io_ring_schematic(t180_config, t180_output, process_node="T180")
        assert isinstance(result, str), "generate_io_ring_schematic should return a string"
        print(result)
    else:
        print(f"⚠️  Config file not found: {t180_config}")
    
    print()

def test_generate_layout():
    """Test generate layout functionality"""
    print("🏗️ Testing generate IO ring layout...")
    
    # Test 28nm process node
    print("\n📌 Test 28nm process node:")
    print("="*50)
    t28_config = "output/example_T28/intent_graph.json"
    t28_output = "output/example_T28/io_ring_layout.il"
    if Path(t28_config).exists():
        result = generate_io_ring_layout(t28_config, t28_output, process_node="T28")
        assert isinstance(result, str), "generate_io_ring_layout should return a string"
        print(result)
    else:
        print(f"⚠️  Config file not found: {t28_config}")
    
    # Test 180nm process node
    print("\n📌 Test 180nm process node:")
    print("="*50)
    t180_config = "output/example_T180/intent_graph.json"
    t180_output = "output/example_T180/io_ring_layout.il"
    if Path(t180_config).exists():
        result = generate_io_ring_layout(t180_config, t180_output, process_node="T180")
        assert isinstance(result, str), "generate_io_ring_layout should return a string"
        print(result)
    else:
        print(f"⚠️  Config file not found: {t180_config}")
    
    print()

def main():
    """Main function"""
    print("🧪 IO Ring Generation Tool Test")
    print("="*50)
    
    # Test list configuration files
    test_list_configs()
    
    # Test configuration validation
    test_validate_config()
    
    # Test generate schematic
    test_generate_schematic()
    
    # Test generate layout
    test_generate_layout()
    
    print("🎉 Test completed!")

if __name__ == "__main__":
    main() 
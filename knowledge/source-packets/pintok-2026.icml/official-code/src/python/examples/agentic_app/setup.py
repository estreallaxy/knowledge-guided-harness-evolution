#!/usr/bin/env python3
"""
Setup script for the RAG application
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description, check=True):
    """Run a shell command with description"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"{description} failed")
            print(f"Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"{description} failed with exception: {e}")
        return False

def check_service(service_name, command, expected_in_output=None):
    """Check if a service is running"""
    print(f"\nChecking {service_name}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            if expected_in_output and expected_in_output.lower() in result.stdout.lower():
                print(f"{service_name} is running")
                return True
            elif not expected_in_output:
                print(f"{service_name} is running")
                return True
        print(f"{service_name} is not running or not responding")
        return False
    except subprocess.TimeoutExpired:
        print(f"{service_name} check timed out")
        return False
    except Exception as e:
        print(f"Error checking {service_name}: {e}")
        return False

def main():
    print("Setting up RAG Application Environment")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Some dependencies may have failed to install. Check the output above.")
    
    # Check if Ollama is installed
    if not run_command("which ollama", "Checking Ollama installation", check=False):
        print("\nOllama not found. Please install Ollama:")
        print("   macOS: brew install ollama")
        print("   Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        print("   Or visit: https://ollama.ai/download")
    else:
        print("Ollama is installed")
        
        # Check if Ollama is running
        if not check_service("Ollama", "curl -s http://localhost:11434/api/version", "version"):
            print("\nStarting Ollama...")
            print("   Run: ollama serve")
            print("   Then in another terminal: ollama pull llama2")
    
    # Check if ChromaDB is available
    print("\nChecking ChromaDB setup...")
    try:
        import chromadb
        print("ChromaDB Python package is available")
        
        # Check if ChromaDB server is running (optional)
        if not check_service("ChromaDB Server", "curl -s http://localhost:8000/api/v1/heartbeat", check=False):
            print("ChromaDB server not running (this is OK if using persistent mode)")
    except ImportError:
        print("ChromaDB package not found")
    
    # Create necessary directories
    os.makedirs("./chroma_db", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    print("Created necessary directories")
    
    # Test basic imports
    print("\nTesting imports...")
    test_imports = [
        "fastapi",
        "uvicorn", 
        "chromadb",
        "sentence_transformers",
        "requests"
    ]
    
    failed_imports = []
    for module in test_imports:
        try:
            __import__(module)
            print(f"OK: {module}")
        except ImportError:
            print(f"Missing: {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nSome imports failed: {', '.join(failed_imports)}")
        print("Try running: pip install -r requirements.txt")
    
    print("\n" + "=" * 50)
    print("Setup Summary:")
    print("=" * 50)
    
    print("\nNext Steps:")
    print("1. Ensure Ollama is running: ollama serve")
    print("2. Pull an Ollama model: ollama pull llama2")
    print("3. (Optional) Start ChromaDB server: chroma run --host localhost --port 8000")
    print("4. Start the application: python main.py")
    print("5. Visit: http://localhost:8080/docs for API documentation")
    
    print("\nUseful Commands:")
    print("- Test health: curl http://localhost:8080/health")
    print("- Add documents: curl -X POST http://localhost:8080/documents ...")
    print("- Query: curl -X POST http://localhost:8080/query ...")
    
    print("\nConfiguration:")
    print("- Edit config.py to customize settings")
    print("- Set environment variables for different configurations")
    
    print("\nSetup complete! Happy coding!")

if __name__ == "__main__":
    main()

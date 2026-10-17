#!/bin/bash

# RAG Application Quick Start Script
# This script sets up and runs the RAG application

echo "RAG Application Quick Start"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: Please run this script from the agentic_app directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a service is running
check_service() {
    local service_name=$1
    local url=$2
    echo "Checking $service_name..."
    
    if curl -s "$url" >/dev/null 2>&1; then
        echo "$service_name is running"
        return 0
    else
        echo "$service_name is not running"
        return 1
    fi
}

# Check Python
if ! command_exists python3; then
    echo "Python 3 is required but not installed"
    exit 1
fi

echo "Python is available"

# Check pip
if ! command_exists pip; then
    echo "pip is required but not installed"
    exit 1
fi

echo "pip is available"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo "Dependencies installed successfully"

# Check Ollama
echo ""
if ! command_exists ollama; then
    echo "Ollama is not installed. Please install it:"
    echo "   macOS: brew install ollama"
    echo "   Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   Or visit: https://ollama.ai/download"
    echo ""
    echo "After installing Ollama, run:"
    echo "   ollama serve"
    echo "   ollama pull llama2"
    echo ""
    read -p "Press Enter to continue without Ollama (application may not work properly)..."
else
    echo "Ollama is installed"
    
    # Check if Ollama is running
    if check_service "Ollama" "http://localhost:11434/api/version"; then
        echo "Ollama is running"
        
        # Check if a model is available
        echo "Checking for available models..."
        if ollama list | grep -q "llama2\|mistral\|phi"; then
            echo "Model found"
        else
            echo "No suitable model found. Downloading llama2..."
            ollama pull llama2
        fi
    else
        echo "Ollama is not running. Starting it now..."
        echo "   In a new terminal, run: ollama serve"
        echo "   Then run: ollama pull llama2"
        echo ""
        read -p "Press Enter to continue after starting Ollama..."
    fi
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p chroma_db logs static
echo "Directories created"

# Check if ChromaDB server should be started
echo ""
echo "ChromaDB Configuration:"
echo "   This app can run with:"
echo "   1. Persistent ChromaDB (files stored locally) - Default"
echo "   2. ChromaDB server (requires running 'chroma run')"
echo ""

read -p "Do you want to use ChromaDB server? (y/N): " use_server

if [[ $use_server =~ ^[Yy]$ ]]; then
    echo "Starting ChromaDB server check..."
    if check_service "ChromaDB Server" "http://localhost:8000/api/v1/heartbeat"; then
        echo "ChromaDB server is running"
        export CHROMA_IS_PERSISTENT=false
        export CHROMA_HOST=localhost
        export CHROMA_PORT=8000
    else
        echo "ChromaDB server is not running."
        echo "   To start it, run in another terminal: chroma run --host localhost --port 8000"
        echo "   Or continue with persistent mode."
        echo ""
        read -p "Continue with persistent mode? (Y/n): " continue_persistent
        if [[ $continue_persistent =~ ^[Nn]$ ]]; then
            echo "Please start ChromaDB server and run this script again."
            exit 1
        fi
    fi
else
    echo "Using persistent ChromaDB mode"
    export CHROMA_IS_PERSISTENT=true
    export CHROMA_PERSIST_DIR=./chroma_db
fi

# Start the application
echo ""
echo "Starting RAG Application..."
echo "   The application will be available at: http://localhost:8080"
echo "   API documentation: http://localhost:8080/docs"
echo "   Web interface: http://localhost:8080/static/index.html"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the app
python main.py

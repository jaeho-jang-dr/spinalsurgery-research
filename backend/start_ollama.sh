#!/bin/bash
# Start Ollama service for SpinalSurgery Research

echo "🚀 Starting Ollama for SpinalSurgery Research..."

# Check if Ollama is installed
if [ ! -f "/home/drjang00/ollama" ]; then
    echo "❌ Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Set environment variables
export OLLAMA_HOST="0.0.0.0:11434"
export OLLAMA_MODELS="$HOME/.ollama/models"
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=2

# Create log directory
mkdir -p /home/drjang00/DevEnvironments/spinalsurgery-research/logs

# Stop any existing Ollama process
pkill -f "ollama serve" 2>/dev/null

# Start Ollama in the background
echo "Starting Ollama server..."
nohup /home/drjang00/ollama serve > /home/drjang00/DevEnvironments/spinalsurgery-research/logs/ollama.log 2>&1 &

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if curl -s http://localhost:11434/api/version > /dev/null; then
    echo "✅ Ollama is running!"
    
    # Pull required models
    echo "📦 Pulling required models..."
    
    # Pull Mistral first (faster)
    echo "Pulling mistral:7b..."
    /home/drjang00/ollama pull mistral:7b
    
    # Pull Llama2
    echo "Pulling llama2:7b..."
    /home/drjang00/ollama pull llama2:7b
    
    # Pull CodeLlama for code assistance
    echo "Pulling codellama:7b..."
    /home/drjang00/ollama pull codellama:7b
    
    echo "✅ All models ready!"
    echo ""
    echo "Ollama is running at: http://localhost:11434"
    echo "Logs: /home/drjang00/DevEnvironments/spinalsurgery-research/logs/ollama.log"
    echo ""
    echo "To stop Ollama: pkill -f 'ollama serve'"
else
    echo "❌ Failed to start Ollama. Check logs at: /home/drjang00/DevEnvironments/spinalsurgery-research/logs/ollama.log"
fi
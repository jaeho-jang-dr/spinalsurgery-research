#!/bin/bash

echo "🚀 SpinalSurgery Research Platform with Ollama"
echo "=============================================="

# Check if Ollama exists
if [ ! -f "/home/drjang00/ollama" ]; then
    echo "❌ Ollama not found at /home/drjang00/ollama"
    echo "Please ensure Ollama is installed first."
    exit 1
fi

# Start Ollama server in background
echo "🤖 Starting Ollama server..."
/home/drjang00/ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "Ollama PID: $OLLAMA_PID"

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama server may not be running properly"
    echo "Check /tmp/ollama.log for details"
else
    echo "✅ Ollama server is running"
    
    # List available models
    echo ""
    echo "📋 Available models:"
    curl -s http://localhost:11434/api/tags | python3 -c "
import json, sys
data = json.load(sys.stdin)
models = data.get('models', [])
if models:
    for model in models:
        print(f\"  - {model['name']}\")
else:
    print('  No models installed. Pull a model with: /home/drjang00/ollama pull llama2')
"
fi

# Navigate to project directory
cd /home/drjang00/DevEnvironments/spinalsurgery-research

# Start backend server
echo ""
echo "🔧 Starting backend server..."
cd backend
python3 run_sqlite_v2.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend server
echo ""
echo "🎨 Starting frontend server..."
cd ../frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Create stop script
cat > ../stop-all.sh << EOF
#!/bin/bash
echo "Stopping all services..."
kill $OLLAMA_PID 2>/dev/null
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
echo "All services stopped"
EOF
chmod +x ../stop-all.sh

echo ""
echo "✅ All services started successfully!"
echo ""
echo "🌐 Access the application at: http://localhost:3001"
echo "🤖 Ollama API available at: http://localhost:11434"
echo "🔧 Backend API available at: http://localhost:8000"
echo ""
echo "📝 Logs:"
echo "  - Ollama: /tmp/ollama.log"
echo "  - Backend: backend.log"
echo "  - Frontend: frontend.log"
echo ""
echo "🛑 To stop all services: ./stop-all.sh"
echo ""
echo "💡 Tips:"
echo "  - Install models: /home/drjang00/ollama pull llama2"
echo "  - List models: /home/drjang00/ollama list"
echo "  - Chat directly: /home/drjang00/ollama run llama2"
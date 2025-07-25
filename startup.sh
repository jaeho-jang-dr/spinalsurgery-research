#!/bin/bash

echo "🚀 Starting SpinalSurgery Research Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Copy environment files if they don't exist
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from example"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ Created frontend/.env from example"
fi

# Start services with Docker Compose
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec backend alembic upgrade head

echo "✅ All services are running!"
echo ""
echo "🌐 Access the application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/docs"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
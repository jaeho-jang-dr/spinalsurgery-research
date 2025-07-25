#!/bin/bash

echo "🔧 SpinalSurgery Research Platform - 개발 환경 설정"
echo "=================================================="

# 환경 변수 파일 생성
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ backend/.env 파일 생성됨"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ frontend/.env 파일 생성됨"
fi

# 필요한 디렉토리 생성
mkdir -p backend/uploads
mkdir -p backend/alembic/versions
echo "✅ 필요한 디렉토리 생성됨"

# Docker 서비스 시작 (개발용)
echo ""
echo "🐳 Docker 서비스 시작 중..."
docker compose -f docker-compose.dev.yml up -d

echo ""
echo "⏳ 서비스가 준비될 때까지 대기 중..."
sleep 10

# Ollama 모델 설치
echo ""
echo "🤖 Ollama 모델 설치 중..."
docker exec spinalsurgery_ollama_dev ollama pull llama2

echo ""
echo "✅ 개발 환경 설정 완료!"
echo ""
echo "📋 다음 단계:"
echo "1. Backend 실행:"
echo "   cd backend"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate  # Windows: venv\\Scripts\\activate"
echo "   pip install -r requirements.txt"
echo "   alembic upgrade head"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Frontend 실행:"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"
echo ""
echo "3. 접속:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/docs"
echo ""
echo "🛑 종료: docker compose -f docker-compose.dev.yml down"
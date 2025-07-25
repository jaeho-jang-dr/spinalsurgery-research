#!/bin/bash

echo "🚀 SpinalSurgery Research Platform - 로컬 실행 스크립트"
echo "======================================================="

# PostgreSQL이 실행 중인지 확인
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL이 설치되어 있지 않습니다."
    echo "설치 방법: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Redis가 실행 중인지 확인
if ! command -v redis-cli &> /dev/null; then
    echo "❌ Redis가 설치되어 있지 않습니다."
    echo "설치 방법: sudo apt-get install redis-server"
    exit 1
fi

# 백엔드 실행을 위한 스크립트
cat > backend/run.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

# Python 가상환경 활성화
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 의존성 설치
echo "Installing dependencies..."
pip install -r requirements.txt

# 데이터베이스 초기화
echo "Initializing database..."
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/spinalsurgery_research"

# 데이터베이스 생성 (이미 있으면 무시)
createdb -U postgres spinalsurgery_research 2>/dev/null || true

# 마이그레이션 실행
alembic upgrade head

# 서버 실행
echo "Starting backend server..."
uvicorn app.main:app --reload --port 8000
EOF

chmod +x backend/run.sh

# 프론트엔드 실행을 위한 스크립트
cat > frontend/run.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

# 의존성 설치
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# 개발 서버 실행
echo "Starting frontend server..."
npm run dev
EOF

chmod +x frontend/run.sh

echo ""
echo "✅ 실행 스크립트가 생성되었습니다!"
echo ""
echo "📋 실행 방법:"
echo "1. PostgreSQL 시작: sudo service postgresql start"
echo "2. Redis 시작: sudo service redis-server start"
echo "3. 새 터미널에서 백엔드 실행: ./backend/run.sh"
echo "4. 또 다른 터미널에서 프론트엔드 실행: ./frontend/run.sh"
echo ""
echo "또는 tmux/screen을 사용하여 한 번에 실행할 수 있습니다."
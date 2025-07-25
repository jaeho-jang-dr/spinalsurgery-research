# SpinalSurgery Research Platform - 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### 1. 개발 환경 설정 (처음 한 번만)

```bash
# 프로젝트 디렉토리로 이동
cd spinalsurgery-research

# 개발 환경 자동 설정 (Docker 서비스 시작)
./scripts/setup.sh
```

### 2. 백엔드 실행

새 터미널을 열고:

```bash
cd backend

# Python 가상환경 생성 (처음 한 번만)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치 (처음 한 번만)
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (처음 한 번만)
alembic upgrade head

# 백엔드 서버 실행
uvicorn app.main:app --reload
```

백엔드가 http://localhost:8000 에서 실행됩니다.

### 3. 프론트엔드 실행

또 다른 터미널을 열고:

```bash
cd frontend

# 의존성 설치 (처음 한 번만)
npm install

# 프론트엔드 개발 서버 실행
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

## 🌐 접속 주소

- **프론트엔드**: http://localhost:3000
- **백엔드 API 문서**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **ChromaDB**: http://localhost:8001

## 🛠️ 개발 도구

### VS Code 추천 확장

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- PostgreSQL

### 유용한 명령어

```bash
# Docker 서비스 상태 확인
docker compose -f docker-compose.dev.yml ps

# 로그 보기
docker compose -f docker-compose.dev.yml logs -f

# 데이터베이스 접속
docker exec -it spinalsurgery_postgres_dev psql -U postgres -d spinalsurgery_research

# Redis CLI
docker exec -it spinalsurgery_redis_dev redis-cli

# 서비스 중지
docker compose -f docker-compose.dev.yml down

# 서비스 및 데이터 완전 삭제
docker compose -f docker-compose.dev.yml down -v
```

## ⚡ 문제 해결

### Python 가상환경 생성 오류
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv python3-pip

# macOS (Homebrew)
brew install python3
```

### Docker 관련 오류
```bash
# Docker 서비스 재시작
sudo systemctl restart docker  # Linux
# macOS/Windows: Docker Desktop 재시작
```

### 포트 충돌
다른 서비스가 포트를 사용 중인 경우:
- PostgreSQL (5432) → `.env`에서 `POSTGRES_PORT` 변경
- Redis (6379) → `.env`에서 `REDIS_PORT` 변경
- Backend (8000) → `uvicorn` 명령에 `--port 8001` 추가
- Frontend (3000) → `package.json`의 dev 스크립트에 `-p 3001` 추가

## 📚 다음 단계

1. 테스트 계정으로 로그인:
   - Email: `test@example.com`
   - Password: `test1234`

2. 새 연구 프로젝트 생성

3. AI 기능 테스트:
   - 논문 검색
   - 초안 생성
   - 통계 분석

자세한 사용법은 [README.md](README.md)를 참조하세요.
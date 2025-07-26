# 🚀 빠른 프로젝트 이전 가이드

## 방법 1: GitHub 사용 (가장 간단) ⭐

### 현재 컴퓨터에서:
```bash
# 이미 GitHub에 push 완료됨!
# Repository: https://github.com/jaeho-jang-dr/spinalsurgery-research
```

### 새 컴퓨터에서:
```bash
# 1. 프로젝트 클론
git clone https://github.com/jaeho-jang-dr/spinalsurgery-research.git
cd spinalsurgery-research

# 2. Backend 설정
cd backend
pip install -r requirements.txt
python run_sqlite_v2.py

# 3. Frontend 설정 (새 터미널)
cd frontend
npm install
npm run dev
```

## 방법 2: Google Drive 백업

### 현재 컴퓨터에서:
```bash
# 백업 스크립트 실행
./backup-to-gdrive.sh
```

### 새 컴퓨터에서:
1. Google Drive에서 백업 파일 다운로드
2. WSL에 복사 후 압축 해제:
```bash
tar -xzf spinalsurgery-research-backup-*.tar.gz
cd spinalsurgery-research
```

## 필수 설치 프로그램
- Node.js 18+
- Python 3.8+
- Git
- WSL2 (Windows)

## AI 서비스 설정 (선택)
```bash
# Ollama 설치
./setup-ollama.sh

# 환경 변수 설정
export OLLAMA_API_URL=http://localhost:11434
export CLAUDE_API_KEY=your-api-key
```

끝! 🎉
# 프로젝트 이전 가이드 (Google Drive 활용)

## 현재 컴퓨터에서 백업하기

### 1. 프로젝트 압축
```bash
cd /home/drjang00/DevEnvironments
tar -czf spinalsurgery-research-backup.tar.gz spinalsurgery-research/
```

### 2. Google Drive에 업로드
1. 압축 파일을 Windows로 복사:
```bash
cp spinalsurgery-research-backup.tar.gz /mnt/c/Users/DRJAY/Desktop/
```

2. Google Drive에 업로드:
- 브라우저에서 drive.google.com 접속
- "새로 만들기" → "파일 업로드"
- Desktop에서 `spinalsurgery-research-backup.tar.gz` 선택

### 3. 환경 설정 백업
```bash
# 중요 설정 파일들도 함께 백업
cd ~
tar -czf wsl-settings-backup.tar.gz \
  .bashrc \
  .zshrc \
  DevEnvironments/.korean-config \
  DevEnvironments/korean-setup.sh \
  DevEnvironments/KOREAN_INPUT_FIXED.md
```

## 새 컴퓨터에서 복원하기

### 1. 필수 프로그램 설치
- WSL2 설치
- Node.js 18+ 설치
- Python 3.8+ 설치
- Git 설치
- VS Code 설치

### 2. Google Drive에서 다운로드
1. drive.google.com에서 백업 파일 다운로드
2. WSL 환경으로 복사:
```bash
# Windows Downloads 폴더에서 WSL로 복사
cp /mnt/c/Users/[사용자명]/Downloads/spinalsurgery-research-backup.tar.gz ~
```

### 3. 프로젝트 복원
```bash
# 홈 디렉토리에 DevEnvironments 생성
mkdir -p ~/DevEnvironments
cd ~/DevEnvironments

# 압축 해제
tar -xzf ~/spinalsurgery-research-backup.tar.gz

# 프로젝트 디렉토리로 이동
cd spinalsurgery-research
```

### 4. 의존성 설치
```bash
# Backend 의존성
cd backend
pip install -r requirements.txt

# Frontend 의존성
cd ../frontend
npm install
```

### 5. 한국어 설정 복원 (선택사항)
```bash
# 설정 파일 복원
cd ~
tar -xzf wsl-settings-backup.tar.gz

# 한국어 설정 실행
cd ~/DevEnvironments
./korean-setup.sh
```

### 6. 실행 확인
```bash
# Backend 실행
cd ~/DevEnvironments/spinalsurgery-research/backend
python run_sqlite_v2.py

# 새 터미널에서 Frontend 실행
cd ~/DevEnvironments/spinalsurgery-research/frontend
npm run dev
```

## GitHub를 통한 동기화 (권장)

### 현재 컴퓨터에서
```bash
cd ~/DevEnvironments/spinalsurgery-research
git add .
git commit -m "최신 변경사항 저장"
git push origin master
```

### 새 컴퓨터에서
```bash
cd ~/DevEnvironments
git clone https://github.com/jaeho-jang-dr/spinalsurgery-research.git
cd spinalsurgery-research

# 의존성 설치
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

## 데이터베이스 백업

SQLite 데이터베이스 파일도 백업이 필요한 경우:
```bash
# 데이터베이스 파일 위치 확인
find . -name "*.db" -o -name "*.sqlite"

# Google Drive에 별도 백업
cp backend/*.db ~/spinalsurgery-databases-backup/
```

## 주의사항
1. `.env` 파일들은 보안상 Git에 포함되지 않으므로 별도 백업 필요
2. `node_modules`와 `__pycache__`는 백업하지 않아도 됨 (재설치 가능)
3. AI API 키들은 안전하게 별도 보관

## 문제 해결
- 포트 충돌 시: package.json에서 포트 번호 변경
- Python 버전 문제: pyenv 또는 conda 사용 권장
- Node 버전 문제: nvm 사용 권장
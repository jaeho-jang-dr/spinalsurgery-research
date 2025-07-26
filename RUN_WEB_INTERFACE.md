# AI Assistant 웹 인터페이스 실행 가이드

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
cd /home/drjang00/DevEnvironments/spinalsurgery-research/web-interface
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
# 포어그라운드 실행
python server.py

# 백그라운드 실행
nohup python server.py > server.log 2>&1 &
```

### 3. 웹 브라우저 접속
- **URL**: http://localhost:5555
- 포트 변경 가능: `python server.py [포트번호]`
- 기본 포트: 5555

## 🔧 사전 준비 사항

### Claude CLI 설정
```bash
# 로그인 (브라우저 인증)
claude login

# 상태 확인
claude auth status
```

### Ollama 설정
```bash
# Ollama 설치
./install-ollama.sh

# 서비스 시작
ollama serve

# 모델 설치
ollama pull mistral:7b
```

## 💡 주요 기능

1. **AI 모델 선택**
   - Claude (고품질, 계정 로그인 사용)
   - Mistral 7B (빠른 응답)
   - Llama 2 (일반 대화)
   - CodeLlama (코드 생성)

2. **빠른 작업**
   - 📚 논문 검색
   - 🔍 초록 분석
   - 📝 개요 생성
   - 📖 참고문헌 확인

3. **토큰 사용량 모니터링**
   - 실시간 토큰 카운트
   - 비용 계산 (Claude만 해당)

## 🐛 문제 해결

### 서버가 시작되지 않을 때
```bash
# 포트 확인
ss -tln | grep 5555

# 프로세스 종료
pkill -f "python server.py"

# 다른 포트로 실행
python server.py 6000
```

### Ollama 연결 오류
```bash
# Ollama 상태 확인
curl http://localhost:11434/api/tags

# Ollama 재시작
ollama serve
```

### Claude CLI 인증 오류
```bash
# 재로그인
claude logout
claude login
```

## 📁 파일 구조
```
web-interface/
├── index.html       # 메인 페이지
├── style.css        # 스타일시트
├── script.js        # 클라이언트 스크립트
├── server.py        # Flask 서버
└── requirements.txt # Python 의존성
```

## 🔄 서버 종료
```bash
# 프로세스 ID 찾기
ps aux | grep server.py

# 종료
kill [PID]
```
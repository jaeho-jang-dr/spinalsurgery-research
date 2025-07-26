# 척추 수술 연구 AI Assistant 종합 가이드

## 📋 현재 상태
- ✅ Claude CLI 인증 완료
- ⚠️  Ollama 설치 필요 (install-ollama.sh 실행)
- ✅ 웹 인터페이스 실행 중 (http://localhost:5555)
- ✅ 논문 템플릿 생성 완료
- ✅ 참고문헌 관리 도구 준비

## 🚀 빠른 시작

### 1. Ollama 설치 (아직 안했다면)
```bash
cd /home/drjang00/DevEnvironments/spinalsurgery-research
./install-ollama.sh
```

### 2. 웹 인터페이스 접속
- URL: http://localhost:5555
- Claude (고품질) 또는 Ollama 모델 선택 가능
- 포트 변경: `python server.py 6000`

### 3. 주요 기능 사용

#### 논문 검색 (PubMed)
```bash
cd reference-manager
./pubmed-search.py "minimally invasive spine surgery"
```

#### 참고문헌 포맷팅
```python
python reference-formatter.py references.json vancouver
```

## 📁 프로젝트 구조

```
spinalsurgery-research/
├── web-interface/           # AI 채팅 웹 인터페이스
│   ├── index.html
│   ├── server.py           # Flask 서버
│   └── requirements.txt
├── templates/              # 논문 템플릿
│   ├── research-paper-template.md
│   ├── case-report-template.md
│   └── systematic-review-template.md
├── reference-manager/      # 참고문헌 도구
│   ├── pubmed-search.py   # PubMed 검색
│   └── reference-formatter.py # 포맷터
├── AI_ASSISTANT_SETUP.md   # AI 설정 가이드
├── OLLAMA_WSL2_SETUP.md   # Ollama 설정
└── RUN_WEB_INTERFACE.md   # 웹 실행 가이드
```

## 💡 사용 시나리오

### 1. 논문 작성 워크플로우
1. 템플릿 선택 (research-paper, case-report, systematic-review)
2. 웹 인터페이스에서 AI와 대화하며 초안 작성
3. PubMed 검색으로 관련 논문 찾기
4. 참고문헌 자동 포맷팅

### 2. 논문 검색 및 분석
```bash
# PubMed 검색
./pubmed-search.py "spinal fusion outcomes 2020-2024"

# 웹에서 초록 분석 요청
"이 논문의 초록을 분석해주세요: [초록 붙여넣기]"
```

### 3. 비용 효율적 사용
- **일반 작업**: Ollama 모델 (무료)
- **고품질 필요**: Claude CLI (계정 로그인)
- **토큰 모니터링**: 웹 인터페이스에서 실시간 확인

## 🔧 문제 해결

### Ollama 관련
```bash
# 상태 확인
curl http://localhost:11434/api/tags

# 수동 실행
ollama serve

# 모델 설치
ollama pull mistral:7b
```

### 웹 서버 관련
```bash
# 서버 재시작
pkill -f "python server.py"
cd web-interface
nohup python server.py > server.log 2>&1 &
```

### Claude CLI 관련
```bash
# 인증 상태
claude auth status

# 재로그인
claude logout
claude login
```

## 📚 추천 워크플로우

### 연구 논문 작성
1. `templates/research-paper-template.md` 복사
2. 웹 인터페이스에서 각 섹션 작성 도움 받기
3. PubMed 검색으로 근거 찾기
4. 참고문헌 자동 포맷팅

### 체계적 문헌고찰
1. `templates/systematic-review-template.md` 사용
2. PubMed 검색 전략 수립
3. AI로 검색식 최적화
4. 결과 분석 및 정리

## 🎯 다음 단계
- [ ] Zotero 연동
- [ ] Google Scholar 검색 추가
- [ ] 통계 분석 도구 통합
- [ ] 이미지/그래프 생성 AI

## 📞 도움말
- 웹 인터페이스: http://localhost:5555
- 가이드 문서: 이 파일 참조
- 문제 발생시: 각 섹션의 문제 해결 참조
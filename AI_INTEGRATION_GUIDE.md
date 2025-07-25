# AI Integration Guide - Spinal Surgery Research Platform

## 🤖 AI 통합 기능

이 플랫폼은 Claude Code, Ollama, NotebookLM 스타일의 AI 기능을 통합하여 척추외과 연구를 지원합니다.

## 📋 목차

1. [주요 기능](#주요-기능)
2. [설치 및 설정](#설치-및-설정)
3. [사용 방법](#사용-방법)
4. [API 엔드포인트](#api-엔드포인트)
5. [VS Code Extension](#vs-code-extension)
6. [문제 해결](#문제-해결)

## 🎯 주요 기능

### 1. **AI 채팅**
- Claude 및 Ollama 모델을 통한 실시간 대화
- 의학 연구 관련 질문 답변
- 프로젝트별 대화 기록 저장

### 2. **문서 분석 (NotebookLM 스타일)**
- 다중 문서 요약
- 자동 Q&A 생성
- 계층적 문서 구조 분석

### 3. **논문 초안 생성**
- 제목과 키워드 기반 자동 초안 작성
- 표준 의학 논문 형식 준수
- 참고문헌 자동 포맷팅

### 4. **MCP Filesystem 통합**
- 프로젝트 파일 자동 읽기/쓰기
- 파일 검색 및 관리
- VS Code와 완벽한 통합

## 🛠️ 설치 및 설정

### 1. Ollama 설치

```bash
# 설치 스크립트 실행
cd ~/DevEnvironments/spinalsurgery-research
./setup-ollama.sh
```

### 2. 환경 변수 설정

```bash
# ~/.bashrc에 추가
export OLLAMA_API_URL=http://localhost:11434
export CLAUDE_API_KEY=your-claude-api-key-here
export GITHUB_TOKEN=your-github-token-here
```

### 3. Python 패키지 설치

```bash
cd backend
pip install mcp aiohttp beautifulsoup4 lxml
```

### 4. VS Code Extension 설치

```bash
# VS Code에서 실행
code --install-extension anthropic.claude-code

# 또는 수동 설치
cd vscode-extension
npm install
code .
```

## 💻 사용 방법

### 1. 백엔드 서버 시작

```bash
cd backend
python3 run_sqlite_v2.py
```

### 2. 프론트엔드 시작

```bash
cd frontend
npm run dev
```

### 3. 웹 인터페이스 접속

브라우저에서 `http://localhost:3001` 접속

### 4. AI 기능 사용

1. 왼쪽 Activity Bar에서 로봇 아이콘(🤖) 클릭
2. 모델 선택 (Claude 또는 Ollama)
3. 원하는 기능 탭 선택:
   - **AI 채팅**: 연구 관련 질문
   - **문서 분석**: 논문/문서 분석
   - **논문 초안**: 자동 초안 생성

## 📡 API 엔드포인트

### AI 모델 목록
```http
POST /api/v1/ai/models
```

### AI 채팅
```http
POST /api/v1/ai/chat
{
  "project_id": "string",
  "message": "string",
  "model": "string",
  "session_id": "string (optional)"
}
```

### 문서 분석
```http
POST /api/v1/ai/analyze-documents
{
  "project_id": "string",
  "document_paths": ["string"],
  "analysis_type": "summary|qa|outline",
  "model": "string"
}
```

### 논문 초안 생성
```http
POST /api/v1/ai/generate-draft
{
  "project_id": "string",
  "title": "string",
  "keywords": ["string"],
  "outline": {},
  "references": [],
  "model": "string"
}
```

## 🔌 VS Code Extension

### 설정

1. `Cmd/Ctrl + ,` 로 설정 열기
2. "Claude Code" 검색
3. API 키 입력

### 명령어

- `Ctrl+Shift+A`: AI에게 질문하기
- `Ctrl+Shift+P`: 논문 초안 생성
- 마우스 오른쪽 클릭 메뉴에서 AI 기능 접근

### MCP 서버 설정

`.vscode/settings.json`:
```json
{
  "claude.apiKey": "${CLAUDE_API_KEY}",
  "mcp.servers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/path/to/project"]
    }
  }
}
```

## 🔧 문제 해결

### Ollama 연결 실패

```bash
# Ollama 서비스 확인
systemctl status ollama

# 수동으로 시작
ollama serve
```

### Claude API 오류

1. API 키 확인
2. 네트워크 연결 확인
3. API 사용량 제한 확인

### MCP 오류

```bash
# MCP 서버 재설치
npm install -g @modelcontextprotocol/server-filesystem
```

## 📚 사용 가능한 모델

### Ollama 모델
- **llama2**: 범용 대화 모델
- **codellama**: 코드 생성 특화
- **mistral**: 빠른 응답 속도
- **neural-chat**: 대화 최적화
- **medllama2**: 의료 특화 (사용 가능 시)

### Claude 모델
- **claude-3-opus**: 최고 성능
- **claude-3-sonnet**: 균형잡힌 성능
- **claude-3-haiku**: 빠른 응답

## 🎨 UI 커스터마이징

### 테마 변경
`frontend/src/styles/vscode-theme.css` 파일 수정

### 단축키 추가
`vscode-extension/package.json`의 `keybindings` 섹션 수정

## 🔐 보안 고려사항

1. API 키는 환경 변수로 관리
2. 민감한 의료 데이터는 로컬에서만 처리
3. HIPAA 규정 준수를 위한 로그 관리

## 📝 라이선스

이 프로젝트는 의료 연구 목적으로만 사용됩니다.

---

## 🆘 지원

문제가 있으시면 다음으로 연락하세요:
- GitHub Issues: [프로젝트 저장소]
- Email: support@spinalsurgery-research.com
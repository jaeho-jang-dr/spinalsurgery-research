# SpinalSurgery Research Platform - VS Code Extension

완전히 통합된 의학 연구 환경을 VS Code에서 직접 사용하세요.

## 주요 기능

### 🔬 연구 프로젝트 관리
- VS Code 내에서 직접 연구 프로젝트 생성 및 관리
- 프로젝트별 폴더 구조 자동 생성
- Git 통합으로 버전 관리

### 🤖 Claude AI 통합
- `Ctrl+Shift+C`: 선택한 텍스트로 Claude와 대화
- 자동 논문 작성 지원
- 문법 검토 및 과학적 정확성 검증
- 참고문헌 추천

### 📚 논문 검색 및 관리
- PubMed, Google Scholar 통합 검색
- 참고문헌 자동 포맷팅
- 인용 관리 시스템

### 📊 데이터 분석
- CSV, Excel 파일 직접 분석
- 통계 분석 자동화
- 시각화 코드 생성

### 💾 실시간 동기화
- 웹 앱과 실시간 데이터 동기화
- 다중 기기에서 작업 가능
- 자동 백업

## 설치 방법

### 1. 사전 요구사항
- VS Code 1.85.0 이상
- Claude Code CLI 설치
- Node.js 18.0 이상

### 2. Extension 설치
```bash
# Extension 디렉토리로 이동
cd spinalsurgery-research/vscode-extension

# 의존성 설치
npm install

# 빌드
npm run compile

# VS Code에서 F5를 눌러 Extension 실행
```

### 3. Claude Code CLI 설정
```bash
# Claude Code 로그인
claude-code login

# 인증 상태 확인
claude-code status
```

## 사용 방법

### 새 연구 프로젝트 시작
1. Command Palette (`Ctrl+Shift+P`)
2. "SpinalSurgery: New Research Project" 선택
3. 프로젝트 이름과 유형 입력

### Claude AI와 작업하기
1. 텍스트 선택
2. `Ctrl+Shift+C` 또는 우클릭 메뉴에서 "Chat with Claude"
3. AI 제안 받기

### 논문 검색
1. Command Palette에서 "SpinalSurgery: Search Academic Papers"
2. 검색어 입력
3. 결과를 Markdown으로 확인

### 데이터 분석
1. Explorer에서 데이터 파일 우클릭
2. "Analyze with SpinalSurgery" 선택
3. 분석 유형 선택

## 단축키

| 명령 | Windows/Linux | macOS |
|------|---------------|-------|
| Claude와 대화 | `Ctrl+Shift+C` | `Cmd+Shift+C` |
| 논문 검색 | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| 대시보드 열기 | `Ctrl+Shift+D` | `Cmd+Shift+D` |

## 설정

VS Code 설정에서 다음 항목을 구성할 수 있습니다:

```json
{
  "spinalsurgery.apiEndpoint": "http://localhost:8000",
  "spinalsurgery.autoSaveInterval": 300,
  "spinalsurgery.defaultExportFormat": "docx",
  "spinalsurgery.enableAISuggestions": true
}
```

## 문제 해결

### Claude Code가 작동하지 않음
```bash
# PATH 확인
which claude-code

# 재인증
claude-code logout
claude-code login
```

### Extension이 로드되지 않음
1. VS Code 재시작
2. Extension 로그 확인: View > Output > SpinalSurgery Research

### 동기화 문제
- 네트워크 연결 확인
- 백엔드 서버 상태 확인: http://localhost:8000/health

## 개발자 정보

Dr. Jang의 SpinalSurgery Research Platform

## 라이센스

MIT License
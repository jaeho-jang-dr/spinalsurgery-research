# SpinalSurgery Research Platform Version History

## v.00.00.00 (2025-07-26)

### 🎉 초기 릴리즈

#### 주요 기능
- **AI 통합 시스템**
  - Claude Code, Ollama, NotebookLM 스타일 통합
  - MCP (Model Context Protocol) 파일시스템 지원
  - AI 채팅, 문서 분석, 논문 초안 생성 기능

- **대량 논문 검색 엔진**
  - PubMed API 통합 (100+ 논문 동시 검색)
  - 실시간 검색 모니터링 (시작/일시정지/재개/종료)
  - 백그라운드 처리 및 검색 결과 색인

- **VS Code 스타일 UI**
  - 완전한 메뉴바 시스템 (File, Edit, Selection, View, Go, Run, Terminal, Help)
  - 드롭다운 메뉴 구현
  - Activity Bar 및 사이드바
  - 통합 터미널 (xterm.js)

- **연구 프로젝트 관리**
  - 프로젝트 생성 및 관리
  - 기존 프로젝트에서 연구 시작 기능
  - 논문 소스 관리 (연락처 추적)

#### 기술 스택
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Zustand
- **Backend**: Python HTTPServer, SQLite, BeautifulSoup4
- **AI**: Claude API, Ollama, MCP

#### 버그 수정
- React Icons barrel optimization 에러 해결
- xterm.js dimensions 런타임 에러 해결
- 한국어 키워드 PubMed 검색 문제 해결

#### 알려진 이슈
- Explorer 패널 미구현
- Search 패널 미구현
- 단축키 시스템 미구현

---
© 2025 SpinalSurgery Research Platform
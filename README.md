# SpinalSurgery Research Platform

척추외과 의료진을 위한 AI 기반 통합 연구 플랫폼

## 주요 기능

- 🤖 **AI 논문 작성 지원**: Claude Code, Ollama, NotebookLM 스타일 통합
- 📚 **논문 검색 및 관리**: PubMed 대량 검색 (100+ 논문 동시 처리)
- 📊 **실시간 검색 모니터링**: 시작/일시정지/재개/종료 기능
- 👥 **논문 소스 관리**: 저자 연락처 추적 시스템
- 📝 **VS Code 스타일 UI**: 친숙한 개발 환경 인터페이스
- 🖨️ **인쇄 지원**: 논문 및 연구 자료 출력

## 기술 스택

### Backend
- Python HTTPServer (SQLite 버전)
- SQLite Database
- BeautifulSoup4 (PubMed 파싱)
- MCP (Model Context Protocol)
- AI Service 통합 (Claude, Ollama)

### Frontend
- Next.js 14 (TypeScript)
- VS Code 스타일 다크 테마
- React Icons (커스텀 최적화)
- Xterm.js Terminal
- Zustand (상태 관리)

## 시작하기

### 사전 요구사항
- Node.js 18+
- Python 3.8+
- Git

### 설치 및 실행

1. 저장소 클론
```bash
git clone https://github.com/yourusername/spinalsurgery-research.git
cd spinalsurgery-research
```

2. 백엔드 설정
```bash
cd backend
pip install -r requirements.txt
python run_sqlite_v2.py
# 서버가 http://localhost:8000 에서 실행됩니다
```

3. 프론트엔드 설정
```bash
cd frontend
npm install
npm run dev
# 애플리케이션이 http://localhost:3001 에서 실행됩니다
```

4. AI 서비스 설정 (선택사항)
```bash
# Ollama 설치
./setup-ollama.sh

# 환경 변수 설정 (~/.bashrc 에 추가)
export OLLAMA_API_URL=http://localhost:11434
export CLAUDE_API_KEY=your-claude-api-key
```

## 프로젝트 구조
```
spinalsurgery-research/
├── backend/               # Python 백엔드
│   ├── run_sqlite_v2.py  # 메인 서버
│   ├── ai_service.py     # AI 통합 서비스
│   └── *.db              # SQLite 데이터베이스
├── frontend/              # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/          # 페이지 및 라우팅
│   │   ├── components/   # React 컴포넌트
│   │   │   ├── layout/   # VS Code 스타일 레이아웃
│   │   │   ├── research/ # 연구 관련 컴포넌트
│   │   │   ├── ai/       # AI 인터페이스
│   │   │   └── icons/    # 아이콘 최적화
│   │   └── lib/          # API 및 유틸리티
│   └── public/           # 정적 파일
└── docs/                  # 프로젝트 문서
```

## 사용법

### 1. 새 연구 프로젝트 시작
1. 메인 화면에서 연구 분야 입력 (예: 척추외과)
2. 키워드 추가 (예: 척추 고정술, VAS score)
3. "연구 시작" 클릭
4. AI가 관련 논문을 자동으로 검색 시작

### 2. 논문 검색 모니터링
- 실시간 검색 진행률 확인
- 일시정지/재개 버튼으로 제어
- 검색된 논문 즉시 확인 가능

### 3. AI 어시스턴트 활용
1. 왼쪽 Activity Bar에서 로봇 아이콘 클릭
2. 모델 선택 (Claude 또는 Ollama)
3. 탭 선택:
   - **AI 채팅**: 연구 관련 질의응답
   - **문서 분석**: 논문 요약 및 분석
   - **논문 초안**: AI 기반 초안 생성

### 4. 터미널 사용
- 하단 터미널에서 명령어 실행
- `help`: 사용 가능한 명령어 확인
- `status`: 시스템 상태 확인
- `analyze`: 데이터 분석 실행

## 주요 기능 상세

### 📊 대량 논문 검색
- PubMed E-utilities API 통합
- 100개 이상 논문 동시 검색
- 백그라운드 처리로 UI 차단 없음
- 검색 결과 실시간 업데이트

### 🤖 AI 통합
- **Claude Code**: VS Code 확장 연동
- **Ollama**: 로컬 LLM 지원
- **NotebookLM 스타일**: 문서 분석 및 Q&A

### 💾 데이터 관리
- SQLite 기반 안정적인 저장
- 논문 메타데이터 색인
- 전문 검색 기능
- 연구 프로젝트별 분류

## 문제 해결

### 포트 충돌
```bash
# 3001 포트가 사용 중인 경우
lsof -i :3001
kill -9 [PID]
```

### React Icons 에러
- 이미 최적화된 아이콘 시스템 사용
- `/src/components/icons/index.ts` 에서 관리

### AI 서비스 연결 실패
- Ollama 서비스 확인: `ollama serve`
- Claude API 키 확인: 환경 변수 설정

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 의료 연구 목적으로만 사용됩니다.

## 문의

- GitHub Issues: [프로젝트 이슈](https://github.com/yourusername/spinalsurgery-research/issues)
- Email: support@spinalsurgery-research.com

---

© 2025 SpinalSurgery Research Platform. All rights reserved.
# SpinalSurgery Research Platform - 초기화 문서

## 프로젝트 개요

### 비전
척추외과 의료진이 연구 활동을 효율적으로 수행할 수 있도록 지원하는 통합 플랫폼을 구축합니다. AI 기술을 활용하여 논문 작성부터 데이터 관리, 통계 분석까지 연구의 전 과정을 자동화하고 최적화합니다.

### 핵심 가치
- **효율성**: 반복적인 작업 자동화로 연구 시간 단축
- **정확성**: AI 기반 데이터 분석 및 논문 작성 지원
- **확장성**: 다른 의료 분야로 쉽게 확장 가능한 모듈화 설계
- **보안성**: 환자 데이터 익명화 및 철저한 접근 권한 관리

## 시스템 아키텍처

### 1. Frontend (사용자 인터페이스)
- **기술 스택**: React + TypeScript + Next.js
- **주요 화면**:
  - 로그인/인증 페이지
  - 대시보드 (연구 프로젝트 목록)
  - AI 질문 인터페이스
  - 논문 작성/편집기
  - 데이터 시각화 대시보드
  - 관리자 패널

### 2. Backend (비즈니스 로직)
- **기술 스택**: FastAPI (Python)
- **주요 모듈**:
  - 인증/권한 관리
  - 프로젝트 관리 API
  - AI 통합 서비스
  - 데이터 분석 엔진
  - 논문 검색/크롤링

### 3. AI Integration
- **로컬 AI**: Ollama (오프라인 작업)
- **클라우드 AI**: Claude (온라인 고급 작업)
- **오케스트레이션**: LangChain
- **벡터 DB**: ChromaDB (논문 유사도 검색)

### 4. Database
- **주 데이터베이스**: PostgreSQL
- **캐시**: Redis
- **파일 저장소**: MinIO (S3 호환)

## 핵심 기능 명세

### 1. 사용자 인증 및 권한 관리
```
- 이메일/비밀번호 로그인
- OAuth2 지원 (Google, Microsoft)
- 역할 기반 접근 제어 (RBAC)
  - Admin: 전체 시스템 관리
  - Researcher: 프로젝트 생성/편집
  - Viewer: 읽기 전용
```

### 2. AI 기반 연구 지원
```
입력 필드:
- 연구 분야 (필수): 예) "척추외과"
- 논문 제목 (선택): 예) "척추 후외방 고정술의 2년 후 결과"
- 키워드/방향 (선택): 예) "CD instrument", "34명", "VAS score"

처리 과정:
1. 관련 논문 검색 (PubMed, Google Scholar)
2. 유사 연구 분석
3. 논문 구조 생성
4. 초안 작성
5. 참고문헌 자동 정리
```

### 3. 데이터 관리
```
- 환자 데이터 익명화 저장
- 연구 데이터 버전 관리
- 통계 분석 자동화
- 결과 시각화
```

### 4. Informed Consent 생성
```
- 템플릿 기반 동의서 생성
- 연구별 커스터마이징
- 버전 관리 및 추적
```

## 개발 환경 설정

### 필수 도구
```bash
# Node.js 18+ (Frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python 3.10+ (Backend)
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# PostgreSQL 14+
sudo apt install postgresql postgresql-contrib

# Redis
sudo apt install redis-server

# Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 프로젝트 초기화
```bash
# 프로젝트 디렉토리 생성
mkdir -p ~/DevEnvironments/spinalsurgery-research
cd ~/DevEnvironments/spinalsurgery-research

# Git 저장소 초기화
git init
git remote add origin [repository-url]

# 기본 디렉토리 구조 생성
mkdir -p {frontend,backend,ai,database,scraper,docker,scripts,docs}
```

## 보안 고려사항

### 1. 데이터 보호
- 모든 환자 데이터는 익명화 처리
- 데이터베이스 암호화 (at-rest)
- HTTPS 통신 필수

### 2. 접근 제어
- JWT 기반 인증
- API Rate Limiting
- IP 화이트리스팅 (관리자)

### 3. 감사 추적
- 모든 데이터 접근 로깅
- 변경 이력 추적
- 정기적인 보안 감사

## 성능 목표

- 페이지 로드 시간: < 2초
- API 응답 시간: < 500ms
- AI 논문 생성: < 30초
- 동시 사용자: 100+

## 확장 계획

### Phase 1 (MVP)
- 기본 로그인/권한 시스템
- 간단한 AI 질문 인터페이스
- 기본 데이터 저장/조회

### Phase 2
- 고급 통계 분석
- 논문 크롤링 자동화
- 다국어 지원

### Phase 3
- 다른 의료 분야 확장
- 모바일 앱 개발
- 클라우드 배포

## 다음 단계

1. `prp.md` 작성 - 상세 요구사항 정의
2. 프로젝트 스캐폴딩 생성
3. 개발 환경 구성
4. 프로토타입 개발 시작

---

작성일: 2025-07-24
버전: 1.0.0
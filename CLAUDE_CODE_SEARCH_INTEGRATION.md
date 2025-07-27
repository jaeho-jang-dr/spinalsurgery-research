# Claude Code Paper Search Integration

## 개요

SpinalSurgery Research Platform에 VS Code의 Claude Code가 직접 논문을 검색하고 다운로드하는 시스템이 통합되었습니다. 사용자가 웹 앱에서 검색 버튼을 누르면 Claude Code가 여러 학술 사이트에서 논문을 검색하고, PDF를 다운로드하며, 한글로 번역합니다.

## 주요 기능

### 1. 다중 학술 사이트 검색
- **PubMed**: 의학 및 생명과학 논문
- **arXiv**: 과학, 수학, 컴퓨터 과학 프리프린트
- **Semantic Scholar**: AI 기반 학술 검색
- **Google Scholar**: (향후 구현 예정)

### 2. 실시간 진행 상황 업데이트
- WebSocket을 통한 실시간 통신
- 검색 진행률 표시
- 현재 검색 중인 사이트 표시
- 다운로드 상태 실시간 업데이트

### 3. 자동 PDF 다운로드
- PMC, arXiv 등에서 자동 PDF 다운로드
- 체계적인 폴더 구조로 저장
- 메타데이터 함께 저장

### 4. 한글 번역
- 논문 제목 자동 번역
- 초록 전체 번역
- 주요 섹션 요약 번역

## 사용 방법

### 웹 인터페이스에서

1. **논문 페이지 접속**
   - SpinalSurgery Research Platform에서 "논문" 메뉴 클릭
   - "Claude Code 검색" 탭 선택

2. **검색어 입력**
   ```
   예시: lumbar fusion 2-year outcomes
   ```

3. **고급 설정 (선택사항)**
   - 검색할 사이트 선택
   - 최대 결과 수 설정 (기본값: 10)

4. **검색 시작**
   - "Claude Code 검색" 버튼 클릭
   - 실시간 진행 상황 확인

5. **결과 확인**
   - 검색된 논문 목록 확인
   - 논문 클릭하여 상세 정보 보기
   - 한글/영어 전환 가능

## API 엔드포인트

### 1. 검색 시작
```http
POST /api/v1/claude-code-search/search
```

**Request Body:**
```json
{
  "query": "lumbar fusion 2-year outcomes",
  "max_results": 10,
  "search_sites": ["pubmed", "arxiv", "semantic_scholar"],
  "download_pdfs": true,
  "translate_to_korean": true,
  "project_id": "optional-project-id"
}
```

**Response:**
```json
{
  "search_id": "uuid-string",
  "status": "initiated",
  "message": "검색이 시작되었습니다."
}
```

### 2. WebSocket 연결
```javascript
ws://localhost:8000/api/v1/claude-code-search/ws/{search_id}
```

**Progress Messages:**
```json
{
  "type": "progress",
  "search_id": "uuid-string",
  "status": "searching",
  "current_site": "pubmed",
  "papers_found": 5,
  "papers_downloaded": 2,
  "progress_percentage": 45,
  "message": "PubMed에서 검색 중..."
}
```

### 3. 검색 상태 확인
```http
GET /api/v1/claude-code-search/search/{search_id}/status
```

### 4. 검색 결과 조회
```http
GET /api/v1/claude-code-search/search/{search_id}/results
```

## 파일 저장 구조

```
/research_papers/
├── project_{project_id}/           # 또는 search_{timestamp}/
│   ├── pubmed_12345678_Paper-Title/
│   │   ├── 12345678.pdf           # 다운로드된 PDF
│   │   ├── metadata.json          # 논문 메타데이터
│   │   └── summary_korean.txt     # 한글 번역 요약
│   ├── arxiv_2301.12345_Another-Paper/
│   │   ├── 2301.12345.pdf
│   │   ├── metadata.json
│   │   └── summary_korean.txt
│   └── ...
```

## 기술 스택

### Backend
- **FastAPI**: REST API 및 WebSocket 서버
- **aiohttp**: 비동기 HTTP 요청
- **pdfplumber**: PDF 텍스트 추출
- **deep-translator**: 한글 번역
- **WebSocket**: 실시간 통신

### Frontend
- **React/Next.js**: UI 프레임워크
- **WebSocket API**: 실시간 업데이트 수신
- **Tailwind CSS**: 스타일링

## 설치 및 실행

### 1. 필요한 패키지 설치
```bash
cd backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (선택사항)
```bash
export PUBMED_API_KEY="your-api-key"
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"
```

### 3. 백엔드 서버 실행
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

## 주의사항

1. **API 제한**: 각 학술 사이트의 API 제한을 준수합니다
2. **저작권**: 다운로드된 논문은 개인 연구 목적으로만 사용하세요
3. **번역 정확도**: 자동 번역은 참고용이며, 정확한 내용은 원문을 확인하세요
4. **저장 공간**: PDF 다운로드 시 충분한 디스크 공간이 필요합니다

## 문제 해결

### WebSocket 연결 실패
- 백엔드 서버가 실행 중인지 확인
- 방화벽 설정 확인
- CORS 설정 확인

### PDF 다운로드 실패
- 일부 논문은 오픈 액세스가 아닐 수 있습니다
- PMC ID가 있는 논문만 PMC에서 다운로드 가능합니다

### 번역 오류
- 네트워크 연결 확인
- 번역 API 제한 확인 (일일 한도)

## 향후 개선 사항

1. **추가 검색 사이트 통합**
   - Google Scholar 완전 지원
   - IEEE Xplore
   - SpringerLink

2. **고급 기능**
   - 중복 논문 제거 개선
   - 논문 인용 관계 분석
   - 자동 리뷰 논문 요약

3. **사용자 경험 개선**
   - 검색 히스토리 저장
   - 즐겨찾기 기능
   - 논문 노트 작성 기능

## 기여 방법

이 프로젝트는 오픈소스입니다. 기여를 환영합니다!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
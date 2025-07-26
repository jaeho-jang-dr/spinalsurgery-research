# SpinalSurgery Research Platform - 통합 워크플로우 가이드

## 🚀 완전 통합된 연구 환경

VS Code와 웹 앱이 완벽하게 통합되어, 하나의 환경에서 모든 연구 작업을 수행할 수 있습니다.

## 시작하기

### 1. 한 번의 명령으로 전체 시스템 시작
```bash
# VS Code에서 
Ctrl+Shift+B (Windows/Linux) 
Cmd+Shift+B (macOS)

# 또는 터미널에서
npm run start:all
```

이 명령은 다음을 자동으로 실행합니다:
- ✅ 백엔드 서버 (Python FastAPI)
- ✅ 프론트엔드 웹 앱 (Next.js)
- ✅ VS Code Extension
- ✅ Claude Code CLI 연결

### 2. Claude Code 인증
```bash
# 최초 1회만 필요
claude-code login
```

## 📋 주요 워크플로우

### 1. 새 연구 프로젝트 시작
```
1. VS Code: Ctrl+Shift+P → "New Research Project"
2. 프로젝트 이름 입력 (예: "척추 수술 결과 분석")
3. 프로젝트 유형 선택
4. 자동으로 생성되는 것들:
   - 📁 프로젝트 폴더 구조
   - 📄 README.md 템플릿
   - 🤖 Claude AI 초기 제안
   - 🌐 웹 대시보드 연동
```

### 2. AI 지원 논문 작성
```
1. Markdown 파일에서 작성 시작
2. 텍스트 선택 → Ctrl+Shift+C
3. Claude에게 질문 또는 개선 요청
4. 실시간으로 제안 받기
5. 웹 앱에서도 동시에 확인 가능
```

### 3. 데이터 분석 워크플로우
```
1. CSV/Excel 파일을 프로젝트에 추가
2. 파일 우클릭 → "Analyze with SpinalSurgery"
3. 분석 유형 선택:
   - 기술 통계
   - 상관 분석
   - 회귀 분석
   - 시각화
4. Claude가 Python 코드 생성
5. 결과를 논문에 바로 삽입
```

### 4. 참고문헌 관리
```
1. 논문 검색: Ctrl+Shift+P → "Search Papers"
2. 검색 결과에서 선택
3. 자동으로 Bibliography에 추가
4. 인용 시: [@author2024] 형식으로 입력
5. 내보낼 때 자동 포맷팅
```

## 🔄 실시간 동기화

### VS Code ↔ 웹 앱 동기화
- 파일 변경사항 자동 동기화
- 프로젝트 상태 실시간 업데이트
- 다중 기기 작업 지원

### 동기화되는 항목들
- ✅ 프로젝트 파일
- ✅ 연구 데이터
- ✅ AI 대화 내역
- ✅ 참고문헌
- ✅ 분석 결과

## 💡 고급 기능

### 1. 멀티 터미널 활용
```typescript
// 홈페이지에서 터미널 열기
// 여러 개의 터미널 탭 지원
- Bash
- PowerShell
- Claude Code CLI
- Python 인터프리터
```

### 2. 협업 기능
```
1. VS Code Live Share 시작
2. 동료 초대
3. 실시간 공동 편집
4. Claude AI 공유 세션
```

### 3. 자동화된 작업
```json
// .vscode/settings.json
{
  "spinalsurgery.autoSave": true,
  "spinalsurgery.autoBackup": true,
  "spinalsurgery.aiSuggestions": true
}
```

## 📊 대시보드 뷰

### VS Code 사이드바
```
Research Platform
├── 📁 Research Projects
│   ├── 척추 수술 결과 분석
│   ├── 디스크 치환술 연구
│   └── 메타분석 프로젝트
├── 📊 Data Sets
│   ├── patient_data.csv
│   └── surgery_outcomes.xlsx
├── 📚 Bibliography
│   ├── PubMed (45)
│   └── Local (12)
└── 🤖 AI Assistant
    ├── Chat History
    └── Suggestions
```

### 웹 대시보드
- 프로젝트 진행 상황
- 통계 시각화
- 타임라인
- 협업자 활동

## 🛠️ 문제 해결

### 연결 문제
```bash
# 상태 확인
curl http://localhost:8000/health
curl http://localhost:3001

# 서비스 재시작
npm run restart:all
```

### Extension 문제
```
1. View → Output → SpinalSurgery Research
2. 에러 로그 확인
3. Extension 재로드: Ctrl+R
```

## 📝 베스트 프랙티스

1. **프로젝트 구조 유지**
   - 각 연구는 별도 폴더
   - 일관된 명명 규칙
   - Git으로 버전 관리

2. **AI 활용 팁**
   - 구체적인 질문하기
   - 컨텍스트 제공하기
   - 제안 검토 후 적용

3. **데이터 관리**
   - 원본 데이터 보존
   - 분석 스크립트 저장
   - 결과 재현 가능하게

## 🎯 Quick Commands

| 작업 | 단축키/명령 |
|------|------------|
| 새 프로젝트 | `Ctrl+Shift+N` |
| Claude 대화 | `Ctrl+Shift+C` |
| 논문 검색 | `Ctrl+Shift+P` |
| 데이터 분석 | `Ctrl+Shift+A` |
| 대시보드 | `Ctrl+Shift+D` |
| 터미널 토글 | `Ctrl+\`` |
| 내보내기 | `Ctrl+Shift+E` |

## 🎉 시작해보세요!

이제 VS Code 하나로 전체 연구 프로세스를 관리할 수 있습니다. 
Claude AI와 함께 더 빠르고 정확한 연구를 진행하세요!
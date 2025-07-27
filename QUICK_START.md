# SpinalSurgery Research Platform - 빠른 시작 가이드

## 🚀 현재 실행 상태

✅ **백엔드**: http://localhost:8000 (정상 작동)
✅ **프론트엔드**: http://localhost:3001 (정상 작동)
✅ **AI Assistant**: 완전 구현 및 작동 중

## 📌 빠른 접속

1. **웹 브라우저에서 http://localhost:3001 접속**

2. **로그인**
   - 이메일: 아무거나 (예: test@test.com)
   - 비밀번호: 아무거나 (예: 1234)
   - Mock 인증이 활성화되어 있어 어떤 값이든 가능

3. **AI Assistant 사용하기**
   - 왼쪽 사이드바에서 "AI 어시스턴트" 아이콘 클릭
   - 고급 AI 기능이 바로 사용 가능

## 🤖 AI Assistant 주요 기능

### 기본 사용법
```
일반 대화: 그냥 메시지 입력
예: "요추 유합술에 대해 설명해줘"
```

### Magic Commands (매직 명령어)
```
/help                    - 모든 명령어 보기
/think 주제              - 순차적 사고 프로세스
/persona data_analyst    - AI 페르소나 변경
/remember facts: 내용    - 장기 메모리에 저장
/recall 키워드           - 메모리에서 검색
/research 쿼리           - 연구 모드 활성화
/analyze 주제            - 심층 분석
/write 컨텍스트          - 학술 작성 모드
/code 요청               - 코드 지원 모드
/context                 - 현재 컨텍스트 보기
```

### AI 페르소나 (우측 설정에서 변경 가능)
1. **Dr. Serena** - 척추외과 연구 어시스턴트 (기본)
2. **Alex Data** - 의료 데이터 분석 전문가
3. **Professor Write** - 학술 작성 전문가
4. **Dev Helper** - 의료 소프트웨어 개발자

### 메모리 관리
- **내보내기**: Settings → Export Memory
- **가져오기**: Settings → Import Memory
- **메모리 삭제**: Clear Short-term / Clear Long-term

## 🔧 서버 관리 명령어

### 서버 상태 확인
```bash
# 백엔드 상태
ps aux | grep uvicorn

# 프론트엔드 상태
ps aux | grep next
```

### 서버 재시작 (필요시)
```bash
# 백엔드 재시작
cd ~/DevEnvironments/spinalsurgery-research/backend
pkill -f uvicorn
uvicorn app.main:app --reload --port 8000 &

# 프론트엔드 재시작
cd ~/DevEnvironments/spinalsurgery-research/frontend
pkill -f "next dev"
npm run dev &
```

## 📝 문제 해결

1. **localhost:3001 접속 안됨**
   - 프론트엔드 재시작 필요
   - `npm run dev` 실행

2. **AI가 응답하지 않음**
   - 백엔드 상태 확인
   - http://localhost:8000/docs 접속 확인

3. **로그인 안됨**
   - Mock 인증 사용 중
   - 아무 이메일/비밀번호 입력

## 💡 활용 예시

### 연구 논문 분석
```
/think 요추 유합술 2년 추적 결과의 주요 예후 인자
```

### 데이터 분석 지원
```
/persona data_analyst
PLIF와 TLIF의 fusion rate 비교 통계 분석 방법을 추천해줘
```

### 논문 초록 작성
```
/persona paper_writer
/write 요추 유합술 2년 추적 연구 초록
```

---

**준비 완료!** 이제 SpinalSurgery Research Platform의 모든 기능을 사용할 수 있습니다. 🎉
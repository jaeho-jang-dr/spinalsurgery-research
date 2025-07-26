# Universal VS Code 단축키 가이드

## 설정 완료: Ctrl+Shift+7

이제 `Ctrl+Shift+7`을 누르면 다음 위치에서 명령어가 입력됩니다:

### 1. 터미널 (Terminal)
- 명령어 입력 후 자동 실행 (Enter 포함)
- 예: Bash, PowerShell, Command Prompt

### 2. 에디터 (Editor)
- 코드 편집기, 마크다운 파일 등
- 커서 위치에 텍스트 삽입

### 3. 입력 필드 (Input Fields)
- 검색창 (Ctrl+F)
- 명령 팔레트 (Ctrl+Shift+P)
- 파일 검색 (Ctrl+P)
- Claude Code CLI 채팅창
- Git 커밋 메시지 입력창
- 기타 모든 텍스트 입력 필드

## 작동 방식

```
/sc implement --c7 --seq --magic --memory --persona endpoint
```

위 명령어가:
- **터미널**: 입력 + Enter (자동 실행)
- **에디터/입력필드**: 텍스트만 입력 (수동 실행)

## 사용 예시

1. **Claude Code CLI에서**:
   - 채팅 입력창에 포커스
   - `Ctrl+Shift+7` 누르기
   - 명령어 자동 입력됨
   - Enter로 실행

2. **터미널에서**:
   - `Ctrl+Shift+7` 누르기
   - 자동 실행됨

3. **코드 편집기에서**:
   - 주석이나 문서에 명령어 기록할 때
   - `Ctrl+Shift+7`로 빠르게 입력

## 문제 해결

만약 특정 위치에서 작동하지 않는다면:
1. `Ctrl+Shift+P` → "Developer: Inspect Context Keys"
2. 현재 포커스 상태 확인
3. keybindings.json에 해당 조건 추가

## 커스터마이징

다른 명령어도 추가하려면:
```json
{
  "key": "ctrl+shift+8",
  "command": "type",
  "args": {
    "text": "your-custom-command"
  },
  "when": "inputFocus"
}
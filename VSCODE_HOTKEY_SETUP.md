# VS Code 단축키 설정 가이드

## 자동 설정 (프로젝트 전용)
이 프로젝트의 `.vscode/keybindings.json` 파일에 이미 설정되어 있습니다.

## 수동 설정 (전역 적용)

### 방법 1: GUI를 통한 설정
1. VS Code에서 `Ctrl+K Ctrl+S` (키보드 단축키 메뉴 열기)
2. 검색창에 "terminal.sendSequence" 입력
3. "Terminal: Send Sequence" 찾기
4. 왼쪽 + 버튼 클릭하여 새 단축키 추가
5. `Ctrl+Shift+7` 입력
6. When 조건에 `terminalFocus` 입력
7. 오른쪽 기어 아이콘 → "Change Keybinding"
8. Args 입력창에:
```json
{
  "text": "/sc implement --c7 --seq --magic --memory --persona endpoint\n"
}
```

### 방법 2: keybindings.json 직접 편집
1. `Ctrl+Shift+P` → "Preferences: Open Keyboard Shortcuts (JSON)"
2. 다음 내용 추가:
```json
[
  {
    "key": "ctrl+shift+7",
    "command": "workbench.action.terminal.sendSequence",
    "args": {
      "text": "/sc implement --c7 --seq --magic --memory --persona endpoint\n"
    },
    "when": "terminalFocus"
  },
  {
    "key": "ctrl+shift+7",
    "command": "runCommands",
    "args": {
      "commands": [
        "workbench.action.terminal.focus",
        {
          "command": "workbench.action.terminal.sendSequence",
          "args": {
            "text": "/sc implement --c7 --seq --magic --memory --persona endpoint\n"
          }
        }
      ]
    },
    "when": "!terminalFocus"
  }
]
```

## 사용법
- **터미널에 포커스가 있을 때**: `Ctrl+Shift+7` → 명령어 즉시 실행
- **터미널에 포커스가 없을 때**: `Ctrl+Shift+7` → 터미널로 이동 후 명령어 실행

## 주의사항
- 명령어에서 `--serena`를 제거했습니다 (요청대로)
- 명령어 끝에 `\n`이 포함되어 자동으로 Enter가 입력됩니다
- `Ctrl+Shift+7`은 기존 단축키와 충돌하지 않습니다

## 원래 단축키 복원
Save All 기능을 다른 키로 변경하려면:
```json
{
  "key": "ctrl+alt+s",
  "command": "workbench.action.files.saveAll"
}
```
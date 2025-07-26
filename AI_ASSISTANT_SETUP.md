# AI Assistant 통합 환경 설정 가이드

## 목표
논문 검색 및 작성을 위한 AI Assistant 환경 구축
- Claude Code (VSCode 확장) + CLI 로그인 방식
- Ollama 로컬 LLM 연동

## 1. Claude Code Windows VSCode 확장 프로그램 설치

### 사전 요구사항
- Visual Studio Code 설치
- Windows Terminal 또는 PowerShell
- WSL2 설정 완료

### 설치 단계

1. **VSCode 확장 설치**
   ```bash
   # VSCode에서 Extensions 탭 열기 (Ctrl+Shift+X)
   # "Claude Code" 검색
   # 또는 명령어로 설치:
   code --install-extension claude.claude-code
   ```

2. **Claude CLI 설치**
   ```bash
   # Windows PowerShell 관리자 권한으로 실행
   iwr https://github.com/anthropics/claude-cli/releases/latest/download/claude-windows-amd64.exe -OutFile claude.exe
   
   # 환경 변수에 추가
   $env:Path += ";$PWD"
   [Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::User)
   ```

3. **WSL2에서 Claude CLI 설치**
   ```bash
   # WSL2 터미널에서 실행
   curl -fsSL https://github.com/anthropics/claude-cli/releases/latest/download/claude-linux-amd64 -o claude
   chmod +x claude
   sudo mv claude /usr/local/bin/
   ```

## 2. Claude CLI 로그인 방식 설정 (API 비용 절감)

### 계정 로그인 방식 사용
```bash
# 브라우저 인증 방식 (API 키 불필요)
claude login

# 로그인 상태 확인
claude auth status
```

### VSCode 설정
```json
{
  "claude-code.authentication": {
    "method": "cli",
    "useAccountLogin": true
  },
  "claude-code.features": {
    "autoComplete": true,
    "inlineChat": true,
    "codeActions": true
  }
}
```

## 3. Ollama 연동 설정

### Ollama 확인 및 모델 설치
```bash
# Ollama 상태 확인
ollama list

# 추천 모델 설치
ollama pull llama2:13b
ollama pull codellama:13b
ollama pull mistral:7b
```

### VSCode Ollama 확장 설치
```bash
code --install-extension continue.continue
```

### Continue 설정 (config.json)
```json
{
  "models": [
    {
      "title": "Ollama - Llama 2",
      "provider": "ollama",
      "model": "llama2:13b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Claude (Account)",
      "provider": "anthropic",
      "model": "claude-3-opus-20240229",
      "useCliAuth": true
    }
  ],
  "tabAutocompleteModel": {
    "title": "Ollama CodeLlama",
    "provider": "ollama",
    "model": "codellama:13b"
  }
}
```

## 4. 통합 사용 시나리오

### 논문 검색
```bash
# Claude로 논문 검색 (무료)
claude chat "Find recent papers on spinal surgery techniques"

# Ollama로 로컬 분석
ollama run llama2 "Analyze this abstract: [paste abstract]"
```

### 논문 작성
```bash
# VSCode에서
# 1. Claude Code 확장으로 초안 작성
# 2. Ollama로 로컬 검토 및 수정
# 3. Claude CLI로 최종 검토
```

## 5. 비용 절감 팁

1. **일반 작업**: Ollama 로컬 모델 사용
2. **고품질 필요시**: Claude CLI 계정 로그인 사용
3. **API 사용 최소화**: 꼭 필요한 경우만 API 키 사용

## 6. 문제 해결

### Claude CLI 로그인 실패
```bash
# 캐시 정리
claude auth logout
rm -rf ~/.claude/
claude login
```

### Ollama 연결 실패
```bash
# Ollama 서비스 재시작
sudo systemctl restart ollama
# 또는
ollama serve
```

## 다음 단계
- Research Assistant 워크플로우 구성
- 논문 템플릿 설정
- 참고문헌 관리 도구 연동
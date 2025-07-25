#!/bin/bash

echo "🚀 Ollama 설치 및 설정 스크립트"
echo "================================"

# Ollama 설치 확인
if ! command -v ollama &> /dev/null; then
    echo "📦 Ollama 설치 중..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama가 이미 설치되어 있습니다"
fi

# Ollama 서비스 시작
echo "🔧 Ollama 서비스 시작 중..."
ollama serve &
OLLAMA_PID=$!

# 잠시 대기
sleep 5

# 기본 모델 다운로드
echo "📥 기본 모델 다운로드 중..."

# Llama 2 (7B) - 가장 인기 있는 오픈소스 모델
echo "1. Llama 2 다운로드..."
ollama pull llama2

# CodeLlama - 코드 생성에 특화된 모델
echo "2. CodeLlama 다운로드..."
ollama pull codellama

# Mistral - 빠르고 효율적인 모델
echo "3. Mistral 다운로드..."
ollama pull mistral

# Neural Chat - 대화에 최적화된 모델
echo "4. Neural Chat 다운로드..."
ollama pull neural-chat

# 의료 분야 특화 모델 (있는 경우)
echo "5. 의료 관련 모델 확인 중..."
ollama pull medllama2 2>/dev/null || echo "의료 특화 모델은 아직 사용할 수 없습니다"

# 설치된 모델 목록 확인
echo ""
echo "📋 설치된 모델 목록:"
ollama list

echo ""
echo "✅ Ollama 설정 완료!"
echo ""
echo "🔗 Ollama API 엔드포인트: http://localhost:11434"
echo ""
echo "📌 사용 가능한 명령어:"
echo "   ollama serve        - 서버 시작"
echo "   ollama list         - 모델 목록 확인"
echo "   ollama pull <model> - 새 모델 다운로드"
echo "   ollama run <model>  - 모델과 대화"
echo ""
echo "🎯 SpinalSurgery Research 플랫폼에서 AI 기능을 사용할 준비가 완료되었습니다!"

# 환경 변수 설정
echo ""
echo "🔧 환경 변수 설정 중..."
echo "export OLLAMA_API_URL=http://localhost:11434" >> ~/.bashrc
echo "환경 변수가 ~/.bashrc에 추가되었습니다"

# VS Code Extension 설정 파일 생성
echo ""
echo "📝 VS Code 설정 파일 생성 중..."
cat > ~/DevEnvironments/spinalsurgery-research/.vscode/settings.json << EOF
{
  "claude.apiKey": "\${CLAUDE_API_KEY}",
  "claude.model": "claude-3-opus-20240229",
  "ollama.apiEndpoint": "http://localhost:11434",
  "ollama.defaultModel": "llama2",
  "mcp.servers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/drjang00/DevEnvironments/spinalsurgery-research"]
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "\${GITHUB_TOKEN}"
      }
    }
  }
}
EOF

echo "✅ VS Code 설정 파일이 생성되었습니다"
echo ""
echo "🎉 모든 설정이 완료되었습니다!"
echo ""
echo "다음 단계:"
echo "1. 새 터미널을 열어 환경 변수를 적용하세요"
echo "2. 'cd ~/DevEnvironments/spinalsurgery-research/backend && python3 run_sqlite_v2.py' 실행"
echo "3. 웹브라우저에서 http://localhost:3001 접속"
echo "4. AI 어시스턴트 메뉴에서 모델을 선택하고 사용하세요"
#!/bin/bash
# Ollama WSL2 간편 설치 스크립트

echo "=== Ollama WSL2 설치 시작 ==="

# 1. Ollama 설치
echo "1. Ollama 설치 중..."
curl -fsSL https://ollama.com/install.sh | sh

# 2. 설치 확인
if command -v ollama &> /dev/null; then
    echo "✅ Ollama 설치 완료!"
    ollama --version
else
    echo "❌ Ollama 설치 실패. 수동 설치를 시도하세요."
    exit 1
fi

# 3. 환경 변수 설정
echo "2. 환경 변수 설정 중..."
cat >> ~/.bashrc << 'EOF'

# Ollama 설정
export OLLAMA_HOST="0.0.0.0:11434"
export OLLAMA_MODELS="$HOME/.ollama/models"
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=2
EOF

# 4. 서비스 시작
echo "3. Ollama 서비스 시작 중..."
if systemctl is-system-running &>/dev/null; then
    sudo systemctl start ollama
    sudo systemctl enable ollama
    echo "✅ Systemd 서비스로 시작됨"
else
    echo "⚠️  Systemd를 사용할 수 없습니다. 백그라운드로 실행합니다."
    nohup ollama serve > ~/ollama.log 2>&1 &
    echo "✅ 백그라운드로 실행 중 (로그: ~/ollama.log)"
fi

# 5. 기본 모델 설치
echo "4. 기본 모델 설치 중..."
echo "   이 작업은 시간이 걸릴 수 있습니다..."

# 서비스가 시작될 때까지 대기
sleep 5

# 가벼운 모델부터 설치
ollama pull mistral:7b
echo "✅ Mistral 7B 설치 완료"

# 6. 설치 완료
echo ""
echo "=== Ollama 설치 완료! ==="
echo ""
echo "사용 가능한 명령어:"
echo "  ollama list          - 설치된 모델 확인"
echo "  ollama run mistral   - Mistral 모델 실행"
echo "  ollama pull llama2   - 추가 모델 설치"
echo ""
echo "추천 모델:"
echo "  - mistral:7b (설치됨) - 빠르고 효율적"
echo "  - llama2:7b           - 일반 대화용"
echo "  - codellama:7b        - 코드 생성용"
echo ""
echo "환경 변수를 적용하려면 다음 명령어를 실행하세요:"
echo "  source ~/.bashrc"
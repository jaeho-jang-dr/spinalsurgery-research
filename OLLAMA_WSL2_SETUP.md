# Ollama WSL2 설치 가이드

## 1. Ollama 설치 (WSL2)

### 자동 설치 스크립트
```bash
# WSL2 터미널에서 실행
curl -fsSL https://ollama.com/install.sh | sh
```

### 수동 설치
```bash
# 1. 바이너리 다운로드
curl -L https://ollama.com/download/ollama-linux-amd64 -o ollama
chmod +x ollama
sudo mv ollama /usr/local/bin/

# 2. 서비스 설정
sudo useradd -r -s /bin/false -m -d /usr/share/ollama ollama
sudo mkdir -p /etc/systemd/system

# 3. systemd 서비스 파일 생성
cat <<EOF | sudo tee /etc/systemd/system/ollama.service
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Type=simple
User=ollama
Group=ollama
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 4. 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
```

## 2. WSL2 특별 설정

### WSL2에서 systemd 활성화 확인
```bash
# /etc/wsl.conf 파일 확인/생성
sudo tee /etc/wsl.conf <<EOF
[boot]
systemd=true
EOF

# WSL 재시작 (Windows PowerShell에서)
wsl --shutdown
wsl
```

### 대체 방법 (systemd 없이)
```bash
# 백그라운드로 Ollama 실행
nohup ollama serve > ~/ollama.log 2>&1 &

# 또는 screen/tmux 사용
screen -dmS ollama ollama serve
```

## 3. 모델 설치 및 테스트

```bash
# Ollama 상태 확인
ollama list

# 추천 모델 설치
ollama pull llama2:7b      # 일반 대화용
ollama pull codellama:7b   # 코드 생성용
ollama pull mistral:7b     # 빠른 응답용

# 테스트
ollama run llama2:7b "Hello, how are you?"
```

## 4. 메모리 및 성능 최적화

### WSL2 메모리 할당 (.wslconfig)
```powershell
# Windows에서 %USERPROFILE%\.wslconfig 생성
[wsl2]
memory=8GB
processors=4
swap=4GB
```

### Ollama 환경 변수
```bash
# ~/.bashrc에 추가
export OLLAMA_HOST="0.0.0.0:11434"
export OLLAMA_MODELS="/home/$USER/.ollama/models"
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=2
```

## 5. Windows에서 접근 설정

### 포트 포워딩
```bash
# WSL2 IP 확인
ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'

# Windows 방화벽 규칙 추가 (관리자 PowerShell)
New-NetFirewallRule -DisplayName "Ollama" -Direction Inbound -Protocol TCP -LocalPort 11434 -Action Allow
```

### Windows에서 테스트
```powershell
# PowerShell에서
curl http://localhost:11434/api/tags
```

## 6. 문제 해결

### "ollama: command not found"
```bash
# PATH 확인
echo $PATH
# 수동으로 PATH 추가
export PATH=$PATH:/usr/local/bin
```

### 서비스 시작 실패
```bash
# 직접 실행으로 에러 확인
/usr/local/bin/ollama serve

# 포트 충돌 확인
sudo lsof -i :11434
```

### WSL2 메모리 부족
```bash
# 현재 메모리 확인
free -h

# WSL 재시작
wsl --shutdown
wsl
```

## 7. VSCode 연동 확인

```bash
# API 엔드포인트 테스트
curl http://localhost:11434/api/generate -d '{
  "model": "llama2:7b",
  "prompt": "Test"
}'
```

## 다음 단계
- Continue 확장 프로그램 설정
- Claude + Ollama 워크플로우 구성
- 모델 성능 비교 및 선택
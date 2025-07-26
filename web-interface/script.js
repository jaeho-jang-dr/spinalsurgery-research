// AI Assistant 웹 인터페이스 스크립트

let currentModel = 'claude';
let isProcessing = false;

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 모델 선택 이벤트
    document.querySelectorAll('input[name="model"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentModel = e.target.value;
            addSystemMessage(`모델 변경: ${getModelName(currentModel)}`);
        });
    });

    // Enter 키 이벤트
    document.getElementById('user-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 초기 설정 확인
    checkSetup();
});

// 모델 이름 가져오기
function getModelName(model) {
    const names = {
        'claude': 'Claude (고품질)',
        'ollama-mistral': 'Mistral 7B (빠름)',
        'ollama-llama2': 'Llama 2 (일반)',
        'ollama-codellama': 'CodeLlama (코드)'
    };
    return names[model] || model;
}

// 메시지 전송
async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message || isProcessing) return;
    
    isProcessing = true;
    input.value = '';
    document.getElementById('send-btn').disabled = true;
    
    // 사용자 메시지 추가
    addMessage('user', message);
    
    // AI 응답 요청
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                model: currentModel
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        addMessage('assistant', data.response);
        
        // 토큰 사용량 업데이트
        if (data.tokens) {
            updateTokenUsage(data.tokens, data.cost);
        }
    } catch (error) {
        addMessage('assistant', `오류가 발생했습니다: ${error.message}`);
    }
    
    isProcessing = false;
    document.getElementById('send-btn').disabled = false;
}

// 메시지 추가
function addMessage(role, content) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'content';
    
    // 마크다운 간단 처리
    content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
    content = content.replace(/\n/g, '<br>');
    
    contentDiv.innerHTML = content;
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    
    // 스크롤을 최하단으로
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 시스템 메시지 추가
function addSystemMessage(message) {
    addMessage('assistant', `📢 ${message}`);
}

// 빠른 작업 함수들
function searchPapers() {
    const query = prompt('검색할 논문 주제를 입력하세요:');
    if (query) {
        document.getElementById('user-input').value = `최근 척추 수술 관련 논문 중 "${query}"에 대한 논문을 검색해주세요.`;
        sendMessage();
    }
}

function analyzeAbstract() {
    const abstract = prompt('분석할 초록을 입력하세요:');
    if (abstract) {
        document.getElementById('user-input').value = `다음 논문 초록을 분석해주세요:\n\n${abstract}`;
        sendMessage();
    }
}

function generateOutline() {
    const topic = prompt('논문 주제를 입력하세요:');
    if (topic) {
        document.getElementById('user-input').value = `"${topic}"에 대한 연구 논문 개요를 작성해주세요. Introduction, Methods, Results, Discussion 구조로 작성해주세요.`;
        sendMessage();
    }
}

function checkReferences() {
    const references = prompt('확인할 참고문헌을 입력하세요 (각 줄에 하나씩):');
    if (references) {
        document.getElementById('user-input').value = `다음 참고문헌의 형식을 확인하고 수정이 필요한 부분을 알려주세요:\n\n${references}`;
        sendMessage();
    }
}

// 토큰 사용량 업데이트
function updateTokenUsage(tokens, cost) {
    const currentTokens = parseInt(document.getElementById('today-tokens').textContent) || 0;
    const currentCost = parseFloat(document.getElementById('today-cost').textContent) || 0;
    
    document.getElementById('today-tokens').textContent = (currentTokens + tokens).toLocaleString();
    document.getElementById('today-cost').textContent = (currentCost + cost).toFixed(2);
}

// 설정 확인
async function checkSetup() {
    try {
        const response = await fetch('/api/check-setup');
        const data = await response.json();
        
        if (data.claude && data.ollama) {
            document.getElementById('setup-guide').classList.add('hidden');
            addSystemMessage('✅ 모든 AI 모델이 준비되었습니다!');
        } else {
            const missing = [];
            if (!data.claude) missing.push('Claude CLI');
            if (!data.ollama) missing.push('Ollama');
            addSystemMessage(`⚠️ 설정 필요: ${missing.join(', ')}`);
        }
    } catch (error) {
        console.error('Setup check failed:', error);
    }
}
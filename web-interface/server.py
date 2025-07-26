#!/usr/bin/env python3
"""
Spinal Surgery Research AI Assistant 웹 서버
"""

import os
import json
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='.')
CORS(app)

# Ollama API 엔드포인트
OLLAMA_API = "http://localhost:11434"

@app.route('/')
def index():
    """메인 페이지"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """정적 파일 서빙"""
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI 채팅 엔드포인트"""
    data = request.json
    message = data.get('message', '')
    model = data.get('model', 'claude')
    
    try:
        if model == 'claude':
            # Claude CLI 사용
            response = use_claude_cli(message)
        else:
            # Ollama 사용
            ollama_model = model.replace('ollama-', '')
            response = use_ollama(message, ollama_model)
        
        # 토큰 계산 (추정치)
        tokens = len(message.split()) + len(response.split())
        cost = calculate_cost(model, tokens)
        
        return jsonify({
            'response': response,
            'tokens': tokens,
            'cost': cost
        })
    
    except Exception as e:
        return jsonify({
            'response': f'오류 발생: {str(e)}',
            'error': True
        }), 500

@app.route('/api/check-setup', methods=['GET'])
def check_setup():
    """설정 상태 확인"""
    claude_ok = check_claude_cli()
    ollama_ok = check_ollama()
    
    return jsonify({
        'claude': claude_ok,
        'ollama': ollama_ok
    })

def use_claude_cli(message):
    """Claude CLI를 사용하여 응답 생성"""
    try:
        # Claude CLI 명령 실행
        result = subprocess.run(
            ['claude', 'chat', message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            # 로그인 필요 확인
            if "not authenticated" in result.stderr:
                return "Claude CLI 로그인이 필요합니다. 터미널에서 'claude login'을 실행하세요."
            return f"Claude 오류: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Claude 응답 시간 초과"
    except FileNotFoundError:
        return "Claude CLI가 설치되지 않았습니다. 설치 가이드를 확인하세요."
    except Exception as e:
        return f"Claude 오류: {str(e)}"

def use_ollama(message, model='mistral'):
    """Ollama API를 사용하여 응답 생성"""
    try:
        # Ollama generate API 호출
        response = requests.post(
            f"{OLLAMA_API}/api/generate",
            json={
                "model": model,
                "prompt": message,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '응답을 생성할 수 없습니다.')
        else:
            return f"Ollama 오류: HTTP {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return "Ollama 서버에 연결할 수 없습니다. 'ollama serve'를 실행하세요."
    except requests.exceptions.Timeout:
        return "Ollama 응답 시간 초과"
    except Exception as e:
        return f"Ollama 오류: {str(e)}"

def check_claude_cli():
    """Claude CLI 설치 및 로그인 상태 확인"""
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def check_ollama():
    """Ollama 서버 상태 확인"""
    try:
        response = requests.get(f"{OLLAMA_API}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def calculate_cost(model, tokens):
    """토큰 비용 계산 (추정치)"""
    # 실제 비용은 모델에 따라 다름
    costs = {
        'claude': 0.015,  # $15 per 1M tokens (추정)
        'ollama-mistral': 0,  # 로컬 실행
        'ollama-llama2': 0,
        'ollama-codellama': 0
    }
    
    rate = costs.get(model, 0)
    return (tokens / 1000000) * rate * 1000  # 달러로 변환

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5555
    
    print("🚀 Spinal Surgery Research AI Assistant")
    print(f"📍 URL: http://localhost:{port}")
    print("⚠️  Claude CLI 로그인: claude login")
    print("⚠️  Ollama 실행: ollama serve")
    print("-" * 40)
    
    app.run(host='0.0.0.0', port=port, debug=True)
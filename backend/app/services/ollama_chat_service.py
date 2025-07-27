import httpx
from typing import Dict, List, Optional, AsyncGenerator
import json
from datetime import datetime
import os
import asyncio

class OllamaChatService:
    def __init__(self):
        self.ollama_path = "/home/drjang00/ollama"
        self.base_url = "http://localhost:11434"
        self.model = "llama2"
        self.ollama_process = None
        self._ensure_ollama_running()
    
    def _ensure_ollama_running(self):
        """Ensure Ollama server is running"""
        # Skip Ollama server check for now - use mock service instead
        print("Ollama service disabled - using mock AI service")
        return
    
    async def chat(self, message: str, context: List[Dict] = None) -> str:
        """Send a chat message to Ollama"""
        # For now, return a mock response immediately
        if "안녕" in message or "hello" in message.lower() or "hi" in message.lower():
            return "안녕하세요! 척추외과 연구를 도와드리는 AI 어시스턴트입니다. 무엇을 도와드릴까요?"
        elif "연구" in message or "research" in message.lower():
            return "연구 관련 질문이시군요. 구체적으로 어떤 부분을 도와드릴까요? 논문 작성, 데이터 분석, 문헌 검색 등을 지원할 수 있습니다."
        elif "논문" in message or "paper" in message.lower():
            return "논문 작성을 도와드릴 수 있습니다. 초록 작성, 연구 방법론 설계, 통계 분석 계획 등 어떤 부분이 필요하신가요?"
        else:
            return f"'{message}'에 대한 답변을 준비하고 있습니다. 척추외과 연구와 관련된 구체적인 질문을 해주시면 더 정확한 답변을 드릴 수 있습니다."
        
        # Original Ollama code commented out for now
        # try:
        #     async with httpx.AsyncClient() as client:
        #         ...
        # except Exception as e:
        #     return f"Error communicating with Ollama: {str(e)}"
    
    async def chat_stream(self, message: str, context: List[Dict] = None) -> AsyncGenerator[str, None]:
        """Stream chat responses from Ollama"""
        try:
            async with httpx.AsyncClient() as client:
                # Prepare the prompt with context
                prompt = message
                if context:
                    conversation = "\n".join([
                        f"Human: {msg['content']}" if msg['role'] == 'user' else f"Assistant: {msg['content']}"
                        for msg in context[-5:]
                    ])
                    prompt = f"{conversation}\nHuman: {message}\nAssistant:"
                
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True
                    },
                    timeout=30.0
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        # Return mock models for now
        return ["llama2", "codellama", "mistral", "neural-chat"]
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a new model from Ollama"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                    timeout=600.0  # 10 minutes timeout for model download
                )
                return response.status_code == 200
        except:
            return False
    
    def set_model(self, model_name: str):
        """Set the active model"""
        self.model = model_name
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        if self.ollama_process:
            self.ollama_process.terminate()
            self.ollama_process.wait()

# Singleton instance
ollama_chat_service = OllamaChatService()
#!/usr/bin/env python3
"""
AI Integration Service
- Claude Code integration (via MCP)
- Ollama local LLM support
- NotebookLM-style document processing
"""

import os
import json
import asyncio
import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import aiohttp
import requests
from pathlib import Path
import subprocess
import sys

# Add MCP client support
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("MCP not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client


class AIService:
    def __init__(self, db_path='spinalsurgery_research.db'):
        self.db_path = db_path
        self.init_ai_tables()
        self.ollama_base_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        self.claude_api_key = os.getenv('CLAUDE_API_KEY', '')
        
    def init_ai_tables(self):
        """AI 관련 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # AI 세션 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS ai_sessions (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            session_type TEXT NOT NULL,  -- claude, ollama, notebook
            model_name TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ended_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )''')
        
        # AI 대화 기록
        c.execute('''CREATE TABLE IF NOT EXISTS ai_conversations (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,  -- user, assistant, system
            content TEXT NOT NULL,
            metadata TEXT,  -- JSON for additional data
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES ai_sessions (id)
        )''')
        
        # 문서 분석 결과
        c.execute('''CREATE TABLE IF NOT EXISTS document_analyses (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            document_path TEXT NOT NULL,
            analysis_type TEXT NOT NULL,  -- summary, qa, outline
            result TEXT NOT NULL,  -- JSON
            model_used TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )''')
        
        # MCP 서버 설정
        c.execute('''CREATE TABLE IF NOT EXISTS mcp_servers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            command TEXT NOT NULL,
            args TEXT,  -- JSON array
            env TEXT,  -- JSON object
            enabled INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # 기본 MCP 서버 추가
        self._insert_default_mcp_servers(c)
        
        conn.commit()
        conn.close()
    
    def _insert_default_mcp_servers(self, cursor):
        """기본 MCP 서버 설정 추가"""
        default_servers = [
            {
                'id': 'filesystem',
                'name': 'Filesystem MCP',
                'command': 'npx',
                'args': json.dumps(['@modelcontextprotocol/server-filesystem', '/home/drjang00/DevEnvironments/spinalsurgery-research']),
                'env': json.dumps({})
            },
            {
                'id': 'github',
                'name': 'GitHub MCP',
                'command': 'npx',
                'args': json.dumps(['@modelcontextprotocol/server-github']),
                'env': json.dumps({'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN', '')})
            }
        ]
        
        for server in default_servers:
            cursor.execute('''INSERT OR IGNORE INTO mcp_servers 
                            (id, name, command, args, env)
                            VALUES (?, ?, ?, ?, ?)''',
                         (server['id'], server['name'], server['command'],
                          server['args'], server['env']))
    
    async def create_mcp_session(self, server_id: str) -> Optional[ClientSession]:
        """MCP 서버와 연결"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM mcp_servers WHERE id = ? AND enabled = 1', (server_id,))
        server = c.fetchone()
        conn.close()
        
        if not server:
            return None
        
        command = server[2]
        args = json.loads(server[3])
        env = json.loads(server[4])
        
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return session
    
    async def query_filesystem_mcp(self, operation: str, params: Dict[str, Any]) -> Dict:
        """파일시스템 MCP를 통한 파일 작업"""
        try:
            session = await self.create_mcp_session('filesystem')
            if not session:
                return {'error': 'Failed to connect to filesystem MCP'}
            
            # MCP 도구 호출
            if operation == 'read_file':
                result = await session.call_tool('read_file', params)
            elif operation == 'write_file':
                result = await session.call_tool('write_file', params)
            elif operation == 'list_directory':
                result = await session.call_tool('list_directory', params)
            elif operation == 'search_files':
                result = await session.call_tool('search_files', params)
            else:
                return {'error': f'Unknown operation: {operation}'}
            
            return {'success': True, 'result': result}
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_ollama_status(self) -> bool:
        """Ollama 서버 상태 확인"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def list_ollama_models(self) -> List[str]:
        """사용 가능한 Ollama 모델 목록"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []
    
    async def query_ollama(self, prompt: str, model: str = 'llama2', 
                          system_prompt: str = None, stream: bool = False) -> Dict:
        """Ollama 모델에 쿼리"""
        url = f"{self.ollama_base_url}/api/generate"
        
        payload = {
            'model': model,
            'prompt': prompt,
            'stream': stream
        }
        
        if system_prompt:
            payload['system'] = system_prompt
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if stream:
                        # 스트리밍 응답 처리
                        full_response = ""
                        async for line in response.content:
                            if line:
                                data = json.loads(line)
                                if 'response' in data:
                                    full_response += data['response']
                                if data.get('done', False):
                                    break
                        return {'response': full_response, 'model': model}
                    else:
                        # 일반 응답
                        result = await response.json()
                        return result
        except Exception as e:
            return {'error': str(e)}
    
    def create_ai_session(self, project_id: str, session_type: str, 
                         model_name: str = None) -> str:
        """새 AI 세션 생성"""
        session_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO ai_sessions 
                    (id, project_id, session_type, model_name)
                    VALUES (?, ?, ?, ?)''',
                 (session_id, project_id, session_type, model_name))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def save_conversation(self, session_id: str, role: str, content: str, 
                         metadata: Dict = None):
        """대화 기록 저장"""
        conv_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO ai_conversations 
                    (id, session_id, role, content, metadata)
                    VALUES (?, ?, ?, ?, ?)''',
                 (conv_id, session_id, role, content, 
                  json.dumps(metadata) if metadata else None))
        
        conn.commit()
        conn.close()
    
    async def analyze_documents(self, project_id: str, document_paths: List[str],
                               analysis_type: str = 'summary', 
                               model: str = 'llama2') -> Dict:
        """문서 분석 (NotebookLM 스타일)"""
        all_content = []
        
        # 문서 읽기 (MCP 사용)
        for path in document_paths:
            result = await self.query_filesystem_mcp('read_file', {'path': path})
            if result.get('success'):
                all_content.append(result['result'])
        
        if not all_content:
            return {'error': 'No documents could be read'}
        
        # 전체 컨텐츠 결합
        combined_content = "\n\n---\n\n".join(all_content)
        
        # 분석 타입에 따른 프롬프트 생성
        if analysis_type == 'summary':
            prompt = f"""Please provide a comprehensive summary of the following documents:

{combined_content}

Generate:
1. Executive summary (2-3 paragraphs)
2. Key findings and insights
3. Main topics covered
4. Recommendations or conclusions"""
        
        elif analysis_type == 'qa':
            prompt = f"""Based on the following documents, generate 10 important questions and their answers:

{combined_content}

Format each Q&A as:
Q: [Question]
A: [Detailed answer based on the documents]"""
        
        elif analysis_type == 'outline':
            prompt = f"""Create a detailed outline of the following documents:

{combined_content}

Generate a hierarchical outline with:
- Main sections
- Subsections
- Key points under each section
- Important details or data"""
        
        else:
            prompt = combined_content
        
        # Ollama로 분석
        result = await self.query_ollama(
            prompt=prompt,
            model=model,
            system_prompt="You are an expert research assistant analyzing medical documents."
        )
        
        if 'error' not in result:
            # 결과 저장
            analysis_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO document_analyses 
                        (id, project_id, document_path, analysis_type, result, model_used)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (analysis_id, project_id, json.dumps(document_paths),
                      analysis_type, json.dumps(result), model))
            
            conn.commit()
            conn.close()
            
            result['analysis_id'] = analysis_id
        
        return result
    
    async def generate_paper_draft(self, project_id: str, title: str, 
                                  keywords: List[str], outline: Dict,
                                  references: List[Dict], model: str = 'llama2') -> Dict:
        """논문 초안 생성"""
        # 참고문헌 포맷팅
        refs_text = "\n".join([
            f"{i+1}. {ref.get('title', 'Unknown')} - {ref.get('authors', 'Unknown')} ({ref.get('year', 'Unknown')})"
            for i, ref in enumerate(references)
        ])
        
        prompt = f"""Generate a research paper draft with the following specifications:

Title: {title}
Keywords: {', '.join(keywords)}

Outline:
{json.dumps(outline, indent=2)}

References to incorporate:
{refs_text}

Please generate:
1. Abstract (150-250 words)
2. Introduction with background and objectives
3. Methods section
4. Expected results/discussion
5. Conclusion
6. Properly formatted references

Follow standard medical research paper format."""
        
        result = await self.query_ollama(
            prompt=prompt,
            model=model,
            system_prompt="You are an expert medical researcher and paper writer."
        )
        
        return result
    
    def get_ai_sessions(self, project_id: str) -> List[Dict]:
        """프로젝트의 AI 세션 목록"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''SELECT * FROM ai_sessions 
                    WHERE project_id = ? 
                    ORDER BY created_at DESC''', (project_id,))
        
        sessions = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return sessions
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """세션의 대화 기록"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''SELECT * FROM ai_conversations 
                    WHERE session_id = ? 
                    ORDER BY created_at''', (session_id,))
        
        conversations = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return conversations


# Claude Code Extension 설정
class ClaudeCodeExtension:
    """VS Code Extension API 연동"""
    
    def __init__(self):
        self.extension_id = "anthropic.claude-code"
        self.config_path = Path.home() / ".vscode" / "extensions" / "claude-code" / "config.json"
    
    def install_extension(self) -> bool:
        """VS Code에 Claude Code Extension 설치"""
        try:
            # VS Code CLI를 통한 설치
            result = subprocess.run(
                ["code", "--install-extension", self.extension_id],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Extension installation failed: {e}")
            return False
    
    def configure_auth(self, api_key: str) -> bool:
        """Extension 인증 설정"""
        config = {
            "claude.apiKey": api_key,
            "claude.apiEndpoint": "https://api.anthropic.com/v1",
            "claude.model": "claude-3-opus-20240229",
            "claude.maxTokens": 4096
        }
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Configuration failed: {e}")
            return False
    
    def create_vscode_task(self, task_name: str, command: str) -> Dict:
        """VS Code 태스크 생성"""
        task = {
            "label": task_name,
            "type": "shell",
            "command": command,
            "group": {
                "kind": "build",
                "isDefault": True
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        }
        return task


# NotebookLM 스타일 API
class NotebookLMService:
    """NotebookLM 스타일 문서 처리"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def create_notebook(self, project_id: str, source_documents: List[str]) -> Dict:
        """노트북 생성 및 문서 분석"""
        # 요약 생성
        summary = await self.ai_service.analyze_documents(
            project_id, source_documents, 'summary'
        )
        
        # Q&A 생성
        qa = await self.ai_service.analyze_documents(
            project_id, source_documents, 'qa'
        )
        
        # 개요 생성
        outline = await self.ai_service.analyze_documents(
            project_id, source_documents, 'outline'
        )
        
        return {
            'summary': summary,
            'qa': qa,
            'outline': outline,
            'source_documents': source_documents
        }
    
    async def ask_question(self, project_id: str, question: str, 
                          context_documents: List[str]) -> Dict:
        """문서 기반 질문 응답"""
        # 문서 내용 읽기
        context = []
        for doc in context_documents:
            result = await self.ai_service.query_filesystem_mcp(
                'read_file', {'path': doc}
            )
            if result.get('success'):
                context.append(result['result'])
        
        prompt = f"""Based on the following documents, please answer this question:

Question: {question}

Documents:
{chr(10).join(context)}

Provide a detailed answer based only on the information in the documents."""
        
        return await self.ai_service.query_ollama(prompt)


if __name__ == '__main__':
    # 테스트
    import asyncio
    
    async def test():
        service = AIService()
        
        # Ollama 상태 확인
        print("Ollama status:", service.check_ollama_status())
        print("Available models:", service.list_ollama_models())
        
        # 파일시스템 테스트
        result = await service.query_filesystem_mcp(
            'list_directory', 
            {'path': '/home/drjang00/DevEnvironments/spinalsurgery-research'}
        )
        print("Directory listing:", result)
    
    asyncio.run(test())
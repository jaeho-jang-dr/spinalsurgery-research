#!/usr/bin/env python3
"""
향상된 SQLite 기반 백엔드 서버
논문 검색 기능 추가
"""

import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import hashlib
import uuid
from datetime import datetime
import sys
import os

# paper_search_service 임포트
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from paper_search_service import PaperSearchService
from search_engine import SearchEngine
from ai_service import AIService
import asyncio

# SQLite 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('spinalsurgery_research.db')
    c = conn.cursor()
    
    # Users 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        institution TEXT,
        department TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Projects 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        field TEXT NOT NULL,
        keywords TEXT,
        description TEXT,
        status TEXT DEFAULT 'draft',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Papers 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        project_id TEXT,
        title TEXT NOT NULL,
        authors TEXT,
        abstract TEXT,
        journal_name TEXT,
        publication_year INTEGER,
        is_own_paper INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )''')
    
    # Paper Sources 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS paper_sources (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        priority INTEGER DEFAULT 5,
        url TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        address TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 테스트 데이터 삽입
    # 테스트 사용자
    test_user_id = str(uuid.uuid4())
    c.execute('''INSERT OR IGNORE INTO users (id, email, password_hash, name, role, institution, department)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (test_user_id, 'test@example.com', hashlib.sha256('test1234'.encode()).hexdigest(),
               '테스트 사용자', 'researcher', '서울대학교병원', '척추외과'))
    
    # 테스트 프로젝트
    c.execute('''INSERT OR IGNORE INTO projects (id, user_id, title, field, keywords, status)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              ('1', test_user_id, '척추 후외방 고정술의 2년 후 결과', '척추외과', 
               '["척추", "고정술", "CD instrument"]', 'in_progress'))
    
    c.execute('''INSERT OR IGNORE INTO projects (id, user_id, title, field, keywords, status)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              ('2', test_user_id, '최소 침습 척추 수술의 효과 분석', '척추외과',
               '["최소침습", "척추수술", "VAS score"]', 'draft'))
    
    # 논문 소스
    c.execute('''INSERT OR IGNORE INTO paper_sources (id, name, type, priority, url, contact_email, contact_phone, address)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              ('1', 'PubMed Central', 'database', 1, 'https://www.ncbi.nlm.nih.gov/pmc/',
               'info@ncbi.nlm.nih.gov', None, None))
    
    c.execute('''INSERT OR IGNORE INTO paper_sources (id, name, type, priority, url, contact_email, contact_phone, address)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              ('2', '서울대학교 의학도서관', 'institution', 1, 'http://medlib.snu.ac.kr',
               'medlib@snu.ac.kr', '02-740-8045', '서울특별시 종로구 대학로 103'))
    
    conn.commit()
    conn.close()

class APIHandler(BaseHTTPRequestHandler):
    search_engine = None  # 클래스 변수로 검색 엔진 공유
    ai_service = None  # AI 서비스 공유
    
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        conn = sqlite3.connect('spinalsurgery_research.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            if path == '/api/v1/users/me':
                self._set_headers()
                response = {
                    "id": "test-user-id",
                    "email": "test@example.com",
                    "name": "테스트 사용자",
                    "role": "researcher",
                    "institution": "서울대학교병원",
                    "department": "척추외과"
                }
                self.wfile.write(json.dumps(response).encode())
            
            elif path == '/api/v1/projects':
                c.execute('''SELECT p.*, 
                            (SELECT COUNT(*) FROM papers WHERE project_id = p.id) as papers_count
                            FROM projects p''')
                projects = []
                for row in c.fetchall():
                    project = dict(row)
                    project['keywords'] = json.loads(project.get('keywords', '[]'))
                    project['patients_count'] = 34 if project['id'] == '1' else 0
                    project['collaborators_count'] = 3 if project['id'] == '1' else 1
                    project['created_at'] = project.get('created_at', '2025-01-15T10:00:00')
                    project['updated_at'] = project.get('created_at', '2025-01-20T15:30:00')
                    projects.append(project)
                
                self._set_headers()
                self.wfile.write(json.dumps(projects).encode())
            
            elif path == '/api/v1/papers/sources':
                c.execute('SELECT * FROM paper_sources ORDER BY priority, name')
                sources = [dict(row) for row in c.fetchall()]
                self._set_headers()
                self.wfile.write(json.dumps(sources).encode())
            
            elif path == '/api/v1/papers/search-sites':
                # 논문 검색 사이트 목록
                search_service = PaperSearchService()
                sites = search_service.get_search_sites()
                self._set_headers()
                self.wfile.write(json.dumps(sites).encode())
            
            elif path.startswith('/api/v1/projects/') and path.endswith('/search-sessions'):
                # 프로젝트의 검색 세션 목록
                project_id = path.split('/')[-2]
                c.execute('''SELECT s.*, j.status as job_status, j.progress, j.total_expected
                            FROM search_sessions s
                            LEFT JOIN search_jobs j ON s.id = j.session_id
                            WHERE s.project_id = ? 
                            ORDER BY s.started_at DESC''', (project_id,))
                sessions = []
                for row in c.fetchall():
                    session = dict(row)
                    session['search_sites'] = json.loads(session.get('search_sites', '[]'))
                    sessions.append(session)
                
                self._set_headers()
                self.wfile.write(json.dumps(sessions).encode())
            
            elif path.startswith('/api/v1/search/jobs/'):
                # 검색 작업 상태 조회
                job_id = path.split('/')[-1]
                job_info = self.search_engine.get_job_info(job_id)
                
                if job_info:
                    self._set_headers()
                    self.wfile.write(json.dumps(job_info).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Job not found"}).encode())
            
            elif path == '/api/v1/search/papers':
                # 저장된 논문에서 검색
                query_params = parse_qs(parsed_path.query)
                query = query_params.get('q', [''])[0]
                project_id = query_params.get('project_id', [None])[0]
                
                if query:
                    results = self.search_engine.search_in_papers(query, project_id)
                    self._set_headers()
                    self.wfile.write(json.dumps(results).encode())
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Query parameter required"}).encode())
            
            elif path == '/':
                self._set_headers()
                response = {"message": "SpinalSurgery Research Platform API - SQLite Backend v2"}
                self.wfile.write(json.dumps(response).encode())
            
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
                
        finally:
            conn.close()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/v1/auth/login':
            self._set_headers()
            response = {
                "access_token": "test-access-token-" + str(uuid.uuid4()),
                "refresh_token": "test-refresh-token-" + str(uuid.uuid4()),
                "token_type": "bearer"
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif path == '/api/v1/projects':
            try:
                data = json.loads(post_data)
                conn = sqlite3.connect('spinalsurgery_research.db')
                c = conn.cursor()
                
                project_id = str(uuid.uuid4())
                c.execute('''INSERT INTO projects (id, user_id, title, field, keywords, description, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (project_id, 'test-user-id', data.get('title'), data.get('field'),
                          json.dumps(data.get('keywords', [])), data.get('description'), 'draft'))
                conn.commit()
                conn.close()
                
                self._set_headers(201)
                response = {
                    "id": project_id,
                    "title": data.get('title'),
                    "field": data.get('field'),
                    "keywords": data.get('keywords', []),
                    "description": data.get('description'),
                    "status": "draft",
                    "papers_count": 0,
                    "patients_count": 0,
                    "collaborators_count": 0,
                    "created_at": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif path == '/api/v1/papers/search':
            try:
                data = json.loads(post_data)
                project_id = data.get('project_id')
                query = data.get('query')
                site_ids = data.get('site_ids', ['pubmed'])
                target_count = data.get('target_count', 100)
                
                # 대량 논문 검색 시작
                job_id = self.search_engine.start_search(project_id, query, site_ids, target_count)
                
                self._set_headers()
                response = {
                    "job_id": job_id,
                    "message": f"검색 작업이 시작되었습니다. 목표: {target_count}개 논문"
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif path.startswith('/api/v1/search/jobs/') and path.endswith('/pause'):
            # 검색 일시정지
            job_id = path.split('/')[-2]
            self.search_engine.pause_search(job_id)
            self._set_headers()
            self.wfile.write(json.dumps({"status": "paused"}).encode())
        
        elif path.startswith('/api/v1/search/jobs/') and path.endswith('/resume'):
            # 검색 재개
            job_id = path.split('/')[-2]
            self.search_engine.resume_search(job_id)
            self._set_headers()
            self.wfile.write(json.dumps({"status": "resumed"}).encode())
        
        elif path.startswith('/api/v1/search/jobs/') and path.endswith('/cancel'):
            # 검색 취소
            job_id = path.split('/')[-2]
            self.search_engine.cancel_search(job_id)
            self._set_headers()
            self.wfile.write(json.dumps({"status": "cancelled"}).encode())
        
        elif path.startswith('/api/v1/projects/') and path.endswith('/start-research'):
            try:
                project_id = path.split('/')[-2]
                data = json.loads(post_data)
                
                # 프로젝트 정보 조회
                conn = sqlite3.connect('spinalsurgery_research.db')
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                
                c.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
                project = dict(c.fetchone())
                conn.close()
                
                # 검색어 생성 (영어로 변환)
                keywords = json.loads(project['keywords'])
                # 한글 키워드를 영어로 매핑 (간단한 예시)
                keyword_map = {
                    '척추': 'spine',
                    '척추외과': 'spine surgery',
                    '고정술': 'fusion',
                    '최소침습': 'minimally invasive',
                    '척추수술': 'spine surgery',
                    'VAS score': 'VAS score',
                    'CD instrument': 'CD instrument'
                }
                
                # 영어 키워드로 변환
                english_keywords = []
                for keyword in keywords:
                    english_keywords.append(keyword_map.get(keyword, keyword))
                
                field_english = keyword_map.get(project['field'], project['field'])
                query = f"{field_english} {' '.join(english_keywords)}"
                
                # AI 옵션에 따른 처리
                ai_option = data.get('ai_option', 'search')
                
                if ai_option == 'search':
                    # 대량 논문 검색 시작 (백그라운드)
                    job_id = self.search_engine.start_search(
                        project_id, 
                        query, 
                        data.get('site_ids', ['pubmed', 'pmc']),
                        target_count=data.get('target_count', 100)
                    )
                    
                    self._set_headers()
                    response = {
                        "status": "success",
                        "action": "search_started",
                        "job_id": job_id,
                        "message": "논문 검색이 시작되었습니다. 백그라운드에서 진행됩니다."
                    }
                    self.wfile.write(json.dumps(response).encode())
                
                else:
                    # TODO: 다른 AI 옵션 구현
                    self._set_headers()
                    response = {
                        "status": "pending",
                        "action": ai_option,
                        "message": f"{ai_option} 기능은 준비 중입니다"
                    }
                    self.wfile.write(json.dumps(response).encode())
                    
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif path == '/api/v1/ai/models':
            # 사용 가능한 AI 모델 목록
            try:
                ollama_models = self.ai_service.list_ollama_models()
                models = [
                    {'id': 'claude-3-opus', 'name': 'Claude 3 Opus', 'type': 'claude', 'available': bool(self.ai_service.claude_api_key)},
                    {'id': 'claude-3-sonnet', 'name': 'Claude 3 Sonnet', 'type': 'claude', 'available': bool(self.ai_service.claude_api_key)},
                ]
                for model in ollama_models:
                    models.append({'id': model, 'name': model, 'type': 'ollama', 'available': True})
                
                self._set_headers()
                self.wfile.write(json.dumps(models).encode())
                
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif path == '/api/v1/ai/chat':
            # AI 채팅
            try:
                data = json.loads(post_data)
                project_id = data.get('project_id')
                message = data.get('message')
                model = data.get('model', 'llama2')
                session_id = data.get('session_id')
                
                if not session_id:
                    session_id = self.ai_service.create_ai_session(project_id, 'chat', model)
                
                # 메시지 저장
                self.ai_service.save_conversation(session_id, 'user', message)
                
                # AI 응답 생성
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.ai_service.query_ollama(message, model)
                )
                
                if 'response' in result:
                    response_text = result['response']
                    self.ai_service.save_conversation(session_id, 'assistant', response_text)
                    
                    self._set_headers()
                    self.wfile.write(json.dumps({
                        'session_id': session_id,
                        'response': response_text,
                        'model': model
                    }).encode())
                else:
                    self._set_headers(500)
                    self.wfile.write(json.dumps(result).encode())
                    
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif path == '/api/v1/ai/analyze-documents':
            # 문서 분석
            try:
                data = json.loads(post_data)
                project_id = data.get('project_id')
                document_paths = data.get('document_paths', [])
                analysis_type = data.get('analysis_type', 'summary')
                model = data.get('model', 'llama2')
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.ai_service.analyze_documents(project_id, document_paths, analysis_type, model)
                )
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif path == '/api/v1/ai/generate-draft':
            # 논문 초안 생성
            try:
                data = json.loads(post_data)
                project_id = data.get('project_id')
                title = data.get('title')
                keywords = data.get('keywords', [])
                outline = data.get('outline', {})
                references = data.get('references', [])
                model = data.get('model', 'llama2')
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.ai_service.generate_paper_draft(
                        project_id, title, keywords, outline, references, model
                    )
                )
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run(port=8000):
    # 데이터베이스 초기화
    init_db()
    
    # 논문 검색 서비스 초기화
    search_service = PaperSearchService()
    search_engine = SearchEngine()
    
    # AI 서비스 초기화
    ai_service = AIService()
    
    # APIHandler에 서비스 주입
    APIHandler.search_engine = search_engine
    APIHandler.ai_service = ai_service
    
    # 서버 시작
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    print(f'🚀 SpinalSurgery Research Backend v2 (SQLite + Paper Search)')
    print(f'📦 Database: spinalsurgery_research.db')
    print(f'🌐 Server running on http://localhost:{port}')
    print(f'📋 API endpoints:')
    print(f'   GET  /api/v1/users/me')
    print(f'   GET  /api/v1/projects')
    print(f'   POST /api/v1/projects')
    print(f'   GET  /api/v1/papers/sources')
    print(f'   GET  /api/v1/papers/search-sites')
    print(f'   POST /api/v1/papers/search - 대량 검색 시작')
    print(f'   GET  /api/v1/search/papers?q=query - 저장된 논문 검색')
    print(f'   GET  /api/v1/search/jobs/:id - 검색 작업 상태')
    print(f'   POST /api/v1/search/jobs/:id/pause - 검색 일시정지')
    print(f'   POST /api/v1/search/jobs/:id/resume - 검색 재개')
    print(f'   POST /api/v1/search/jobs/:id/cancel - 검색 취소')
    print(f'   GET  /api/v1/projects/:id/search-sessions - 검색 세션 목록')
    print(f'   POST /api/v1/projects/:id/start-research')
    print(f'   POST /api/v1/auth/login')
    print(f'   POST /api/v1/ai/models - AI 모델 목록')
    print(f'   POST /api/v1/ai/chat - AI 채팅')
    print(f'   POST /api/v1/ai/analyze-documents - 문서 분석')
    print(f'   POST /api/v1/ai/generate-draft - 논문 초안 생성')
    print(f'\n Press Ctrl+C to stop')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Server stopped')

if __name__ == '__main__':
    run()
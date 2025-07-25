#!/usr/bin/env python3
"""
간단한 SQLite 기반 백엔드 서버
PostgreSQL 없이 로컬에서 실행 가능
"""

import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import hashlib
import uuid
from datetime import datetime

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
            
            elif path == '/':
                self._set_headers()
                response = {"message": "SpinalSurgery Research Platform API - SQLite Backend"}
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
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run(port=8000):
    # 데이터베이스 초기화
    init_db()
    
    # 서버 시작
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    print(f'🚀 SpinalSurgery Research Backend (SQLite)')
    print(f'📦 Database: spinalsurgery_research.db')
    print(f'🌐 Server running on http://localhost:{port}')
    print(f'📋 API endpoints:')
    print(f'   GET  /api/v1/users/me')
    print(f'   GET  /api/v1/projects')
    print(f'   POST /api/v1/projects')
    print(f'   GET  /api/v1/papers/sources')
    print(f'   POST /api/v1/auth/login')
    print(f'\n Press Ctrl+C to stop')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Server stopped')

if __name__ == '__main__':
    run()
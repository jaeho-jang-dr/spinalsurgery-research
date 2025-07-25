#!/usr/bin/env python3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class CORSRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/v1/users/me':
            self._set_headers()
            response = {
                "id": "test-user-id",
                "email": "test@example.com",
                "name": "테스트 사용자",
                "role": "researcher"
            }
            self.wfile.write(json.dumps(response).encode())

        elif path == '/api/v1/projects':
            self._set_headers()
            response = [
                {
                    "id": "1",
                    "title": "척추 후외방 고정술의 2년 후 결과",
                    "field": "척추외과",
                    "keywords": ["척추", "고정술", "CD instrument"],
                    "status": "in_progress",
                    "papers_count": 5,
                    "patients_count": 34,
                    "collaborators_count": 3,
                    "created_at": "2025-01-15T10:00:00",
                    "updated_at": "2025-01-20T15:30:00"
                },
                {
                    "id": "2",
                    "title": "최소 침습 척추 수술의 효과 분석",
                    "field": "척추외과",
                    "keywords": ["최소침습", "척추수술", "VAS score"],
                    "status": "draft",
                    "papers_count": 2,
                    "patients_count": 0,
                    "collaborators_count": 1,
                    "created_at": "2025-01-10T09:00:00",
                    "updated_at": "2025-01-18T14:20:00"
                }
            ]
            self.wfile.write(json.dumps(response).encode())

        elif path == '/api/v1/papers/sources':
            self._set_headers()
            response = [
                {
                    "id": "1",
                    "name": "PubMed Central",
                    "type": "database",
                    "priority": 1,
                    "url": "https://www.ncbi.nlm.nih.gov/pmc/",
                    "contact_email": "info@ncbi.nlm.nih.gov"
                },
                {
                    "id": "2",
                    "name": "서울대학교 의학도서관",
                    "type": "institution",
                    "priority": 1,
                    "url": "http://medlib.snu.ac.kr",
                    "contact_email": "medlib@snu.ac.kr",
                    "contact_phone": "02-740-8045",
                    "address": "서울특별시 종로구 대학로 103"
                }
            ]
            self.wfile.write(json.dumps(response).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/v1/auth/login':
            self._set_headers()
            response = {
                "access_token": "test-access-token",
                "refresh_token": "test-refresh-token",
                "token_type": "bearer"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run(server_class=HTTPServer, handler_class=CORSRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'🚀 Test server running on http://localhost:{port}')
    print(f'📋 Available endpoints:')
    print(f'   GET  /api/v1/users/me')
    print(f'   GET  /api/v1/projects')
    print(f'   GET  /api/v1/papers/sources')
    print(f'   POST /api/v1/auth/login')
    print(f'\n Press Ctrl+C to stop')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
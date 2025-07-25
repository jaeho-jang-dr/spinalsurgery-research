#!/usr/bin/env python3
"""
향상된 논문 검색 엔진
- 대량 검색 (100+ 논문)
- 백그라운드 작업
- 검색 상태 관리
- 논문 색인
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime
import threading
import queue
import time
from typing import List, Dict, Optional
from paper_search_service import PaperSearchService
import hashlib

class SearchEngine:
    def __init__(self, db_path='spinalsurgery_research.db'):
        self.db_path = db_path
        self.search_service = PaperSearchService(db_path)
        self.search_queue = queue.Queue()
        self.active_searches = {}
        self._init_search_tables()
        
        # 백그라운드 워커 시작
        self.worker_thread = threading.Thread(target=self._search_worker, daemon=True)
        self.worker_thread.start()
    
    def _init_search_tables(self):
        """검색 엔진 관련 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 검색 작업 상태 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS search_jobs (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',  -- pending, running, paused, completed, failed
            progress INTEGER DEFAULT 0,
            total_expected INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES search_sessions (id)
        )''')
        
        # 논문 색인 테이블 (전문 검색용)
        c.execute('''CREATE TABLE IF NOT EXISTS paper_index (
            paper_id TEXT PRIMARY KEY,
            title_tokens TEXT,
            abstract_tokens TEXT,
            author_tokens TEXT,
            keyword_tokens TEXT,
            year INTEGER,
            citation_count INTEGER DEFAULT 0,
            relevance_score REAL DEFAULT 0.0,
            indexed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES searched_papers (id)
        )''')
        
        # 검색 통계 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS search_stats (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            search_site TEXT,
            papers_found INTEGER DEFAULT 0,
            fulltext_found INTEGER DEFAULT 0,
            search_time_seconds REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES search_sessions (id)
        )''')
        
        conn.commit()
        conn.close()
    
    def start_search(self, project_id: str, query: str, site_ids: List[str], 
                    target_count: int = 100) -> str:
        """새로운 검색 작업 시작"""
        # 검색 세션 생성
        session_id = self.search_service.create_search_session(project_id, query, site_ids)
        
        # 검색 작업 생성
        job_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO search_jobs (id, session_id, status, total_expected)
                    VALUES (?, ?, ?, ?)''',
                 (job_id, session_id, 'pending', target_count))
        conn.commit()
        conn.close()
        
        # 검색 작업을 큐에 추가
        search_task = {
            'job_id': job_id,
            'session_id': session_id,
            'project_id': project_id,
            'query': query,
            'site_ids': site_ids,
            'target_count': target_count
        }
        
        self.active_searches[job_id] = search_task
        self.search_queue.put(search_task)
        
        return job_id
    
    def _search_worker(self):
        """백그라운드 검색 워커"""
        while True:
            try:
                task = self.search_queue.get(timeout=1)
                self._execute_search(task)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Search worker error: {e}")
    
    def _execute_search(self, task: Dict):
        """실제 검색 실행"""
        job_id = task['job_id']
        session_id = task['session_id']
        query = task['query']
        site_ids = task['site_ids']
        target_count = task['target_count']
        
        # 상태 업데이트: running
        self._update_job_status(job_id, 'running')
        
        all_papers = []
        total_fetched = 0
        
        try:
            for site_id in site_ids:
                if site_id == 'pubmed':
                    # PubMed에서 대량 검색
                    start = 0
                    while total_fetched < target_count:
                        # 작업 상태 확인
                        status = self._get_job_status(job_id)
                        if status == 'paused':
                            time.sleep(1)
                            continue
                        elif status == 'cancelled':
                            break
                        
                        # 검색 실행
                        result = self.search_service.search_pubmed(
                            query, session_id, 
                            max_results=min(100, target_count - total_fetched),
                            start=start
                        )
                        
                        papers = result['papers']
                        if not papers:
                            break
                        
                        all_papers.extend(papers)
                        total_fetched += len(papers)
                        
                        # 진행 상황 업데이트
                        self._update_job_progress(job_id, total_fetched)
                        
                        # 배치 저장
                        if len(all_papers) >= 20:
                            self._save_papers_batch(session_id, all_papers)
                            all_papers = []
                        
                        # 더 이상 결과가 없으면 중단
                        if not result['has_more']:
                            break
                        
                        start += len(papers)
                        time.sleep(1)  # API 제한 회피
                
                # TODO: 다른 검색 사이트 구현
            
            # 남은 논문 저장
            if all_papers:
                self._save_papers_batch(session_id, all_papers)
            
            # 논문 색인화
            self._index_session_papers(session_id)
            
            # 보고서 생성
            report_path = self.search_service.generate_result_report(session_id, task['project_id'])
            
            # 완료 상태 업데이트
            self._update_job_status(job_id, 'completed')
            
        except Exception as e:
            print(f"Search execution error: {e}")
            self._update_job_status(job_id, 'failed', str(e))
        
        finally:
            # 활성 검색에서 제거
            if job_id in self.active_searches:
                del self.active_searches[job_id]
    
    def _save_papers_batch(self, session_id: str, papers: List[Dict]):
        """논문 배치 저장"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for paper in papers:
            # 중복 체크 (DOI 또는 PMID 기준)
            if paper.get('doi'):
                c.execute('SELECT id FROM searched_papers WHERE doi = ?', (paper['doi'],))
                if c.fetchone():
                    continue
            elif paper.get('pmid'):
                c.execute('SELECT id FROM searched_papers WHERE pmid = ?', (paper['pmid'],))
                if c.fetchone():
                    continue
            
            # 논문 저장
            c.execute('''INSERT INTO searched_papers 
                        (id, session_id, source_site_id, title, authors, abstract, 
                         journal_name, publication_year, doi, pmid, url, access_type, 
                         fulltext_url, keywords, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (paper['id'], session_id, paper['source_site_id'],
                      paper['title'], paper['authors'], paper['abstract'],
                      paper['journal_name'], paper['publication_year'], paper['doi'],
                      paper['pmid'], paper['url'], paper['access_type'],
                      paper.get('fulltext_url', ''), paper['keywords'],
                      datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _index_session_papers(self, session_id: str):
        """세션의 논문들을 색인화"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM searched_papers WHERE session_id = ?', (session_id,))
        papers = c.fetchall()
        
        for paper in papers:
            # 토큰화 (간단한 구현)
            title_tokens = self._tokenize(paper['title'])
            abstract_tokens = self._tokenize(paper['abstract'] or '')
            author_tokens = self._tokenize(paper['authors'] or '')
            keyword_tokens = paper['keywords'] or '[]'
            
            # 색인 저장
            c.execute('''INSERT OR REPLACE INTO paper_index 
                        (paper_id, title_tokens, abstract_tokens, author_tokens, 
                         keyword_tokens, year, indexed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (paper['id'], title_tokens, abstract_tokens, author_tokens,
                      keyword_tokens, paper['publication_year'],
                      datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _tokenize(self, text: str) -> str:
        """텍스트 토큰화 (검색용)"""
        if not text:
            return ''
        # 소문자 변환, 특수문자 제거, 공백으로 분리
        tokens = text.lower().replace(',', ' ').replace('.', ' ').replace('-', ' ').split()
        return ' '.join(tokens)
    
    def _update_job_status(self, job_id: str, status: str, error_message: str = None):
        """작업 상태 업데이트"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if error_message:
            c.execute('''UPDATE search_jobs 
                        SET status = ?, error_message = ?, updated_at = ?
                        WHERE id = ?''',
                     (status, error_message, datetime.now().isoformat(), job_id))
        else:
            c.execute('''UPDATE search_jobs 
                        SET status = ?, updated_at = ?
                        WHERE id = ?''',
                     (status, datetime.now().isoformat(), job_id))
        
        conn.commit()
        conn.close()
    
    def _update_job_progress(self, job_id: str, progress: int):
        """작업 진행 상황 업데이트"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''UPDATE search_jobs 
                    SET progress = ?, updated_at = ?
                    WHERE id = ?''',
                 (progress, datetime.now().isoformat(), job_id))
        
        conn.commit()
        conn.close()
    
    def _get_job_status(self, job_id: str) -> str:
        """작업 상태 조회"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT status FROM search_jobs WHERE id = ?', (job_id,))
        result = c.fetchone()
        
        conn.close()
        
        return result[0] if result else 'unknown'
    
    def pause_search(self, job_id: str):
        """검색 일시정지"""
        self._update_job_status(job_id, 'paused')
    
    def resume_search(self, job_id: str):
        """검색 재개"""
        if job_id in self.active_searches:
            self._update_job_status(job_id, 'running')
        else:
            # 재시작이 필요한 경우
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute('''SELECT j.*, s.project_id, s.search_query, s.search_sites
                        FROM search_jobs j
                        JOIN search_sessions s ON j.session_id = s.id
                        WHERE j.id = ?''', (job_id,))
            
            job_data = c.fetchone()
            conn.close()
            
            if job_data and job_data['status'] == 'paused':
                task = {
                    'job_id': job_id,
                    'session_id': job_data['session_id'],
                    'project_id': job_data['project_id'],
                    'query': job_data['search_query'],
                    'site_ids': json.loads(job_data['search_sites']),
                    'target_count': job_data['total_expected']
                }
                
                self.active_searches[job_id] = task
                self.search_queue.put(task)
    
    def cancel_search(self, job_id: str):
        """검색 취소"""
        self._update_job_status(job_id, 'cancelled')
    
    def get_job_info(self, job_id: str) -> Dict:
        """작업 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''SELECT j.*, s.search_query, s.total_results, s.abstract_count, s.fulltext_count
                    FROM search_jobs j
                    LEFT JOIN search_sessions s ON j.session_id = s.id
                    WHERE j.id = ?''', (job_id,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def search_in_papers(self, query: str, project_id: str = None) -> List[Dict]:
        """저장된 논문에서 검색"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # 쿼리 토큰화
        query_tokens = self._tokenize(query)
        
        # 검색 쿼리 구성
        sql = '''SELECT DISTINCT p.*, 
                (CASE 
                    WHEN p.title LIKE ? THEN 10
                    WHEN i.title_tokens LIKE ? THEN 8
                    WHEN i.abstract_tokens LIKE ? THEN 5
                    WHEN i.author_tokens LIKE ? THEN 3
                    ELSE 1
                END) as relevance
                FROM searched_papers p
                LEFT JOIN paper_index i ON p.id = i.paper_id
                WHERE 1=1'''
        
        params = [f'%{query}%', f'%{query_tokens}%', f'%{query_tokens}%', f'%{query_tokens}%']
        
        if project_id:
            sql += ' AND p.session_id IN (SELECT id FROM search_sessions WHERE project_id = ?)'
            params.append(project_id)
        
        sql += ''' AND (p.title LIKE ? OR p.abstract LIKE ? OR p.authors LIKE ?
                   OR i.title_tokens LIKE ? OR i.abstract_tokens LIKE ? OR i.author_tokens LIKE ?)
                ORDER BY relevance DESC, p.publication_year DESC
                LIMIT 100'''
        
        params.extend([f'%{query}%', f'%{query}%', f'%{query}%',
                      f'%{query_tokens}%', f'%{query_tokens}%', f'%{query_tokens}%'])
        
        c.execute(sql, params)
        results = [dict(row) for row in c.fetchall()]
        
        conn.close()
        
        return results


if __name__ == '__main__':
    # 테스트
    engine = SearchEngine()
    
    # 대량 검색 시작
    job_id = engine.start_search(
        project_id='1',
        query='spine surgery minimally invasive',
        site_ids=['pubmed'],
        target_count=100
    )
    
    print(f"Search job started: {job_id}")
    
    # 상태 확인
    import time
    for i in range(10):
        time.sleep(2)
        info = engine.get_job_info(job_id)
        if info:
            print(f"Status: {info['status']}, Progress: {info['progress']}/{info['total_expected']}")
            if info['status'] == 'completed':
                break
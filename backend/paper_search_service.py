#!/usr/bin/env python3
"""
논문 검색 및 관리 서비스
- 논문 검색 사이트 관리
- 논문 검색 및 수집
- Abstract/Full-text 분류
- 검색 결과 저장
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
import re

class PaperSearchService:
    def __init__(self, db_path='spinalsurgery_research.db'):
        self.db_path = db_path
        self.init_search_tables()
        
    def init_search_tables(self):
        """논문 검색 관련 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 논문 검색 사이트 정보
        c.execute('''CREATE TABLE IF NOT EXISTS search_sites (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            base_url TEXT NOT NULL,
            search_url_template TEXT,
            site_type TEXT NOT NULL,  -- pubmed, google_scholar, korean_db, etc
            access_type TEXT,  -- free, subscription, mixed
            api_available INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # 검색 세션 정보
        c.execute('''CREATE TABLE IF NOT EXISTS search_sessions (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            search_query TEXT NOT NULL,
            search_sites TEXT,  -- JSON array of site IDs
            total_results INTEGER DEFAULT 0,
            abstract_count INTEGER DEFAULT 0,
            fulltext_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            started_at TEXT,
            completed_at TEXT,
            result_file_path TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )''')
        
        # 검색된 논문 상세 정보
        c.execute('''CREATE TABLE IF NOT EXISTS searched_papers (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            source_site_id TEXT,
            title TEXT NOT NULL,
            authors TEXT,
            abstract TEXT,
            journal_name TEXT,
            publication_year INTEGER,
            doi TEXT,
            pmid TEXT,
            url TEXT,
            access_type TEXT,  -- abstract_only, fulltext_available, subscription_required
            fulltext_url TEXT,
            keywords TEXT,  -- JSON array
            citation_count INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES search_sessions (id),
            FOREIGN KEY (source_site_id) REFERENCES search_sites (id)
        )''')
        
        # 기본 검색 사이트 추가
        self._insert_default_sites(c)
        
        conn.commit()
        conn.close()
    
    def _insert_default_sites(self, cursor):
        """기본 논문 검색 사이트 추가"""
        default_sites = [
            {
                'id': 'pubmed',
                'name': 'PubMed',
                'base_url': 'https://pubmed.ncbi.nlm.nih.gov',
                'search_url_template': 'https://pubmed.ncbi.nlm.nih.gov/?term={query}',
                'site_type': 'pubmed',
                'access_type': 'free',
                'api_available': 1,
                'notes': 'NIH/NLM의 생의학 문헌 데이터베이스'
            },
            {
                'id': 'pmc',
                'name': 'PubMed Central',
                'base_url': 'https://www.ncbi.nlm.nih.gov/pmc',
                'search_url_template': 'https://www.ncbi.nlm.nih.gov/pmc/?term={query}',
                'site_type': 'pmc',
                'access_type': 'free',
                'api_available': 1,
                'notes': '무료 전문(Full-text) 제공'
            },
            {
                'id': 'google_scholar',
                'name': 'Google Scholar',
                'base_url': 'https://scholar.google.com',
                'search_url_template': 'https://scholar.google.com/scholar?q={query}',
                'site_type': 'google_scholar',
                'access_type': 'free',
                'api_available': 0,
                'notes': '광범위한 학술 검색'
            },
            {
                'id': 'kmbase',
                'name': 'KMbase',
                'base_url': 'http://kmbase.medric.or.kr',
                'search_url_template': 'http://kmbase.medric.or.kr/Main.aspx?searchWord={query}',
                'site_type': 'korean_db',
                'access_type': 'mixed',
                'api_available': 0,
                'notes': '한국 의학논문 데이터베이스'
            },
            {
                'id': 'kiss',
                'name': 'KISS (한국학술정보)',
                'base_url': 'http://kiss.kstudy.com',
                'search_url_template': 'http://kiss.kstudy.com/search/SearchDetailList.asp?key={query}',
                'site_type': 'korean_db',
                'access_type': 'subscription',
                'api_available': 0,
                'notes': '한국 학술 데이터베이스'
            }
        ]
        
        for site in default_sites:
            cursor.execute('''INSERT OR IGNORE INTO search_sites 
                            (id, name, base_url, search_url_template, site_type, access_type, api_available, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (site['id'], site['name'], site['base_url'], site['search_url_template'],
                          site['site_type'], site['access_type'], site['api_available'], site['notes']))
    
    def get_search_sites(self) -> List[Dict]:
        """검색 가능한 사이트 목록 반환"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM search_sites ORDER BY name')
        sites = [dict(row) for row in c.fetchall()]
        
        conn.close()
        return sites
    
    def create_search_session(self, project_id: str, query: str, site_ids: List[str]) -> str:
        """새 검색 세션 생성"""
        session_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO search_sessions 
                    (id, project_id, search_query, search_sites, status, started_at)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (session_id, project_id, query, json.dumps(site_ids), 'in_progress', 
                  datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def search_pubmed(self, query: str, session_id: str, max_results: int = 100, start: int = 0) -> Dict:
        """PubMed 검색 (페이지네이션 지원)"""
        results = []
        total_count = 0
        
        # PubMed E-utilities API 사용
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': min(max_results, 500),  # PubMed API 최대 500
            'retstart': start,
            'retmode': 'json',
            'sort': 'relevance'
        }
        
        try:
            response = requests.get(search_url, params=params)
            data = response.json()
            
            search_result = data.get('esearchresult', {})
            id_list = search_result.get('idlist', [])
            total_count = int(search_result.get('count', 0))
            
            if id_list:
                # 배치로 상세 정보 가져오기 (한 번에 최대 20개)
                batch_size = 20
                for i in range(0, len(id_list), batch_size):
                    batch_ids = id_list[i:i + batch_size]
                    
                    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                    fetch_params = {
                        'db': 'pubmed',
                        'id': ','.join(batch_ids),
                        'retmode': 'xml'
                    }
                    
                    fetch_response = requests.get(fetch_url, params=fetch_params)
                    
                    # XML 파싱
                    soup = BeautifulSoup(fetch_response.text, 'xml')
                    articles = soup.find_all('PubmedArticle')
                    
                    for article in articles:
                        paper = self._parse_pubmed_article(article)
                        paper['session_id'] = session_id
                        paper['source_site_id'] = 'pubmed'
                        results.append(paper)
                    
                    # API 제한 회피를 위한 짧은 대기
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"PubMed 검색 오류: {e}")
        
        return {
            'papers': results,
            'total_count': total_count,
            'fetched_count': len(results),
            'has_more': total_count > (start + len(results))
        }
    
    def _parse_pubmed_article(self, article) -> Dict:
        """PubMed 논문 정보 파싱"""
        paper = {
            'id': str(uuid.uuid4()),
            'title': '',
            'authors': '',
            'abstract': '',
            'journal_name': '',
            'publication_year': None,
            'doi': '',
            'pmid': '',
            'url': '',
            'access_type': 'abstract_only',
            'keywords': []
        }
        
        # Title
        title_elem = article.find('ArticleTitle')
        if title_elem:
            paper['title'] = title_elem.text
        
        # Authors
        authors = []
        author_list = article.find('AuthorList')
        if author_list:
            for author in author_list.find_all('Author'):
                last_name = author.find('LastName')
                fore_name = author.find('ForeName')
                if last_name and fore_name:
                    authors.append(f"{last_name.text} {fore_name.text}")
        paper['authors'] = '; '.join(authors)
        
        # Abstract
        abstract_elem = article.find('Abstract')
        if abstract_elem:
            abstract_texts = []
            for text in abstract_elem.find_all('AbstractText'):
                label = text.get('Label', '')
                content = text.text
                if label:
                    abstract_texts.append(f"{label}: {content}")
                else:
                    abstract_texts.append(content)
            paper['abstract'] = ' '.join(abstract_texts)
        
        # Journal
        journal = article.find('Journal')
        if journal:
            title = journal.find('Title')
            if title:
                paper['journal_name'] = title.text
        
        # Year
        pub_date = article.find('PubDate')
        if pub_date:
            year = pub_date.find('Year')
            if year:
                paper['publication_year'] = int(year.text)
        
        # PMID
        pmid = article.find('PMID')
        if pmid:
            paper['pmid'] = pmid.text
            paper['url'] = f"https://pubmed.ncbi.nlm.nih.gov/{pmid.text}/"
        
        # DOI
        article_ids = article.find_all('ArticleId')
        for aid in article_ids:
            if aid.get('IdType') == 'doi':
                paper['doi'] = aid.text
                break
        
        # Keywords
        keywords = []
        keyword_list = article.find('KeywordList')
        if keyword_list:
            for keyword in keyword_list.find_all('Keyword'):
                keywords.append(keyword.text)
        paper['keywords'] = json.dumps(keywords)
        
        # Check PMC availability
        for aid in article_ids:
            if aid.get('IdType') == 'pmc':
                paper['access_type'] = 'fulltext_available'
                paper['fulltext_url'] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{aid.text}/"
                break
        
        return paper
    
    def save_search_results(self, session_id: str, papers: List[Dict]):
        """검색 결과 저장"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        abstract_count = 0
        fulltext_count = 0
        
        for paper in papers:
            c.execute('''INSERT INTO searched_papers 
                        (id, session_id, source_site_id, title, authors, abstract, 
                         journal_name, publication_year, doi, pmid, url, access_type, 
                         fulltext_url, keywords, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (paper['id'], paper['session_id'], paper['source_site_id'],
                      paper['title'], paper['authors'], paper['abstract'],
                      paper['journal_name'], paper['publication_year'], paper['doi'],
                      paper['pmid'], paper['url'], paper['access_type'],
                      paper.get('fulltext_url', ''), paper['keywords'],
                      datetime.now().isoformat()))
            
            if paper['access_type'] == 'fulltext_available':
                fulltext_count += 1
            else:
                abstract_count += 1
        
        # 세션 업데이트
        c.execute('''UPDATE search_sessions 
                    SET total_results = ?, abstract_count = ?, fulltext_count = ?, 
                        status = ?, completed_at = ?
                    WHERE id = ?''',
                 (len(papers), abstract_count, fulltext_count, 'completed',
                  datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
    
    def generate_result_report(self, session_id: str, project_id: str) -> str:
        """검색 결과 보고서 생성 및 파일 저장"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # 세션 정보
        c.execute('SELECT * FROM search_sessions WHERE id = ?', (session_id,))
        session = dict(c.fetchone())
        
        # 프로젝트 정보
        c.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = dict(c.fetchone())
        
        # 검색된 논문들
        c.execute('''SELECT * FROM searched_papers WHERE session_id = ? 
                    ORDER BY access_type DESC, publication_year DESC''', (session_id,))
        papers = [dict(row) for row in c.fetchall()]
        
        conn.close()
        
        # 보고서 생성
        report = f"""# 논문 검색 결과 보고서

## 프로젝트 정보
- **제목**: {project['title']}
- **분야**: {project['field']}
- **키워드**: {project['keywords']}

## 검색 정보
- **검색어**: {session['search_query']}
- **검색일시**: {session['started_at']}
- **총 결과**: {session['total_results']}건
- **Abstract**: {session['abstract_count']}건
- **Full-text**: {session['fulltext_count']}건

## 검색 사이트
"""
        
        site_ids = json.loads(session['search_sites'])
        for site_id in site_ids:
            report += f"- {site_id}\n"
        
        report += "\n## 논문 목록\n\n"
        
        # Full-text 논문
        report += "### Full-text 이용 가능 논문\n\n"
        fulltext_papers = [p for p in papers if p['access_type'] == 'fulltext_available']
        
        for i, paper in enumerate(fulltext_papers, 1):
            report += f"{i}. **{paper['title']}**\n"
            report += f"   - 저자: {paper['authors']}\n"
            report += f"   - 저널: {paper['journal_name']} ({paper['publication_year']})\n"
            if paper['doi']:
                report += f"   - DOI: {paper['doi']}\n"
            report += f"   - URL: {paper['url']}\n"
            report += f"   - Full-text: {paper['fulltext_url']}\n"
            if paper['abstract']:
                report += f"   - 초록: {paper['abstract'][:200]}...\n"
            report += "\n"
        
        # Abstract only 논문
        report += "### Abstract만 이용 가능한 논문\n\n"
        abstract_papers = [p for p in papers if p['access_type'] != 'fulltext_available']
        
        for i, paper in enumerate(abstract_papers, 1):
            report += f"{i}. **{paper['title']}**\n"
            report += f"   - 저자: {paper['authors']}\n"
            report += f"   - 저널: {paper['journal_name']} ({paper['publication_year']})\n"
            if paper['doi']:
                report += f"   - DOI: {paper['doi']}\n"
            report += f"   - URL: {paper['url']}\n"
            if paper['abstract']:
                report += f"   - 초록: {paper['abstract'][:200]}...\n"
            report += "\n"
        
        # 파일로 저장
        project_dir = f"./project_files/{project_id}"
        os.makedirs(project_dir, exist_ok=True)
        
        filename = f"search_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(project_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 세션에 파일 경로 저장
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE search_sessions SET result_file_path = ? WHERE id = ?',
                 (filepath, session_id))
        conn.commit()
        conn.close()
        
        return filepath
    
    def search_and_save(self, project_id: str, query: str, site_ids: List[str]) -> Dict:
        """통합 검색 및 저장 프로세스"""
        # 검색 세션 생성
        session_id = self.create_search_session(project_id, query, site_ids)
        
        all_papers = []
        
        # 각 사이트별 검색
        for site_id in site_ids:
            if site_id == 'pubmed':
                papers = self.search_pubmed(query, session_id)
                all_papers.extend(papers)
            # TODO: 다른 사이트 검색 구현
        
        # 결과 저장
        if all_papers:
            self.save_search_results(session_id, all_papers)
        
        # 보고서 생성
        report_path = self.generate_result_report(session_id, project_id)
        
        return {
            'session_id': session_id,
            'total_results': len(all_papers),
            'report_path': report_path
        }


if __name__ == '__main__':
    # 테스트
    service = PaperSearchService()
    
    # 검색 사이트 목록
    sites = service.get_search_sites()
    print("Available search sites:")
    for site in sites:
        print(f"- {site['name']} ({site['site_type']})")
    
    # 테스트 검색
    result = service.search_and_save(
        project_id='1',
        query='spine surgery CD instrument',
        site_ids=['pubmed']
    )
    
    print(f"\nSearch completed: {result}")
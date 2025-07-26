#!/usr/bin/env python3
"""
PubMed 검색 도구 - 척추 수술 관련 논문 검색
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
import json
from datetime import datetime

class PubMedSearcher:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.search_url = self.base_url + "esearch.fcgi"
        self.fetch_url = self.base_url + "efetch.fcgi"
    
    def search(self, query: str, max_results: int = 20, 
               start_year: int = None, end_year: int = None) -> List[str]:
        """PubMed 검색 수행"""
        # 날짜 필터 추가
        if start_year or end_year:
            current_year = datetime.now().year
            start = start_year or 1900
            end = end_year or current_year
            query += f" AND {start}:{end}[dp]"
        
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'sort': 'relevance'
        }
        
        response = requests.get(self.search_url, params=params)
        if response.status_code != 200:
            return []
        
        # XML 파싱
        root = ET.fromstring(response.text)
        id_list = root.find('IdList')
        if id_list is None:
            return []
        
        return [id_elem.text for id_elem in id_list.findall('Id')]
    
    def fetch_details(self, pmids: List[str]) -> List[Dict]:
        """PMID로 상세 정보 가져오기"""
        if not pmids:
            return []
        
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'rettype': 'abstract'
        }
        
        response = requests.get(self.fetch_url, params=params)
        if response.status_code != 200:
            return []
        
        # XML 파싱
        root = ET.fromstring(response.text)
        articles = []
        
        for article in root.findall('.//PubmedArticle'):
            article_data = self._parse_article(article)
            if article_data:
                articles.append(article_data)
        
        return articles
    
    def _parse_article(self, article_elem) -> Dict:
        """논문 정보 파싱"""
        try:
            medline = article_elem.find('.//MedlineCitation')
            article = medline.find('.//Article')
            
            # 기본 정보
            pmid = medline.find('.//PMID').text
            
            # 제목
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else ''
            
            # 초록
            abstract_elem = article.find('.//Abstract/AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else ''
            
            # 저자
            authors = []
            for author in article.findall('.//Author'):
                last_name = author.find('.//LastName')
                fore_name = author.find('.//ForeName')
                if last_name is not None:
                    name = last_name.text
                    if fore_name is not None:
                        name = f"{fore_name.text} {name}"
                    authors.append(name)
            
            # 저널 정보
            journal = article.find('.//Journal')
            journal_title = ''
            if journal is not None:
                title_elem = journal.find('.//Title')
                journal_title = title_elem.text if title_elem is not None else ''
            
            # 출판 정보
            pub_date = article.find('.//Journal/JournalIssue/PubDate')
            year = ''
            if pub_date is not None:
                year_elem = pub_date.find('.//Year')
                year = year_elem.text if year_elem is not None else ''
            
            # 볼륨, 이슈, 페이지
            volume_elem = article.find('.//Journal/JournalIssue/Volume')
            volume = volume_elem.text if volume_elem is not None else ''
            
            issue_elem = article.find('.//Journal/JournalIssue/Issue')
            issue = issue_elem.text if issue_elem is not None else ''
            
            pagination = article.find('.//Pagination/MedlinePgn')
            pages = pagination.text if pagination is not None else ''
            
            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': journal_title,
                'year': year,
                'volume': volume,
                'issue': issue,
                'pages': pages,
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
        
        except Exception as e:
            print(f"Error parsing article: {e}")
            return None
    
    def search_spinal_surgery(self, specific_terms: str = "", 
                            max_results: int = 20,
                            recent_years: int = 5) -> List[Dict]:
        """척추 수술 관련 검색 (최근 연도 필터링)"""
        base_query = '("spine surgery"[MeSH] OR "spinal surgery"[Title/Abstract] OR "spine surgical procedures"[MeSH])'
        
        if specific_terms:
            query = f"{base_query} AND ({specific_terms})"
        else:
            query = base_query
        
        current_year = datetime.now().year
        start_year = current_year - recent_years
        
        pmids = self.search(query, max_results, start_year, current_year)
        return self.fetch_details(pmids)


# CLI 인터페이스
if __name__ == "__main__":
    import sys
    
    searcher = PubMedSearcher()
    
    if len(sys.argv) > 1:
        # 명령줄 인자로 검색
        search_term = ' '.join(sys.argv[1:])
        print(f"Searching for: {search_term}")
        print("-" * 50)
        
        results = searcher.search_spinal_surgery(search_term, max_results=10)
    else:
        # 기본 검색
        print("Recent spinal surgery papers:")
        print("-" * 50)
        results = searcher.search_spinal_surgery(max_results=5)
    
    # 결과 출력
    for i, article in enumerate(results, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Authors: {', '.join(article['authors'][:3])}")
        if len(article['authors']) > 3:
            print(f"            et al.")
        print(f"   Journal: {article['journal']} ({article['year']})")
        print(f"   URL: {article['url']}")
    
    # JSON 파일로 저장
    if results:
        filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {filename}")
"""
Claude Code Search Service
VS Code의 Claude Code가 직접 논문을 검색하고 다운로드하는 서비스
"""
import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json
from pathlib import Path
import re
import hashlib
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
import PyPDF2
import pdfplumber
from deep_translator import GoogleTranslator

class ClaudeCodeSearchService:
    def __init__(self):
        # API endpoints for different academic sites
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.arxiv_base = "http://export.arxiv.org/api/query"
        self.semantic_scholar_base = "https://api.semanticscholar.org/graph/v1"
        
        # Storage configuration
        self.storage_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers")
        self.storage_path.mkdir(exist_ok=True)
        
        # Translation service
        self.translator = GoogleTranslator(source='en', target='ko')
        
        # API keys (if available)
        self.pubmed_api_key = os.getenv("PUBMED_API_KEY", "")
        self.semantic_scholar_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        
    async def search_papers(
        self,
        query: str,
        sites: List[str],
        max_results: int = 10,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """
        Search papers across multiple academic sites
        """
        all_results = []
        results_per_site = max(1, max_results // len(sites))
        
        for site in sites:
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "searching",
                    "current_site": site,
                    "message": f"{site}에서 검색 중...",
                    "papers_found": len(all_results)
                })
            
            try:
                if site == "pubmed":
                    results = await self._search_pubmed(query, results_per_site)
                elif site == "arxiv":
                    results = await self._search_arxiv(query, results_per_site)
                elif site == "google_scholar":
                    results = await self._search_google_scholar(query, results_per_site)
                elif site == "semantic_scholar":
                    results = await self._search_semantic_scholar(query, results_per_site)
                else:
                    continue
                    
                all_results.extend(results)
                
            except Exception as e:
                print(f"Error searching {site}: {e}")
                if progress_callback:
                    await progress_callback({
                        "type": "warning",
                        "status": "searching",
                        "current_site": site,
                        "message": f"{site} 검색 중 오류 발생: {str(e)}"
                    })
        
        # Remove duplicates based on title similarity
        unique_results = self._deduplicate_results(all_results)
        
        if progress_callback:
            await progress_callback({
                "type": "progress",
                "status": "searching",
                "message": f"검색 완료: 총 {len(unique_results)}개의 논문을 찾았습니다.",
                "papers_found": len(unique_results)
            })
        
        return unique_results[:max_results]
    
    async def _search_pubmed(self, query: str, max_results: int) -> List[Dict]:
        """Search PubMed database"""
        papers = []
        
        # Search for PMIDs
        search_url = f"{self.pubmed_base}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        if self.pubmed_api_key:
            params['api_key'] = self.pubmed_api_key
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    pmids = data.get('esearchresult', {}).get('idlist', [])
                    
                    # Fetch details for each PMID
                    for pmid in pmids:
                        paper_details = await self._fetch_pubmed_details(pmid)
                        if paper_details:
                            papers.append(paper_details)
        
        return papers
    
    async def _fetch_pubmed_details(self, pmid: str) -> Optional[Dict]:
        """Fetch detailed information for a PubMed paper"""
        fetch_url = f"{self.pubmed_base}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': pmid,
            'rettype': 'abstract',
            'retmode': 'xml'
        }
        
        if self.pubmed_api_key:
            params['api_key'] = self.pubmed_api_key
        
        async with aiohttp.ClientSession() as session:
            async with session.get(fetch_url, params=params) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    return self._parse_pubmed_xml(xml_data, pmid)
        
        return None
    
    def _parse_pubmed_xml(self, xml_data: str, pmid: str) -> Dict:
        """Parse PubMed XML response"""
        root = ET.fromstring(xml_data)
        article = root.find('.//PubmedArticle')
        
        if not article:
            return {}
        
        paper = {
            'id': f"pubmed_{pmid}",
            'source': 'pubmed',
            'pmid': pmid,
            'title': '',
            'abstract': '',
            'authors': [],
            'journal': '',
            'year': '',
            'doi': '',
            'pmc_id': '',
            'keywords': [],
            'pdf_url': None
        }
        
        # Extract title
        title = article.find('.//ArticleTitle')
        if title is not None and title.text:
            paper['title'] = title.text
        
        # Extract abstract
        abstract_texts = []
        for abstract in article.findall('.//AbstractText'):
            if abstract.text:
                label = abstract.get('Label', '')
                if label:
                    abstract_texts.append(f"{label}: {abstract.text}")
                else:
                    abstract_texts.append(abstract.text)
        paper['abstract'] = '\n\n'.join(abstract_texts)
        
        # Extract authors
        for author in article.findall('.//Author'):
            last_name = author.find('LastName')
            fore_name = author.find('ForeName')
            if last_name is not None and fore_name is not None:
                paper['authors'].append(f"{fore_name.text} {last_name.text}")
        
        # Extract journal info
        journal = article.find('.//Journal/Title')
        if journal is not None and journal.text:
            paper['journal'] = journal.text
        
        year = article.find('.//PubDate/Year')
        if year is not None and year.text:
            paper['year'] = year.text
        
        # Extract identifiers
        doi = article.find('.//ArticleId[@IdType="doi"]')
        if doi is not None and doi.text:
            paper['doi'] = doi.text
        
        pmc = article.find('.//ArticleId[@IdType="pmc"]')
        if pmc is not None and pmc.text:
            paper['pmc_id'] = pmc.text
            paper['pdf_url'] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc.text}/pdf/"
        
        # Extract keywords
        for keyword in article.findall('.//Keyword'):
            if keyword.text:
                paper['keywords'].append(keyword.text)
        
        return paper
    
    async def _search_arxiv(self, query: str, max_results: int) -> List[Dict]:
        """Search arXiv database"""
        papers = []
        
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.arxiv_base, params=params) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    papers = self._parse_arxiv_xml(xml_data)
        
        return papers
    
    def _parse_arxiv_xml(self, xml_data: str) -> List[Dict]:
        """Parse arXiv XML response"""
        papers = []
        
        # Remove namespace for easier parsing
        xml_data = re.sub(r'xmlns="[^"]+"', '', xml_data)
        root = ET.fromstring(xml_data)
        
        for entry in root.findall('.//entry'):
            paper = {
                'source': 'arxiv',
                'title': '',
                'abstract': '',
                'authors': [],
                'year': '',
                'pdf_url': None,
                'arxiv_id': ''
            }
            
            # Title
            title = entry.find('title')
            if title is not None and title.text:
                paper['title'] = title.text.strip()
            
            # Abstract
            summary = entry.find('summary')
            if summary is not None and summary.text:
                paper['abstract'] = summary.text.strip()
            
            # Authors
            for author in entry.findall('.//author/name'):
                if author.text:
                    paper['authors'].append(author.text)
            
            # Published date
            published = entry.find('published')
            if published is not None and published.text:
                paper['year'] = published.text[:4]
            
            # arXiv ID and PDF URL
            arxiv_id = entry.find('id')
            if arxiv_id is not None and arxiv_id.text:
                # Extract ID from URL
                id_match = re.search(r'(\d+\.\d+)', arxiv_id.text)
                if id_match:
                    paper['arxiv_id'] = id_match.group(1)
                    paper['pdf_url'] = f"https://arxiv.org/pdf/{paper['arxiv_id']}.pdf"
                    paper['id'] = f"arxiv_{paper['arxiv_id']}"
            
            papers.append(paper)
        
        return papers
    
    async def _search_semantic_scholar(self, query: str, max_results: int) -> List[Dict]:
        """Search Semantic Scholar database"""
        papers = []
        
        search_url = f"{self.semantic_scholar_base}/paper/search"
        params = {
            'query': query,
            'limit': max_results,
            'fields': 'title,abstract,authors,year,venue,doi,url,openAccessPdf'
        }
        
        headers = {}
        if self.semantic_scholar_api_key:
            headers['x-api-key'] = self.semantic_scholar_api_key
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get('data', []):
                        paper = {
                            'id': f"s2_{item.get('paperId', '')}",
                            'source': 'semantic_scholar',
                            'title': item.get('title', ''),
                            'abstract': item.get('abstract', ''),
                            'authors': [author.get('name', '') for author in item.get('authors', [])],
                            'journal': item.get('venue', ''),
                            'year': str(item.get('year', '')),
                            'doi': item.get('doi', ''),
                            'pdf_url': None
                        }
                        
                        # Check for open access PDF
                        if item.get('openAccessPdf'):
                            paper['pdf_url'] = item['openAccessPdf'].get('url')
                        
                        papers.append(paper)
        
        return papers
    
    async def _search_google_scholar(self, query: str, max_results: int) -> List[Dict]:
        """
        Search Google Scholar (limited implementation)
        Note: Google Scholar doesn't provide official API, so this is a placeholder
        """
        # In a real implementation, you might use scholarly library or web scraping
        # For now, we'll return empty list to avoid issues
        return []
    
    def _deduplicate_results(self, papers: List[Dict]) -> List[Dict]:
        """Remove duplicate papers based on title similarity"""
        unique_papers = []
        seen_titles = set()
        
        for paper in papers:
            # Normalize title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', paper['title'].lower())
            normalized_title = ' '.join(normalized_title.split())
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_papers.append(paper)
        
        return unique_papers
    
    async def download_papers(
        self,
        papers: List[Dict],
        project_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Download PDFs for papers"""
        downloaded_papers = []
        
        # Create project folder if specified
        if project_id:
            project_folder = self.storage_path / f"project_{project_id}"
        else:
            project_folder = self.storage_path / f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_folder.mkdir(exist_ok=True)
        
        for idx, paper in enumerate(papers):
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "downloading",
                    "current_paper": paper['title'][:50] + "...",
                    "papers_downloaded": idx,
                    "message": f"다운로드 중: {paper['title'][:50]}..."
                })
            
            # Create folder for each paper
            safe_title = re.sub(r'[^\w\s-]', '', paper['title'])[:50]
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            paper_folder = project_folder / f"{paper['id']}_{safe_title}"
            paper_folder.mkdir(exist_ok=True)
            
            # Download PDF if URL is available
            pdf_path = None
            if paper.get('pdf_url'):
                pdf_filename = f"{paper['id']}.pdf"
                pdf_path = paper_folder / pdf_filename
                
                if await self._download_file(paper['pdf_url'], pdf_path):
                    paper['pdf_path'] = str(pdf_path)
                    paper['pdf_downloaded'] = True
                else:
                    paper['pdf_downloaded'] = False
            else:
                paper['pdf_downloaded'] = False
            
            # Save metadata
            metadata_path = paper_folder / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(paper, f, ensure_ascii=False, indent=2)
            
            paper['folder'] = str(paper_folder)
            downloaded_papers.append(paper)
        
        return downloaded_papers
    
    async def _download_file(self, url: str, filepath: Path) -> bool:
        """Download file from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        return True
        except Exception as e:
            print(f"Download error for {url}: {e}")
        
        return False
    
    async def translate_papers(
        self,
        papers: List[Dict],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Translate paper titles and abstracts to Korean"""
        translated_papers = []
        
        for idx, paper in enumerate(papers):
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "translating",
                    "current_paper": paper['title'][:50] + "...",
                    "message": f"번역 중: {paper['title'][:50]}..."
                })
            
            try:
                # Translate title
                if paper.get('title'):
                    paper['korean_title'] = self.translator.translate(paper['title'])
                
                # Translate abstract
                if paper.get('abstract'):
                    # Split long abstracts
                    abstract_parts = self._split_text(paper['abstract'], 4500)
                    translated_parts = []
                    
                    for part in abstract_parts:
                        translated = self.translator.translate(part)
                        translated_parts.append(translated)
                        await asyncio.sleep(0.5)  # Avoid rate limiting
                    
                    paper['korean_abstract'] = '\n'.join(translated_parts)
                
                # If PDF was downloaded, extract and translate key sections
                if paper.get('pdf_path') and Path(paper['pdf_path']).exists():
                    pdf_text = self._extract_pdf_text(Path(paper['pdf_path']))
                    if pdf_text:
                        key_sections = self._extract_key_sections(pdf_text)
                        if key_sections:
                            paper['korean_summary'] = self.translator.translate(key_sections[:1000])
                
                # Save Korean translation
                if paper.get('folder'):
                    korean_path = Path(paper['folder']) / "summary_korean.txt"
                    self._save_korean_summary(paper, korean_path)
                
            except Exception as e:
                print(f"Translation error for {paper['title']}: {e}")
            
            translated_papers.append(paper)
        
        return translated_papers
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Split long text into chunks"""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        sentences = text.split('. ')
        current_part = ""
        
        for sentence in sentences:
            if len(current_part) + len(sentence) + 2 <= max_length:
                current_part += sentence + ". "
            else:
                if current_part:
                    parts.append(current_part.strip())
                current_part = sentence + ". "
        
        if current_part:
            parts.append(current_part.strip())
        
        return parts
    
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF"""
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:10]:  # First 10 pages only
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"PDF extraction error: {e}")
        
        return text
    
    def _extract_key_sections(self, text: str) -> str:
        """Extract key sections from paper text"""
        sections = {
            'abstract': r'(?i)abstract.*?(?=introduction|keywords)',
            'introduction': r'(?i)introduction.*?(?=methods|materials)',
            'conclusion': r'(?i)(conclusion|summary).*?(?=references|acknowledgments)'
        }
        
        extracted = []
        
        for section_name, pattern in sections.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                section_text = match.group(0)[:500]
                extracted.append(f"[{section_name.upper()}]\n{section_text}")
        
        return '\n\n'.join(extracted) if extracted else text[:1000]
    
    def _save_korean_summary(self, paper: Dict, filepath: Path):
        """Save Korean translation summary"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"제목: {paper.get('korean_title', paper.get('title', 'N/A'))}\n")
            f.write(f"원제: {paper.get('title', 'N/A')}\n\n")
            
            f.write("저자: " + ", ".join(paper.get('authors', [])) + "\n")
            f.write(f"저널: {paper.get('journal', 'N/A')}\n")
            f.write(f"연도: {paper.get('year', 'N/A')}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("초록\n")
            f.write("=" * 80 + "\n")
            f.write(paper.get('korean_abstract', paper.get('abstract', '초록 없음')) + "\n\n")
            
            if paper.get('korean_summary'):
                f.write("=" * 80 + "\n")
                f.write("주요 내용 요약\n")
                f.write("=" * 80 + "\n")
                f.write(paper['korean_summary'] + "\n")

# Singleton instance
claude_code_search_service = ClaudeCodeSearchService()
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re
import json


class ScraperService:
    def __init__(self):
        self.pubmed_base = "https://pubmed.ncbi.nlm.nih.gov"
        self.scholar_base = "https://scholar.google.com"
        
    async def search_papers(
        self,
        query: str,
        sources: List[str] = ["pubmed", "scholar"],
        limit: int = 20
    ) -> List[Dict]:
        """Search papers from multiple sources"""
        all_results = []
        
        tasks = []
        if "pubmed" in sources:
            tasks.append(self._search_pubmed(query, limit))
        if "scholar" in sources:
            tasks.append(self._search_google_scholar(query, limit))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
            else:
                print(f"Error in search: {result}")
                
        return all_results[:limit]
    
    async def _search_pubmed(self, query: str, limit: int) -> List[Dict]:
        """Search papers from PubMed"""
        results = []
        
        async with httpx.AsyncClient() as client:
            # Search for papers
            search_url = f"{self.pubmed_base}/?term={query}&size={limit}&format=json"
            response = await client.get(search_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Parse search results
                articles = soup.find_all('article', class_='full-docsum')
                
                for article in articles[:limit]:
                    paper = self._parse_pubmed_article(article)
                    if paper:
                        results.append(paper)
                        
        return results
    
    def _parse_pubmed_article(self, article) -> Optional[Dict]:
        """Parse PubMed article element"""
        try:
            title_elem = article.find('a', class_='docsum-title')
            title = title_elem.text.strip() if title_elem else ""
            
            authors_elem = article.find('span', class_='docsum-authors')
            authors = authors_elem.text.strip() if authors_elem else ""
            
            journal_elem = article.find('span', class_='docsum-journal-citation')
            journal = journal_elem.text.strip() if journal_elem else ""
            
            pmid_elem = article.find('span', class_='docsum-pmid')
            pmid = pmid_elem.text.strip() if pmid_elem else ""
            
            # Extract year from journal citation
            year_match = re.search(r'(\d{4})', journal)
            year = int(year_match.group(1)) if year_match else None
            
            return {
                "title": title,
                "authors": [a.strip() for a in authors.split(',')],
                "journal": journal,
                "pmid": pmid,
                "year": year,
                "source": "PubMed",
                "url": f"{self.pubmed_base}/{pmid}",
                "scraped_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error parsing PubMed article: {e}")
            return None
    
    async def _search_google_scholar(self, query: str, limit: int) -> List[Dict]:
        """Search papers from Google Scholar using Playwright"""
        results = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to Google Scholar
                await page.goto(f"{self.scholar_base}/scholar?q={query}")
                
                # Wait for results
                await page.wait_for_selector('.gs_r', timeout=10000)
                
                # Extract results
                articles = await page.query_selector_all('.gs_r')
                
                for article in articles[:limit]:
                    paper = await self._parse_scholar_article(page, article)
                    if paper:
                        results.append(paper)
                        
            except Exception as e:
                print(f"Error searching Google Scholar: {e}")
            finally:
                await browser.close()
                
        return results
    
    async def _parse_scholar_article(self, page, article) -> Optional[Dict]:
        """Parse Google Scholar article element"""
        try:
            # Extract title
            title_elem = await article.query_selector('h3 a')
            title = await title_elem.inner_text() if title_elem else ""
            url = await title_elem.get_attribute('href') if title_elem else ""
            
            # Extract authors and publication info
            info_elem = await article.query_selector('.gs_a')
            info_text = await info_elem.inner_text() if info_elem else ""
            
            # Parse info text
            authors = []
            journal = ""
            year = None
            
            if info_text:
                parts = info_text.split(' - ')
                if parts:
                    authors = [a.strip() for a in parts[0].split(',')]
                if len(parts) > 1:
                    journal = parts[1]
                    year_match = re.search(r'(\d{4})', info_text)
                    year = int(year_match.group(1)) if year_match else None
            
            # Extract abstract
            abstract_elem = await article.query_selector('.gs_rs')
            abstract = await abstract_elem.inner_text() if abstract_elem else ""
            
            return {
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "abstract": abstract[:500],  # Limit abstract length
                "source": "Google Scholar",
                "url": url,
                "scraped_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error parsing Scholar article: {e}")
            return None
    
    async def fetch_paper_details(self, url: str) -> Optional[Dict]:
        """Fetch detailed paper information from URL"""
        if "pubmed" in url:
            return await self._fetch_pubmed_details(url)
        else:
            return await self._fetch_generic_details(url)
    
    async def _fetch_pubmed_details(self, url: str) -> Optional[Dict]:
        """Fetch detailed information from PubMed"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract abstract
                abstract_elem = soup.find('div', class_='abstract-content')
                abstract = abstract_elem.text.strip() if abstract_elem else ""
                
                # Extract DOI
                doi_elem = soup.find('span', class_='citation-doi')
                doi = doi_elem.text.replace('doi:', '').strip() if doi_elem else ""
                
                # Extract keywords
                keywords_elem = soup.find_all('span', class_='keyword')
                keywords = [kw.text.strip() for kw in keywords_elem]
                
                return {
                    "abstract": abstract,
                    "doi": doi,
                    "keywords": keywords,
                    "full_text_available": bool(soup.find('a', text=re.compile('Full text')))
                }
                
        return None
    
    async def _fetch_generic_details(self, url: str) -> Optional[Dict]:
        """Fetch details from generic webpage"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try to extract PDF link
                    pdf_link = None
                    pdf_elem = soup.find('a', href=re.compile(r'\.pdf'))
                    if pdf_elem:
                        pdf_link = pdf_elem.get('href')
                        
                    return {
                        "pdf_link": pdf_link,
                        "page_title": soup.title.string if soup.title else ""
                    }
            except Exception as e:
                print(f"Error fetching generic details: {e}")
                
        return None


# Singleton instance
scraper_service = ScraperService()
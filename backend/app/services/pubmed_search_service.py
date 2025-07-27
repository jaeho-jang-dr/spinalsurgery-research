import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
import os
import json
import re
from urllib.parse import quote

class PubMedSearchService:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = "research@spinalsurgery.com"  # Required by NCBI
        self.api_key = None  # Optional: can improve rate limits
        self.results_dir = "/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers"
        
    async def search_plif_papers(self, 
                                year_start: int = 2022, 
                                year_end: int = 2025,
                                max_results: int = 100) -> List[Dict]:
        """Search for PLIF papers with 2-year outcomes"""
        
        # Construct search query - broader search
        search_terms = [
            "(posterior lumbar interbody fusion OR PLIF)",
            "(2 year OR two year OR 24 month OR 2-year OR two-year)",
            "(outcome OR follow-up OR results)",
            f"({year_start}[PDAT]:{year_end}[PDAT])"  # Publication date filter
        ]
        
        query = " AND ".join(search_terms)
        print(f"Search query: {query}")
        
        # Search PubMed
        search_results = await self._search_pubmed(query, max_results)
        
        # Get detailed information for each paper
        papers = []
        if search_results:
            paper_details = await self._fetch_paper_details(search_results)
            papers = paper_details
            
        return papers
    
    async def _search_pubmed(self, query: str, max_results: int) -> List[str]:
        """Search PubMed and return list of PMIDs"""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'email': self.email
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
                
            response = await client.get(f"{self.base_url}/esearch.fcgi", params=params)
            
            print(f"Search URL: {response.url}")
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('esearchresult', {})
                count = result.get('count', '0')
                print(f"Total results found: {count}")
                id_list = result.get('idlist', [])
                print(f"Retrieved {len(id_list)} PMIDs")
                return id_list
            
        return []
    
    async def _fetch_paper_details(self, pmids: List[str]) -> List[Dict]:
        """Fetch detailed information for each PMID"""
        papers = []
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Fetch in batches of 20
            for i in range(0, len(pmids), 20):
                batch = pmids[i:i+20]
                
                params = {
                    'db': 'pubmed',
                    'id': ','.join(batch),
                    'retmode': 'xml',
                    'email': self.email
                }
                
                if self.api_key:
                    params['api_key'] = self.api_key
                    
                response = await client.get(f"{self.base_url}/efetch.fcgi", params=params)
                
                if response.status_code == 200:
                    # Parse XML response
                    root = ET.fromstring(response.text)
                    
                    for article in root.findall('.//PubmedArticle'):
                        paper = self._parse_article(article)
                        if paper:
                            papers.append(paper)
                            
                # Be nice to NCBI servers
                await asyncio.sleep(0.5)
                
        return papers
    
    def _parse_article(self, article_elem) -> Optional[Dict]:
        """Parse article XML element"""
        try:
            # Extract basic information
            pmid = article_elem.find('.//PMID').text
            
            article = article_elem.find('.//Article')
            title = article.find('.//ArticleTitle').text
            
            # Abstract
            abstract_elem = article.find('.//Abstract')
            abstract = ""
            if abstract_elem is not None:
                abstract_texts = []
                for abstract_text in abstract_elem.findall('.//AbstractText'):
                    label = abstract_text.get('Label', '')
                    text = abstract_text.text or ''
                    if label:
                        abstract_texts.append(f"{label}: {text}")
                    else:
                        abstract_texts.append(text)
                abstract = '\n'.join(abstract_texts)
            
            # Authors
            authors = []
            for author in article.findall('.//Author'):
                last_name = author.find('.//LastName')
                fore_name = author.find('.//ForeName')
                if last_name is not None:
                    name = last_name.text
                    if fore_name is not None:
                        name = f"{fore_name.text} {name}"
                    authors.append(name)
            
            # Journal info
            journal = article.find('.//Journal')
            journal_title = journal.find('.//Title').text if journal.find('.//Title') is not None else ""
            
            pub_date_elem = journal.find('.//PubDate')
            year = pub_date_elem.find('.//Year').text if pub_date_elem.find('.//Year') is not None else ""
            
            # DOI
            doi = None
            for article_id in article_elem.findall('.//ArticleId'):
                if article_id.get('IdType') == 'doi':
                    doi = article_id.text
                    break
            
            # Check if PMC full text is available
            pmc_id = None
            for article_id in article_elem.findall('.//ArticleId'):
                if article_id.get('IdType') == 'pmc':
                    pmc_id = article_id.text
                    break
            
            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': journal_title,
                'year': year,
                'doi': doi,
                'pmc_id': pmc_id,
                'has_full_text': pmc_id is not None
            }
            
        except Exception as e:
            print(f"Error parsing article: {e}")
            return None
    
    async def download_and_save_papers(self, search_folder: str = "plif_2year_outcomes"):
        """Search, download and save papers"""
        print("Searching for PLIF papers with 2-year outcomes...")
        
        # Create folder
        folder_path = os.path.join(self.results_dir, search_folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Search papers
        papers = await self.search_plif_papers()
        
        print(f"Found {len(papers)} papers")
        
        # Save metadata
        metadata_file = os.path.join(folder_path, "papers_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        # Save individual paper files
        for i, paper in enumerate(papers):
            # Create filename
            safe_title = re.sub(r'[^\w\s-]', '', paper['title'])[:50]
            filename = f"{i+1:03d}_{paper['pmid']}_{safe_title}"
            
            # Save abstract
            abstract_file = os.path.join(folder_path, f"{filename}_abstract.txt")
            with open(abstract_file, 'w', encoding='utf-8') as f:
                f.write(f"Title: {paper['title']}\n")
                f.write(f"Authors: {', '.join(paper['authors'])}\n")
                f.write(f"Journal: {paper['journal']} ({paper['year']})\n")
                f.write(f"PMID: {paper['pmid']}\n")
                if paper['doi']:
                    f.write(f"DOI: {paper['doi']}\n")
                f.write(f"\nAbstract:\n{paper['abstract']}\n")
                
            # If PMC full text is available, note it
            if paper['has_full_text']:
                full_text_note = os.path.join(folder_path, f"{filename}_FULL_TEXT_AVAILABLE.txt")
                with open(full_text_note, 'w') as f:
                    f.write(f"Full text available at: https://www.ncbi.nlm.nih.gov/pmc/articles/{paper['pmc_id']}/\n")
        
        # Create summary report
        summary_file = os.path.join(folder_path, "search_summary.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("PLIF 2-Year Outcomes Literature Search Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Papers Found: {len(papers)}\n")
            f.write(f"Papers with Full Text: {sum(1 for p in papers if p['has_full_text'])}\n\n")
            
            f.write("Search Terms:\n")
            f.write("- Posterior lumbar interbody fusion (PLIF)\n")
            f.write("- 2-year outcomes/follow-up\n")
            f.write("- CD instrumentation/pedicle screw fixation\n")
            f.write("- Published: 2024-2025\n\n")
            
            f.write("Papers List:\n")
            for i, paper in enumerate(papers):
                f.write(f"\n{i+1}. {paper['title']}\n")
                f.write(f"   Authors: {', '.join(paper['authors'][:3])}")
                if len(paper['authors']) > 3:
                    f.write(" et al.")
                f.write(f"\n   Journal: {paper['journal']} ({paper['year']})\n")
                f.write(f"   PMID: {paper['pmid']}")
                if paper['has_full_text']:
                    f.write(" [Full Text Available]")
                f.write("\n")
        
        print(f"Papers saved to: {folder_path}")
        return folder_path

# Singleton instance
pubmed_search_service = PubMedSearchService()
"""
Mock Claude Code Search Service for testing WebSocket connections
"""
import asyncio
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import random

class MockClaudeCodeSearchService:
    def __init__(self):
        self.mock_papers = [
            {
                'id': 'pubmed_12345',
                'source': 'pubmed',
                'title': 'Minimally Invasive Lumbar Decompression: A Review of Indications and Techniques',
                'abstract': 'Background: Minimally invasive spine surgery has evolved significantly over the past two decades...',
                'authors': ['Smith JD', 'Johnson KL', 'Williams RT'],
                'journal': 'Spine',
                'year': '2023',
                'doi': '10.1097/BRS.0000000000004567',
                'pdf_url': 'https://example.com/paper1.pdf'
            },
            {
                'id': 'arxiv_2023.00123',
                'source': 'arxiv',
                'title': 'Deep Learning Applications in Spinal Imaging: A Comprehensive Survey',
                'abstract': 'This survey examines the recent advances in deep learning methods applied to spinal imaging...',
                'authors': ['Lee S', 'Park J', 'Kim H'],
                'journal': 'arXiv',
                'year': '2023',
                'doi': '10.48550/arXiv.2023.00123',
                'pdf_url': 'https://arxiv.org/pdf/2023.00123.pdf'
            },
            {
                'id': 's2_87654321',
                'source': 'semantic_scholar',
                'title': 'Long-term Outcomes of Lumbar Fusion: A Systematic Review and Meta-analysis',
                'abstract': 'Objective: To evaluate the long-term clinical outcomes of lumbar fusion surgery...',
                'authors': ['Chen M', 'Davis R', 'Thompson A'],
                'journal': 'Journal of Neurosurgery: Spine',
                'year': '2022',
                'doi': '10.3171/2022.5.SPINE21234',
                'pdf_url': None
            }
        ]
    
    async def search_papers(
        self,
        query: str,
        sites: List[str],
        max_results: int = 10,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Mock paper search with realistic delays"""
        results = []
        
        # Simulate searching each site
        for idx, site in enumerate(sites):
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "searching",
                    "current_site": site,
                    "message": f"{site}에서 검색 중... ({idx + 1}/{len(sites)})",
                    "papers_found": len(results),
                    "progress_percentage": int((idx / len(sites)) * 30)
                })
            
            # Simulate network delay
            await asyncio.sleep(random.uniform(1.0, 2.5))
            
            # Add mock results from this site
            site_papers = [p for p in self.mock_papers if p['source'] == site or site == 'google_scholar']
            results.extend(site_papers[:max_results // len(sites)])
        
        if progress_callback:
            await progress_callback({
                "type": "progress",
                "status": "searching",
                "message": f"검색 완료: 총 {len(results)}개의 논문을 찾았습니다.",
                "papers_found": len(results),
                "progress_percentage": 30
            })
        
        return results[:max_results]
    
    async def download_papers(
        self,
        papers: List[Dict],
        project_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Mock PDF download with progress updates"""
        downloaded_papers = []
        
        for idx, paper in enumerate(papers):
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "downloading",
                    "current_paper": paper['title'][:50] + "...",
                    "papers_downloaded": idx,
                    "message": f"다운로드 중: {paper['title'][:50]}...",
                    "progress_percentage": 30 + int((idx / len(papers)) * 40)
                })
            
            # Simulate download delay
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Mock download success/failure
            paper['pdf_downloaded'] = paper.get('pdf_url') is not None and random.random() > 0.1
            paper['folder'] = f"/mock/storage/{paper['id']}"
            downloaded_papers.append(paper)
        
        return downloaded_papers
    
    async def translate_papers(
        self,
        papers: List[Dict],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Mock translation with progress updates"""
        translated_papers = []
        
        korean_translations = {
            'Minimally Invasive Lumbar Decompression': '최소 침습적 요추 감압술',
            'Deep Learning Applications in Spinal Imaging': '척추 영상에서의 딥러닝 응용',
            'Long-term Outcomes of Lumbar Fusion': '요추 유합술의 장기 결과'
        }
        
        for idx, paper in enumerate(papers):
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "translating",
                    "current_paper": paper['title'][:50] + "...",
                    "message": f"번역 중: {paper['title'][:50]}...",
                    "progress_percentage": 70 + int((idx / len(papers)) * 25)
                })
            
            # Simulate translation delay
            await asyncio.sleep(random.uniform(0.8, 1.8))
            
            # Add mock Korean translations
            for eng_phrase, kor_phrase in korean_translations.items():
                if eng_phrase in paper['title']:
                    paper['korean_title'] = paper['title'].replace(eng_phrase, kor_phrase)
                    break
            else:
                paper['korean_title'] = paper['title'] + ' (한글 번역)'
            
            paper['korean_abstract'] = paper.get('abstract', '') + '\n\n[한글 번역된 초록]'
            translated_papers.append(paper)
        
        return translated_papers

# Singleton instance
mock_claude_code_search_service = MockClaudeCodeSearchService()
"""
Paper Download Service - 실제 논문 다운로드 및 처리
"""
import os
import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import xml.etree.ElementTree as ET
import PyPDF2
import pdfplumber
from deep_translator import GoogleTranslator
import hashlib
import json
from pathlib import Path
import re

class PaperDownloaderService:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.pmc_base = "https://www.ncbi.nlm.nih.gov/pmc/articles"
        self.pubmed_base = "https://pubmed.ncbi.nlm.nih.gov"
        
        # 저장 경로
        self.storage_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/downloaded_papers")
        self.storage_path.mkdir(exist_ok=True)
        
        # 번역기
        self.translator = GoogleTranslator(source='en', target='ko')
        
        # API 키 (필요시)
        self.api_key = os.getenv("PUBMED_API_KEY", "")
        
    async def search_and_download_papers(
        self, 
        query: str, 
        max_results: int = 5,
        translate_to_korean: bool = True
    ) -> List[Dict]:
        """논문 검색 및 다운로드 메인 함수"""
        print(f"🔍 Searching for: {query}")
        
        # 1. PubMed 검색
        pmids = await self._search_pubmed(query, max_results)
        if not pmids:
            print("❌ No papers found")
            return []
            
        print(f"📄 Found {len(pmids)} papers")
        
        # 2. 각 논문 처리
        results = []
        for i, pmid in enumerate(pmids, 1):
            print(f"\n--- Processing paper {i}/{len(pmids)} (PMID: {pmid}) ---")
            
            # 논문 메타데이터 가져오기
            metadata = await self._fetch_paper_metadata(pmid)
            if not metadata:
                continue
                
            # 폴더 생성
            paper_folder = self._create_paper_folder(metadata)
            
            # 논문 다운로드 시도
            pdf_path = await self._download_paper_pdf(pmid, metadata, paper_folder)
            
            # PDF에서 텍스트 추출
            if pdf_path and pdf_path.exists():
                full_text = self._extract_text_from_pdf(pdf_path)
                metadata['full_text'] = full_text
            else:
                # PDF가 없으면 abstract만 사용
                full_text = metadata.get('abstract', '')
                
            # 한글 번역
            if translate_to_korean and full_text:
                print("🌐 Translating to Korean...")
                metadata['korean_translation'] = await self._translate_to_korean(
                    metadata, full_text
                )
                
            # 메타데이터 저장
            self._save_metadata(metadata, paper_folder)
            
            # 요약 생성
            summary = self._create_summary(metadata, paper_folder)
            
            results.append({
                'pmid': pmid,
                'metadata': metadata,
                'folder': str(paper_folder),
                'summary': summary,
                'pdf_downloaded': pdf_path is not None and pdf_path.exists()
            })
            
        return results
        
    async def _search_pubmed(self, query: str, max_results: int) -> List[str]:
        """PubMed 검색"""
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('esearchresult', {}).get('idlist', [])
                    else:
                        print(f"Search error: {response.status}")
                        text = await response.text()
                        print(f"Response: {text[:200]}")
        except Exception as e:
            print(f"Exception during search: {e}")
        return []
        
    async def _fetch_paper_metadata(self, pmid: str) -> Optional[Dict]:
        """논문 메타데이터 가져오기"""
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': pmid,
            'rettype': 'abstract',
            'retmode': 'xml'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        async with aiohttp.ClientSession() as session:
            async with session.get(fetch_url, params=params) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    return self._parse_pubmed_xml(xml_data, pmid)
        return None
        
    def _parse_pubmed_xml(self, xml_data: str, pmid: str) -> Dict:
        """PubMed XML 파싱"""
        root = ET.fromstring(xml_data)
        article = root.find('.//PubmedArticle')
        
        if not article:
            return {}
            
        metadata = {'pmid': pmid}
        
        # Title
        title = article.find('.//ArticleTitle')
        metadata['title'] = title.text if title is not None else 'Unknown Title'
        
        # Abstract
        abstract_texts = []
        for abstract in article.findall('.//AbstractText'):
            if abstract.text:
                label = abstract.get('Label', '')
                if label:
                    abstract_texts.append(f"{label}: {abstract.text}")
                else:
                    abstract_texts.append(abstract.text)
        metadata['abstract'] = '\n\n'.join(abstract_texts)
        
        # Authors
        authors = []
        for author in article.findall('.//Author'):
            last_name = author.find('LastName')
            fore_name = author.find('ForeName')
            if last_name is not None and fore_name is not None:
                authors.append(f"{fore_name.text} {last_name.text}")
        metadata['authors'] = authors
        
        # Journal
        journal = article.find('.//Journal/Title')
        metadata['journal'] = journal.text if journal is not None else ''
        
        # Year
        year = article.find('.//PubDate/Year')
        metadata['year'] = year.text if year is not None else ''
        
        # DOI
        doi = article.find('.//ArticleId[@IdType="doi"]')
        metadata['doi'] = doi.text if doi is not None else ''
        
        # PMC ID
        pmc = article.find('.//ArticleId[@IdType="pmc"]')
        metadata['pmc_id'] = pmc.text if pmc is not None else ''
        
        # Keywords
        keywords = []
        for keyword in article.findall('.//Keyword'):
            if keyword.text:
                keywords.append(keyword.text)
        metadata['keywords'] = keywords
        
        return metadata
        
    def _create_paper_folder(self, metadata: Dict) -> Path:
        """논문별 폴더 생성"""
        # 안전한 파일명 생성
        safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])[:50]
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        
        folder_name = f"{metadata['pmid']}_{safe_title}"
        folder_path = self.storage_path / folder_name
        folder_path.mkdir(exist_ok=True)
        
        return folder_path
        
    async def _download_paper_pdf(
        self, 
        pmid: str, 
        metadata: Dict, 
        folder: Path
    ) -> Optional[Path]:
        """논문 PDF 다운로드"""
        pdf_path = folder / f"{pmid}.pdf"
        
        # PMC ID가 있는 경우 PMC에서 다운로드 시도
        if metadata.get('pmc_id'):
            pmc_pdf_url = f"{self.pmc_base}/{metadata['pmc_id']}/pdf/"
            if await self._download_file(pmc_pdf_url, pdf_path):
                print(f"✅ Downloaded PDF from PMC")
                return pdf_path
                
        # DOI를 통한 다운로드 시도 (Sci-Hub 등 사용 가능)
        if metadata.get('doi'):
            # 실제 구현에서는 적절한 방법 사용
            print(f"⚠️ PDF download via DOI not implemented (DOI: {metadata['doi']})")
            
        # PDF를 찾을 수 없는 경우
        print(f"❌ Could not download PDF for PMID: {pmid}")
        return None
        
    async def _download_file(self, url: str, filepath: Path) -> bool:
        """파일 다운로드"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        return True
        except Exception as e:
            print(f"Download error: {e}")
        return False
        
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """PDF에서 텍스트 추출"""
        text = ""
        
        try:
            # pdfplumber 사용 (더 정확한 텍스트 추출)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
            if not text.strip():
                # PyPDF2로 재시도
                with open(pdf_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                        
        except Exception as e:
            print(f"PDF extraction error: {e}")
            
        return text.strip()
        
    async def _translate_to_korean(self, metadata: Dict, full_text: str) -> Dict:
        """한글 번역"""
        korean_data = {}
        
        try:
            # 제목 번역
            if metadata.get('title'):
                korean_data['title'] = self.translator.translate(metadata['title'])
                
            # 초록 번역
            if metadata.get('abstract'):
                # 긴 텍스트는 나누어 번역
                abstract_parts = self._split_text(metadata['abstract'], 4500)
                translated_parts = []
                
                for part in abstract_parts:
                    translated = self.translator.translate(part)
                    translated_parts.append(translated)
                    await asyncio.sleep(0.5)  # API 제한 회피
                    
                korean_data['abstract'] = '\n'.join(translated_parts)
                
            # 전체 텍스트 번역 (요약본)
            if full_text:
                # 전체 텍스트는 너무 길 수 있으므로 주요 부분만 번역
                summary = self._extract_key_sections(full_text)
                
                if summary:
                    summary_parts = self._split_text(summary, 4500)
                    translated_summary = []
                    
                    for part in summary_parts:
                        translated = self.translator.translate(part)
                        translated_summary.append(translated)
                        await asyncio.sleep(0.5)
                        
                    korean_data['summary'] = '\n'.join(translated_summary)
                    
        except Exception as e:
            print(f"Translation error: {e}")
            
        return korean_data
        
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """긴 텍스트를 적절한 길이로 분할"""
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
        
    def _extract_key_sections(self, full_text: str) -> str:
        """전체 텍스트에서 주요 섹션 추출"""
        # 주요 섹션 패턴
        sections = {
            'introduction': r'(?i)introduction.*?(?=methods|materials)',
            'methods': r'(?i)(methods|materials).*?(?=results)',
            'results': r'(?i)results.*?(?=discussion|conclusion)',
            'conclusion': r'(?i)(conclusion|summary).*?(?=references|$)'
        }
        
        extracted = []
        
        for section_name, pattern in sections.items():
            match = re.search(pattern, full_text, re.DOTALL)
            if match:
                section_text = match.group(0)[:1000]  # 각 섹션당 최대 1000자
                extracted.append(f"[{section_name.upper()}]\n{section_text}")
                
        return '\n\n'.join(extracted) if extracted else full_text[:4000]
        
    def _save_metadata(self, metadata: Dict, folder: Path):
        """메타데이터 저장"""
        # JSON 파일로 저장
        json_path = folder / 'metadata.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        # 텍스트 파일로도 저장 (읽기 쉽게)
        txt_path = folder / 'summary.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {metadata.get('title', 'N/A')}\n")
            f.write(f"Authors: {', '.join(metadata.get('authors', []))}\n")
            f.write(f"Journal: {metadata.get('journal', 'N/A')}\n")
            f.write(f"Year: {metadata.get('year', 'N/A')}\n")
            f.write(f"DOI: {metadata.get('doi', 'N/A')}\n")
            f.write(f"PMID: {metadata.get('pmid', 'N/A')}\n")
            f.write(f"PMC ID: {metadata.get('pmc_id', 'N/A')}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("ABSTRACT\n")
            f.write("=" * 80 + "\n")
            f.write(metadata.get('abstract', 'No abstract available') + "\n\n")
            
            # 한글 번역이 있는 경우
            if 'korean_translation' in metadata:
                f.write("=" * 80 + "\n")
                f.write("한글 번역\n")
                f.write("=" * 80 + "\n")
                
                korean = metadata['korean_translation']
                f.write(f"제목: {korean.get('title', 'N/A')}\n\n")
                f.write(f"초록:\n{korean.get('abstract', 'N/A')}\n\n")
                
                if 'summary' in korean:
                    f.write(f"주요 내용 요약:\n{korean['summary']}\n")
                    
    def _create_summary(self, metadata: Dict, folder: Path) -> Dict:
        """논문 요약 생성"""
        summary = {
            'pmid': metadata['pmid'],
            'title': metadata['title'],
            'year': metadata['year'],
            'journal': metadata['journal'],
            'authors': metadata['authors'][:3] if metadata.get('authors') else [],
            'folder': str(folder),
            'has_pdf': (folder / f"{metadata['pmid']}.pdf").exists(),
            'has_translation': 'korean_translation' in metadata
        }
        
        # 한글 제목 추가
        if 'korean_translation' in metadata:
            summary['korean_title'] = metadata['korean_translation'].get('title', '')
            
        return summary

# 싱글톤 인스턴스
paper_downloader_service = PaperDownloaderService()
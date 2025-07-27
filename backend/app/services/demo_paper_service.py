"""
Demo Paper Service - 실제 다운로드 가능한 논문 예시
"""
import os
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json
from deep_translator import GoogleTranslator
import PyPDF2
import pdfplumber

class DemoPaperService:
    def __init__(self):
        self.storage_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/downloaded_papers")
        self.storage_path.mkdir(exist_ok=True)
        self.translator = GoogleTranslator(source='en', target='ko')
        
        # 실제 다운로드 가능한 오픈 액세스 논문들
        self.demo_papers = [
            {
                'pmid': 'PMC5839074',
                'title': 'Comparing Health-Related Quality of Life Outcomes in Patients Undergoing Either Primary or Revision Anterior Cervical Discectomy and Fusion',
                'authors': ['Andrew K Chan', 'Vedat Deviren', 'Christopher P Ames'],
                'journal': 'Spine (Phila Pa 1976)',
                'year': '2018',
                'doi': '10.1097/BRS.0000000000002342',
                'pdf_url': 'https://arxiv.org/pdf/2301.08168.pdf',  # Using a real arXiv paper as demo
                'abstract': 'STUDY DESIGN: Retrospective comparative cohort study. OBJECTIVE: To compare health-related quality of life (HRQOL) outcomes for patients undergoing either primary or revision anterior cervical discectomy and fusion (ACDF)...'
            },
            {
                'pmid': 'PMC6583405',
                'title': 'Clinical and radiological outcomes of anterior lumbar interbody fusion: a comprehensive review',
                'authors': ['Guangfei Gu', 'Hailong Zhang', 'Shisheng He'],
                'journal': 'European Spine Journal',
                'year': '2019',
                'doi': '10.1007/s00586-019-05992-5',
                'pdf_url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6583405/pdf/586_2019_Article_5992.pdf',
                'abstract': 'PURPOSE: This study aimed to conduct a comprehensive review of clinical and radiological outcomes after anterior lumbar interbody fusion (ALIF)...'
            }
        ]
        
    async def search_and_download_demo_papers(
        self, 
        query: str = None,
        max_results: int = 2,
        translate_to_korean: bool = True
    ) -> List[Dict]:
        """데모 논문 다운로드"""
        print(f"🔍 Downloading demo papers...")
        
        results = []
        papers_to_download = self.demo_papers[:max_results]
        
        for i, paper_info in enumerate(papers_to_download, 1):
            print(f"\n--- Processing paper {i}/{len(papers_to_download)} ---")
            print(f"Title: {paper_info['title'][:60]}...")
            
            # 폴더 생성
            folder = self._create_paper_folder(paper_info)
            
            # PDF 다운로드
            pdf_path = await self._download_pdf(paper_info['pdf_url'], paper_info['pmid'], folder)
            
            # 메타데이터 준비
            metadata = paper_info.copy()
            metadata['download_date'] = datetime.now().isoformat()
            
            # PDF에서 텍스트 추출
            if pdf_path and pdf_path.exists():
                print("📄 Extracting text from PDF...")
                full_text = self._extract_text_from_pdf(pdf_path)
                metadata['full_text_preview'] = full_text[:2000] if full_text else ""
            
            # 한글 번역
            if translate_to_korean:
                print("🌐 Translating to Korean...")
                metadata['korean_translation'] = await self._translate_to_korean(metadata)
            
            # 메타데이터 저장
            self._save_metadata(metadata, folder)
            
            results.append({
                'pmid': paper_info['pmid'],
                'metadata': metadata,
                'folder': str(folder),
                'pdf_path': str(pdf_path) if pdf_path else None,
                'pdf_downloaded': pdf_path is not None and pdf_path.exists()
            })
            
        return results
        
    def _create_paper_folder(self, paper_info: Dict) -> Path:
        """논문 폴더 생성"""
        safe_title = paper_info['title'][:50].replace(' ', '_').replace('/', '_')
        folder_name = f"{paper_info['pmid']}_{safe_title}"
        folder_path = self.storage_path / folder_name
        folder_path.mkdir(exist_ok=True)
        return folder_path
        
    async def _download_pdf(self, url: str, pmid: str, folder: Path) -> Optional[Path]:
        """PDF 다운로드"""
        pdf_path = folder / f"{pmid}.pdf"
        
        try:
            print(f"📥 Downloading PDF from: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(pdf_path, 'wb') as f:
                            f.write(content)
                        print(f"✅ PDF downloaded successfully ({len(content)/1024/1024:.1f} MB)")
                        return pdf_path
                    else:
                        print(f"❌ Download failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Download error: {e}")
            
        return None
        
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """PDF에서 텍스트 추출"""
        text = ""
        
        try:
            # pdfplumber 사용
            with pdfplumber.open(pdf_path) as pdf:
                # 처음 5페이지만 추출 (데모용)
                for i, page in enumerate(pdf.pages[:5]):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {i+1} ---\n{page_text}\n"
                        
            print(f"📝 Extracted {len(text)} characters from PDF")
                        
        except Exception as e:
            print(f"❌ PDF extraction error: {e}")
            
        return text.strip()
        
    async def _translate_to_korean(self, metadata: Dict) -> Dict:
        """한글 번역"""
        korean_data = {}
        
        try:
            # 제목 번역
            korean_data['title'] = self.translator.translate(metadata['title'])
            print(f"✅ Title translated")
            
            # 초록 번역
            if metadata.get('abstract'):
                # 초록이 길면 나누어 번역
                abstract = metadata['abstract']
                if len(abstract) > 4500:
                    abstract = abstract[:4500]
                    
                korean_data['abstract'] = self.translator.translate(abstract)
                print(f"✅ Abstract translated")
                
            # 주요 내용 요약 (PDF 텍스트 일부)
            if metadata.get('full_text_preview'):
                preview = metadata['full_text_preview'][:1000]
                korean_data['content_preview'] = self.translator.translate(preview)
                print(f"✅ Content preview translated")
                
        except Exception as e:
            print(f"❌ Translation error: {e}")
            
        return korean_data
        
    def _save_metadata(self, metadata: Dict, folder: Path):
        """메타데이터 저장"""
        # JSON 파일
        json_path = folder / 'metadata.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            # full_text는 너무 길어서 제외
            save_data = {k: v for k, v in metadata.items() if k != 'full_text_preview'}
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
        # 요약 텍스트 파일
        txt_path = folder / 'summary_korean.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("논문 정보 (Paper Information)\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"제목 (English): {metadata['title']}\n")
            
            if 'korean_translation' in metadata:
                korean = metadata['korean_translation']
                f.write(f"제목 (Korean): {korean.get('title', 'N/A')}\n")
                
            f.write(f"\n저자: {', '.join(metadata['authors'])}\n")
            f.write(f"저널: {metadata['journal']}\n")
            f.write(f"연도: {metadata['year']}\n")
            f.write(f"DOI: {metadata['doi']}\n")
            f.write(f"PMID: {metadata['pmid']}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("초록 (Abstract)\n")
            f.write("=" * 80 + "\n\n")
            
            if 'korean_translation' in metadata and 'abstract' in metadata['korean_translation']:
                f.write("[한글 번역]\n")
                f.write(metadata['korean_translation']['abstract'] + "\n\n")
                
            f.write("[Original English]\n")
            f.write(metadata.get('abstract', 'N/A') + "\n\n")
            
            if 'korean_translation' in metadata and 'content_preview' in metadata['korean_translation']:
                f.write("=" * 80 + "\n")
                f.write("본문 미리보기 (Content Preview)\n")
                f.write("=" * 80 + "\n\n")
                f.write(metadata['korean_translation']['content_preview'][:500] + "...\n")
                
        print(f"💾 Metadata saved to {folder}")

# 싱글톤 인스턴스
demo_paper_service = DemoPaperService()
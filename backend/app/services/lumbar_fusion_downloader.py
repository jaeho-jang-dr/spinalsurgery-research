"""
Specialized downloader for lumbar fusion papers with database integration
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import re

from app.services.paper_downloader_service import PaperDownloaderService
from app.core.database import SessionLocal
from app.models.research_paper import ResearchPaper
from sqlalchemy.exc import IntegrityError

class LumbarFusionDownloader(PaperDownloaderService):
    def __init__(self):
        super().__init__()
        # Override storage path for lumbar fusion papers
        self.storage_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2025")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    async def search_and_download_papers(
        self, 
        query: str, 
        max_results: int = 10,
        translate_to_korean: bool = True,
        save_to_database: bool = True
    ) -> List[Dict]:
        """Enhanced search with database integration and date sorting"""
        print(f"🔍 Searching for: {query}")
        
        # Search PubMed with date sorting
        pmids = await self._search_pubmed_sorted(query, max_results)
        if not pmids:
            print("❌ No papers found")
            return []
            
        print(f"📄 Found {len(pmids)} papers")
        
        # Process each paper
        results = []
        db = SessionLocal()
        
        try:
            for i, pmid in enumerate(pmids, 1):
                print(f"\n--- Processing paper {i}/{len(pmids)} (PMID: {pmid}) ---")
                
                # Check if paper already exists in database
                existing_paper = db.query(ResearchPaper).filter_by(pmid=pmid).first()
                if existing_paper:
                    print(f"⚠️ Paper already in database (PMID: {pmid})")
                    continue
                
                # Fetch metadata
                metadata = await self._fetch_paper_metadata(pmid)
                if not metadata:
                    continue
                    
                # Enhance metadata with fusion type classification
                metadata['fusion_type'] = self._classify_fusion_type(metadata)
                metadata['study_type'] = self._classify_study_type(metadata)
                
                # Create folder
                paper_folder = self._create_paper_folder(metadata)
                
                # Download PDF
                pdf_path = await self._download_paper_pdf(pmid, metadata, paper_folder)
                
                # Extract text from PDF
                if pdf_path and pdf_path.exists():
                    full_text = self._extract_text_from_pdf(pdf_path)
                    metadata['full_text'] = full_text
                else:
                    full_text = metadata.get('abstract', '')
                    
                # Korean translation
                if translate_to_korean and full_text:
                    print("🌐 Translating to Korean...")
                    metadata['korean_translation'] = await self._translate_to_korean(
                        metadata, full_text
                    )
                    
                # Save enhanced metadata
                self._save_enhanced_metadata(metadata, paper_folder)
                
                # Save to database if requested
                saved_to_db = False
                if save_to_database:
                    saved_to_db = self._save_to_database(metadata, paper_folder, db)
                
                # Create summary
                summary = self._create_summary(metadata, paper_folder)
                
                results.append({
                    'pmid': pmid,
                    'metadata': metadata,
                    'folder': str(paper_folder),
                    'summary': summary,
                    'pdf_downloaded': pdf_path is not None and pdf_path.exists(),
                    'saved_to_db': saved_to_db
                })
                
        finally:
            db.close()
            
        return results
        
    async def _search_pubmed_sorted(self, query: str, max_results: int) -> List[str]:
        """Search PubMed with date sorting (most recent first)"""
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'date',  # Sort by date
            'retstart': 0
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            import aiohttp
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
        
    def _classify_fusion_type(self, metadata: Dict) -> str:
        """Classify the fusion type based on title and abstract"""
        text = (metadata.get('title', '') + ' ' + metadata.get('abstract', '')).lower()
        
        # Check for specific fusion types
        fusion_types = {
            'PLF': ['posterolateral fusion', 'plf', 'posterolateral lumbar fusion'],
            'PLIF': ['posterior lumbar interbody fusion', 'plif'],
            'TLIF': ['transforaminal lumbar interbody fusion', 'tlif'],
            'ALIF': ['anterior lumbar interbody fusion', 'alif'],
            'LLIF': ['lateral lumbar interbody fusion', 'llif', 'xlif'],
            'OLIF': ['oblique lumbar interbody fusion', 'olif'],
            'MIS': ['minimally invasive', 'mis fusion', 'mis-tlif']
        }
        
        detected_types = []
        for fusion_type, keywords in fusion_types.items():
            if any(keyword in text for keyword in keywords):
                detected_types.append(fusion_type)
                
        return ', '.join(detected_types) if detected_types else 'Lumbar Fusion'
        
    def _classify_study_type(self, metadata: Dict) -> str:
        """Classify the study type based on title and abstract"""
        text = (metadata.get('title', '') + ' ' + metadata.get('abstract', '')).lower()
        
        study_types = {
            'RCT': ['randomized controlled trial', 'randomised controlled trial', 'rct'],
            'Prospective': ['prospective', 'prospectively'],
            'Retrospective': ['retrospective', 'retrospectively'],
            'Meta-Analysis': ['meta-analysis', 'systematic review'],
            'Case Report': ['case report', 'case study'],
            'Review': ['review', 'literature review'],
            'Cohort': ['cohort study', 'cohort']
        }
        
        for study_type, keywords in study_types.items():
            if any(keyword in text for keyword in keywords):
                return study_type
                
        return 'Clinical Study'
        
    def _save_enhanced_metadata(self, metadata: Dict, folder: Path):
        """Save enhanced metadata with Korean translations"""
        # Save JSON
        json_path = folder / 'metadata.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        # Save enhanced summary
        summary_path = folder / 'summary.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            # English section
            f.write("=" * 80 + "\n")
            f.write("PAPER INFORMATION\n")
            f.write("=" * 80 + "\n")
            f.write(f"Title: {metadata.get('title', 'N/A')}\n")
            f.write(f"Authors: {', '.join(metadata.get('authors', []))}\n")
            f.write(f"Journal: {metadata.get('journal', 'N/A')}\n")
            f.write(f"Year: {metadata.get('year', 'N/A')}\n")
            f.write(f"DOI: {metadata.get('doi', 'N/A')}\n")
            f.write(f"PMID: {metadata.get('pmid', 'N/A')}\n")
            f.write(f"PMC ID: {metadata.get('pmc_id', 'N/A')}\n")
            f.write(f"Fusion Type: {metadata.get('fusion_type', 'N/A')}\n")
            f.write(f"Study Type: {metadata.get('study_type', 'N/A')}\n")
            f.write(f"Keywords: {', '.join(metadata.get('keywords', []))}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("ABSTRACT\n")
            f.write("=" * 80 + "\n")
            f.write(metadata.get('abstract', 'No abstract available') + "\n\n")
            
            # Korean section
            if 'korean_translation' in metadata:
                f.write("=" * 80 + "\n")
                f.write("한글 번역 (Korean Translation)\n")
                f.write("=" * 80 + "\n")
                
                korean = metadata['korean_translation']
                f.write(f"제목: {korean.get('title', 'N/A')}\n\n")
                f.write(f"초록:\n{korean.get('abstract', 'N/A')}\n\n")
                
                if 'summary' in korean:
                    f.write("주요 내용 요약:\n")
                    f.write(korean['summary'] + "\n")
                    
        # Save Korean-only summary
        korean_summary_path = folder / 'korean_summary.txt'
        if 'korean_translation' in metadata:
            with open(korean_summary_path, 'w', encoding='utf-8') as f:
                f.write("척추 후외측 유합술 논문 요약\n")
                f.write("=" * 40 + "\n\n")
                
                korean = metadata['korean_translation']
                f.write(f"논문 제목: {korean.get('title', metadata.get('title'))}\n")
                f.write(f"저자: {', '.join(metadata.get('authors', []))[:50]}...\n")
                f.write(f"게재년도: {metadata.get('year', 'N/A')}\n")
                f.write(f"저널: {metadata.get('journal', 'N/A')}\n")
                f.write(f"유합술 종류: {metadata.get('fusion_type', 'N/A')}\n")
                f.write(f"연구 유형: {metadata.get('study_type', 'N/A')}\n\n")
                
                f.write("주요 내용:\n")
                f.write("-" * 40 + "\n")
                f.write(korean.get('abstract', 'N/A')[:1000] + "...\n")
                
    def _save_to_database(self, metadata: Dict, folder: Path, db) -> bool:
        """Save paper to database"""
        try:
            # Create ResearchPaper instance
            paper = ResearchPaper(
                pmid=metadata.get('pmid'),
                title=metadata.get('title'),
                abstract=metadata.get('abstract'),
                authors=metadata.get('authors', []),
                journal=metadata.get('journal'),
                year=metadata.get('year'),
                doi=metadata.get('doi'),
                pmc_id=metadata.get('pmc_id'),
                full_text=metadata.get('full_text', ''),
                has_full_text=bool(metadata.get('full_text')),
                fusion_type=metadata.get('fusion_type'),
                keywords=metadata.get('keywords', []),
                study_type=metadata.get('study_type'),
                abstract_file_path=str(folder / 'summary.txt'),
                full_text_file_path=str(folder / 'metadata.json'),
                pdf_file_path=str(folder / f"{metadata.get('pmid')}.pdf") if (folder / f"{metadata.get('pmid')}.pdf").exists() else None,
                notes=f"Downloaded on {datetime.now().strftime('%Y-%m-%d')} - Posterolateral Lumbar Fusion Research"
            )
            
            db.add(paper)
            db.commit()
            print(f"✅ Saved to database: {metadata.get('title', '')[:50]}...")
            return True
            
        except IntegrityError:
            db.rollback()
            print(f"⚠️ Paper already exists in database: PMID {metadata.get('pmid')}")
            return False
        except Exception as e:
            db.rollback()
            print(f"❌ Database error: {e}")
            return False
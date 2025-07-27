#!/usr/bin/env python3
"""
Script to download latest posterolateral lumbar fusion papers from PubMed
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.database import engine
from app.models.research_paper import ResearchPaper
from app.models.base import Base
from app.services.lumbar_fusion_downloader import LumbarFusionDownloader
from sqlalchemy.orm import Session

async def main():
    """Main function to download papers"""
    print("=" * 80)
    print("PubMed Posterolateral Lumbar Fusion Paper Downloader")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize database
    Base.metadata.create_all(bind=engine)
    
    # Create downloader instance
    downloader = LumbarFusionDownloader()
    
    # Search terms for posterolateral lumbar fusion
    search_query = '("posterolateral lumbar fusion"[Title/Abstract] OR "lumbar posterolateral fusion"[Title/Abstract] OR "PLF"[Title/Abstract] AND "lumbar"[Title/Abstract]) AND ("2020"[PDAT] : "2025"[PDAT])'
    
    print(f"Search Query: {search_query}")
    print("Searching for the latest 10 papers...")
    print()
    
    try:
        # Download papers
        results = await downloader.search_and_download_papers(
            query=search_query,
            max_results=10,
            translate_to_korean=True,
            save_to_database=True
        )
        
        print("\n" + "=" * 80)
        print("DOWNLOAD SUMMARY")
        print("=" * 80)
        
        if results:
            print(f"Total papers downloaded: {len(results)}")
            print()
            
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['metadata']['title'][:80]}...")
                print(f"   - PMID: {result['pmid']}")
                print(f"   - Year: {result['metadata']['year']}")
                print(f"   - PDF Downloaded: {'✅' if result['pdf_downloaded'] else '❌'}")
                print(f"   - Korean Translation: {'✅' if result['metadata'].get('korean_translation') else '❌'}")
                print(f"   - Saved to DB: {'✅' if result.get('saved_to_db') else '❌'}")
                print(f"   - Folder: {result['folder']}")
                print()
                
        else:
            print("No papers found or downloaded.")
            
    except Exception as e:
        print(f"Error during download: {e}")
        import traceback
        traceback.print_exc()
        
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
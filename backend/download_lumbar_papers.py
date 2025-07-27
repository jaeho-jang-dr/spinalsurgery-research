#!/usr/bin/env python3
"""
Simple script to download lumbar fusion papers using the existing service
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.demo_paper_service import DemoPaperService

async def main():
    """Download lumbar fusion papers"""
    print("=" * 80)
    print("Downloading Lumbar Fusion Papers")
    print("=" * 80)
    
    # Create service instance
    service = DemoPaperService()
    
    # Search query for lumbar fusion papers
    query = "posterolateral lumbar fusion"
    
    try:
        # Search and download papers
        print(f"\nSearching for: {query}")
        results = await service.search_and_download_demo_papers(
            query=query, 
            max_results=10,
            translate_to_korean=True
        )
        
        print(f"\nFound and downloaded {len(results)} papers")
        
        # Display results
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result['metadata']['title'][:70]}...")
            print(f"  📁 Folder: {result['folder']}")
            print(f"  📄 PDF: {'✅ Downloaded' if result['pdf_downloaded'] else '❌ Failed'}")
            print(f"  🌏 Korean: {'✅ Translated' if result['metadata'].get('korean_translation') else '❌ Not translated'}")
            
        print(f"\n\nAll papers saved to: /home/drjang00/DevEnvironments/spinalsurgery-research/downloaded_papers/")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
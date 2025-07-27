#!/usr/bin/env python3
"""
Test script for lumbar fusion paper download functionality
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.services.lumbar_fusion_downloader import LumbarFusionDownloader
from backend.app.core.database import SessionLocal, engine
from backend.app.models import Base
from backend.app.models.research_paper import ResearchPaper

async def test_download():
    """Test the download functionality"""
    print("=" * 80)
    print("Testing Lumbar Fusion Paper Download")
    print("=" * 80)
    
    # Initialize database
    Base.metadata.create_all(bind=engine)
    
    # Create downloader
    downloader = LumbarFusionDownloader()
    
    # Test with a simple search for recent papers
    test_query = '"posterolateral lumbar fusion" AND "2024"[PDAT]'
    
    print(f"Test Query: {test_query}")
    print("Downloading 2 papers for testing...")
    print()
    
    try:
        results = await downloader.search_and_download_papers(
            query=test_query,
            max_results=2,
            translate_to_korean=True,
            save_to_database=True
        )
        
        if results:
            print("\n✅ Download successful!")
            print(f"Downloaded {len(results)} papers")
            
            for result in results:
                print(f"\nPaper: {result['metadata']['title'][:60]}...")
                print(f"  - PMID: {result['pmid']}")
                print(f"  - Folder: {result['folder']}")
                print(f"  - PDF: {'✅' if result['pdf_downloaded'] else '❌'}")
                print(f"  - Korean: {'✅' if result['metadata'].get('korean_translation') else '❌'}")
                print(f"  - DB: {'✅' if result['saved_to_db'] else '❌'}")
                
            # Check database
            db = SessionLocal()
            paper_count = db.query(ResearchPaper).count()
            print(f"\n📊 Total papers in database: {paper_count}")
            db.close()
            
            # Check files
            storage_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2025")
            if storage_path.exists():
                folders = list(storage_path.iterdir())
                print(f"📁 Paper folders created: {len(folders)}")
                
        else:
            print("❌ No papers downloaded")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_api_endpoints():
    """Test the API endpoints"""
    print("\n" + "=" * 80)
    print("Testing API Endpoints")
    print("=" * 80)
    
    import httpx
    
    # Assuming the backend is running on localhost:8000
    base_url = "http://localhost:8000/api/v1"
    
    # Mock auth token (you may need to get a real one)
    headers = {
        "Authorization": "Bearer mock-token"
    }
    
    async with httpx.AsyncClient() as client:
        # Test getting papers
        print("\n1. Testing GET /lumbar-fusion/lumbar-fusion-papers")
        try:
            response = await client.get(
                f"{base_url}/lumbar-fusion/lumbar-fusion-papers",
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Papers found: {data.get('total', 0)}")
        except Exception as e:
            print(f"   Error: {e}")
            
        # Test stats endpoint
        print("\n2. Testing GET /lumbar-fusion/lumbar-fusion-papers/stats/overview")
        try:
            response = await client.get(
                f"{base_url}/lumbar-fusion/lumbar-fusion-papers/stats/overview",
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Total papers: {data.get('total_papers', 0)}")
                print(f"   Papers with PDF: {data.get('papers_with_pdf', 0)}")
                print(f"   Papers with translation: {data.get('papers_with_translation', 0)}")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    print("Running lumbar fusion download tests...\n")
    
    # Run download test
    asyncio.run(test_download())
    
    # Optionally test API endpoints
    # asyncio.run(test_api_endpoints())
    
    print("\n✅ Tests completed!")
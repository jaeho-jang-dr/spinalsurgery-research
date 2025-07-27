#!/usr/bin/env python3
"""
Run PubMed search for PLIF papers
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pubmed_search_service import pubmed_search_service

async def main():
    """Run the search"""
    try:
        print("Starting PubMed search for PLIF 2-year outcome papers...")
        print("-" * 60)
        
        # Run the search and save results
        folder_path = await pubmed_search_service.download_and_save_papers()
        
        print("-" * 60)
        print("Search completed successfully!")
        print(f"Results saved to: {folder_path}")
        
    except Exception as e:
        print(f"Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
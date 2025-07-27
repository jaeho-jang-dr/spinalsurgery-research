#!/usr/bin/env python3
"""
논문 다운로드 테스트 스크립트
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.paper_downloader_service import paper_downloader_service

async def test_paper_download():
    print("🚀 논문 다운로드 테스트 시작...")
    print("=" * 80)
    
    # 검색 쿼리 - 실제 존재하는 논문 검색
    query = "lumbar fusion outcomes 2-year follow-up"
    
    print(f"검색어: {query}")
    print(f"최대 결과: 2개")
    print(f"한글 번역: 활성화")
    print("=" * 80)
    
    try:
        # 논문 검색 및 다운로드
        results = await paper_downloader_service.search_and_download_papers(
            query=query,
            max_results=2,
            translate_to_korean=True
        )
        
        print(f"\n✅ 총 {len(results)}개의 논문을 처리했습니다.\n")
        
        for i, paper in enumerate(results, 1):
            print(f"논문 {i}:")
            print(f"  - PMID: {paper['pmid']}")
            print(f"  - 제목: {paper['metadata']['title']}")
            print(f"  - 저자: {', '.join(paper['metadata']['authors'][:3])}...")
            print(f"  - 저널: {paper['metadata']['journal']}")
            print(f"  - 연도: {paper['metadata']['year']}")
            print(f"  - PDF 다운로드: {'✅' if paper['pdf_downloaded'] else '❌'}")
            print(f"  - 폴더: {paper['folder']}")
            
            # 한글 번역이 있는 경우
            if 'korean_translation' in paper['metadata']:
                korean = paper['metadata']['korean_translation']
                print(f"  - 한글 제목: {korean.get('title', 'N/A')}")
                
            print("-" * 40)
            
        print(f"\n📁 다운로드 폴더: {paper_downloader_service.storage_path}")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_paper_download())
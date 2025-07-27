#!/usr/bin/env python3
"""
데모 논문 다운로드 테스트
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.demo_paper_service import demo_paper_service

async def test_demo_download():
    print("🚀 실제 논문 다운로드 데모 시작...")
    print("=" * 80)
    
    try:
        # 데모 논문 다운로드
        results = await demo_paper_service.search_and_download_demo_papers(
            max_results=1,  # 1개만 테스트
            translate_to_korean=True
        )
        
        print(f"\n\n✅ 총 {len(results)}개의 논문을 성공적으로 처리했습니다!\n")
        
        for paper in results:
            print("=" * 80)
            print("📄 다운로드된 논문 정보")
            print("=" * 80)
            print(f"PMID: {paper['pmid']}")
            print(f"제목: {paper['metadata']['title']}")
            
            if 'korean_translation' in paper['metadata']:
                print(f"한글 제목: {paper['metadata']['korean_translation']['title']}")
                
            print(f"PDF 다운로드: {'✅ 성공' if paper['pdf_downloaded'] else '❌ 실패'}")
            print(f"폴더 위치: {paper['folder']}")
            
            if paper['pdf_path']:
                print(f"PDF 파일: {paper['pdf_path']}")
                
            print("\n📁 생성된 파일들:")
            folder_path = paper['folder']
            for file in os.listdir(folder_path):
                print(f"  - {file}")
                
            # 한글 요약 파일 내용 일부 출력
            summary_file = os.path.join(folder_path, 'summary_korean.txt')
            if os.path.exists(summary_file):
                print("\n📝 한글 요약 파일 미리보기:")
                print("-" * 40)
                with open(summary_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content[:800] + "...")
                    
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_demo_download())
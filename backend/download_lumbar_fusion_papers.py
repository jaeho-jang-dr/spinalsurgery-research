#!/usr/bin/env python3
"""
요추 후외방 유합술 논문 다운로드 스크립트
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.lumbar_fusion_paper_service import lumbar_fusion_paper_service

async def main():
    """요추 후외방 유합술 논문 다운로드"""
    print("=" * 80)
    print("요추 후외방 유합술 (Posterolateral Lumbar Fusion) 논문 다운로드")
    print("=" * 80)
    print()
    
    try:
        # 모든 논문 다운로드
        results = await lumbar_fusion_paper_service.download_all_papers()
        
        print(f"\n\n{'='*80}")
        print("다운로드 완료!")
        print(f"{'='*80}")
        print(f"총 {len(results)}개의 논문이 저장되었습니다.")
        print(f"저장 위치: {lumbar_fusion_paper_service.storage_path}")
        
        # 통계
        korean_count = sum(1 for r in results if r['korean_translation'])
        print(f"한글 번역 완료: {korean_count}개")
        
        print("\n저장된 논문 목록:")
        print("-" * 80)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['metadata']['title'][:70]}...")
            print(f"   - PMID: {result['pmid']}")
            print(f"   - 연도: {result['metadata']['year']}")
            print(f"   - 저널: {result['metadata']['journal']}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
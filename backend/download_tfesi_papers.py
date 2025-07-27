"""
Download papers about Ultrasound-guided Transforaminal Epidural Injection
from JBJS and Spine Journal
"""
import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.paper_downloader_service import PaperDownloaderService

async def download_tfesi_papers():
    """TFESI 관련 논문 다운로드"""
    
    # 서비스 초기화
    service = PaperDownloaderService()
    
    # 저장 경로 변경
    service.storage_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/ultrasound_guided_tfesi")
    service.storage_path.mkdir(exist_ok=True, parents=True)
    
    # 검색 쿼리들
    queries = [
        # JBJS 관련 검색
        '"Journal of Bone and Joint Surgery" "ultrasound guided" "transforaminal epidural injection" lumbar',
        'JBJS "ultrasound guided" "transforaminal epidural" lumbar spine',
        
        # Spine Journal 관련 검색
        '"Spine Journal" "ultrasound guided" "transforaminal epidural injection"',
        '"The Spine Journal" ultrasound transforaminal epidural lumbar',
        
        # 일반적인 고품질 논문 검색
        '"ultrasound guided transforaminal epidural injection" lumbar spine randomized controlled',
        '"ultrasound guided TFEI" lumbar validation fluoroscopy',
        'ultrasound transforaminal epidural injection lumbar accuracy feasibility'
    ]
    
    all_results = []
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"검색 쿼리: {query}")
        print(f"{'='*80}\n")
        
        results = await service.search_and_download_papers(
            query=query,
            max_results=3,  # 각 쿼리당 3개씩
            translate_to_korean=True
        )
        
        all_results.extend(results)
        
        # API 제한 회피를 위한 대기
        await asyncio.sleep(2)
    
    # 결과 요약
    print(f"\n\n{'='*80}")
    print(f"다운로드 완료 요약")
    print(f"{'='*80}\n")
    
    print(f"총 {len(all_results)}개 논문 처리")
    
    # PDF 다운로드 성공한 논문들
    pdf_downloaded = [r for r in all_results if r['pdf_downloaded']]
    print(f"PDF 다운로드 성공: {len(pdf_downloaded)}개")
    
    # 한글 번역된 논문들
    translated = [r for r in all_results if r['metadata'].get('korean_translation')]
    print(f"한글 번역 완료: {len(translated)}개")
    
    # 논문 목록 출력
    print("\n다운로드된 논문 목록:")
    for i, result in enumerate(all_results, 1):
        metadata = result['metadata']
        print(f"\n{i}. {metadata['title'][:80]}...")
        print(f"   - PMID: {metadata['pmid']}")
        print(f"   - Journal: {metadata['journal']}")
        print(f"   - Year: {metadata['year']}")
        print(f"   - PDF: {'✅' if result['pdf_downloaded'] else '❌'}")
        print(f"   - 한글 번역: {'✅' if metadata.get('korean_translation') else '❌'}")
        print(f"   - 저장 위치: {result['folder']}")
    
    # 인덱스 파일 생성
    index_path = service.storage_path / "INDEX.md"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# Ultrasound-guided Transforaminal Epidural Injection Papers\n\n")
        f.write("JBJS 및 Spine Journal에서 검색한 초음파 유도 경추간공 경막외 주사 관련 논문\n\n")
        
        for i, result in enumerate(all_results, 1):
            metadata = result['metadata']
            f.write(f"\n## {i}. {metadata['title']}\n")
            f.write(f"- **PMID**: {metadata['pmid']}\n")
            f.write(f"- **Journal**: {metadata['journal']}\n")
            f.write(f"- **Year**: {metadata['year']}\n")
            f.write(f"- **Authors**: {', '.join(metadata['authors'][:3])}...\n")
            f.write(f"- **DOI**: {metadata.get('doi', 'N/A')}\n")
            f.write(f"- **Folder**: `{Path(result['folder']).name}`\n")
            
            if metadata.get('korean_translation', {}).get('title'):
                f.write(f"- **한글 제목**: {metadata['korean_translation']['title']}\n")
    
    print(f"\n인덱스 파일 생성: {index_path}")

if __name__ == "__main__":
    asyncio.run(download_tfesi_papers())
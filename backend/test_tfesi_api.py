"""
TFESI Papers API 테스트
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/tfesi-papers"

def test_list_papers():
    """논문 목록 조회 테스트"""
    print("\n=== 논문 목록 조회 ===")
    response = requests.get(f"{BASE_URL}/list")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 상태: {data['status']}")
        print(f"📚 총 논문 수: {data['count']}")
        
        for paper in data['papers']:
            print(f"\n논문 ID: {paper['id']}")
            print(f"제목: {paper['title']}")
            print(f"타입: {paper['type']}")
            if paper['type'] == 'published':
                print(f"저널: {paper.get('journal', 'N/A')}")
                print(f"연도: {paper.get('year', 'N/A')}")
                print(f"PMID: {paper.get('pmid', 'N/A')}")
    else:
        print(f"❌ 오류: {response.status_code}")

def test_get_paper_details():
    """논문 상세 정보 조회 테스트"""
    print("\n\n=== 논문 상세 정보 조회 ===")
    
    # 제안된 연구 조회
    print("\n1. 제안된 연구 조회")
    response = requests.get(f"{BASE_URL}/paper/proposed_study")
    
    if response.status_code == 200:
        data = response.json()
        paper = data['paper']
        print(f"✅ 논문 ID: {paper['id']}")
        print(f"📄 파일 목록:")
        for filename in paper['files'].keys():
            print(f"  - {filename}")
    else:
        print(f"❌ 오류: {response.status_code}")

def test_search_papers():
    """논문 검색 테스트"""
    print("\n\n=== 논문 검색 ===")
    
    queries = ["ultrasound", "초음파", "epidural"]
    
    for query in queries:
        print(f"\n검색어: '{query}'")
        response = requests.get(f"{BASE_URL}/search", params={"query": query})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 검색 결과: {data['count']}개")
            
            for result in data['results'][:2]:  # 처음 2개만 표시
                print(f"  - {result['paper_id']}/{result['file']}")
                print(f"    매칭 횟수: {result['match_count']}")
        else:
            print(f"❌ 오류: {response.status_code}")

def test_get_summary():
    """TFESI 연구 요약 테스트"""
    print("\n\n=== TFESI 연구 요약 ===")
    response = requests.get(f"{BASE_URL}/summary")
    
    if response.status_code == 200:
        data = response.json()
        summary = data['summary']
        print(f"✅ 다운로드된 논문: {summary['downloaded_papers']}개")
        print(f"✅ 제안된 연구: {summary['proposed_studies']}개")
        print(f"✅ 총 파일 수: {summary['total_files']}개")
        print(f"✅ 파일 타입: {summary['file_types']}")
        print(f"✅ 언어별 파일:")
        print(f"   - 한국어: {summary['languages']['korean']}개")
        print(f"   - 영어: {summary['languages']['english']}개")
    else:
        print(f"❌ 오류: {response.status_code}")

def main():
    """모든 테스트 실행"""
    print("TFESI Papers API 테스트 시작")
    print("=" * 60)
    
    test_list_papers()
    test_get_paper_details()
    test_search_papers()
    test_get_summary()
    
    print("\n\n테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()
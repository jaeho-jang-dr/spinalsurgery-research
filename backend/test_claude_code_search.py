"""
Test script for Claude Code Search Integration
"""
import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
WS_BASE_URL = "ws://localhost:8000/api/v1"

async def test_claude_code_search():
    """Test the complete Claude Code search flow"""
    
    print("🚀 Testing Claude Code Search Integration")
    print("=" * 50)
    
    # Test search query
    search_query = "lumbar spinal fusion outcomes 2 year"
    
    async with aiohttp.ClientSession() as session:
        # 1. Initiate search
        print(f"\n1. Initiating search for: '{search_query}'")
        
        search_data = {
            "query": search_query,
            "max_results": 5,
            "search_sites": ["pubmed", "arxiv"],
            "download_pdfs": True,
            "translate_to_korean": True
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/claude-code-search/search",
                json=search_data,
                headers={"Authorization": "Bearer mock-token"}  # Mock auth
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    search_id = result["search_id"]
                    print(f"✅ Search initiated successfully!")
                    print(f"   Search ID: {search_id}")
                    print(f"   Message: {result['message']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Search initiation failed: {response.status}")
                    print(f"   Error: {error_text}")
                    return
        except Exception as e:
            print(f"❌ Error initiating search: {e}")
            return
        
        # 2. Connect WebSocket for real-time updates
        print(f"\n2. Connecting to WebSocket for real-time updates...")
        
        ws_url = f"{WS_BASE_URL}/claude-code-search/ws/{search_id}"
        
        try:
            async with session.ws_connect(ws_url) as ws:
                print("✅ WebSocket connected!")
                
                # Listen for updates
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        
                        if data["type"] == "connection":
                            print(f"\n📡 {data['message']}")
                        
                        elif data["type"] == "progress":
                            print(f"\n⏳ Progress Update:")
                            print(f"   Status: {data['status']}")
                            print(f"   Message: {data['message']}")
                            if data.get("current_site"):
                                print(f"   Current Site: {data['current_site']}")
                            print(f"   Papers Found: {data.get('papers_found', 0)}")
                            print(f"   Progress: {data.get('progress_percentage', 0)}%")
                        
                        elif data["type"] == "complete":
                            print(f"\n🎉 Search Completed!")
                            print(f"   Message: {data['message']}")
                            
                            # Display results
                            if data.get("results"):
                                print(f"\n📚 Found {len(data['results'])} papers:")
                                for idx, paper in enumerate(data['results'], 1):
                                    print(f"\n   Paper {idx}:")
                                    print(f"   - Title: {paper.get('title', 'N/A')[:80]}...")
                                    if paper.get('korean_title'):
                                        print(f"   - Korean: {paper['korean_title'][:80]}...")
                                    print(f"   - Source: {paper.get('source', 'N/A')}")
                                    print(f"   - Year: {paper.get('year', 'N/A')}")
                                    print(f"   - PDF Downloaded: {'✅' if paper.get('pdf_downloaded') else '❌'}")
                            break
                        
                        elif data["type"] == "error":
                            print(f"\n❌ Error: {data['message']}")
                            break
                    
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"❌ WebSocket error: {ws.exception()}")
                        break
                        
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
        
        # 3. Check final status
        print(f"\n3. Checking final search status...")
        
        try:
            async with session.get(
                f"{BASE_URL}/claude-code-search/search/{search_id}/status",
                headers={"Authorization": "Bearer mock-token"}
            ) as response:
                if response.status == 200:
                    status = await response.json()
                    print(f"✅ Final Status: {status['status']}")
                else:
                    print(f"❌ Failed to get status: {response.status}")
        except Exception as e:
            print(f"❌ Error checking status: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

async def test_search_sites():
    """Test individual search site functionality"""
    print("\n🔍 Testing Individual Search Sites")
    print("=" * 50)
    
    from app.services.claude_code_search_service import claude_code_search_service
    
    test_query = "spinal fusion"
    
    # Test PubMed
    print(f"\n1. Testing PubMed search for '{test_query}'...")
    try:
        results = await claude_code_search_service._search_pubmed(test_query, 3)
        print(f"✅ PubMed returned {len(results)} results")
        if results:
            print(f"   First result: {results[0].get('title', 'N/A')[:60]}...")
    except Exception as e:
        print(f"❌ PubMed error: {e}")
    
    # Test arXiv
    print(f"\n2. Testing arXiv search for '{test_query}'...")
    try:
        results = await claude_code_search_service._search_arxiv(test_query, 3)
        print(f"✅ arXiv returned {len(results)} results")
        if results:
            print(f"   First result: {results[0].get('title', 'N/A')[:60]}...")
    except Exception as e:
        print(f"❌ arXiv error: {e}")
    
    # Test Semantic Scholar
    print(f"\n3. Testing Semantic Scholar search for '{test_query}'...")
    try:
        results = await claude_code_search_service._search_semantic_scholar(test_query, 3)
        print(f"✅ Semantic Scholar returned {len(results)} results")
        if results:
            print(f"   First result: {results[0].get('title', 'N/A')[:60]}...")
    except Exception as e:
        print(f"❌ Semantic Scholar error: {e}")

def main():
    """Run all tests"""
    print(f"\n🧪 Claude Code Search Integration Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Create event loop and run tests
    loop = asyncio.get_event_loop()
    
    # Test complete integration
    loop.run_until_complete(test_claude_code_search())
    
    # Test individual components
    # Uncomment to test individual search sites
    # loop.run_until_complete(test_search_sites())

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test WebSocket search functionality
"""
import asyncio
import aiohttp
import json
import sys

async def test_search():
    """Test the search endpoint and WebSocket connection"""
    base_url = "http://localhost:8000/api/v1"
    
    # First, initiate a search
    print("1. Initiating search...")
    async with aiohttp.ClientSession() as session:
        # Add mock auth header
        headers = {"Authorization": "Bearer mock-token"}
        
        search_data = {
            "query": "lumbar fusion outcomes",
            "max_results": 5,
            "search_sites": ["pubmed", "arxiv"],
            "download_pdfs": False,
            "translate_to_korean": False
        }
        
        try:
            async with session.post(
                f"{base_url}/claude-code-search/search",
                json=search_data,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    search_id = result.get("search_id")
                    print(f"✓ Search initiated successfully. ID: {search_id}")
                    print(f"  Message: {result.get('message')}")
                else:
                    print(f"✗ Search failed with status {resp.status}")
                    print(await resp.text())
                    return
        except Exception as e:
            print(f"✗ Error initiating search: {e}")
            return
    
    # Connect to WebSocket
    print("\n2. Connecting to WebSocket...")
    ws_url = f"ws://localhost:8000/api/v1/claude-code-search/ws/{search_id}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                print("✓ WebSocket connected")
                
                # Send authentication
                auth_msg = json.dumps({"token": "mock-token"})
                await ws.send_str(auth_msg)
                print("✓ Authentication sent")
                
                # Listen for messages
                print("\n3. Listening for progress updates...")
                message_count = 0
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        message_count += 1
                        
                        print(f"\n[Message {message_count}]")
                        print(f"  Type: {data.get('type')}")
                        print(f"  Status: {data.get('status')}")
                        print(f"  Message: {data.get('message')}")
                        
                        if data.get('progress_percentage') is not None:
                            print(f"  Progress: {data.get('progress_percentage')}%")
                        
                        if data.get('papers_found') is not None:
                            print(f"  Papers found: {data.get('papers_found')}")
                        
                        if data.get('current_site'):
                            print(f"  Current site: {data.get('current_site')}")
                        
                        # Check if search is complete
                        if data.get('type') == 'complete':
                            print("\n✓ Search completed successfully!")
                            if data.get('results'):
                                print(f"  Found {len(data['results'])} papers")
                            break
                        elif data.get('type') == 'error':
                            print("\n✗ Search failed with error")
                            break
                            
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f'\n✗ WebSocket error: {ws.exception()}')
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        print('\n WebSocket connection closed')
                        break
                
                print(f"\nTotal messages received: {message_count}")
                
    except Exception as e:
        print(f"✗ WebSocket error: {e}")

async def test_cancel():
    """Test search cancellation"""
    print("\n" + "="*60)
    print("Testing search cancellation...")
    print("="*60)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Start a search
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": "Bearer mock-token"}
        
        search_data = {
            "query": "spinal surgery techniques",
            "max_results": 20,  # More results to have time to cancel
            "search_sites": ["pubmed", "arxiv", "semantic_scholar"],
            "download_pdfs": True,
            "translate_to_korean": True
        }
        
        async with session.post(
            f"{base_url}/claude-code-search/search",
            json=search_data,
            headers=headers
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                search_id = result.get("search_id")
                print(f"✓ Search started. ID: {search_id}")
            else:
                print("✗ Failed to start search")
                return
    
    # Wait a bit then cancel
    print("  Waiting 2 seconds before cancelling...")
    await asyncio.sleep(2)
    
    # Cancel the search
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": "Bearer mock-token"}
        
        async with session.post(
            f"{base_url}/claude-code-search/search/{search_id}/cancel",
            headers=headers
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✓ Cancel request sent: {result.get('message')}")
            else:
                print(f"✗ Cancel failed with status {resp.status}")

if __name__ == "__main__":
    print("WebSocket Search Test")
    print("=" * 60)
    print("Make sure the backend server is running on localhost:8000")
    print("=" * 60)
    
    asyncio.run(test_search())
    # asyncio.run(test_cancel())  # Uncomment to test cancellation
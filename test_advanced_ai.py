#!/usr/bin/env python3
"""Test the Advanced AI System"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.advanced_ollama_service import advanced_ollama_service

async def test_ai():
    print("🧪 Testing Advanced AI System...")
    print("=" * 50)
    
    # Test 1: Basic chat with persona
    print("\n1️⃣ Testing basic chat with Dr. Serena:")
    async for response in advanced_ollama_service.process_message("Hello, can you help me with spinal surgery research?"):
        print(response, end='', flush=True)
    print("\n")
    
    # Test 2: Magic command - help
    print("\n2️⃣ Testing /help command:")
    async for response in advanced_ollama_service.process_message("/help"):
        print(response, end='', flush=True)
    print("\n")
    
    # Test 3: Switch persona
    print("\n3️⃣ Testing persona switch to data analyst:")
    async for response in advanced_ollama_service.process_message("/persona data_analyst"):
        print(response, end='', flush=True)
    print("\n")
    
    # Test 4: Sequential thinking
    print("\n4️⃣ Testing sequential thinking:")
    async for response in advanced_ollama_service.process_message("/think lumbar fusion outcomes"):
        print(response, end='', flush=True)
    print("\n")
    
    # Test 5: Memory save
    print("\n5️⃣ Testing memory save:")
    async for response in advanced_ollama_service.process_message("/remember facts: Lumbar fusion has 85-95% success rate at 2 years"):
        print(response, end='', flush=True)
    print("\n")
    
    # Test 6: Memory recall
    print("\n6️⃣ Testing memory recall:")
    async for response in advanced_ollama_service.process_message("/recall lumbar fusion success"):
        print(response, end='', flush=True)
    print("\n")
    
    # Test 7: Context display
    print("\n7️⃣ Testing context display:")
    async for response in advanced_ollama_service.process_message("/context"):
        print(response, end='', flush=True)
    print("\n")
    
    print("=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_ai())
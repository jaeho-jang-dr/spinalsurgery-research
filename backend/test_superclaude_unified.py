"""
Test script for SuperClaude Unified Endpoint
Tests all integrated features: Context7, Sequential, Magic, Memory, Serena, Persona
"""
import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any


class SuperClaudeUnifiedTester:
    """Test client for SuperClaude Unified API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1/superclaude-unified"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
    
    async def authenticate(self, username: str = "test@example.com", password: str = "testpass123"):
        """Authenticate and get token"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.auth_token}"
            print("✅ Authentication successful")
            return True
        else:
            print("❌ Authentication failed:", response.text)
            return False
    
    async def test_unified_execute(self):
        """Test unified execution endpoint"""
        print("\n🔄 Testing Unified Execute Endpoint...")
        
        request_data = {
            "query": "Analyze the effectiveness of lumbar fusion surgery for chronic back pain",
            "mode": "intelligent",
            "features": {
                "context7": True,
                "sequential": True,
                "magic": True,
                "memory": True,
                "serena": True,
                "persona": True
            },
            "context": {
                "domain": "medical_research",
                "task_type": "analysis"
            },
            "metadata": {
                "test": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        response = await self.client.post(
            f"{self.base_url}{self.api_prefix}/execute",
            json=request_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Unified execution successful")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Mode Used: {result.get('mode_used')}")
            print(f"   Features Activated: {result.get('features_activated')}")
            print(f"   Primary Response: {result.get('primary_response')[:100]}...")
            print(f"   Thinking Steps: {len(result.get('thinking_process', []))}")
            print(f"   Serena Recommendations: {len(result.get('serena_recommendations', []))}")
            return result.get('session_id')
        else:
            print(f"❌ Unified execution failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    
    async def test_orchestration(self):
        """Test orchestration endpoint"""
        print("\n🔄 Testing Orchestration Endpoint...")
        
        plan = {
            "objective": "Complete research paper analysis workflow",
            "phases": [
                {
                    "id": "phase1",
                    "name": "Literature Review",
                    "tasks": ["search", "filter", "summarize"]
                },
                {
                    "id": "phase2",
                    "name": "Data Analysis",
                    "tasks": ["collect", "analyze", "visualize"]
                },
                {
                    "id": "phase3",
                    "name": "Report Generation",
                    "tasks": ["write", "review", "finalize"]
                }
            ],
            "dependencies": {
                "phase2": ["phase1"],
                "phase3": ["phase2"]
            },
            "checkpoints": [
                {"phase": "phase1", "criteria": "minimum 50 papers reviewed"},
                {"phase": "phase2", "criteria": "statistical significance achieved"}
            ]
        }
        
        response = await self.client.post(
            f"{self.base_url}{self.api_prefix}/orchestrate",
            json=plan
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Orchestration successful")
            print(f"   Plan ID: {result.get('plan_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Phases Completed: {len([p for p in result.get('phases', []) if p['status'] == 'completed'])}/{len(result.get('phases', []))}")
        else:
            print(f"❌ Orchestration failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    async def test_memory_operations(self):
        """Test advanced memory operations"""
        print("\n🔄 Testing Memory Operations...")
        
        queries = [
            {
                "query_type": "search",
                "query": "lumbar fusion",
                "filters": {"type": "research"},
                "correlation_depth": 2
            },
            {
                "query_type": "analyze",
                "query": "memory_stats",
                "filters": {},
                "correlation_depth": 1
            }
        ]
        
        for query in queries:
            response = await self.client.post(
                f"{self.base_url}{self.api_prefix}/memory/advanced",
                json=query
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Memory {query['query_type']} successful")
                if query['query_type'] == 'analyze':
                    analysis = result.get('analysis', {})
                    print(f"   Total Sessions: {analysis.get('total_sessions', 0)}")
                    print(f"   Total Memories: {analysis.get('total_memories', 0)}")
            else:
                print(f"❌ Memory {query['query_type']} failed: {response.status_code}")
    
    async def test_persona_configuration(self):
        """Test persona configuration"""
        print("\n🔄 Testing Persona Configuration...")
        
        config = {
            "primary_persona": "researcher",
            "secondary_personas": ["clinician", "analyst"],
            "auto_switch": True,
            "context_aware": True,
            "blend_mode": "weighted"
        }
        
        response = await self.client.post(
            f"{self.base_url}{self.api_prefix}/persona/configure",
            json=config
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Persona configuration successful")
            print(f"   Primary: {result.get('primary')}")
            print(f"   Secondary: {result.get('secondary')}")
            print(f"   Blend Mode: {result.get('blend_mode')}")
        else:
            print(f"❌ Persona configuration failed: {response.status_code}")
    
    async def test_serena_directive(self):
        """Test Serena AI directive"""
        print("\n🔄 Testing Serena Directive...")
        
        directive = {
            "task": "Help optimize the research methodology for spine surgery outcomes",
            "guidance_level": "comprehensive",
            "proactive_mode": True,
            "learning_enabled": True
        }
        
        response = await self.client.post(
            f"{self.base_url}{self.api_prefix}/serena/directive",
            json=directive
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Serena directive successful")
            print(f"   Task Understanding: {result.get('task_understanding', '')[:100]}...")
            print(f"   Recommendations: {len(result.get('recommendations', []))}")
            print(f"   Actions Suggested: {len(result.get('actions', []))}")
        else:
            print(f"❌ Serena directive failed: {response.status_code}")
    
    async def test_deep_analysis(self):
        """Test deep analysis"""
        print("\n🔄 Testing Deep Analysis...")
        
        content = """
        Lumbar spinal fusion is a surgical procedure that permanently connects two or more vertebrae 
        in the lower back. The procedure is commonly used to treat conditions such as degenerative 
        disc disease, spondylolisthesis, and spinal stenosis. Success rates vary between 70-90% 
        depending on the specific condition and patient factors.
        """
        
        response = await self.client.post(
            f"{self.base_url}{self.api_prefix}/analyze/deep",
            json={
                "content": content,
                "analysis_types": ["semantic", "structural", "contextual", "predictive"],
                "use_all_features": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Deep analysis successful")
            analyses = result.get('analyses', {})
            for analysis_type, data in analyses.items():
                print(f"   {analysis_type.capitalize()}: {list(data.keys())}")
        else:
            print(f"❌ Deep analysis failed: {response.status_code}")
    
    async def test_batch_execution(self):
        """Test batch execution"""
        print("\n🔄 Testing Batch Execution...")
        
        requests = [
            {
                "query": "What are the latest advances in minimally invasive spine surgery?",
                "mode": "standard",
                "features": {
                    "context7": True,
                    "sequential": False,
                    "magic": True,
                    "memory": True,
                    "serena": False,
                    "persona": True
                }
            },
            {
                "query": "Compare fusion vs non-fusion techniques for lumbar instability",
                "mode": "wave_based",
                "features": {
                    "context7": True,
                    "sequential": True,
                    "magic": True,
                    "memory": True,
                    "serena": True,
                    "persona": True
                }
            }
        ]
        
        response = await self.client.post(
            f"{self.base_url}{self.api_prefix}/batch/execute",
            json=requests,
            params={"parallel": False}
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Batch execution successful")
            print(f"   Total Requests: {len(results)}")
            for i, result in enumerate(results):
                print(f"   Request {i+1}: {result.get('status')} - Mode: {result.get('mode_used')}")
        else:
            print(f"❌ Batch execution failed: {response.status_code}")
    
    async def test_capabilities(self):
        """Test capabilities endpoint"""
        print("\n🔄 Testing Capabilities Endpoint...")
        
        response = await self.client.get(f"{self.base_url}{self.api_prefix}/capabilities")
        
        if response.status_code == 200:
            capabilities = response.json()
            print("✅ Capabilities retrieved successfully")
            print(f"   Version: {capabilities.get('version')}")
            print(f"   Status: {capabilities.get('status')}")
            print("   Features:")
            for feature, config in capabilities.get('features', {}).items():
                print(f"     - {feature}: {config.get('enabled')} ({len(config.get('capabilities', []))} capabilities)")
        else:
            print(f"❌ Capabilities retrieval failed: {response.status_code}")
    
    async def test_session_context(self, session_id: str):
        """Test session context retrieval"""
        print("\n🔄 Testing Session Context Retrieval...")
        
        if not session_id:
            print("⚠️  No session ID available, skipping test")
            return
        
        response = await self.client.get(
            f"{self.base_url}{self.api_prefix}/session/{session_id}/complete-context"
        )
        
        if response.status_code == 200:
            context = response.json()
            print("✅ Session context retrieved successfully")
            print(f"   Session ID: {context.get('session_id')}")
            print(f"   Memory State Entries: {len(context.get('memory_state', {}))}")
            print(f"   Active Personas: {len(context.get('active_personas', {}))}")
            print(f"   Execution History: {len(context.get('execution_history', []))}")
        else:
            print(f"❌ Session context retrieval failed: {response.status_code}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting SuperClaude Unified API Tests")
        print("=" * 50)
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Cannot proceed without authentication")
            return
        
        # Run tests in sequence
        session_id = await self.test_unified_execute()
        await self.test_orchestration()
        await self.test_memory_operations()
        await self.test_persona_configuration()
        await self.test_serena_directive()
        await self.test_deep_analysis()
        await self.test_batch_execution()
        await self.test_capabilities()
        await self.test_session_context(session_id)
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()


async def main():
    """Main test function"""
    tester = SuperClaudeUnifiedTester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
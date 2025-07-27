#!/usr/bin/env python3
"""
Test script for SuperClaude Enhanced API endpoints
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_superclaude_enhanced():
    """Test SuperClaude Enhanced endpoints"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test credentials
    test_user = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    
    async with httpx.AsyncClient() as client:
        print("=== SuperClaude Enhanced API Test ===\n")
        
        # 1. Login
        print("1. Logging in...")
        login_response = await client.post(
            f"{base_url}/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✓ Login successful\n")
        
        # 2. Test Execute Command
        print("2. Testing Execute Command...")
        execute_response = await client.post(
            f"{base_url}/superclaude-enhanced/execute",
            json={
                "command": "analyze",
                "target": "lumbar fusion research protocol",
                "flags": ["--c7", "--seq", "--magic", "--memory", "--serena", "--persona"],
                "context": {
                    "study_type": "RCT",
                    "population": "Adults with degenerative disc disease"
                }
            },
            headers=headers
        )
        
        if execute_response.status_code == 200:
            result = execute_response.json()
            print(f"✓ Command executed successfully")
            print(f"  - Session ID: {result.get('session_id')}")
            print(f"  - Waves executed: {result.get('waves_executed')}")
            print(f"  - Total thinking steps: {result.get('total_thinking_steps')}")
            session_id = result.get('session_id')
        else:
            print(f"✗ Execute command failed: {execute_response.status_code}")
            print(f"  Response: {execute_response.text}")
            session_id = None
        print()
        
        # 3. Test Wave Execution
        print("3. Testing Wave Execution...")
        wave_response = await client.post(
            f"{base_url}/superclaude-enhanced/wave/execute",
            json={
                "wave_type": "analysis",
                "task": "Design clinical trial methodology",
                "context": {"phase": "planning"},
                "session_id": session_id,
                "auto_persona": True,
                "use_mcp": ["context7", "sequential", "magic"]
            },
            headers=headers
        )
        
        if wave_response.status_code == 200:
            wave_result = wave_response.json()
            print(f"✓ Wave executed successfully")
            print(f"  - Wave ID: {wave_result.get('wave_id')}")
            print(f"  - Status: {wave_result.get('status')}")
            print(f"  - Active persona: {wave_result.get('active_persona')}")
        else:
            print(f"✗ Wave execution failed: {wave_response.status_code}")
            print(f"  Response: {wave_response.text}")
        print()
        
        # 4. Test Enhanced Chat
        print("4. Testing Enhanced Chat...")
        chat_response = await client.post(
            f"{base_url}/superclaude-enhanced/chat/enhanced",
            json={
                "message": "What statistical tests should I use for comparing surgical outcomes?",
                "session_id": session_id,
                "context": "Comparing minimally invasive vs traditional surgery",
                "enable_c7": True,
                "enable_seq": True,
                "enable_magic": True,
                "enable_memory": True,
                "enable_serena": True,
                "enable_persona": True
            },
            headers=headers
        )
        
        if chat_response.status_code == 200:
            chat_result = chat_response.json()
            print(f"✓ Enhanced chat successful")
            print(f"  - Response length: {len(chat_result.get('content', ''))}")
            print(f"  - Persona used: {chat_result.get('persona')}")
            if 'serena_enhancements' in chat_result:
                print(f"  - Serena suggestions: {len(chat_result['serena_enhancements'].get('suggestions', []))}")
        else:
            print(f"✗ Enhanced chat failed: {chat_response.status_code}")
            print(f"  Response: {chat_response.text}")
        print()
        
        # 5. Test Memory Operations
        print("5. Testing Memory Operations...")
        memory_save_response = await client.post(
            f"{base_url}/superclaude-enhanced/memory/operation",
            json={
                "operation": "save",
                "session_id": session_id,
                "key": "study_design",
                "value": {
                    "type": "RCT",
                    "arms": 2,
                    "blinding": "double-blind"
                }
            },
            headers=headers
        )
        
        if memory_save_response.status_code == 200:
            print("✓ Memory save successful")
            
            # Try to retrieve
            memory_retrieve_response = await client.post(
                f"{base_url}/superclaude-enhanced/memory/operation",
                json={
                    "operation": "retrieve",
                    "session_id": session_id,
                    "key": "study_design"
                },
                headers=headers
            )
            
            if memory_retrieve_response.status_code == 200:
                retrieved = memory_retrieve_response.json()
                print(f"✓ Memory retrieve successful")
                print(f"  - Retrieved value: {retrieved.get('value')}")
            else:
                print(f"✗ Memory retrieve failed: {memory_retrieve_response.status_code}")
        else:
            print(f"✗ Memory save failed: {memory_save_response.status_code}")
        print()
        
        # 6. Test Persona Management
        print("6. Testing Persona Management...")
        
        # List personas
        personas_response = await client.get(
            f"{base_url}/superclaude-enhanced/persona/list",
            headers=headers
        )
        
        if personas_response.status_code == 200:
            personas = personas_response.json()
            print(f"✓ Listed {len(personas.get('personas', []))} personas")
            
            # Activate a persona
            activate_response = await client.post(
                f"{base_url}/superclaude-enhanced/persona/activate",
                json={
                    "persona_type": "statistician",
                    "task_context": "Sample size calculation",
                    "session_id": session_id
                },
                headers=headers
            )
            
            if activate_response.status_code == 200:
                activated = activate_response.json()
                print(f"✓ Activated persona: {activated['persona']['name']}")
            else:
                print(f"✗ Persona activation failed: {activate_response.status_code}")
        else:
            print(f"✗ List personas failed: {personas_response.status_code}")
        print()
        
        # 7. Test Sequential Thinking
        print("7. Testing Sequential Thinking...")
        thinking_response = await client.post(
            f"{base_url}/superclaude-enhanced/thinking/sequential",
            json={
                "problem": "Design adaptive clinical trial with interim analysis",
                "max_steps": 10,
                "allow_revision": True,
                "session_id": session_id
            },
            headers=headers
        )
        
        if thinking_response.status_code == 200:
            thinking_result = thinking_response.json()
            print(f"✓ Sequential thinking completed")
            print(f"  - Total steps: {thinking_result.get('total_steps')}")
            print(f"  - First thought: {thinking_result['thinking_steps'][0]['thought'][:100]}...")
        else:
            print(f"✗ Sequential thinking failed: {thinking_response.status_code}")
        print()
        
        # 8. Test Magic Analysis
        print("8. Testing Magic Analysis...")
        magic_response = await client.post(
            f"{base_url}/superclaude-enhanced/magic/analyze",
            json={
                "content": "Prospective cohort study comparing surgical techniques in spine surgery",
                "analysis_type": "methodology",
                "depth": "comprehensive",
                "session_id": session_id
            },
            headers=headers
        )
        
        if magic_response.status_code == 200:
            magic_result = magic_response.json()
            print(f"✓ Magic analysis completed")
            print(f"  - Analysis type: {magic_result.get('analysis_type')}")
            print(f"  - Insights: {len(magic_result.get('insights', []))}")
            print(f"  - Recommendations: {len(magic_result.get('recommendations', []))}")
        else:
            print(f"✗ Magic analysis failed: {magic_response.status_code}")
        print()
        
        # 9. Test Research Task
        print("9. Testing Research Task Execution...")
        task_response = await client.post(
            f"{base_url}/superclaude-enhanced/research/task",
            json={
                "task_type": "protocol",
                "description": "Develop protocol for minimally invasive spine surgery outcomes study",
                "requirements": {
                    "population": "Adults with lumbar stenosis",
                    "sample_size": 150,
                    "duration": "24 months follow-up"
                },
                "use_waves": True,
                "auto_persona": True,
                "mcp_integration": True
            },
            headers=headers
        )
        
        if task_response.status_code == 200:
            task_result = task_response.json()
            print(f"✓ Research task executed")
            print(f"  - Waves executed: {len(task_result.get('waves_executed', []))}")
        else:
            print(f"✗ Research task failed: {task_response.status_code}")
        print()
        
        # 10. Test Session Context
        if session_id:
            print("10. Testing Session Context Retrieval...")
            context_response = await client.get(
                f"{base_url}/superclaude-enhanced/session/{session_id}/context",
                headers=headers
            )
            
            if context_response.status_code == 200:
                context = context_response.json()
                print(f"✓ Session context retrieved")
                print(f"  - Session ID: {context.get('session_id')}")
                print(f"  - Wave history: {len(context.get('wave_history', []))} waves")
                print(f"  - Active persona: {context.get('active_persona', {}).get('name', 'None')}")
            else:
                print(f"✗ Session context retrieval failed: {context_response.status_code}")
            print()
        
        # 11. Test MCP Status
        print("11. Testing MCP Status...")
        mcp_response = await client.get(
            f"{base_url}/superclaude-enhanced/mcp/status",
            headers=headers
        )
        
        if mcp_response.status_code == 200:
            mcp_status = mcp_response.json()
            print(f"✓ MCP status retrieved")
            servers = mcp_status.get('mcp_servers', {})
            for server_name, server_info in servers.items():
                print(f"  - {server_name}: {server_info.get('status')}")
        else:
            print(f"✗ MCP status failed: {mcp_response.status_code}")
        print()
        
        # 12. Test Workflow
        print("12. Testing Workflow Management...")
        
        # Create workflow
        workflow_response = await client.post(
            f"{base_url}/superclaude-enhanced/workflow/create",
            json={
                "workflow_name": "Complete Research Protocol",
                "steps": [
                    {
                        "name": "Literature Review",
                        "command": "analyze",
                        "target": "existing research on spine surgery outcomes",
                        "context": {"depth": "systematic"}
                    },
                    {
                        "name": "Protocol Design",
                        "command": "design",
                        "target": "clinical trial protocol",
                        "context": {"based_on": "literature_review"}
                    }
                ]
            },
            headers=headers
        )
        
        if workflow_response.status_code == 200:
            workflow = workflow_response.json()
            print(f"✓ Workflow created")
            print(f"  - Workflow ID: {workflow.get('workflow_id')}")
            print(f"  - Steps: {workflow.get('steps')}")
            
            # Execute workflow
            workflow_id = workflow.get('workflow_id')
            if workflow_id:
                exec_response = await client.post(
                    f"{base_url}/superclaude-enhanced/workflow/{workflow_id}/execute",
                    json={
                        "context": {
                            "study_name": "SPINE-2025",
                            "principal_investigator": "Dr. Test"
                        }
                    },
                    headers=headers
                )
                
                if exec_response.status_code == 200:
                    exec_result = exec_response.json()
                    print(f"✓ Workflow executed")
                    print(f"  - Steps executed: {exec_result.get('steps_executed')}")
                else:
                    print(f"✗ Workflow execution failed: {exec_response.status_code}")
        else:
            print(f"✗ Workflow creation failed: {workflow_response.status_code}")
        
        print("\n=== Test Summary ===")
        print("All SuperClaude Enhanced endpoints have been tested.")
        print("Check the output above for any failures.")


if __name__ == "__main__":
    asyncio.run(test_superclaude_enhanced())
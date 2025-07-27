"""
Claude Code Paper Search Integration Endpoint
웹 앱에서 논문 검색 요청을 받아 Claude Code로 전달하고 결과를 반환
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import asyncio
import json
from datetime import datetime
import aiohttp
from pathlib import Path

from app.api import deps
from app.core.database import get_db
from app.models.user import User

# Use mock service for now since Claude CLI is interactive
# TODO: In the future, integrate with Claude Code's API or MCP server directly
from app.services.mock_claude_code_search_service import mock_claude_code_search_service as claude_code_search_service
print("Using mock Claude Code search service for demonstration")

# Store active search tasks for cancellation
active_searches = {}

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        # WebSocket is already accepted before calling this method
        self.active_connections[session_id] = websocket
        
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            
    async def send_progress(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except:
                self.disconnect(session_id)

manager = ConnectionManager()

class PaperSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10
    search_sites: Optional[List[str]] = ["pubmed", "arxiv", "google_scholar"]
    download_pdfs: Optional[bool] = True
    translate_to_korean: Optional[bool] = True
    project_id: Optional[str] = None
    
class PaperSearchResponse(BaseModel):
    search_id: str
    status: str
    message: str
    
class SearchProgressUpdate(BaseModel):
    search_id: str
    status: str  # searching, downloading, translating, completed, error
    current_site: Optional[str] = None
    papers_found: int = 0
    papers_downloaded: int = 0
    current_paper: Optional[str] = None
    progress_percentage: int = 0
    message: str

@router.post("/search", response_model=PaperSearchResponse)
async def initiate_claude_code_search(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    search_data: PaperSearchRequest,
    background_tasks: BackgroundTasks
) -> Any:
    """
    논문 검색 시작 - Claude Code가 실제 검색을 수행
    """
    try:
        # Generate unique search ID
        search_id = str(uuid.uuid4())
        
        # Create search task
        search_task = {
            "search_id": search_id,
            "user_id": str(current_user.id) if hasattr(current_user, 'id') else "mock-user",
            "query": search_data.query,
            "max_results": search_data.max_results,
            "search_sites": search_data.search_sites,
            "download_pdfs": search_data.download_pdfs,
            "translate_to_korean": search_data.translate_to_korean,
            "project_id": search_data.project_id,
            "status": "initiated",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save search task to database
        # TODO: Implement search task model and save to DB
        
        # Start background search with Claude Code
        background_tasks.add_task(
            execute_claude_code_search,
            search_task,
            db
        )
        
        return PaperSearchResponse(
            search_id=search_id,
            status="initiated",
            message=f"검색이 시작되었습니다. WebSocket을 통해 진행 상황을 확인하세요. (ID: {search_id})"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{search_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    search_id: str
):
    """
    WebSocket endpoint for real-time search progress updates
    """
    # For WebSocket, we need to handle authentication differently
    # Accept the connection first, then validate the token
    await websocket.accept()
    
    try:
        # Expect the first message to contain the authentication token
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        
        # For now, accept mock token for development
        token = auth_data.get("token", "mock-token")
        if not token:
            await websocket.send_json({
                "type": "error",
                "message": "Authentication required"
            })
            await websocket.close(code=1008)  # Policy Violation
            return
            
        # Connect to manager after authentication
        await manager.connect(websocket, search_id)
        
        # Send initial connection confirmation
        await manager.send_progress(search_id, {
            "type": "connection",
            "status": "connected",
            "message": "WebSocket 연결이 성공적으로 설정되었습니다."
        })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong or other messages if needed
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        manager.disconnect(search_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(search_id)

async def execute_claude_code_search(search_task: dict, db: AsyncSession):
    """
    Background task to execute paper search using Claude Code
    """
    search_id = search_task["search_id"]
    
    try:
        # Wait a moment to ensure WebSocket is fully connected and authenticated
        await asyncio.sleep(1)
        
        # Update progress: Starting search
        await manager.send_progress(search_id, {
            "type": "progress",
            "search_id": search_id,
            "status": "searching",
            "message": "Claude Code를 통한 논문 검색을 시작합니다...",
            "progress_percentage": 10
        })
        
        # Store in active searches
        active_searches[search_id] = True
        
        # Call Claude Code search service (mock service doesn't need extra params)
        results = await claude_code_search_service.search_papers(
            query=search_task["query"],
            sites=search_task["search_sites"],
            max_results=search_task["max_results"],
            progress_callback=lambda update: asyncio.create_task(
                manager.send_progress(search_id, update)
            )
        )
        
        # Download PDFs if requested
        if search_task["download_pdfs"]:
            await manager.send_progress(search_id, {
                "type": "progress",
                "search_id": search_id,
                "status": "downloading",
                "message": "논문 PDF 다운로드를 시작합니다...",
                "progress_percentage": 50
            })
            
            downloaded_papers = await claude_code_search_service.download_papers(
                papers=results,
                project_id=search_task.get("project_id"),
                progress_callback=lambda update: asyncio.create_task(
                    manager.send_progress(search_id, update)
                )
            )
        else:
            downloaded_papers = results
            
        # Translate to Korean if requested
        if search_task["translate_to_korean"]:
            await manager.send_progress(search_id, {
                "type": "progress",
                "search_id": search_id,
                "status": "translating",
                "message": "한글 번역을 시작합니다...",
                "progress_percentage": 80
            })
            
            translated_papers = await claude_code_search_service.translate_papers(
                papers=downloaded_papers,
                progress_callback=lambda update: asyncio.create_task(
                    manager.send_progress(search_id, update)
                )
            )
        else:
            translated_papers = downloaded_papers
            
        # Save results to database
        # TODO: Save search results to database
        
        # Send completion message
        await manager.send_progress(search_id, {
            "type": "complete",
            "search_id": search_id,
            "status": "completed",
            "message": f"검색이 완료되었습니다. 총 {len(translated_papers)}개의 논문을 찾았습니다.",
            "progress_percentage": 100,
            "results": translated_papers
        })
        
        # Remove from active searches
        if search_id in active_searches:
            del active_searches[search_id]
        
    except Exception as e:
        # Send error message
        await manager.send_progress(search_id, {
            "type": "error",
            "search_id": search_id,
            "status": "error",
            "message": f"검색 중 오류가 발생했습니다: {str(e)}",
            "progress_percentage": 0
        })
        
        # Remove from active searches
        if search_id in active_searches:
            del active_searches[search_id]

@router.get("/search/{search_id}/status")
async def get_search_status(
    *,
    search_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get current status of a search task
    """
    # TODO: Implement database lookup for search status
    return {
        "search_id": search_id,
        "status": "in_progress",
        "message": "검색이 진행 중입니다."
    }

@router.get("/search/{search_id}/results")
async def get_search_results(
    *,
    search_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get results of a completed search
    """
    # TODO: Implement database lookup for search results
    return {
        "search_id": search_id,
        "status": "completed",
        "papers": []
    }

@router.post("/search/{search_id}/cancel")
async def cancel_search(
    *,
    search_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Cancel an ongoing search
    """
    try:
        # Cancel the CLI process
        cancelled = await claude_code_search_service.cancel_search(search_id)
        
        if cancelled:
            # Send cancellation message via WebSocket
            await manager.send_progress(search_id, {
                "type": "cancelled",
                "search_id": search_id,
                "status": "cancelled",
                "message": "검색이 취소되었습니다.",
                "progress_percentage": 0
            })
            
            # Remove from active searches
            if search_id in active_searches:
                del active_searches[search_id]
            
            return {
                "search_id": search_id,
                "status": "cancelled",
                "message": "검색이 취소되었습니다."
            }
        else:
            return {
                "search_id": search_id,
                "status": "not_found",
                "message": "해당 검색을 찾을 수 없습니다."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Removed duplicate WebSocket endpoint - already defined above
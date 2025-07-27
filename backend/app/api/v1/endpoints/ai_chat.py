"""
AI Chat endpoints
"""
from typing import Any, Dict, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime
import json
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.chat_session import ChatSession, ChatMessage as ChatMessageModel
from app.services.ai_service import ai_service
from app.services.ollama_chat_service import ollama_chat_service

router = APIRouter()

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    model: str

class ChatSessionResponse(BaseModel):
    session_id: str
    title: Optional[str]
    created_at: str
    updated_at: str
    message_count: int
    last_message: Optional[Dict[str, Any]]
    is_active: bool
    model: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    chat_data: ChatMessageRequest
) -> Any:
    """Chat with AI assistant"""
    try:
        # Get or create session
        session_id = chat_data.session_id or str(uuid.uuid4())
        user_id = str(current_user.id) if hasattr(current_user, 'id') else "mock-user"
        
        # Check if session exists in database
        result = await db.execute(
            select(ChatSession).where(
                and_(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id
                )
            )
        )
        session = result.scalar_one_or_none()
        
        # Create new session if doesn't exist
        if not session:
            session = ChatSession(
                id=session_id,
                user_id=user_id,
                model=chat_data.model or "llama2",
                title=chat_data.message[:50] + "..." if len(chat_data.message) > 50 else chat_data.message
            )
            db.add(session)
            await db.flush()
        
        # Add user message to database
        user_message = ChatMessageModel(
            session_id=session_id,
            role="user",
            content=chat_data.message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        await db.flush()
        
        # Get recent messages for context
        recent_messages_result = await db.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.timestamp.desc())
            .limit(10)
        )
        recent_messages = recent_messages_result.scalars().all()
        context_messages = [{
            "role": msg.role,
            "content": msg.content
        } for msg in reversed(recent_messages)]
        
        # Get AI response
        if chat_data.model and chat_data.model != "mock-llm":
            ollama_chat_service.set_model(chat_data.model)
            try:
                response = await ollama_chat_service.chat(
                    message=chat_data.message,
                    context=context_messages
                )
                if response and not response.startswith("Error:"):
                    model_used = f"ollama/{ollama_chat_service.model}"
                else:
                    # Fallback to mock
                    response = await ai_service.mock_service.chat(
                        message=chat_data.message,
                        context=chat_data.context
                    )
                    model_used = "mock-llm"
            except Exception as e:
                print(f"Ollama chat failed: {e}")
                # Fallback to mock
                response = await ai_service.mock_service.chat(
                    message=chat_data.message,
                    context=chat_data.context
                )
                model_used = "mock-llm"
        else:
            # Use mock service
            response = await ai_service.mock_service.chat(
                message=chat_data.message,
                context=chat_data.context
            )
            model_used = "mock-llm"
        
        # Add AI response to database
        ai_message = ChatMessageModel(
            session_id=session_id,
            role="assistant",
            content=response,
            timestamp=datetime.utcnow(),
            model=model_used
        )
        db.add(ai_message)
        
        # Update session
        session.updated_at = datetime.utcnow()
        session.model = model_used
        
        await db.commit()
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat(),
            model=model_used
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions")
async def get_chat_sessions(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Get user's chat sessions"""
    user_id = str(current_user.id) if hasattr(current_user, 'id') else "mock-user"
    
    # Get sessions with message count
    result = await db.execute(
        select(ChatSession)
        .where(
            and_(
                ChatSession.user_id == user_id,
                ChatSession.is_active == True
            )
        )
        .options(selectinload(ChatSession.messages))
        .order_by(ChatSession.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    sessions = result.scalars().all()
    
    user_sessions = []
    for session in sessions:
        messages = sorted(session.messages, key=lambda x: x.timestamp)
        last_message = None
        if messages:
            last_msg = messages[-1]
            last_message = {
                "role": last_msg.role,
                "content": last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content,
                "timestamp": last_msg.timestamp.isoformat()
            }
        
        user_sessions.append(ChatSessionResponse(
            session_id=session.id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            message_count=len(messages),
            last_message=last_message,
            is_active=session.is_active,
            model=session.model
        ))
    
    return {"sessions": user_sessions}

@router.get("/chat/sessions/{session_id}")
async def get_chat_history(
    *,
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get chat history for a session"""
    user_id = str(current_user.id) if hasattr(current_user, 'id') else "mock-user"
    
    # Get session with messages
    result = await db.execute(
        select(ChatSession)
        .where(
            and_(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
        )
        .options(selectinload(ChatSession.messages))
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Sort messages by timestamp
    messages = sorted(session.messages, key=lambda x: x.timestamp)
    
    return {
        "session_id": session_id,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "model": session.model,
        "messages": [{
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "model": msg.model
        } for msg in messages]
    }

@router.get("/models")
async def get_available_models(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get available AI models"""
    models = []
    
    # Get Ollama models
    try:
        ollama_models = await ollama_chat_service.list_models()
        for model_name in ollama_models:
            models.append({
                "id": model_name,
                "name": model_name,
                "provider": "ollama",
                "available": True
            })
    except Exception as e:
        print(f"Failed to get Ollama models: {e}")
    
    # Always include mock model
    models.append({
        "id": "mock-llm",
        "name": "Mock AI (for testing)",
        "provider": "mock",
        "available": True
    })
    
    return {"models": models, "current_model": ollama_chat_service.model}

@router.post("/models/pull/{model_name}")
async def pull_model(
    *,
    model_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Pull a new model from Ollama"""
    try:
        success = await ollama_chat_service.pull_model(model_name)
        if success:
            return {"status": "success", "message": f"Model {model_name} pulled successfully"}
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to pull model {model_name}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error pulling model: {str(e)}"
        )

@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(
    *,
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Delete a chat session and all its messages"""
    user_id = str(current_user.id) if hasattr(current_user, 'id') else "mock-user"
    
    # Check if session exists and belongs to user
    result = await db.execute(
        select(ChatSession).where(
            and_(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete session (messages will be cascade deleted)
    await db.delete(session)
    await db.commit()
    
    return {"status": "success", "message": f"Session {session_id} deleted successfully"}

@router.post("/chat/sessions/{session_id}/export")
async def export_chat_session(
    *,
    session_id: str,
    format: str = Query("json", regex="^(json|csv|markdown)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Export chat session in various formats"""
    user_id = str(current_user.id) if hasattr(current_user, 'id') else "mock-user"
    
    # Get session with messages
    result = await db.execute(
        select(ChatSession)
        .where(
            and_(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
        )
        .options(selectinload(ChatSession.messages))
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Sort messages by timestamp
    messages = sorted(session.messages, key=lambda x: x.timestamp)
    
    if format == "json":
        # Export as JSON
        export_data = {
            "session_id": session.id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "model": session.model,
            "messages": [{
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "model": msg.model
            } for msg in messages]
        }
        return StreamingResponse(
            io=StringIO(json.dumps(export_data, indent=2, ensure_ascii=False)),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=chat_session_{session_id}.json"
            }
        )
    
    elif format == "csv":
        # Export as CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "Role", "Content", "Model"])
        for msg in messages:
            writer.writerow([
                msg.timestamp.isoformat(),
                msg.role,
                msg.content,
                msg.model or ""
            ])
        output.seek(0)
        return StreamingResponse(
            io=output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=chat_session_{session_id}.csv"
            }
        )
    
    else:  # markdown
        # Export as Markdown
        markdown_content = f"# Chat Session: {session.title or session_id}\n\n"
        markdown_content += f"**Created:** {session.created_at.isoformat()}\n"
        markdown_content += f"**Model:** {session.model}\n\n"
        markdown_content += "---\n\n"
        
        for msg in messages:
            if msg.role == "user":
                markdown_content += f"### 👤 User ({msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')})\n\n"
            else:
                markdown_content += f"### 🤖 Assistant ({msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')})\n\n"
            markdown_content += f"{msg.content}\n\n"
        
        return StreamingResponse(
            io=StringIO(markdown_content),
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=chat_session_{session_id}.md"
            }
        )

@router.put("/chat/sessions/{session_id}")
async def update_chat_session(
    *,
    session_id: str,
    title: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Update chat session title"""
    user_id = str(current_user.id) if hasattr(current_user, 'id') else "mock-user"
    
    # Get session
    result = await db.execute(
        select(ChatSession).where(
            and_(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update title
    session.title = title
    session.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"status": "success", "message": "Session updated successfully"}
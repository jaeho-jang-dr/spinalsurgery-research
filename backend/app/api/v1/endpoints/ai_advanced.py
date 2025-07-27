"""
Advanced AI endpoints with full Ollama features
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json

from app.api import deps
from app.models.user import User
from app.services.advanced_ollama_service import advanced_ollama_service

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    persona: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class MemoryExport(BaseModel):
    format: str = "json"  # json, pickle, markdown

class MemoryImport(BaseModel):
    data: Dict[str, Any]
    merge: bool = True

class PersonaConfig(BaseModel):
    name: str
    role: str
    traits: List[str]
    expertise: List[str]
    language_style: str
    system_prompt: str

@router.post("/chat")
async def advanced_chat(
    chat_message: ChatMessage,
    current_user: User = Depends(deps.get_current_user)
):
    """Advanced chat with streaming response"""
    # Switch persona if specified
    if chat_message.persona:
        await advanced_ollama_service._switch_persona(chat_message.persona)
    
    # Update context if provided
    if chat_message.context:
        for level, data in chat_message.context.items():
            advanced_ollama_service._update_context(level, data)
    
    async def generate():
        async for chunk in advanced_ollama_service.process_message(
            chat_message.message, 
            user_id=str(current_user.id)
        ):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/plain")

@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    token: str = None
):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    # Simple auth check
    if not token or token != "mock-token":
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            message = data.get("message", "")
            persona = data.get("persona")
            context = data.get("context", {})
            
            # Switch persona if needed
            if persona:
                await advanced_ollama_service._switch_persona(persona)
            
            # Update context
            for level, ctx_data in context.items():
                advanced_ollama_service._update_context(level, ctx_data)
            
            # Send response chunks
            async for chunk in advanced_ollama_service.process_message(message, user_id="websocket-user"):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })
            
            # Send completion signal
            await websocket.send_json({
                "type": "complete"
            })
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))

@router.get("/personas")
async def list_personas(
    current_user: User = Depends(deps.get_current_user)
):
    """List available AI personas"""
    personas = []
    for key, persona in advanced_ollama_service.personas.items():
        personas.append({
            "id": key,
            "name": persona["name"],
            "role": persona["role"],
            "traits": persona["traits"],
            "expertise": persona["expertise"],
            "language_style": persona["language_style"]
        })
    return {"personas": personas, "current": advanced_ollama_service.current_persona}

@router.post("/personas")
async def create_persona(
    persona_config: PersonaConfig,
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new AI persona"""
    persona_id = persona_config.name.lower().replace(" ", "_")
    
    if persona_id in advanced_ollama_service.personas:
        raise HTTPException(status_code=400, detail="Persona already exists")
    
    advanced_ollama_service.personas[persona_id] = {
        "name": persona_config.name,
        "role": persona_config.role,
        "traits": persona_config.traits,
        "expertise": persona_config.expertise,
        "language_style": persona_config.language_style,
        "system_prompt": persona_config.system_prompt
    }
    
    return {"message": f"Persona '{persona_config.name}' created", "id": persona_id}

@router.put("/personas/{persona_id}")
async def switch_persona(
    persona_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    """Switch to a different persona"""
    if persona_id not in advanced_ollama_service.personas:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    advanced_ollama_service.current_persona = persona_id
    persona = advanced_ollama_service.personas[persona_id]
    
    return {
        "message": f"Switched to {persona['name']}",
        "persona": {
            "id": persona_id,
            "name": persona["name"],
            "role": persona["role"]
        }
    }

@router.get("/memory/export")
async def export_memory(
    format: str = "json",
    current_user: User = Depends(deps.get_current_user)
):
    """Export user's AI memory"""
    memory_data = await advanced_ollama_service.export_memory(str(current_user.id))
    
    if format == "json":
        return memory_data
    elif format == "markdown":
        # Convert to markdown format
        md_content = "# AI Memory Export\n\n"
        md_content += "## Short-term Memory\n"
        for item in memory_data["short_term"]:
            md_content += f"- {item}\n"
        
        md_content += "\n## Long-term Memory\n"
        for category, items in memory_data["long_term"].items():
            md_content += f"### {category.title()}\n"
            for key, value in items.items():
                md_content += f"- {key}: {value}\n"
        
        return {"content": md_content, "format": "markdown"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

@router.post("/memory/import")
async def import_memory(
    memory_import: MemoryImport,
    current_user: User = Depends(deps.get_current_user)
):
    """Import AI memory"""
    await advanced_ollama_service.import_memory(str(current_user.id), memory_import.data)
    return {"message": "Memory imported successfully"}

@router.delete("/memory")
async def clear_memory(
    memory_type: str = "all",  # all, short_term, long_term
    current_user: User = Depends(deps.get_current_user)
):
    """Clear AI memory"""
    if memory_type in ["all", "short_term"]:
        advanced_ollama_service.short_term_memory.clear()
    
    if memory_type in ["all", "long_term"]:
        advanced_ollama_service.long_term_memory = {
            "facts": {},
            "conversations": {},
            "insights": {},
            "user_preferences": {}
        }
        advanced_ollama_service._save_long_term_memory()
    
    return {"message": f"Cleared {memory_type} memory"}

@router.get("/context")
async def get_context(
    level: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user)
):
    """Get current AI context"""
    if level:
        if level in advanced_ollama_service.context_levels:
            return {level: advanced_ollama_service.context_levels[level]}
        else:
            raise HTTPException(status_code=404, detail="Context level not found")
    else:
        return advanced_ollama_service.context_levels

@router.put("/context/{level}")
async def update_context(
    level: str,
    context_data: Dict[str, Any],
    current_user: User = Depends(deps.get_current_user)
):
    """Update AI context at specific level"""
    if level not in advanced_ollama_service.context_levels:
        raise HTTPException(status_code=400, detail="Invalid context level")
    
    advanced_ollama_service._update_context(level, context_data)
    return {"message": f"Updated {level} context"}

@router.get("/thinking-chain")
async def get_thinking_chain(
    current_user: User = Depends(deps.get_current_user)
):
    """Get the current thinking chain"""
    return {
        "thinking_chain": advanced_ollama_service.thinking_chain,
        "length": len(advanced_ollama_service.thinking_chain)
    }

@router.post("/initialize")
async def initialize_ollama(
    current_user: User = Depends(deps.get_current_user)
):
    """Initialize Ollama service and pull models"""
    success = await advanced_ollama_service.initialize()
    if success:
        return {"message": "Ollama initialized successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to initialize Ollama")

@router.get("/models")
async def list_models(
    current_user: User = Depends(deps.get_current_user)
):
    """List available Ollama models"""
    models = await advanced_ollama_service._get_available_models()
    return {
        "models": models,
        "current": advanced_ollama_service.model
    }

@router.get("/commands")
async def list_magic_commands(
    current_user: User = Depends(deps.get_current_user)
):
    """List available magic commands"""
    commands = []
    for cmd in advanced_ollama_service.magic_commands:
        help_text = {
            "/think": "Sequential thinking process for complex problems",
            "/remember": "Save information to long-term memory",
            "/recall": "Recall relevant memories",
            "/analyze": "Deep analysis of a topic",
            "/visualize": "Generate data visualization suggestions",
            "/research": "Activate research mode with Dr. Serena",
            "/write": "Activate academic writing mode",
            "/code": "Activate code assistance mode",
            "/persona": "Switch AI persona",
            "/context": "Show current context levels",
            "/help": "Show help for commands"
        }
        commands.append({
            "command": cmd,
            "description": help_text.get(cmd, "")
        })
    return {"commands": commands}
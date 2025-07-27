"""
SuperClaude Enhanced Endpoint System
Full MCP Integration with Wave-based Execution
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio
import uuid

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.services.superclaude_enhanced_service import superclaude_enhanced_service

router = APIRouter()


class WaveType(str, Enum):
    """Wave execution types"""
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    FINALIZATION = "finalization"


class PersonaType(str, Enum):
    """Available research personas"""
    STATISTICIAN = "statistician"
    CLINICIAN = "clinician"
    METHODOLOGIST = "methodologist"
    WRITER = "writer"
    ETHICIST = "ethicist"
    FRONTEND = "frontend"
    BACKEND = "backend"
    ARCHITECT = "architect"
    SECURITY = "security"
    DEVOPS = "devops"
    FULLSTACK = "fullstack"


class MCPServerType(str, Enum):
    """MCP Server types"""
    CONTEXT7 = "context7"
    SEQUENTIAL = "sequential"
    MAGIC = "magic"
    MEMORY = "memory"
    PLAYWRIGHT = "playwright"


class SuperClaudeCommand(BaseModel):
    """SuperClaude command structure"""
    command: str = Field(..., description="Command to execute (analyze, implement, build, improve, troubleshoot, design, test)")
    target: str = Field(..., description="Target for the command")
    flags: List[str] = Field(default_factory=list, description="Command flags (--c7, --seq, --magic, --memory, --serena, --persona)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    session_id: Optional[str] = Field(default=None, description="Session ID for context persistence")


class WaveExecutionRequest(BaseModel):
    """Wave-based execution request"""
    wave_type: WaveType
    task: str
    context: Dict[str, Any] = {}
    session_id: Optional[str] = None
    auto_persona: bool = True
    use_mcp: List[MCPServerType] = []


class WaveExecutionResponse(BaseModel):
    """Wave execution response"""
    wave_id: str
    wave_type: WaveType
    status: str
    results: Dict[str, Any]
    next_wave: Optional[WaveType] = None
    thinking_steps: int = 0
    active_persona: Optional[str] = None
    mcp_servers_used: List[str] = []


class ResearchTaskRequest(BaseModel):
    """Comprehensive research task request"""
    task_type: str = Field(..., description="Type of research task")
    description: str = Field(..., description="Detailed task description")
    requirements: Dict[str, Any] = Field(default_factory=dict)
    use_waves: bool = Field(default=True, description="Use wave-based execution")
    auto_persona: bool = Field(default=True, description="Auto-activate personas")
    mcp_integration: bool = Field(default=True, description="Enable MCP integration")
    session_id: Optional[str] = None


class EnhancedChatRequest(BaseModel):
    """Enhanced chat request with full capabilities"""
    message: str
    session_id: Optional[str] = None
    context: Optional[str] = None
    enable_c7: bool = True  # Context7
    enable_seq: bool = True  # Sequential thinking
    enable_magic: bool = True  # Magic analysis
    enable_memory: bool = True  # Memory persistence
    enable_serena: bool = True  # Serena capabilities
    enable_persona: bool = True  # Auto-persona


class MemoryOperationRequest(BaseModel):
    """Memory operation request"""
    operation: str = Field(..., description="Operation type: save, retrieve, update, delete")
    session_id: str
    key: str
    value: Optional[Any] = None


class PersonaActivationRequest(BaseModel):
    """Manual persona activation request"""
    persona_type: PersonaType
    task_context: str
    session_id: Optional[str] = None


class SequentialThinkingRequest(BaseModel):
    """Sequential thinking request"""
    problem: str
    max_steps: int = Field(default=10, ge=1, le=50)
    allow_revision: bool = True
    session_id: Optional[str] = None


class MagicAnalysisRequest(BaseModel):
    """Magic analysis request"""
    content: str
    analysis_type: str = Field(..., description="Type of analysis: methodology, statistics, code, architecture")
    depth: str = Field(default="comprehensive", description="Analysis depth: quick, standard, comprehensive")
    session_id: Optional[str] = None


@router.post("/execute", response_model=Dict[str, Any])
async def execute_superclaude_command(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    command: SuperClaudeCommand
) -> Any:
    """
    Execute SuperClaude command with full MCP integration and wave-based processing
    
    Commands:
    - analyze: Comprehensive analysis with multi-persona approach
    - implement: Feature implementation with full lifecycle
    - build: Intelligent build system with optimization
    - improve: Code optimization and enhancement
    - troubleshoot: Advanced debugging and problem resolution
    - design: Architecture and system design
    - test: Comprehensive testing approach
    
    Flags:
    - --c7: Enable Context7 memory persistence
    - --seq: Enable sequential thinking orchestration
    - --magic: Enable Magic server analysis
    - --memory: Enable memory operations
    - --serena: Enable Serena assistant capabilities
    - --persona: Enable auto-persona activation
    """
    try:
        # Parse flags
        enable_features = {
            "context7": "--c7" in command.flags,
            "sequential": "--seq" in command.flags,
            "magic": "--magic" in command.flags,
            "memory": "--memory" in command.flags,
            "serena": "--serena" in command.flags,
            "persona": "--persona" in command.flags
        }
        
        # Execute command with wave system
        result = await superclaude_enhanced_service.execute_command(
            command=command.command,
            target=command.target,
            context=command.context,
            session_id=command.session_id or str(uuid.uuid4()),
            features=enable_features,
            user_id=current_user.id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wave/execute", response_model=WaveExecutionResponse)
async def execute_wave(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    request: WaveExecutionRequest
) -> Any:
    """Execute a specific wave in the SuperClaude system"""
    try:
        result = await superclaude_enhanced_service.execute_wave(
            wave_type=request.wave_type,
            task=request.task,
            context=request.context,
            session_id=request.session_id or str(uuid.uuid4()),
            auto_persona=request.auto_persona,
            mcp_servers=request.use_mcp
        )
        
        return WaveExecutionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/enhanced", response_model=Dict[str, Any])
async def enhanced_chat(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    request: EnhancedChatRequest
) -> Any:
    """Enhanced chat with full SuperClaude capabilities"""
    try:
        response = await superclaude_enhanced_service.enhanced_chat(
            message=request.message,
            session_id=request.session_id or str(uuid.uuid4()),
            context=request.context,
            enable_c7=request.enable_c7,
            enable_seq=request.enable_seq,
            enable_magic=request.enable_magic,
            enable_memory=request.enable_memory,
            enable_serena=request.enable_serena,
            enable_persona=request.enable_persona,
            user_id=current_user.id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/operation", response_model=Dict[str, Any])
async def memory_operation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    request: MemoryOperationRequest
) -> Any:
    """Perform memory operations with Context7 integration"""
    try:
        result = await superclaude_enhanced_service.memory_operation(
            operation=request.operation,
            session_id=request.session_id,
            key=request.key,
            value=request.value,
            user_id=current_user.id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/persona/activate", response_model=Dict[str, Any])
async def activate_persona(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    request: PersonaActivationRequest
) -> Any:
    """Manually activate a specific persona"""
    try:
        persona = await superclaude_enhanced_service.activate_persona(
            persona_type=request.persona_type,
            task_context=request.task_context,
            session_id=request.session_id
        )
        
        return {
            "persona": persona.dict(),
            "activated": True,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/persona/list", response_model=Dict[str, Any])
async def list_personas(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """List all available personas with their capabilities"""
    personas = await superclaude_enhanced_service.list_personas()
    return {"personas": personas}


@router.post("/thinking/sequential", response_model=Dict[str, Any])
async def sequential_thinking(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    request: SequentialThinkingRequest
) -> Any:
    """Execute sequential thinking process"""
    try:
        steps = await superclaude_enhanced_service.sequential_thinking(
            problem=request.problem,
            max_steps=request.max_steps,
            allow_revision=request.allow_revision,
            session_id=request.session_id
        )
        
        return {
            "thinking_steps": steps,
            "total_steps": len(steps),
            "problem": request.problem,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/magic/analyze", response_model=Dict[str, Any])
async def magic_analysis(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    request: MagicAnalysisRequest
) -> Any:
    """Perform Magic server analysis"""
    try:
        analysis = await superclaude_enhanced_service.magic_analysis(
            content=request.content,
            analysis_type=request.analysis_type,
            depth=request.depth,
            session_id=request.session_id
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/task", response_model=Dict[str, Any])
async def execute_research_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    request: ResearchTaskRequest
) -> Any:
    """Execute comprehensive research task with full SuperClaude capabilities"""
    try:
        result = await superclaude_enhanced_service.execute_research_task(
            task_type=request.task_type,
            description=request.description,
            requirements=request.requirements,
            use_waves=request.use_waves,
            auto_persona=request.auto_persona,
            mcp_integration=request.mcp_integration,
            session_id=request.session_id or str(uuid.uuid4()),
            user_id=current_user.id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/context", response_model=Dict[str, Any])
async def get_session_context(
    *,
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get complete session context from memory"""
    try:
        context = await superclaude_enhanced_service.get_session_context(
            session_id=session_id,
            user_id=current_user.id
        )
        
        if not context:
            raise HTTPException(status_code=404, detail="Session context not found")
            
        return context
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/status", response_model=Dict[str, Any])
async def get_mcp_status(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get status of all MCP servers"""
    try:
        status = await superclaude_enhanced_service.get_mcp_status()
        return {"mcp_servers": status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/interactive")
async def websocket_interactive_session(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for interactive SuperClaude sessions"""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    try:
        await websocket.send_json({
            "type": "session_init",
            "session_id": session_id,
            "message": "SuperClaude interactive session initialized"
        })
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process with SuperClaude
            response = await superclaude_enhanced_service.process_websocket_message(
                message=data.get("message"),
                session_id=session_id,
                command_type=data.get("type", "chat"),
                context=data.get("context", {})
            )
            
            # Send response
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        await superclaude_enhanced_service.cleanup_session(session_id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close()


@router.post("/workflow/create", response_model=Dict[str, Any])
async def create_workflow(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    workflow_name: str,
    steps: List[Dict[str, Any]]
) -> Any:
    """Create a multi-step workflow with SuperClaude orchestration"""
    try:
        workflow = await superclaude_enhanced_service.create_workflow(
            workflow_name=workflow_name,
            steps=steps,
            user_id=current_user.id
        )
        
        return workflow
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/{workflow_id}/execute", response_model=Dict[str, Any])
async def execute_workflow(
    *,
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    context: Dict[str, Any] = {}
) -> Any:
    """Execute a predefined workflow"""
    try:
        result = await superclaude_enhanced_service.execute_workflow(
            workflow_id=workflow_id,
            context=context,
            user_id=current_user.id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
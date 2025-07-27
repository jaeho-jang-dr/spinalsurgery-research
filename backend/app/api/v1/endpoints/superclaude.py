"""
SuperClaude Advanced AI Endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.services.superclaude_ai_service import superclaude_ai_service

router = APIRouter()


class ResearchPlanRequest(BaseModel):
    research_question: str
    study_type: str
    resources: Optional[Dict[str, Any]] = {}
    

class ResearchPlanResponse(BaseModel):
    research_question: str
    study_type: str
    phases: List[Dict[str, Any]]
    methodology_insights: Dict[str, Any]
    resources_needed: Dict[str, Any]
    thinking_process: str
    generated_by: str
    session_id: str
    

class PersonaActivationRequest(BaseModel):
    task_description: str
    session_id: Optional[str] = None
    

class PersonaResponse(BaseModel):
    persona_name: str
    role: str
    expertise: List[str]
    activated: bool
    

class ResearchContextRequest(BaseModel):
    session_id: str
    

class ResearchContextResponse(BaseModel):
    session_id: str
    research_topic: Optional[str]
    current_phase: Optional[str]
    key_findings: List[str]
    references: List[Dict[str, Any]]
    has_methodology: bool
    has_statistics_plan: bool


@router.post("/research-plan", response_model=ResearchPlanResponse)
async def generate_research_plan(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    plan_request: ResearchPlanRequest
) -> Any:
    """Generate comprehensive research plan with SuperClaude enhancements"""
    try:
        plan = await superclaude_ai_service.generate_research_plan(
            research_question=plan_request.research_question,
            study_type=plan_request.study_type,
            resources=plan_request.resources
        )
        
        return ResearchPlanResponse(**plan)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/activate-persona", response_model=PersonaResponse)
async def activate_persona(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    request: PersonaActivationRequest
) -> Any:
    """Activate appropriate persona for task"""
    try:
        persona = await superclaude_ai_service._activate_persona(request.task_description)
        
        return PersonaResponse(
            persona_name=persona.name,
            role=persona.role,
            expertise=persona.expertise,
            activated=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/research-context/{session_id}", response_model=ResearchContextResponse)
async def get_research_context(
    *,
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get research context from memory"""
    try:
        context = await superclaude_ai_service._retrieve_from_memory(session_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Research context not found")
            
        return ResearchContextResponse(
            session_id=context.session_id,
            research_topic=context.research_topic,
            current_phase=context.current_phase,
            key_findings=context.key_findings,
            references=context.references,
            has_methodology=context.methodology is not None,
            has_statistics_plan=context.statistics_plan is not None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personas")
async def list_personas(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """List available research personas"""
    personas = []
    for name, persona in superclaude_ai_service.personas.items():
        personas.append({
            "id": name,
            "name": persona.name,
            "role": persona.role,
            "expertise": persona.expertise,
            "active": superclaude_ai_service.active_persona == persona
        })
        
    return {"personas": personas}


@router.post("/analyze-methodology")
async def analyze_methodology(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    content: str,
    session_id: Optional[str] = None
) -> Any:
    """Analyze research methodology with Magic server"""
    try:
        analysis = await superclaude_ai_service._magic_analysis(
            content=content,
            analysis_type="methodology"
        )
        
        # Save to memory if session provided
        if session_id:
            await superclaude_ai_service._save_to_memory(
                session_id=session_id,
                key="methodology",
                value=analysis
            )
            
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-statistics")
async def analyze_statistics(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    content: str,
    session_id: Optional[str] = None
) -> Any:
    """Analyze statistical approach with Magic server"""
    try:
        analysis = await superclaude_ai_service._magic_analysis(
            content=content,
            analysis_type="statistics"
        )
        
        # Save to memory if session provided
        if session_id:
            await superclaude_ai_service._save_to_memory(
                session_id=session_id,
                key="statistics",
                value=analysis
            )
            
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
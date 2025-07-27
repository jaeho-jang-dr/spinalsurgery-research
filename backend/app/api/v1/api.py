from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, projects, papers, ai, search, mock_auth, ai_chat, research_papers, ai_advanced

# Import research AI router - handle import error gracefully
try:
    from app.api import research_ai
    has_research_ai = True
except ImportError:
    has_research_ai = False

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(mock_auth.router, prefix="/auth", tags=["mock-auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(research_papers.router, prefix="/research-papers", tags=["research-papers"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(ai_advanced.router, prefix="/ai-advanced", tags=["ai-advanced"])

# Include search router
api_router.include_router(search.router, prefix="/search", tags=["search"])

# Include AI chat router
api_router.include_router(ai_chat.router, prefix="/ai", tags=["ai-chat"])

# Include research AI router if available
if has_research_ai:
    api_router.include_router(research_ai.router, tags=["research-ai"])
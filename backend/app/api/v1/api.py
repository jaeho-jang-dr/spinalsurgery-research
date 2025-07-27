from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, projects, papers, ai, search, mock_auth, ai_chat, research_papers, ai_advanced, paper_download, superclaude, claude_code_search, lumbar_fusion_papers, file_browser, superclaude_enhanced, tfesi_papers, superclaude_unified

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
api_router.include_router(paper_download.router, prefix="/paper-download", tags=["paper-download"])

# Include search router
api_router.include_router(search.router, prefix="/search", tags=["search"])

# Include AI chat router
api_router.include_router(ai_chat.router, prefix="/ai", tags=["ai-chat"])

# Include SuperClaude router
api_router.include_router(superclaude.router, prefix="/superclaude", tags=["superclaude"])

# Include Claude Code search router
api_router.include_router(claude_code_search.router, prefix="/claude-code-search", tags=["claude-code-search"])

# Include Lumbar Fusion papers router
api_router.include_router(lumbar_fusion_papers.router, prefix="/lumbar-fusion", tags=["lumbar-fusion"])

# Include File Browser router
api_router.include_router(file_browser.router, prefix="/file-browser", tags=["file-browser"])

# Include SuperClaude Enhanced router
api_router.include_router(superclaude_enhanced.router, prefix="/superclaude-enhanced", tags=["superclaude-enhanced"])

# Include TFESI Papers router
api_router.include_router(tfesi_papers.router, prefix="/tfesi-papers", tags=["tfesi-papers"])

# Include SuperClaude Unified router - Complete integration of all features
api_router.include_router(superclaude_unified.router, prefix="/superclaude-unified", tags=["superclaude-unified"])

# Include research AI router if available
if has_research_ai:
    api_router.include_router(research_ai.router, tags=["research-ai"])
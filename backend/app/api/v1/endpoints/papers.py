from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.paper import Paper, PaperSource, PaperPortfolio
from app.services.scraper_service import scraper_service

router = APIRouter()


@router.get("/sources")
async def get_paper_sources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
) -> Any:
    """Get list of paper sources"""
    query = (
        select(PaperSource)
        .order_by(PaperSource.priority.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    sources = result.scalars().all()
    
    return sources


@router.post("/sources")
async def create_paper_source(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    source_in: dict
) -> Any:
    """Create new paper source (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    source = PaperSource(**source_in)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    
    return source


@router.post("/search")
async def search_papers(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    search_data: dict
) -> Any:
    """Search papers from multiple sources"""
    try:
        results = await scraper_service.search_papers(
            query=search_data['query'],
            sources=search_data.get('sources', ['pubmed', 'scholar']),
            limit=search_data.get('limit', 20)
        )
        
        # Optionally save search results to database
        if search_data.get('save_results', False):
            for paper_data in results:
                paper = Paper(
                    title=paper_data['title'],
                    authors=paper_data.get('authors', []),
                    journal_name=paper_data.get('journal'),
                    publication_year=paper_data.get('year'),
                    url=paper_data.get('url'),
                    abstract=paper_data.get('abstract'),
                    is_own_paper=False
                )
                db.add(paper)
            
            await db.commit()
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio")
async def get_portfolio(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    category: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
) -> Any:
    """Get user's paper portfolio"""
    query = (
        select(PaperPortfolio)
        .where(PaperPortfolio.user_id == current_user.id)
        .options(selectinload(PaperPortfolio.paper))
        .offset(skip)
        .limit(limit)
    )
    
    if category:
        query = query.where(PaperPortfolio.category == category)
    
    result = await db.execute(query)
    portfolio_items = result.scalars().all()
    
    return portfolio_items


@router.post("/portfolio/{paper_id}")
async def add_to_portfolio(
    *,
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    portfolio_data: dict
) -> Any:
    """Add paper to user's portfolio"""
    # Check if paper exists
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Check if already in portfolio
    existing = await db.execute(
        select(PaperPortfolio).where(
            PaperPortfolio.user_id == current_user.id,
            PaperPortfolio.paper_id == paper_id
        )
    )
    
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Paper already in portfolio")
    
    # Add to portfolio
    portfolio_item = PaperPortfolio(
        user_id=current_user.id,
        paper_id=paper_id,
        category=portfolio_data.get('category'),
        tags=portfolio_data.get('tags', []),
        notes=portfolio_data.get('notes')
    )
    
    db.add(portfolio_item)
    await db.commit()
    await db.refresh(portfolio_item)
    
    return portfolio_item


@router.delete("/portfolio/{paper_id}")
async def remove_from_portfolio(
    *,
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Remove paper from portfolio"""
    result = await db.execute(
        select(PaperPortfolio).where(
            PaperPortfolio.user_id == current_user.id,
            PaperPortfolio.paper_id == paper_id
        )
    )
    
    portfolio_item = result.scalar_one_or_none()
    if not portfolio_item:
        raise HTTPException(status_code=404, detail="Paper not in portfolio")
    
    await db.delete(portfolio_item)
    await db.commit()
    
    return {"message": "Paper removed from portfolio"}
"""
Rate limiting middleware for API endpoints
"""
from typing import Dict, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import asyncio


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 10, period: int = 60):
        """
        Initialize rate limiter
        
        Args:
            app: FastAPI application
            calls: Number of allowed calls per period
            period: Time period in seconds
        """
        super().__init__(app)
        self.calls = calls
        self.period = timedelta(seconds=period)
        self.clients: Dict[str, list] = defaultdict(list)
        self._cleanup_task = None
        
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for non-AI endpoints
        if not request.url.path.startswith("/api/v1/ai"):
            return await call_next(request)
            
        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._is_allowed(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Record the request
        self._record_request(client_id)
        
        # Process the request
        response = await call_next(request)
        
        # Start cleanup task if not already running
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_old_requests())
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get user ID from authorization header
        auth_header = request.headers.get("authorization")
        if auth_header:
            # Simple extraction, in production use proper JWT decoding
            return f"user_{auth_header}"
        
        # Fallback to IP address
        client_host = request.client.host if request.client else "unknown"
        return f"ip_{client_host}"
    
    def _is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request"""
        now = datetime.now()
        # Remove old requests
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id]
            if now - req_time < self.period
        ]
        
        # Check if under limit
        return len(self.clients[client_id]) < self.calls
    
    def _record_request(self, client_id: str):
        """Record a request from client"""
        self.clients[client_id].append(datetime.now())
    
    async def _cleanup_old_requests(self):
        """Periodically clean up old request records"""
        while True:
            await asyncio.sleep(60)  # Clean up every minute
            now = datetime.now()
            
            # Remove old requests from all clients
            for client_id in list(self.clients.keys()):
                self.clients[client_id] = [
                    req_time for req_time in self.clients[client_id]
                    if now - req_time < self.period
                ]
                
                # Remove client if no recent requests
                if not self.clients[client_id]:
                    del self.clients[client_id]


# Decorator for individual endpoint rate limiting
def rate_limit(calls: int = 5, period: int = 60):
    """
    Rate limit decorator for individual endpoints
    
    Args:
        calls: Number of allowed calls per period
        period: Time period in seconds
    """
    clients: Dict[str, list] = defaultdict(list)
    period_delta = timedelta(seconds=period)
    
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get client identifier
            client_id = request.client.host if request.client else "unknown"
            
            # Check rate limit
            now = datetime.now()
            clients[client_id] = [
                req_time for req_time in clients[client_id]
                if now - req_time < period_delta
            ]
            
            if len(clients[client_id]) >= calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {calls} requests per {period} seconds."
                )
            
            # Record request
            clients[client_id].append(now)
            
            # Call the original function
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator
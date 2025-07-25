from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 테스트 데이터
class Project(BaseModel):
    id: str
    title: str
    field: str
    keywords: List[str]
    status: str
    papers_count: int
    patients_count: int
    collaborators_count: int

class User(BaseModel):
    id: str
    email: str
    name: str
    role: str

# 테스트 엔드포인트
@app.get("/")
async def root():
    return {"message": "SpinalSurgery Research Platform API - Test Server"}

@app.get("/api/v1/users/me")
async def get_current_user():
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "name": "테스트 사용자",
        "role": "researcher"
    }

@app.get("/api/v1/projects")
async def get_projects():
    return [
        {
            "id": "1",
            "title": "척추 후외방 고정술의 2년 후 결과",
            "field": "척추외과",
            "keywords": ["척추", "고정술", "CD instrument"],
            "status": "in_progress",
            "papers_count": 5,
            "patients_count": 34,
            "collaborators_count": 3,
            "created_at": "2025-01-15T10:00:00",
            "updated_at": "2025-01-20T15:30:00"
        },
        {
            "id": "2",
            "title": "최소 침습 척추 수술의 효과 분석",
            "field": "척추외과",
            "keywords": ["최소침습", "척추수술", "VAS score"],
            "status": "draft",
            "papers_count": 2,
            "patients_count": 0,
            "collaborators_count": 1,
            "created_at": "2025-01-10T09:00:00",
            "updated_at": "2025-01-18T14:20:00"
        }
    ]

@app.post("/api/v1/auth/login")
async def login():
    return {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "token_type": "bearer"
    }

@app.get("/api/v1/papers/sources")
async def get_paper_sources():
    return [
        {
            "id": "1",
            "name": "PubMed Central",
            "type": "database",
            "priority": 1,
            "url": "https://www.ncbi.nlm.nih.gov/pmc/",
            "email": "info@ncbi.nlm.nih.gov"
        },
        {
            "id": "2",
            "name": "서울대학교 의학도서관",
            "type": "institution",
            "priority": 1,
            "url": "http://medlib.snu.ac.kr",
            "email": "medlib@snu.ac.kr",
            "phone": "02-740-8045"
        }
    ]

if __name__ == "__main__":
    print("🚀 Starting test server on http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
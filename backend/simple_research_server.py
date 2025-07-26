"""
Simple research AI server for demo
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import json
import os
from pathlib import Path
import random

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    title: str
    type: str
    keywords: List[str]
    objectives: Optional[str] = ""
    description: Optional[str] = ""

# Store for demo
research_projects = {}

@app.post("/api/research-ai/start")
async def start_research(request: ResearchRequest):
    """Start a new AI-powered research project"""
    
    # Generate project ID
    project_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create project directory
    project_path = Path(f"./research_projects/{project_id}")
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    for subdir in ['literature', 'data', 'drafts', 'consent_forms', 'figures']:
        (project_path / subdir).mkdir(exist_ok=True)
    
    # Simulate research process
    print(f"Starting research: {request.title}")
    
    # Generate mock paper structure
    paper_structure = {
        "title": request.title,
        "type": request.type,
        "sections": {
            "abstract": {
                "background": "Background section",
                "methods": "Methods summary",
                "results": "Key results",
                "conclusions": "Main conclusions"
            },
            "introduction": {
                "background": "Detailed background",
                "objectives": request.objectives or "Study objectives",
                "hypotheses": "Research hypotheses"
            },
            "methods": {
                "study_design": f"{request.type} design",
                "participants": "Participant selection criteria",
                "procedures": "Study procedures",
                "statistical_analysis": "Statistical methods"
            },
            "results": {
                "demographics": "Patient demographics",
                "primary_outcomes": "Primary outcome results",
                "secondary_outcomes": "Secondary outcomes"
            },
            "discussion": {
                "key_findings": "Summary of key findings",
                "limitations": "Study limitations",
                "implications": "Clinical implications"
            }
        }
    }
    
    # Generate mock data
    n_patients = random.randint(100, 200)
    mock_data = {
        "demographics": {
            "total_patients": n_patients,
            "age": {
                "mean": round(random.uniform(45, 65), 1),
                "sd": round(random.uniform(8, 15), 1)
            },
            "gender": {
                "male": n_patients // 2,
                "female": n_patients - (n_patients // 2)
            }
        },
        "outcomes": {
            "primary": {
                "improvement_rate": round(random.uniform(0.65, 0.85), 2),
                "p_value": round(random.uniform(0.001, 0.05), 4)
            }
        }
    }
    
    # Generate draft paper
    draft_paper = f"""# {request.title}

## Abstract

**Background:** This study investigates {request.title} using a {request.type} approach.

**Methods:** We conducted a comprehensive analysis with {n_patients} participants to evaluate the effectiveness of the intervention.

**Results:** The primary outcome showed a significant improvement rate of {mock_data['outcomes']['primary']['improvement_rate']*100:.1f}% (p = {mock_data['outcomes']['primary']['p_value']}).

**Conclusions:** The findings suggest that this approach is effective and warrants further investigation.

## Introduction

The field of spinal surgery has seen significant advances in recent years. {request.objectives or 'This study aims to contribute to the growing body of knowledge in this area.'}

### Background

Spinal disorders affect millions of people worldwide, causing significant morbidity and reduced quality of life. Current treatment options include conservative management and surgical intervention.

### Objectives

The primary objectives of this study are:
1. To evaluate the effectiveness of the proposed intervention
2. To assess safety and adverse events
3. To identify factors associated with treatment success

## Methods

### Study Design

This {request.type} was conducted following ethical guidelines and with appropriate institutional approval.

### Participants

A total of {n_patients} participants were enrolled based on the following criteria:
- Inclusion: Adults aged 18-80 with confirmed diagnosis
- Exclusion: Previous surgery, contraindications

### Statistical Analysis

Data were analyzed using appropriate statistical methods. Continuous variables are presented as mean ± SD, and categorical variables as frequencies and percentages.

## Results

### Demographics

The study included {n_patients} participants with a mean age of {mock_data['demographics']['age']['mean']} ± {mock_data['demographics']['age']['sd']} years.

### Primary Outcomes

The intervention resulted in significant improvements in the primary outcome measure (p < 0.05).

## Discussion

This study demonstrates the effectiveness of the proposed approach in treating spinal conditions. The results are consistent with previous literature and support the use of this intervention in clinical practice.

### Limitations

- Single-center design
- Relatively short follow-up period
- Lack of control group (if applicable)

## Conclusion

In conclusion, this research provides evidence supporting the use of {request.title} in clinical practice. Further multicenter studies are recommended to validate these findings.

## References

1. Smith J, et al. Advances in spinal surgery. Spine J. 2023;23(1):45-52.
2. Johnson K, et al. Outcomes in spinal interventions. J Neurosurg Spine. 2023;38(2):234-241.
3. Williams R, et al. Patient-reported outcomes in spine surgery. Eur Spine J. 2023;32(5):1678-1685.
"""
    
    # Generate informed consent
    consent_form = f"""INFORMED CONSENT FORM

Study Title: {request.title}

Principal Investigator: Dr. John Smith, MD, PhD
Institution: Medical Research Center
Contact: (555) 123-4567 | research@medical.center

1. INVITATION TO PARTICIPATE

You are being invited to participate in a research study about {request.title}. This form provides important information about the study.

2. PURPOSE OF THE STUDY

{request.objectives or 'The purpose is to evaluate new treatment approaches for spinal conditions.'}

3. WHAT WILL HAPPEN

If you agree to participate:
- You will undergo standard medical evaluations
- Treatment will be provided according to the study protocol
- Follow-up visits will be scheduled at regular intervals
- Data will be collected on your progress and outcomes

4. RISKS AND BENEFITS

Potential Risks:
- Minimal risks associated with standard medical procedures
- Possible side effects from treatment
- Time commitment for study visits

Potential Benefits:
- Access to new treatment approaches
- Close medical monitoring
- Contribution to medical knowledge

5. CONFIDENTIALITY

All information collected will be kept strictly confidential. You will be assigned a study ID number, and your name will not be used in any publications.

6. VOLUNTARY PARTICIPATION

Your participation is entirely voluntary. You may withdraw from the study at any time without affecting your medical care.

7. COSTS AND COMPENSATION

There are no costs to you for participating. Study-related procedures will be provided at no charge.

8. QUESTIONS

If you have questions about:
- The study: Contact Dr. Smith at (555) 123-4567
- Your rights: Contact the IRB at (555) 987-6543

9. CONSENT

I have read and understood the information provided. All my questions have been answered to my satisfaction.

□ I agree to participate in this research study
□ I agree to be contacted for future research

_______________________    _______________________    __________
Participant Name            Signature                  Date

_______________________    _______________________    __________
Investigator Name           Signature                  Date
"""
    
    # Save all files
    with open(project_path / "paper_structure.json", "w") as f:
        json.dump(paper_structure, f, indent=2)
    
    with open(project_path / "data" / "mock_data.json", "w") as f:
        json.dump(mock_data, f, indent=2)
    
    with open(project_path / "drafts" / "draft_v1.md", "w") as f:
        f.write(draft_paper)
    
    with open(project_path / "consent_forms" / "informed_consent_v1.md", "w") as f:
        f.write(consent_form)
    
    # Create literature summary with search sites info
    literature_summary = {
        "total_documents": 15,
        "sources": {
            "pubmed": 8,
            "google_scholar": 5,
            "clinical_trials": 2
        },
        "search_sites_used": [
            {
                "name": "PubMed",
                "url": "https://pubmed.ncbi.nlm.nih.gov/",
                "documents_found": 8,
                "search_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "search_terms": request.keywords
            },
            {
                "name": "Google Scholar",
                "url": "https://scholar.google.com/",
                "documents_found": 5,
                "search_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "search_terms": request.keywords
            },
            {
                "name": "ClinicalTrials.gov",
                "url": "https://clinicaltrials.gov/",
                "documents_found": 2,
                "search_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "search_terms": request.keywords
            }
        ],
        "key_papers": [
            {
                "title": "Recent advances in minimally invasive spine surgery",
                "authors": "Chen et al.",
                "year": 2023,
                "journal": "Spine",
                "relevance": "High",
                "source": "PubMed"
            },
            {
                "title": "Outcomes of spinal fusion in elderly patients",
                "authors": "Park et al.",
                "year": 2023,
                "journal": "J Neurosurg Spine",
                "relevance": "Medium",
                "source": "Google Scholar"
            }
        ]
    }
    
    with open(project_path / "literature" / "summary.json", "w") as f:
        json.dump(literature_summary, f, indent=2)
    
    # Create search sites documentation
    search_sites_doc = f"""# 논문 검색 사이트 정보

프로젝트: {request.title}
검색일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 사용된 검색 사이트

### 1. PubMed
- **URL**: https://pubmed.ncbi.nlm.nih.gov/
- **설명**: 미국 국립의학도서관(NLM)의 생의학 문헌 데이터베이스
- **검색어**: {', '.join(request.keywords)}
- **발견 문서**: 8개
- **특징**: 
  - 3,300만 개 이상의 의학 문헌 보유
  - MeSH (Medical Subject Headings) 용어 지원
  - 무료 초록 접근

### 2. Google Scholar
- **URL**: https://scholar.google.com/
- **설명**: 학술 검색 엔진
- **검색어**: {', '.join(request.keywords)}
- **발견 문서**: 5개
- **특징**:
  - 다양한 학문 분야 포괄
  - 인용 횟수 추적
  - 전문(full-text) 링크 제공

### 3. ClinicalTrials.gov
- **URL**: https://clinicaltrials.gov/
- **설명**: 임상시험 레지스트리
- **검색어**: {', '.join(request.keywords)}
- **발견 문서**: 2개
- **특징**:
  - 진행 중인 임상시험 정보
  - 연구 프로토콜 상세 정보
  - 연구자 연락처 제공

## 검색 전략

1. **키워드 조합**: {' AND '.join(request.keywords)}
2. **검색 필터**:
   - 출판 연도: 최근 5년
   - 언어: 영어, 한국어
   - 문서 유형: 연구 논문, 리뷰, 임상시험

## 검색 결과 요약

- **총 발견 문서**: 15개
- **초록 확보**: 10개
- **전문 확보**: 5개

## 주요 발견 논문

1. Chen et al. (2023) - Recent advances in minimally invasive spine surgery
2. Park et al. (2023) - Outcomes of spinal fusion in elderly patients

---
*이 문서는 AI 연구 시스템에 의해 자동 생성되었습니다.*
"""
    
    with open(project_path / "literature" / "SEARCH_SITES_INFO.md", "w", encoding="utf-8") as f:
        f.write(search_sites_doc)
    
    # Save project summary
    summary = f"""# Research Project Summary

Project ID: {project_id}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Title
{request.title}

## Type
{request.type}

## Keywords
{', '.join(request.keywords)}

## Generated Outputs

1. **Paper Structure**: Hierarchical structure with all sections
2. **Mock Data**: Statistical data for {n_patients} patients
3. **Draft Paper**: Complete draft ready for review
4. **Informed Consent**: IRB-ready consent form
5. **Literature Review**: 15 relevant papers identified

## File Structure
```
{project_id}/
├── paper_structure.json
├── data/
│   └── mock_data.json
├── drafts/
│   └── draft_v1.md
├── consent_forms/
│   └── informed_consent_v1.md
├── literature/
│   └── summary.json
└── figures/
    └── (ready for charts)
```

## Next Steps

1. Review and refine the draft paper
2. Replace mock data with actual research data
3. Add institutional details to consent form
4. Create figures and tables
5. Format for target journal
"""
    
    with open(project_path / "PROJECT_SUMMARY.md", "w") as f:
        f.write(summary)
    
    # Store in memory
    research_projects[project_id] = {
        "request": request.dict(),
        "created_at": datetime.now().isoformat(),
        "path": str(project_path)
    }
    
    return {
        "project_id": project_id,
        "project_path": str(project_path),
        "status": "completed",
        "outputs": {
            "paper_structure": paper_structure,
            "draft_preview": draft_paper[:500] + "...",
            "informed_consent_preview": consent_form[:300] + "...",
            "documents_collected": 15,
            "mock_data_generated": True
        },
        "created_at": datetime.now().isoformat()
    }

@app.get("/api/research-ai/projects")
async def list_projects():
    """List all research projects"""
    projects = []
    
    research_base = Path("./research_projects")
    if research_base.exists():
        for project_dir in research_base.iterdir():
            if project_dir.is_dir():
                summary_file = project_dir / "PROJECT_SUMMARY.md"
                if summary_file.exists():
                    projects.append({
                        "project_id": project_dir.name,
                        "path": str(project_dir),
                        "created": datetime.fromtimestamp(project_dir.stat().st_ctime).isoformat()
                    })
    
    return {"projects": projects}

@app.get("/api/research-ai/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    project_path = Path(f"./research_projects/{project_id}")
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    outputs = {}
    
    # Read files
    files_to_read = [
        ("drafts/draft_v1.md", "draft"),
        ("consent_forms/informed_consent_v1.md", "consent"),
        ("paper_structure.json", "structure"),
        ("data/mock_data.json", "data"),
        ("PROJECT_SUMMARY.md", "summary")
    ]
    
    for file_path, key in files_to_read:
        full_path = project_path / file_path
        if full_path.exists():
            with open(full_path, "r") as f:
                content = f.read()
                if file_path.endswith(".json"):
                    outputs[key] = json.loads(content)
                else:
                    outputs[key] = content
    
    return {
        "project_id": project_id,
        "project_path": str(project_path),
        "outputs": outputs
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "research-ai"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Research AI Server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
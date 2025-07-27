"""
Mock AI Service for testing without Ollama
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import random
import uuid


class MockAIService:
    """Mock AI service that simulates Ollama responses"""
    
    def __init__(self):
        self.model = "mock-llm"
        self.mock_papers = [
            {
                "title": "Minimally Invasive Spine Surgery: A Systematic Review",
                "authors": ["Kim, J.H.", "Lee, S.M.", "Park, K.W."],
                "year": 2023,
                "journal": "Spine",
                "doi": "10.1097/BRS.0000000000004567"
            },
            {
                "title": "Outcomes of Spinal Fusion in Elderly Patients",
                "authors": ["Chen, L.", "Wang, X.", "Zhang, Y."],
                "year": 2023,
                "journal": "Journal of Neurosurgery: Spine",
                "doi": "10.3171/2023.1.SPINE22234"
            },
            {
                "title": "Pain Management After Spinal Surgery: Current Strategies",
                "authors": ["Johnson, M.D.", "Smith, R.A.", "Brown, K.L."],
                "year": 2022,
                "journal": "Pain Medicine",
                "doi": "10.1093/pm/pnac123"
            }
        ]
    
    async def generate_paper_draft(
        self,
        title: str,
        field: str,
        keywords: List[str],
        details: str,
        references: List[Dict] = None
    ) -> Dict:
        """Generate mock paper draft"""
        
        # Simulate processing delay
        await asyncio.sleep(1)
        
        abstract = f"""Background: This study investigates {title} in the field of {field}. 
        Methods: We conducted a comprehensive analysis using advanced methodologies relevant to {', '.join(keywords)}.
        Results: Our findings demonstrate significant improvements in patient outcomes.
        Conclusions: {title} shows promising results for clinical application in {field}."""
        
        introduction = f"""The field of {field} has seen significant advances in recent years. 
        {details}
        
        This research aims to address critical gaps in our understanding of {title}.
        Previous studies have shown mixed results, highlighting the need for further investigation."""
        
        methods = f"""Study Design: This is a prospective cohort study investigating {title}.
        
        Participants: We recruited patients from multiple medical centers specializing in {field}.
        
        Data Collection: Data was collected using standardized protocols including:
        - Clinical assessments
        - Patient-reported outcomes
        - Imaging studies
        - Laboratory tests
        
        Statistical Analysis: We used advanced statistical methods including multivariate regression analysis."""
        
        results = f"""Patient Demographics:
        - Total participants: {random.randint(100, 500)}
        - Mean age: {random.randint(45, 65)} years
        - Gender distribution: {random.randint(40, 60)}% male
        
        Primary Outcomes:
        - Improvement rate: {random.randint(60, 85)}%
        - Complication rate: {random.randint(5, 15)}%
        - Patient satisfaction: {random.randint(70, 90)}%
        
        Statistical significance was achieved for all primary outcomes (p < 0.05)."""
        
        discussion = f"""Our study on {title} provides important insights into {field}.
        
        The results demonstrate that the proposed approach is both effective and safe.
        These findings align with recent literature suggesting improved outcomes with modern techniques.
        
        Limitations include the relatively short follow-up period and single-center design.
        Future studies should investigate long-term outcomes and multi-center validation."""
        
        conclusion = f"""In conclusion, this study on {title} shows promising results for improving patient care in {field}.
        The findings support the implementation of these approaches in clinical practice.
        Further research is warranted to optimize protocols and expand applications."""
        
        return {
            "title": title,
            "abstract": abstract,
            "introduction": introduction,
            "methods": methods,
            "results": results,
            "discussion": discussion,
            "conclusion": conclusion,
            "references": references or self.mock_papers,
            "generated_at": datetime.utcnow().isoformat(),
            "model": self.model,
            "status": "success"
        }
    
    async def generate_informed_consent(
        self,
        project_title: str,
        field: str,
        procedures: str,
        risks: str,
        benefits: str
    ) -> str:
        """Generate mock informed consent document"""
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        consent = f"""INFORMED CONSENT FORM

Study Title: {project_title}
Field of Study: {field}

Principal Investigator: Dr. John Smith, MD, PhD
Institution: Medical Research Center
Contact: (555) 123-4567 | research@medical.center

1. INVITATION TO PARTICIPATE
You are being invited to participate in a research study about {project_title}. This form provides important information about the study to help you make an informed decision.

2. PURPOSE OF THE STUDY
This study aims to investigate {project_title} in the field of {field}. We hope to improve patient outcomes and advance medical knowledge.

3. STUDY PROCEDURES
If you agree to participate, you will be asked to:
{procedures}

The total time commitment is approximately 2-4 hours over 6 months.

4. RISKS AND DISCOMFORTS
{risks}

All procedures will be performed by qualified medical professionals following standard safety protocols.

5. POTENTIAL BENEFITS
{benefits}

While we cannot guarantee individual benefits, your participation may contribute to medical advances.

6. CONFIDENTIALITY
Your privacy is important to us. All information collected will be kept strictly confidential and stored securely. You will be assigned a study ID number to protect your identity.

7. VOLUNTARY PARTICIPATION
Participation is entirely voluntary. You may withdraw at any time without penalty or loss of benefits. Your decision will not affect your medical care.

8. QUESTIONS
If you have questions about this study, please contact:
- Principal Investigator: Dr. John Smith at (555) 123-4567
- Ethics Committee: (555) 987-6543

9. CONSENT
By signing below, you indicate that:
- You have read and understood this information
- Your questions have been answered
- You voluntarily agree to participate

_________________________________    _____________
Participant Name (Print)              Date

_________________________________    _____________
Participant Signature                 Date

_________________________________    _____________
Researcher Name                       Date

_________________________________    _____________
Researcher Signature                  Date

Version 1.0 - Generated on {datetime.now().strftime('%Y-%m-%d')}"""
        
        return consent
    
    async def analyze_statistics(
        self,
        data_description: str,
        analysis_type: str,
        variables: List[str]
    ) -> Dict:
        """Generate mock statistical analysis plan"""
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        analysis_plan = f"""STATISTICAL ANALYSIS PLAN

Data Description: {data_description}
Analysis Type: {analysis_type}
Variables: {', '.join(variables)}

1. DESCRIPTIVE STATISTICS
- Continuous variables: Mean, SD, median, IQR
- Categorical variables: Frequencies and percentages
- Missing data assessment

2. STATISTICAL TESTS
Based on {analysis_type}, we recommend:
- Primary analysis: {'ANOVA' if 'comparison' in analysis_type.lower() else 'Regression analysis'}
- Secondary analyses: Chi-square tests, correlation analysis
- Sensitivity analyses: Per-protocol and intention-to-treat

3. SAMPLE SIZE CALCULATION
- Effect size: Medium (Cohen's d = 0.5)
- Power: 80%
- Alpha: 0.05
- Required sample size: {random.randint(50, 200)} per group

4. ASSUMPTIONS TO CHECK
- Normality: Shapiro-Wilk test
- Homogeneity of variance: Levene's test
- Independence of observations
- Linearity (for regression)

5. ANALYSIS STEPS
1. Data cleaning and validation
2. Exploratory data analysis
3. Assumption checking
4. Primary analysis
5. Sensitivity analyses
6. Effect size calculation
7. Results interpretation

6. SOFTWARE RECOMMENDATIONS
- SPSS 28.0 or later
- R 4.3.0 with packages: tidyverse, lme4, emmeans
- Python with statsmodels, scipy, pandas

7. REPORTING GUIDELINES
Follow CONSORT guidelines for clinical trials or STROBE for observational studies."""
        
        return {
            "analysis_plan": analysis_plan,
            "recommended_software": ["SPSS", "R", "Python"],
            "generated_at": datetime.utcnow().isoformat(),
            "estimated_duration": "2-4 weeks",
            "statistician_review": "Recommended"
        }
    
    async def search_similar_papers(
        self,
        title: str,
        abstract: str,
        limit: int = 10
    ) -> List[Dict]:
        """Return mock similar papers"""
        
        # Simulate processing delay
        await asyncio.sleep(0.3)
        
        similar_papers = []
        for i in range(min(limit, len(self.mock_papers))):
            paper = self.mock_papers[i].copy()
            paper["id"] = str(uuid.uuid4())
            paper["similarity_score"] = round(random.uniform(0.7, 0.95), 3)
            paper["relevance"] = random.choice(["High", "Medium", "Low"])
            similar_papers.append(paper)
        
        return similar_papers
    
    async def chat(
        self,
        message: str,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """Simple chat response for testing"""
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        responses = {
            "help": "I can help you with:\n- Generating paper drafts\n- Creating informed consent forms\n- Statistical analysis planning\n- Finding similar research papers",
            "hello": "Hello! I'm your AI research assistant. How can I help you today?",
            "thanks": "You're welcome! Let me know if you need anything else.",
        }
        
        # Check for keywords
        message_lower = message.lower()
        for keyword, response in responses.items():
            if keyword in message_lower:
                return response
        
        # Default response
        return f"I understand you're asking about: {message}\n\nAs an AI research assistant, I can help with various aspects of medical research including paper drafting, statistical analysis, and literature review. Please be more specific about what you need."


# Singleton instance
mock_ai_service = MockAIService()
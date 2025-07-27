import httpx
from typing import Dict, List, Optional
import json
from datetime import datetime
import os

from app.core.config import settings

# Try to import Ollama, fallback to mock if not available
try:
    from langchain_community.llms import Ollama
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    import chromadb
    from chromadb.config import Settings
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama/LangChain not available, using mock AI service")


class AIService:
    def __init__(self):
        self.ollama_available = False
        self.model = "llama2"
        
        if OLLAMA_AVAILABLE:
            try:
                # Try to connect to Ollama
                import httpx
                response = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2.0)
                if response.status_code == 200:
                    self.ollama = Ollama(
                        base_url=settings.OLLAMA_BASE_URL,
                        model=self.model
                    )
                    self.embeddings = OllamaEmbeddings(
                        base_url=settings.OLLAMA_BASE_URL,
                        model=self.model
                    )
                    self.chroma = chromadb.Client(Settings(anonymized_telemetry=False))
                    self.ollama_available = True
                    print(f"Connected to Ollama at {settings.OLLAMA_BASE_URL}")
            except Exception as e:
                print(f"Failed to connect to Ollama: {e}")
        
        if not self.ollama_available:
            # Use mock service
            from app.services.mock_ai_service import mock_ai_service
            self.mock_service = mock_ai_service
            print("Using mock AI service")
        
    async def generate_paper_draft(
        self,
        title: str,
        field: str,
        keywords: List[str],
        details: str,
        references: List[Dict] = None
    ) -> Dict:
        """Generate paper draft using AI"""
        
        if not self.ollama_available:
            return await self.mock_service.generate_paper_draft(
                title=title,
                field=field,
                keywords=keywords,
                details=details,
                references=references
            )
        
        prompt_template = """
        You are a medical research assistant specializing in {field}.
        
        Generate a research paper draft with the following information:
        Title: {title}
        Keywords: {keywords}
        Research Details: {details}
        
        The paper should include:
        1. Abstract (250-300 words)
        2. Introduction
        3. Methods
        4. Expected Results
        5. Discussion
        6. Conclusion
        
        Use formal academic language appropriate for medical journals.
        """
        
        prompt = PromptTemplate(
            input_variables=["field", "title", "keywords", "details"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.ollama, prompt=prompt)
        
        result = await chain.arun(
            field=field,
            title=title,
            keywords=", ".join(keywords),
            details=details
        )
        
        # Structure the result
        sections = self._parse_paper_sections(result)
        
        return {
            "title": title,
            "abstract": sections.get("abstract", ""),
            "introduction": sections.get("introduction", ""),
            "methods": sections.get("methods", ""),
            "results": sections.get("results", ""),
            "discussion": sections.get("discussion", ""),
            "conclusion": sections.get("conclusion", ""),
            "generated_at": datetime.utcnow().isoformat(),
            "model": f"ollama/{self.model}"
        }
    
    async def generate_informed_consent(
        self,
        project_title: str,
        field: str,
        procedures: str,
        risks: str,
        benefits: str
    ) -> str:
        """Generate informed consent document"""
        
        if not self.ollama_available:
            return await self.mock_service.generate_informed_consent(
                project_title=project_title,
                field=field,
                procedures=procedures,
                risks=risks,
                benefits=benefits
            )
        
        prompt_template = """
        Generate an informed consent form for a medical research study.
        
        Study Title: {project_title}
        Field: {field}
        Procedures: {procedures}
        Risks: {risks}
        Benefits: {benefits}
        
        The consent form should include:
        1. Study purpose and background
        2. What participation involves
        3. Risks and discomforts
        4. Potential benefits
        5. Confidentiality
        6. Voluntary participation
        7. Contact information
        8. Consent statement
        
        Use clear, patient-friendly language.
        """
        
        prompt = PromptTemplate(
            input_variables=["project_title", "field", "procedures", "risks", "benefits"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.ollama, prompt=prompt)
        
        result = await chain.arun(
            project_title=project_title,
            field=field,
            procedures=procedures,
            risks=risks,
            benefits=benefits
        )
        
        return result
    
    async def analyze_statistics(
        self,
        data_description: str,
        analysis_type: str,
        variables: List[str]
    ) -> Dict:
        """Generate statistical analysis plan"""
        
        if not self.ollama_available:
            return await self.mock_service.analyze_statistics(
                data_description=data_description,
                analysis_type=analysis_type,
                variables=variables
            )
        
        prompt_template = """
        As a biostatistician, create a statistical analysis plan for the following research:
        
        Data Description: {data_description}
        Analysis Type: {analysis_type}
        Variables: {variables}
        
        Provide:
        1. Appropriate statistical tests
        2. Sample size considerations
        3. Data assumptions to check
        4. Analysis steps
        5. Interpretation guidelines
        """
        
        prompt = PromptTemplate(
            input_variables=["data_description", "analysis_type", "variables"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.ollama, prompt=prompt)
        
        result = await chain.arun(
            data_description=data_description,
            analysis_type=analysis_type,
            variables=", ".join(variables)
        )
        
        return {
            "analysis_plan": result,
            "recommended_software": ["SPSS", "R", "Python"],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def search_similar_papers(
        self,
        title: str,
        abstract: str,
        limit: int = 10
    ) -> List[Dict]:
        """Search for similar papers using embeddings"""
        
        if not self.ollama_available:
            return await self.mock_service.search_similar_papers(
                title=title,
                abstract=abstract,
                limit=limit
            )
        
        # Create or get collection
        collection = self.chroma.get_or_create_collection(
            name="research_papers",
            embedding_function=self.embeddings
        )
        
        # Search similar papers
        results = collection.query(
            query_texts=[f"{title} {abstract}"],
            n_results=limit
        )
        
        similar_papers = []
        if results["ids"][0]:
            for i, paper_id in enumerate(results["ids"][0]):
                similar_papers.append({
                    "id": paper_id,
                    "similarity_score": 1 - results["distances"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                })
        
        return similar_papers
    
    def _parse_paper_sections(self, text: str) -> Dict[str, str]:
        """Parse AI-generated text into paper sections"""
        sections = {
            "abstract": "",
            "introduction": "",
            "methods": "",
            "results": "",
            "discussion": "",
            "conclusion": ""
        }
        
        # Simple parsing logic - can be improved
        current_section = None
        lines = text.split("\n")
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if "abstract" in line_lower:
                current_section = "abstract"
            elif "introduction" in line_lower:
                current_section = "introduction"
            elif "method" in line_lower:
                current_section = "methods"
            elif "result" in line_lower:
                current_section = "results"
            elif "discussion" in line_lower:
                current_section = "discussion"
            elif "conclusion" in line_lower:
                current_section = "conclusion"
            elif current_section and line.strip():
                sections[current_section] += line + "\n"
        
        return sections


# Singleton instance
ai_service = AIService()
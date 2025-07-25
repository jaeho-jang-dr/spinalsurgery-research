import httpx
from typing import Dict, List, Optional
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.embeddings import OllamaEmbeddings
from chromadb import Client as ChromaClient
from chromadb.config import Settings
import json
from datetime import datetime

from app.core.config import settings


class AIService:
    def __init__(self):
        self.ollama = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model="llama2"
        )
        self.embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model="llama2"
        )
        self.chroma = ChromaClient(Settings(anonymized_telemetry=False))
        
    async def generate_paper_draft(
        self,
        title: str,
        field: str,
        keywords: List[str],
        details: str,
        references: List[Dict]
    ) -> Dict:
        """Generate paper draft using AI"""
        
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
            "model": "ollama/llama2"
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
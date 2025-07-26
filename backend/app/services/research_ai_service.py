"""
AI-powered research workflow service
Integrates Claude API for comprehensive research automation
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
import anthropic
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from scholarly import scholarly
import pubmed_parser as pp

class ResearchAIService:
    def __init__(self):
        self.claude_client = anthropic.Anthropic(
            api_key=os.getenv("CLAUDE_API_KEY", "")
        )
        self.research_base_path = Path("./research_projects")
        self.research_base_path.mkdir(exist_ok=True)
        
    async def start_new_research(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete research workflow from start to finish
        """
        project_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_path = self.research_base_path / project_id
        project_path.mkdir(exist_ok=True)
        
        # 1. Initialize project structure
        await self._create_project_structure(project_path)
        
        # 2. Research and crawl relevant documents
        print(f"Starting research for: {research_data['title']}")
        documents = await self._research_and_crawl(research_data)
        
        # 3. Organize and save documents
        await self._organize_documents(project_path, documents)
        
        # 4. Generate paper structure using Claude
        paper_structure = await self._generate_paper_structure(research_data, documents)
        
        # 5. Generate mock data
        mock_data = await self._generate_mock_data(research_data, paper_structure)
        
        # 6. Write draft paper
        draft_paper = await self._write_draft_paper(research_data, paper_structure, mock_data, documents)
        
        # 7. Generate informed consent
        informed_consent = await self._generate_informed_consent(research_data)
        
        # 8. Save all outputs
        await self._save_research_outputs(project_path, {
            'structure': paper_structure,
            'data': mock_data,
            'draft': draft_paper,
            'consent': informed_consent,
            'references': documents
        })
        
        return {
            'project_id': project_id,
            'project_path': str(project_path),
            'status': 'completed',
            'outputs': {
                'paper_structure': paper_structure,
                'draft_preview': draft_paper[:1000] + '...',
                'informed_consent_preview': informed_consent[:500] + '...',
                'documents_collected': len(documents),
                'mock_data_generated': bool(mock_data)
            }
        }
    
    async def _create_project_structure(self, project_path: Path):
        """Create organized directory structure"""
        directories = [
            'literature',
            'data',
            'analysis',
            'drafts',
            'figures',
            'consent_forms',
            'references'
        ]
        
        for dir_name in directories:
            (project_path / dir_name).mkdir(exist_ok=True)
            
        # Create README
        readme_content = f"""# Research Project
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Directory Structure
- `/literature`: Collected research papers and documents
- `/data`: Research data and datasets
- `/analysis`: Statistical analysis and results
- `/drafts`: Paper drafts and versions
- `/figures`: Charts, graphs, and images
- `/consent_forms`: Informed consent documents
- `/references`: Bibliography and citations
"""
        
        with open(project_path / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
    
    async def _research_and_crawl(self, research_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Research and crawl relevant documents"""
        documents = []
        
        # 1. Search PubMed
        pubmed_results = await self._search_pubmed(research_data['keywords'])
        documents.extend(pubmed_results)
        
        # 2. Search Google Scholar
        scholar_results = await self._search_google_scholar(research_data['keywords'])
        documents.extend(scholar_results)
        
        # 3. Web search for additional resources
        web_results = await self._search_web(research_data['title'], research_data['keywords'])
        documents.extend(web_results)
        
        return documents[:20]  # Limit to top 20 documents
    
    async def _search_pubmed(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search PubMed for relevant papers"""
        results = []
        query = " ".join(keywords)
        
        try:
            # Use pubmed_parser or NCBI E-utilities API
            # This is a simplified example
            search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': 10,
                'retmode': 'json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Process and fetch full articles
                        # This is simplified - real implementation would fetch full details
                        for pmid in data.get('esearchresult', {}).get('idlist', [])[:5]:
                            results.append({
                                'source': 'pubmed',
                                'pmid': pmid,
                                'title': f'PubMed Article {pmid}',
                                'abstract': 'Abstract would be fetched here',
                                'url': f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'
                            })
        except Exception as e:
            print(f"PubMed search error: {e}")
            
        return results
    
    async def _search_google_scholar(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search Google Scholar for academic papers"""
        results = []
        query = " ".join(keywords)
        
        try:
            search_query = scholarly.search_pubs(query)
            for i, article in enumerate(search_query):
                if i >= 5:  # Limit to 5 results
                    break
                    
                results.append({
                    'source': 'google_scholar',
                    'title': article.get('bib', {}).get('title', ''),
                    'authors': article.get('bib', {}).get('author', ''),
                    'abstract': article.get('bib', {}).get('abstract', ''),
                    'year': article.get('bib', {}).get('pub_year', ''),
                    'url': article.get('pub_url', '')
                })
        except Exception as e:
            print(f"Google Scholar search error: {e}")
            
        return results
    
    async def _search_web(self, title: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search web for additional resources"""
        results = []
        # Implement web search using appropriate API
        # This is a placeholder
        return results
    
    async def _organize_documents(self, project_path: Path, documents: List[Dict[str, Any]]):
        """Organize and save collected documents"""
        lit_path = project_path / "literature"
        
        # Save summary file
        summary = {
            'total_documents': len(documents),
            'sources': {},
            'documents': []
        }
        
        for i, doc in enumerate(documents):
            filename = f"{i+1:03d}_{doc['source']}_{doc.get('title', 'untitled')[:50]}.json"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            with open(lit_path / f"{filename}.json", "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
                
            summary['documents'].append({
                'filename': filename,
                'title': doc.get('title', ''),
                'source': doc['source']
            })
            
            source = doc['source']
            summary['sources'][source] = summary['sources'].get(source, 0) + 1
        
        with open(lit_path / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    
    async def _generate_paper_structure(self, research_data: Dict[str, Any], documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate paper structure using Claude"""
        
        # Prepare context from documents
        doc_summaries = []
        for doc in documents[:10]:  # Use top 10 documents
            doc_summaries.append(f"- {doc.get('title', 'Untitled')}: {doc.get('abstract', '')[:200]}...")
        
        prompt = f"""You are a medical research expert. Create a comprehensive paper structure for the following research:

Title: {research_data['title']}
Type: {research_data['type']}
Keywords: {', '.join(research_data['keywords'])}
Objectives: {research_data.get('objectives', 'To be defined')}

Based on these reference papers:
{chr(10).join(doc_summaries)}

Generate a detailed paper structure including:
1. Title and Authors
2. Abstract structure
3. Introduction with subsections
4. Methods with detailed subsections
5. Expected Results sections
6. Discussion points
7. Conclusion
8. References format

Provide the structure in JSON format with sections and subsections."""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse Claude's response
            structure_text = response.content[0].text
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', structure_text, re.DOTALL)
            if json_match:
                structure = json.loads(json_match.group())
            else:
                # Fallback structure
                structure = self._get_default_paper_structure(research_data)
                
        except Exception as e:
            print(f"Claude API error: {e}")
            structure = self._get_default_paper_structure(research_data)
            
        return structure
    
    def _get_default_paper_structure(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get default paper structure as fallback"""
        return {
            "title": research_data['title'],
            "authors": ["Dr. John Doe", "Dr. Jane Smith"],
            "sections": {
                "abstract": {
                    "background": "",
                    "methods": "",
                    "results": "",
                    "conclusions": ""
                },
                "introduction": {
                    "background": "",
                    "literature_review": "",
                    "objectives": "",
                    "hypotheses": ""
                },
                "methods": {
                    "study_design": "",
                    "participants": "",
                    "procedures": "",
                    "measurements": "",
                    "statistical_analysis": ""
                },
                "results": {
                    "demographics": "",
                    "primary_outcomes": "",
                    "secondary_outcomes": "",
                    "adverse_events": ""
                },
                "discussion": {
                    "key_findings": "",
                    "comparison_with_literature": "",
                    "limitations": "",
                    "clinical_implications": ""
                },
                "conclusion": "",
                "references": []
            }
        }
    
    async def _generate_mock_data(self, research_data: Dict[str, Any], paper_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock research data"""
        
        prompt = f"""Generate realistic mock data for a medical research paper:

Title: {research_data['title']}
Type: {research_data['type']}

Based on this structure:
{json.dumps(paper_structure['sections']['methods'], indent=2)}

Generate:
1. Patient demographics (n=100-200)
2. Primary outcome measures with statistics
3. Secondary outcomes
4. Subgroup analyses
5. Safety data

Provide in JSON format with realistic medical values and proper statistical measures (means, SD, p-values, confidence intervals)."""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            data_text = response.content[0].text
            
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', data_text, re.DOTALL)
            if json_match:
                mock_data = json.loads(json_match.group())
            else:
                mock_data = self._get_default_mock_data()
                
        except Exception as e:
            print(f"Mock data generation error: {e}")
            mock_data = self._get_default_mock_data()
            
        return mock_data
    
    def _get_default_mock_data(self) -> Dict[str, Any]:
        """Generate default mock data"""
        import random
        import numpy as np
        
        n_patients = random.randint(100, 200)
        
        return {
            "demographics": {
                "total_patients": n_patients,
                "age": {
                    "mean": round(random.uniform(45, 65), 1),
                    "sd": round(random.uniform(8, 15), 1),
                    "range": [25, 85]
                },
                "gender": {
                    "male": random.randint(40, 60),
                    "female": n_patients - random.randint(40, 60)
                }
            },
            "primary_outcomes": {
                "pain_reduction": {
                    "baseline": round(random.uniform(7, 9), 1),
                    "post_treatment": round(random.uniform(2, 4), 1),
                    "p_value": round(random.uniform(0.001, 0.05), 4),
                    "confidence_interval": [round(random.uniform(2, 3), 1), round(random.uniform(4, 5), 1)]
                }
            },
            "safety": {
                "adverse_events": random.randint(5, 20),
                "serious_adverse_events": random.randint(0, 3)
            }
        }
    
    async def _write_draft_paper(self, research_data: Dict[str, Any], structure: Dict[str, Any], 
                                mock_data: Dict[str, Any], documents: List[Dict[str, Any]]) -> str:
        """Write complete draft paper"""
        
        # Prepare references
        references = []
        for i, doc in enumerate(documents[:15]):
            references.append(f"{i+1}. {doc.get('title', 'Untitled')}. {doc.get('authors', 'Unknown')}. {doc.get('year', '2024')}.")
        
        prompt = f"""Write a complete medical research paper based on:

Title: {research_data['title']}
Structure: {json.dumps(structure, indent=2)}
Data: {json.dumps(mock_data, indent=2)}
References to cite: {chr(10).join(references[:5])}

Write a professional, publication-ready paper including:
1. Structured abstract (250 words)
2. Introduction with proper citations
3. Detailed methods section
4. Results with data interpretation
5. Comprehensive discussion
6. Clear conclusions

Use medical writing standards and include placeholders [1], [2] for citations."""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            draft_paper = response.content[0].text
            
        except Exception as e:
            print(f"Paper writing error: {e}")
            draft_paper = self._generate_template_paper(research_data, structure, mock_data)
            
        return draft_paper
    
    def _generate_template_paper(self, research_data: Dict[str, Any], structure: Dict[str, Any], 
                                mock_data: Dict[str, Any]) -> str:
        """Generate template paper as fallback"""
        return f"""# {research_data['title']}

## Abstract

**Background:** This study investigates {research_data['title']}.

**Methods:** A {research_data['type']} was conducted with {mock_data['demographics']['total_patients']} participants.

**Results:** The primary outcome showed significant improvement (p < {mock_data.get('primary_outcomes', {}).get('pain_reduction', {}).get('p_value', 0.05)}).

**Conclusions:** The findings suggest that the intervention is effective and safe.

## Introduction

[Introduction text would be generated here based on the literature review]

## Methods

### Study Design
This was a {research_data['type']} conducted according to ethical guidelines.

### Participants
A total of {mock_data['demographics']['total_patients']} participants were enrolled.

### Statistical Analysis
Data were analyzed using appropriate statistical methods.

## Results

### Demographics
The mean age was {mock_data['demographics']['age']['mean']} ± {mock_data['demographics']['age']['sd']} years.

### Primary Outcomes
[Results would be detailed here]

## Discussion

The findings of this study demonstrate...

## Conclusion

In conclusion, this research provides evidence...

## References

[References would be listed here]
"""
    
    async def _generate_informed_consent(self, research_data: Dict[str, Any]) -> str:
        """Generate informed consent form"""
        
        prompt = f"""Create a comprehensive informed consent form for:

Study Title: {research_data['title']}
Study Type: {research_data['type']}

Include all standard sections:
1. Study information and purpose
2. What participation involves
3. Risks and benefits
4. Confidentiality
5. Voluntary participation
6. Contact information
7. Consent statement

Follow medical ethics guidelines and make it patient-friendly."""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.6,
                messages=[{"role": "user", "content": prompt}]
            )
            
            consent_form = response.content[0].text
            
        except Exception as e:
            print(f"Consent generation error: {e}")
            consent_form = self._get_template_consent(research_data)
            
        return consent_form
    
    def _get_template_consent(self, research_data: Dict[str, Any]) -> str:
        """Get template consent form"""
        return f"""INFORMED CONSENT FORM

Study Title: {research_data['title']}

Principal Investigator: Dr. [Name]
Institution: [Hospital/University Name]

1. INVITATION TO PARTICIPATE
You are being invited to participate in a research study. Before you decide, it is important that you understand why the research is being done and what it will involve.

2. PURPOSE OF THE STUDY
{research_data.get('objectives', 'The purpose of this study is to investigate...')}

3. WHAT WILL HAPPEN
If you agree to participate, you will be asked to...

4. RISKS AND BENEFITS
The potential risks include...
The potential benefits include...

5. CONFIDENTIALITY
All information collected will be kept strictly confidential...

6. VOLUNTARY PARTICIPATION
Your participation is entirely voluntary...

7. CONTACT INFORMATION
If you have any questions, please contact:
Dr. [Name] at [Phone] or [Email]

8. CONSENT
I have read and understood the information provided above. All my questions have been answered to my satisfaction.

_____________________    _____________________    __________
Participant Name         Signature                Date

_____________________    _____________________    __________
Investigator Name        Signature                Date
"""
    
    async def _save_research_outputs(self, project_path: Path, outputs: Dict[str, Any]):
        """Save all research outputs to files"""
        
        # Save paper structure
        with open(project_path / "paper_structure.json", "w", encoding="utf-8") as f:
            json.dump(outputs['structure'], f, indent=2, ensure_ascii=False)
        
        # Save mock data
        with open(project_path / "data" / "mock_data.json", "w", encoding="utf-8") as f:
            json.dump(outputs['data'], f, indent=2, ensure_ascii=False)
        
        # Save draft paper
        with open(project_path / "drafts" / "draft_v1.md", "w", encoding="utf-8") as f:
            f.write(outputs['draft'])
        
        # Save informed consent
        with open(project_path / "consent_forms" / "informed_consent_v1.md", "w", encoding="utf-8") as f:
            f.write(outputs['consent'])
        
        # Create summary report
        summary = f"""# Research Project Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Outputs Generated

1. **Paper Structure**: Complete hierarchical structure saved
2. **Mock Data**: Statistical data for {outputs['data']['demographics']['total_patients']} patients
3. **Draft Paper**: Full draft with {len(outputs['draft'].split())} words
4. **Informed Consent**: Patient consent form ready
5. **Literature Review**: {len(outputs['references'])} documents collected and organized

## Next Steps

1. Review and refine the draft paper
2. Validate mock data or replace with real data
3. Customize informed consent for your institution
4. Add actual figures and tables
5. Format references according to journal requirements
"""
        
        with open(project_path / "PROJECT_SUMMARY.md", "w", encoding="utf-8") as f:
            f.write(summary)
"""
Claude Code CLI Service - Execute actual Claude Code commands via CLI
"""
import asyncio
import subprocess
import json
import os
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import re
from pathlib import Path
import shlex

class ClaudeCodeCLIService:
    def __init__(self):
        # Configure paths
        self.base_storage_path = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/backend/research_projects")
        self.claude_code_cmd = "/home/drjang00/bin/claude"  # Full path to claude command
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {}
    
    async def search_papers(
        self,
        query: str,
        sites: List[str],
        max_results: int = 10,
        search_id: str = None,
        project_id: str = None,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Execute Claude Code search command and parse results"""
        
        # Create storage directory for this search
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_dir = self.base_storage_path / f"search_{search_id or timestamp}"
        search_dir.mkdir(parents=True, exist_ok=True)
        
        # Build the Claude Code search command as a natural language prompt
        # Claude Code expects natural language commands, not structured CLI args
        sites_str = ", ".join(sites)
        prompt = f"Search for papers about '{query}' on {sites_str}. Find up to {max_results} results. Save the results to {search_dir}. Format the output as JSON with fields: id, source, title, abstract, authors, journal, year, doi, pdf_url."
        
        command = [
            self.claude_code_cmd,
            "search",
            prompt
        ]
        
        # Log the command
        command_str = " ".join(shlex.quote(arg) for arg in command)
        print(f"Executing Claude Code command: {command_str}")
        
        try:
            # Start the subprocess
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.base_storage_path)
            )
            
            # Store process for potential cancellation
            if search_id:
                self.active_processes[search_id] = process
            
            # Send initial progress
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "searching",
                    "message": "Claude Code 검색을 시작했습니다...",
                    "progress_percentage": 10
                })
            
            # Read output line by line for real-time updates
            results = []
            papers_found = 0
            current_site = None
            has_output = False
            
            async def read_stream(stream, is_stderr=False):
                nonlocal papers_found, current_site, results, has_output
                
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    
                    line_text = line.decode('utf-8').strip()
                    if not line_text:
                        continue
                    
                    has_output = True
                    print(f"{'STDERR' if is_stderr else 'STDOUT'}: {line_text}")
                    
                    # Parse progress indicators from Claude Code output
                    # Adjust these patterns based on actual Claude Code output format
                    
                    # Check for various progress indicators
                    # Looking for patterns like "Searching PubMed...", "Searching on arxiv", etc.
                    site_patterns = [
                        r'Searching\s+(\w+)',
                        r'Search(?:ing)?\s+on\s+(\w+)',
                        r'Looking\s+in\s+(\w+)',
                        r'Querying\s+(\w+)'
                    ]
                    
                    for pattern in site_patterns:
                        site_match = re.search(pattern, line_text, re.IGNORECASE)
                        if site_match:
                            current_site = site_match.group(1)
                            if progress_callback:
                                await progress_callback({
                                    "type": "progress",
                                    "status": "searching",
                                    "current_site": current_site,
                                    "message": f"{current_site}에서 검색 중...",
                                    "papers_found": papers_found,
                                    "progress_percentage": 20
                                })
                            break
                    
                    # Check for paper found patterns
                    paper_patterns = [
                        r'Found\s+paper:',
                        r'Found\s+(\d+)\s+paper',
                        r'Found\s+(\d+)\s+result',
                        r'Paper\s+(\d+):',
                        r'Result\s+(\d+):'
                    ]
                    
                    for pattern in paper_patterns:
                        paper_match = re.search(pattern, line_text, re.IGNORECASE)
                        if paper_match:
                            if paper_match.groups():
                                try:
                                    papers_found = max(papers_found, int(paper_match.group(1)))
                                except:
                                    papers_found += 1
                            else:
                                papers_found += 1
                                
                            if progress_callback:
                                await progress_callback({
                                    "type": "progress",
                                    "status": "searching",
                                    "current_site": current_site,
                                    "message": f"논문 {papers_found}개 찾음",
                                    "papers_found": papers_found,
                                    "progress_percentage": min(20 + papers_found * 5, 50)
                                })
                            break
                    
                    # Try to parse JSON results if the line looks like JSON
                    if line_text.startswith('{') or line_text.startswith('['):
                        try:
                            json_data = json.loads(line_text)
                            if isinstance(json_data, list):
                                results.extend(json_data)
                            elif isinstance(json_data, dict) and 'papers' in json_data:
                                results.extend(json_data['papers'])
                            elif isinstance(json_data, dict) and 'title' in json_data:
                                results.append(json_data)
                        except json.JSONDecodeError:
                            pass
            
            # Read both stdout and stderr concurrently
            await asyncio.gather(
                read_stream(process.stdout, False),
                read_stream(process.stderr, True)
            )
            
            # Wait for process to complete
            return_code = await process.wait()
            
            # Remove from active processes
            if search_id and search_id in self.active_processes:
                del self.active_processes[search_id]
            
            if return_code != 0:
                raise Exception(f"Claude Code command failed with return code {return_code}")
            
            # If no JSON results were parsed, try to read from output files
            if not results:
                results = await self._read_results_from_files(search_dir)
            
            # Send completion progress
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "searching",
                    "message": f"검색 완료: 총 {len(results)}개의 논문을 찾았습니다.",
                    "papers_found": len(results),
                    "progress_percentage": 50
                })
            
            return results
            
        except Exception as e:
            print(f"Error executing Claude Code command: {e}")
            if search_id and search_id in self.active_processes:
                del self.active_processes[search_id]
            raise
    
    async def _read_results_from_files(self, search_dir: Path) -> List[Dict]:
        """Read search results from files if Claude Code saves them"""
        results = []
        
        # Look for JSON files in the search directory
        for json_file in search_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        results.extend(data)
                    elif isinstance(data, dict) and 'papers' in data:
                        results.extend(data['papers'])
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
        
        # Also check for markdown files that might contain paper info
        for md_file in search_dir.glob("*.md"):
            try:
                paper_data = self._parse_markdown_paper(md_file)
                if paper_data:
                    results.append(paper_data)
            except Exception as e:
                print(f"Error parsing {md_file}: {e}")
        
        return results
    
    def _parse_markdown_paper(self, md_file: Path) -> Optional[Dict]:
        """Parse paper information from markdown file"""
        # This is a placeholder - implement based on actual Claude Code output format
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract paper metadata using regex patterns
            # Adjust these patterns based on actual Claude Code markdown format
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            authors_match = re.search(r'Authors?:\s*(.+)$', content, re.MULTILINE)
            journal_match = re.search(r'Journal:\s*(.+)$', content, re.MULTILINE)
            year_match = re.search(r'Year:\s*(\d{4})', content)
            doi_match = re.search(r'DOI:\s*(.+)$', content, re.MULTILINE)
            
            if title_match:
                return {
                    'id': md_file.stem,
                    'source': 'claude_code',
                    'title': title_match.group(1).strip(),
                    'authors': [a.strip() for a in authors_match.group(1).split(',')] if authors_match else [],
                    'journal': journal_match.group(1).strip() if journal_match else '',
                    'year': year_match.group(1) if year_match else '',
                    'doi': doi_match.group(1).strip() if doi_match else '',
                    'file_path': str(md_file)
                }
        except Exception as e:
            print(f"Error parsing markdown file {md_file}: {e}")
        
        return None
    
    async def download_papers(
        self,
        papers: List[Dict],
        project_id: Optional[str] = None,
        search_id: str = None,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Download PDFs using Claude Code"""
        
        # Create download directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_dir = self.base_storage_path / f"downloads_{search_id or timestamp}"
        download_dir.mkdir(parents=True, exist_ok=True)
        
        downloaded_papers = []
        
        for idx, paper in enumerate(papers):
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "downloading",
                    "current_paper": paper['title'][:50] + "...",
                    "papers_downloaded": idx,
                    "message": f"다운로드 중: {paper['title'][:50]}...",
                    "progress_percentage": 50 + int((idx / len(papers)) * 30)
                })
            
            # Build download command as natural language
            if paper.get('doi'):
                prompt = f"Download the PDF for the paper with DOI {paper['doi']} and save it to {download_dir}"
                command = [
                    self.claude_code_cmd,
                    "download",
                    prompt
                ]
            elif paper.get('pdf_url'):
                prompt = f"Download the PDF from {paper['pdf_url']} and save it to {download_dir} as {paper['id']}.pdf"
                command = [
                    self.claude_code_cmd,
                    "download",
                    prompt
                ]
                
                try:
                    process = await asyncio.create_subprocess_exec(
                        *command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        paper['pdf_downloaded'] = True
                        paper['pdf_path'] = str(download_dir / f"{paper['id']}.pdf")
                    else:
                        paper['pdf_downloaded'] = False
                        print(f"Failed to download {paper['title']}: {stderr.decode()}")
                        
                except Exception as e:
                    paper['pdf_downloaded'] = False
                    print(f"Error downloading {paper['title']}: {e}")
            else:
                paper['pdf_downloaded'] = False
            
            paper['folder'] = str(download_dir)
            downloaded_papers.append(paper)
        
        return downloaded_papers
    
    async def translate_papers(
        self,
        papers: List[Dict],
        search_id: str = None,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Translate papers to Korean using Claude Code"""
        
        translated_papers = []
        
        for idx, paper in enumerate(papers):
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "status": "translating",
                    "current_paper": paper['title'][:50] + "...",
                    "message": f"번역 중: {paper['title'][:50]}...",
                    "progress_percentage": 80 + int((idx / len(papers)) * 15)
                })
            
            # Build translation command as natural language
            translate_prompt = f"Translate the following paper title and abstract to Korean:\n\nTitle: {paper['title']}\n\n"
            if paper.get('abstract'):
                translate_prompt += f"Abstract: {paper['abstract'][:500]}..."  # Limit abstract length
            
            # Translate title
            try:
                # Create a temporary file with the content to translate
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                    tmp.write(f"Title: {paper['title']}\n\n")
                    if paper.get('abstract'):
                        tmp.write(f"Abstract: {paper['abstract']}")
                    tmp_path = tmp.name
                
                command = [
                    self.claude_code_cmd,
                    "translate",
                    translate_prompt
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    translated_text = stdout.decode('utf-8')
                    # Parse translated output - look for Korean text patterns
                    # The output might be formatted differently
                    korean_title_match = re.search(r'제목:?\s*(.+?)(?:\n|요약:|초록:)', translated_text, re.IGNORECASE | re.DOTALL)
                    korean_abstract_match = re.search(r'(?:요약:|초록:)\s*(.+)', translated_text, re.IGNORECASE | re.DOTALL)
                    
                    if korean_title_match:
                        paper['korean_title'] = korean_title_match.group(1).strip()
                    elif '\n' in translated_text:
                        # If no specific markers, assume first line is title
                        lines = translated_text.strip().split('\n')
                        if lines:
                            paper['korean_title'] = lines[0].strip()
                            if len(lines) > 1:
                                paper['korean_abstract'] = '\n'.join(lines[1:]).strip()
                    
                    if korean_abstract_match and not paper.get('korean_abstract'):
                        paper['korean_abstract'] = korean_abstract_match.group(1).strip()
                
                # Clean up temp file
                os.unlink(tmp_path)
                
            except Exception as e:
                print(f"Error translating {paper['title']}: {e}")
                # Fallback to adding suffix
                paper['korean_title'] = paper['title'] + ' (번역 실패)'
            
            translated_papers.append(paper)
        
        return translated_papers
    
    async def cancel_search(self, search_id: str) -> bool:
        """Cancel an ongoing search"""
        if search_id in self.active_processes:
            process = self.active_processes[search_id]
            try:
                process.terminate()
                await asyncio.sleep(0.5)  # Give it time to terminate gracefully
                if process.returncode is None:
                    process.kill()  # Force kill if still running
                del self.active_processes[search_id]
                return True
            except Exception as e:
                print(f"Error cancelling search {search_id}: {e}")
        return False

# Singleton instance
claude_code_cli_service = ClaudeCodeCLIService()
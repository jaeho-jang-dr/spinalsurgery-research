"""
File browser API endpoints for managing research papers
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil
import json
import os
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# Base directory for research papers
PAPERS_BASE_DIR = Path("/home/drjang00/DevEnvironments/spinalsurgery-research/data/papers")

class FileNode(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'directory'
    size: Optional[int] = None
    modified: Optional[datetime] = None
    children: Optional[List['FileNode']] = None
    extension: Optional[str] = None

class FileOperation(BaseModel):
    source: str
    destination: str
    operation: str  # 'move', 'copy'

class FileContent(BaseModel):
    path: str
    content: str

class SearchQuery(BaseModel):
    query: str
    path: Optional[str] = None
    extensions: Optional[List[str]] = None

def get_file_tree(path: Path, max_depth: int = 5, current_depth: int = 0) -> FileNode:
    """Recursively build file tree structure"""
    if current_depth >= max_depth:
        return None
    
    try:
        stat = path.stat()
        node = FileNode(
            name=path.name,
            path=str(path.relative_to(PAPERS_BASE_DIR)),
            type="directory" if path.is_dir() else "file",
            size=stat.st_size if path.is_file() else None,
            modified=datetime.fromtimestamp(stat.st_mtime),
            extension=path.suffix if path.is_file() else None
        )
        
        if path.is_dir():
            children = []
            for child in sorted(path.iterdir()):
                child_node = get_file_tree(child, max_depth, current_depth + 1)
                if child_node:
                    children.append(child_node)
            node.children = children
            
        return node
    except Exception as e:
        return None

@router.get("/tree")
async def get_directory_tree(path: str = "") -> FileNode:
    """Get directory tree structure"""
    try:
        target_path = PAPERS_BASE_DIR / path if path else PAPERS_BASE_DIR
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not target_path.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return get_file_tree(target_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_files(path: str = "") -> List[FileNode]:
    """List files in a directory"""
    try:
        target_path = PAPERS_BASE_DIR / path if path else PAPERS_BASE_DIR
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not target_path.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        files = []
        for item in sorted(target_path.iterdir()):
            stat = item.stat()
            files.append(FileNode(
                name=item.name,
                path=str(item.relative_to(PAPERS_BASE_DIR)),
                type="directory" if item.is_dir() else "file",
                size=stat.st_size if item.is_file() else None,
                modified=datetime.fromtimestamp(stat.st_mtime),
                extension=item.suffix if item.is_file() else None
            ))
        
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content")
async def get_file_content(path: str) -> Dict[str, Any]:
    """Get file content"""
    try:
        target_path = PAPERS_BASE_DIR / path
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not target_path.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not target_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Handle different file types
        if target_path.suffix in ['.json']:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return {"type": "json", "content": content}
        elif target_path.suffix in ['.txt', '.md']:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"type": "text", "content": content}
        elif target_path.suffix in ['.pdf']:
            return {"type": "pdf", "path": str(path)}
        else:
            # Try to read as text
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"type": "text", "content": content}
            except:
                return {"type": "binary", "path": str(path)}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/content")
async def update_file_content(file_content: FileContent) -> Dict[str, str]:
    """Update file content"""
    try:
        target_path = PAPERS_BASE_DIR / file_content.path
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not target_path.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not target_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Backup original file
        backup_path = target_path.with_suffix(target_path.suffix + '.bak')
        shutil.copy2(target_path, backup_path)
        
        # Write new content
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(file_content.content)
        
        return {"message": "File updated successfully", "backup": str(backup_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/directory")
async def create_directory(path: str, name: str) -> Dict[str, str]:
    """Create a new directory"""
    try:
        parent_path = PAPERS_BASE_DIR / path if path else PAPERS_BASE_DIR
        if not parent_path.exists():
            raise HTTPException(status_code=404, detail="Parent directory not found")
        
        if not parent_path.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        new_dir = parent_path / name
        if new_dir.exists():
            raise HTTPException(status_code=409, detail="Directory already exists")
        
        new_dir.mkdir(parents=True)
        return {"message": "Directory created successfully", "path": str(new_dir.relative_to(PAPERS_BASE_DIR))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file-operation")
async def perform_file_operation(operation: FileOperation) -> Dict[str, str]:
    """Perform file operations (move/copy)"""
    try:
        source_path = PAPERS_BASE_DIR / operation.source
        dest_path = PAPERS_BASE_DIR / operation.destination
        
        if not source_path.exists():
            raise HTTPException(status_code=404, detail="Source file not found")
        
        if not source_path.is_relative_to(PAPERS_BASE_DIR) or not dest_path.parent.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if operation.operation == "move":
            shutil.move(str(source_path), str(dest_path))
            message = "File moved successfully"
        elif operation.operation == "copy":
            if source_path.is_file():
                shutil.copy2(source_path, dest_path)
            else:
                shutil.copytree(source_path, dest_path)
            message = "File copied successfully"
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
        
        return {"message": message, "destination": str(dest_path.relative_to(PAPERS_BASE_DIR))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file")
async def delete_file(path: str) -> Dict[str, str]:
    """Delete a file or directory"""
    try:
        target_path = PAPERS_BASE_DIR / path
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not target_path.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if target_path.is_file():
            target_path.unlink()
        else:
            shutil.rmtree(target_path)
        
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_files(query: SearchQuery) -> List[Dict[str, Any]]:
    """Search for files by name or content"""
    try:
        search_path = PAPERS_BASE_DIR / query.path if query.path else PAPERS_BASE_DIR
        if not search_path.exists():
            raise HTTPException(status_code=404, detail="Search path not found")
        
        if not search_path.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        results = []
        
        def search_recursive(path: Path):
            for item in path.iterdir():
                if item.is_dir():
                    search_recursive(item)
                elif item.is_file():
                    # Check file name
                    if query.query.lower() in item.name.lower():
                        results.append({
                            "path": str(item.relative_to(PAPERS_BASE_DIR)),
                            "name": item.name,
                            "type": "filename_match",
                            "size": item.stat().st_size
                        })
                    
                    # Check file content for text files
                    elif item.suffix in ['.txt', '.json', '.md'] and (not query.extensions or item.suffix in query.extensions):
                        try:
                            with open(item, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if query.query.lower() in content.lower():
                                    # Find line with match
                                    lines = content.split('\n')
                                    for i, line in enumerate(lines):
                                        if query.query.lower() in line.lower():
                                            results.append({
                                                "path": str(item.relative_to(PAPERS_BASE_DIR)),
                                                "name": item.name,
                                                "type": "content_match",
                                                "line": i + 1,
                                                "preview": line.strip()[:100]
                                            })
                                            break
                        except:
                            pass
        
        search_recursive(search_path)
        return results[:100]  # Limit results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(path: str, file: UploadFile = File(...)) -> Dict[str, str]:
    """Upload a file to specified directory"""
    try:
        target_dir = PAPERS_BASE_DIR / path if path else PAPERS_BASE_DIR
        if not target_dir.exists():
            raise HTTPException(status_code=404, detail="Target directory not found")
        
        if not target_dir.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        file_path = target_dir / file.filename
        
        # Save uploaded file
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        return {"message": "File uploaded successfully", "path": str(file_path.relative_to(PAPERS_BASE_DIR))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download")
async def download_file(path: str):
    """Download a file"""
    from fastapi.responses import FileResponse
    
    try:
        target_path = PAPERS_BASE_DIR / path
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not target_path.is_relative_to(PAPERS_BASE_DIR):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not target_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        return FileResponse(
            path=str(target_path),
            filename=target_path.name,
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fix for recursive model
FileNode.model_rebuild()
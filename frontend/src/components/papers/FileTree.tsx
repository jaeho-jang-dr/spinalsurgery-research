'use client';

import React, { useState, useEffect } from 'react';
import {
  ChevronRight,
  ChevronDown,
  Folder,
  FolderOpen,
  File,
  FileText,
  FileJson,
  FileImage,
  MoreVertical,
  Plus,
  Copy,
  Move,
  Trash2,
  Edit
} from 'lucide-react';
// VS Code style components are used directly with Tailwind classes

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: string;
  children?: FileNode[];
  extension?: string;
}

interface FileTreeProps {
  rootPath?: string;
  selectedPath?: string;
  onSelectFile: (path: string, node: FileNode) => void;
  onCreateFolder?: (parentPath: string) => void;
  onDeleteItem?: (path: string) => void;
  onRenameItem?: (path: string, newName: string) => void;
  onMoveItem?: (sourcePath: string, destinationPath: string) => void;
  onCopyItem?: (sourcePath: string, destinationPath: string) => void;
}

const FileIcon: React.FC<{ extension?: string }> = ({ extension }) => {
  if (!extension) return <File className="w-4 h-4" />;
  
  const ext = extension.toLowerCase();
  if (['.txt', '.md'].includes(ext)) return <FileText className="w-4 h-4" />;
  if (['.json'].includes(ext)) return <FileJson className="w-4 h-4" />;
  if (['.pdf'].includes(ext)) return <FileText className="w-4 h-4 text-red-500" />;
  if (['.jpg', '.jpeg', '.png', '.gif'].includes(ext)) return <FileImage className="w-4 h-4" />;
  
  return <File className="w-4 h-4" />;
};

const TreeNode: React.FC<{
  node: FileNode;
  level: number;
  selectedPath?: string;
  expandedPaths: Set<string>;
  onToggle: (path: string) => void;
  onSelect: (path: string, node: FileNode) => void;
  onContextMenu: (e: React.MouseEvent, node: FileNode) => void;
}> = ({ node, level, selectedPath, expandedPaths, onToggle, onSelect, onContextMenu }) => {
  const isExpanded = expandedPaths.has(node.path);
  const isSelected = selectedPath === node.path;
  const isDirectory = node.type === 'directory';
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div>
      <div
        className={`flex items-center gap-1 px-2 py-1 hover:bg-vscode-hover cursor-pointer rounded ${
          isSelected ? "bg-vscode-selection hover:bg-vscode-selection" : ""
        }`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => {
          if (isDirectory) {
            onToggle(node.path);
          }
          onSelect(node.path, node);
        }}
        onContextMenu={(e) => onContextMenu(e, node)}
      >
        {isDirectory && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggle(node.path);
            }}
            className="p-0.5 hover:bg-vscode-hover rounded"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>
        )}
        {!isDirectory && <div className="w-5" />}
        
        {isDirectory ? (
          isExpanded ? (
            <FolderOpen className="w-4 h-4 text-vscode-blue" />
          ) : (
            <Folder className="w-4 h-4 text-vscode-blue" />
          )
        ) : (
          <FileIcon extension={node.extension} />
        )}
        
        <span className="text-sm truncate flex-1">{node.name}</span>
      </div>
      
      {isDirectory && isExpanded && hasChildren && (
        <div>
          {node.children!.map((child) => (
            <TreeNode
              key={child.path}
              node={child}
              level={level + 1}
              selectedPath={selectedPath}
              expandedPaths={expandedPaths}
              onToggle={onToggle}
              onSelect={onSelect}
              onContextMenu={onContextMenu}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const FileTree: React.FC<FileTreeProps> = ({
  rootPath = '',
  selectedPath,
  onSelectFile,
  onCreateFolder,
  onDeleteItem,
  onRenameItem,
  onMoveItem,
  onCopyItem,
}) => {
  const [treeData, setTreeData] = useState<FileNode | null>(null);
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [contextMenuNode, setContextMenuNode] = useState<FileNode | null>(null);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    fetchTree();
  }, [rootPath]);

  const fetchTree = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/file-browser/tree?path=${encodeURIComponent(rootPath)}`);
      if (!response.ok) throw new Error('Failed to fetch tree');
      const data = await response.json();
      setTreeData(data);
      
      // Auto-expand root
      if (data.type === 'directory') {
        setExpandedPaths(new Set([data.path]));
      }
    } catch (error) {
      console.error('Error fetching tree:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const handleContextMenu = (e: React.MouseEvent, node: FileNode) => {
    e.preventDefault();
    setContextMenuPosition({ x: e.clientX, y: e.clientY });
    setContextMenuNode(node);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-vscode-blue"></div>
      </div>
    );
  }

  if (!treeData) {
    return (
      <div className="text-center text-vscode-text-dim p-4">
        <p>No files found</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto">
      <div className="p-2">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-vscode-text">Files</h3>
          {onCreateFolder && (
            <button
              onClick={() => onCreateFolder(rootPath)}
              className="h-6 px-2 text-xs hover:bg-vscode-hover rounded flex items-center"
            >
              <Plus className="w-3 h-3 mr-1" />
              New Folder
            </button>
          )}
        </div>
        
        <TreeNode
          node={treeData}
          level={0}
          selectedPath={selectedPath}
          expandedPaths={expandedPaths}
          onToggle={handleToggle}
          onSelect={onSelectFile}
          onContextMenu={handleContextMenu}
        />
      </div>
      
      {contextMenuNode && (
        <>
          {/* Backdrop to close menu when clicking outside */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setContextMenuNode(null)}
          />
          
          {/* Context Menu */}
          <div 
            className="fixed bg-vscode-bg-light border border-vscode-border rounded shadow-lg z-50 py-1 min-w-[200px]"
            style={{ 
              left: `${contextMenuPosition.x}px`, 
              top: `${contextMenuPosition.y}px`
            }}
          >
            {contextMenuNode.type === 'directory' && onCreateFolder && (
              <>
                <button
                  className="w-full px-3 py-1.5 text-left hover:bg-vscode-hover flex items-center text-sm"
                  onClick={() => {
                    onCreateFolder(contextMenuNode.path);
                    setContextMenuNode(null);
                  }}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  New Folder
                </button>
                <div className="border-t border-vscode-border my-1" />
              </>
            )}
            
            {onRenameItem && (
              <button
                className="w-full px-3 py-1.5 text-left hover:bg-vscode-hover flex items-center text-sm"
                onClick={() => {
                  const newName = prompt('Enter new name:', contextMenuNode.name);
                  if (newName && newName !== contextMenuNode.name) {
                    onRenameItem(contextMenuNode.path, newName);
                  }
                  setContextMenuNode(null);
                }}
              >
                <Edit className="w-4 h-4 mr-2" />
                Rename
              </button>
            )}
            
            {onCopyItem && (
              <button
                className="w-full px-3 py-1.5 text-left hover:bg-vscode-hover flex items-center text-sm"
                onClick={() => {
                  // In a real app, this would open a dialog to select destination
                  setContextMenuNode(null);
                }}
              >
                <Copy className="w-4 h-4 mr-2" />
                Copy
              </button>
            )}
            
            {onMoveItem && (
              <button
                className="w-full px-3 py-1.5 text-left hover:bg-vscode-hover flex items-center text-sm"
                onClick={() => {
                  // In a real app, this would open a dialog to select destination
                  setContextMenuNode(null);
                }}
              >
                <Move className="w-4 h-4 mr-2" />
                Move
              </button>
            )}
            
            {onDeleteItem && (
              <>
                <div className="border-t border-vscode-border my-1" />
                <button
                  className="w-full px-3 py-1.5 text-left hover:bg-vscode-hover flex items-center text-sm text-red-500"
                  onClick={() => {
                    if (confirm(`Delete ${contextMenuNode.name}?`)) {
                      onDeleteItem(contextMenuNode.path);
                    }
                    setContextMenuNode(null);
                  }}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </button>
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
};
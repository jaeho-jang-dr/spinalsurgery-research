'use client';

import React, { useState, useCallback } from 'react';
import { Search, Upload, FolderPlus, RefreshCw, X } from 'lucide-react';
import { FileTree } from './FileTree';
import { FileViewer } from './FileViewer';
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

interface SearchResult {
  path: string;
  name: string;
  type: 'filename_match' | 'content_match';
  line?: number;
  preview?: string;
}

export const FileBrowser: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [showNewFolderDialog, setShowNewFolderDialog] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderParent, setNewFolderParent] = useState('');
  const [uploadTarget, setUploadTarget] = useState('');
  const [showToast, setShowToast] = useState<{ title: string; description: string; variant?: string } | null>(null);

  // Simple toast implementation
  const toast = ({ title, description, variant }: { title: string; description: string; variant?: string }) => {
    setShowToast({ title, description, variant });
    setTimeout(() => setShowToast(null), 3000);
  };

  const handleSelectFile = useCallback((path: string, node: FileNode) => {
    if (node.type === 'file') {
      setSelectedFile(node);
    }
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setSearching(true);
      const response = await fetch('/api/v1/file-browser/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) throw new Error('Search failed');
      
      const results = await response.json();
      setSearchResults(results);
      
      if (results.length === 0) {
        toast({
          title: 'No results found',
          description: `No files matching "${searchQuery}" were found.`,
        });
      }
    } catch (error) {
      toast({
        title: 'Search error',
        description: error instanceof Error ? error.message : 'Failed to search files',
        variant: 'destructive',
      });
    } finally {
      setSearching(false);
    }
  };

  const handleCreateFolder = async (parentPath: string) => {
    setNewFolderParent(parentPath);
    setShowNewFolderDialog(true);
  };

  const confirmCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    try {
      const response = await fetch('/api/v1/file-browser/directory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: newFolderParent,
          name: newFolderName,
        }),
      });

      if (!response.ok) throw new Error('Failed to create folder');

      toast({
        title: 'Folder created',
        description: `Created folder "${newFolderName}" successfully.`,
      });

      setRefreshKey(prev => prev + 1);
      setShowNewFolderDialog(false);
      setNewFolderName('');
    } catch (error) {
      toast({
        title: 'Error creating folder',
        description: error instanceof Error ? error.message : 'Failed to create folder',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteItem = async (path: string) => {
    try {
      const response = await fetch(`/api/v1/file-browser/file?path=${encodeURIComponent(path)}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete item');

      toast({
        title: 'Item deleted',
        description: 'The selected item has been deleted.',
      });

      if (selectedFile?.path === path) {
        setSelectedFile(null);
      }

      setRefreshKey(prev => prev + 1);
    } catch (error) {
      toast({
        title: 'Error deleting item',
        description: error instanceof Error ? error.message : 'Failed to delete item',
        variant: 'destructive',
      });
    }
  };

  const handleSaveFile = async (path: string, content: string) => {
    const response = await fetch('/api/v1/file-browser/content', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path, content }),
    });

    if (!response.ok) throw new Error('Failed to save file');

    toast({
      title: 'File saved',
      description: 'Your changes have been saved successfully.',
    });
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`/api/v1/file-browser/upload?path=${encodeURIComponent(uploadTarget)}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to upload file');

      toast({
        title: 'File uploaded',
        description: `${file.name} has been uploaded successfully.`,
      });

      setRefreshKey(prev => prev + 1);
    } catch (error) {
      toast({
        title: 'Upload error',
        description: error instanceof Error ? error.message : 'Failed to upload file',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="flex h-full bg-vscode-bg">
      {/* Left Sidebar - File Tree */}
      <div className="w-80 bg-vscode-bg-light border-r border-vscode-border flex flex-col">
        <div className="p-4 border-b border-vscode-border">
          <h2 className="text-lg font-semibold mb-4">Research Papers</h2>
          
          {/* Search */}
          <div className="flex gap-2 mb-4">
            <input
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1 vscode-input"
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              className="vscode-button px-2"
            >
              {searching ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
              ) : (
                <Search className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={() => handleCreateFolder('')}
              className="flex-1 vscode-button-secondary flex items-center justify-center"
            >
              <FolderPlus className="w-4 h-4 mr-2" />
              New Folder
            </button>
            
            <button
              className="flex-1 vscode-button-secondary flex items-center justify-center"
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload
            </button>
            <input
              id="file-upload"
              type="file"
              className="hidden"
              onChange={handleUpload}
            />
            
            <button
              onClick={() => setRefreshKey(prev => prev + 1)}
              className="vscode-button-secondary px-2"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* File Tree or Search Results */}
        <div className="flex-1 overflow-auto">
          {searchResults.length > 0 ? (
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">Search Results ({searchResults.length})</h3>
                <button
                  onClick={() => {
                    setSearchResults([]);
                    setSearchQuery('');
                  }}
                  className="text-xs text-vscode-text-dim hover:text-vscode-text"
                >
                  Clear
                </button>
              </div>
              {searchResults.map((result, idx) => (
                <div
                  key={idx}
                  className="p-2 hover:bg-vscode-hover rounded cursor-pointer text-sm"
                  onClick={() => {
                    handleSelectFile(result.path, {
                      name: result.name,
                      path: result.path,
                      type: 'file',
                    });
                  }}
                >
                  <div className="font-medium">{result.name}</div>
                  <div className="text-xs text-vscode-text-dim">{result.path}</div>
                  {result.type === 'content_match' && result.preview && (
                    <div className="text-xs text-vscode-text-dim mt-1">
                      Line {result.line}: {result.preview}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <FileTree
              key={refreshKey}
              selectedPath={selectedFile?.path}
              onSelectFile={handleSelectFile}
              onCreateFolder={handleCreateFolder}
              onDeleteItem={handleDeleteItem}
            />
          )}
        </div>
      </div>

      {/* Right Panel - File Viewer */}
      <div className="flex-1 p-4">
        {selectedFile ? (
          <FileViewer
            filePath={selectedFile.path}
            fileName={selectedFile.name}
            onClose={() => setSelectedFile(null)}
            onSave={handleSaveFile}
          />
        ) : (
          <div className="h-full flex items-center justify-center text-vscode-text-dim">
            <div className="text-center">
              <p className="text-lg mb-2">Select a file to view</p>
              <p className="text-sm">Choose a file from the tree on the left</p>
            </div>
          </div>
        )}
      </div>

      {/* New Folder Dialog */}
      {showNewFolderDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-vscode-bg-light border border-vscode-border rounded p-6 w-96">
            <h3 className="text-lg font-semibold mb-2">Create New Folder</h3>
            <p className="text-sm text-vscode-text-dim mb-4">
              Enter a name for the new folder.
            </p>
            <div className="mb-4">
              <label htmlFor="folder-name" className="block text-sm mb-2">
                Name
              </label>
              <input
                id="folder-name"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                className="vscode-input w-full"
                placeholder="New Folder"
                onKeyPress={(e) => e.key === 'Enter' && confirmCreateFolder()}
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowNewFolderDialog(false)}
                className="vscode-button-secondary"
              >
                Cancel
              </button>
              <button
                onClick={confirmCreateFolder}
                disabled={!newFolderName.trim()}
                className="vscode-button"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast notification */}
      {showToast && (
        <div className={`fixed bottom-4 right-4 p-4 rounded shadow-lg z-50 ${
          showToast.variant === 'destructive' 
            ? 'bg-red-900 border border-red-700' 
            : 'bg-vscode-bg-lighter border border-vscode-border'
        }`}>
          <div className="flex items-start gap-3">
            <div className="flex-1">
              <p className="font-semibold text-sm">{showToast.title}</p>
              <p className="text-sm text-vscode-text-dim mt-1">{showToast.description}</p>
            </div>
            <button
              onClick={() => setShowToast(null)}
              className="text-vscode-text-dim hover:text-vscode-text"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
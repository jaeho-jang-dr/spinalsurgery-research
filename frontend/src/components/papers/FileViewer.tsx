'use client';

import React, { useState, useEffect } from 'react';
import { Save, X, Download, Edit2, Eye } from 'lucide-react';
// VS Code style components are used directly with Tailwind classes

interface FileViewerProps {
  filePath: string;
  fileName: string;
  onClose?: () => void;
  onSave?: (path: string, content: string) => Promise<void>;
}

interface FileContent {
  type: 'text' | 'json' | 'pdf' | 'binary';
  content?: string | any;
  path?: string;
}

export const FileViewer: React.FC<FileViewerProps> = ({
  filePath,
  fileName,
  onClose,
  onSave,
}) => {
  const [fileContent, setFileContent] = useState<FileContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    fetchFileContent();
  }, [filePath]);

  const fetchFileContent = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/v1/file-browser/content?path=${encodeURIComponent(filePath)}`);
      if (!response.ok) throw new Error('Failed to fetch file content');
      
      const data: FileContent = await response.json();
      setFileContent(data);
      
      // Set initial content for editing
      if (data.type === 'text') {
        setEditedContent(data.content as string);
      } else if (data.type === 'json') {
        setEditedContent(JSON.stringify(data.content, null, 2));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load file');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!onSave || !isDirty) return;
    
    try {
      setSaving(true);
      setError(null);
      
      await onSave(filePath, editedContent);
      
      // Refresh content after save
      await fetchFileContent();
      setEditMode(false);
      setIsDirty(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save file');
    } finally {
      setSaving(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([editedContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-vscode-blue"></div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="bg-red-900 border border-red-700 p-4 rounded">
          <p className="text-sm">{error}</p>
        </div>
      );
    }

    if (!fileContent) return null;

    switch (fileContent.type) {
      case 'pdf':
        return (
          <div className="flex flex-col items-center justify-center h-64 text-vscode-text-dim">
            <p className="mb-4">PDF Preview not available</p>
            <button 
              className="vscode-button-secondary flex items-center"
              onClick={() => window.open(`/api/v1/file-browser/download?path=${encodeURIComponent(filePath)}`, '_blank')}
            >
              <Download className="w-4 h-4 mr-2" />
              Download PDF
            </button>
          </div>
        );

      case 'binary':
        return (
          <div className="flex flex-col items-center justify-center h-64 text-vscode-text-dim">
            <p className="mb-4">Binary file cannot be displayed</p>
            <button 
              className="vscode-button-secondary flex items-center"
              onClick={() => window.open(`/api/v1/file-browser/download?path=${encodeURIComponent(filePath)}`, '_blank')}
            >
              <Download className="w-4 h-4 mr-2" />
              Download File
            </button>
          </div>
        );

      case 'text':
      case 'json':
        if (editMode) {
          return (
            <textarea
              value={editedContent}
              onChange={(e) => {
                setEditedContent(e.target.value);
                setIsDirty(true);
              }}
              className="vscode-input font-mono text-sm h-full min-h-[400px] resize-none"
              placeholder="File content..."
            />
          );
        }

        return (
          <div className="h-full overflow-auto">
            <pre className="p-4 text-sm font-mono whitespace-pre-wrap">
              {fileContent.type === 'json' 
                ? JSON.stringify(fileContent.content, null, 2)
                : fileContent.content}
            </pre>
          </div>
        );

      default:
        return <div>Unsupported file type</div>;
    }
  };

  const canEdit = fileContent && ['text', 'json'].includes(fileContent.type);

  return (
    <div className="flex flex-col h-full bg-vscode-bg-light rounded-lg shadow-sm border border-vscode-border">
      <div className="flex items-center justify-between p-4 border-b border-vscode-border">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-lg">{fileName}</h3>
          {isDirty && <span className="text-xs text-vscode-yellow">Modified</span>}
        </div>
        
        <div className="flex items-center gap-2">
          {canEdit && onSave && (
            <>
              {editMode ? (
                <>
                  <button
                    className="vscode-button-secondary"
                    onClick={() => {
                      setEditMode(false);
                      setEditedContent(
                        fileContent.type === 'json' 
                          ? JSON.stringify(fileContent.content, null, 2)
                          : fileContent.content as string
                      );
                      setIsDirty(false);
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    className="vscode-button flex items-center"
                    onClick={handleSave}
                    disabled={!isDirty || saving}
                  >
                    {saving ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        Save
                      </>
                    )}
                  </button>
                </>
              ) : (
                <button
                  className="vscode-button-secondary flex items-center"
                  onClick={() => setEditMode(true)}
                >
                  <Edit2 className="w-4 h-4 mr-2" />
                  Edit
                </button>
              )}
            </>
          )}
          
          <button
            className="vscode-button-secondary px-2"
            onClick={handleDownload}
            disabled={!fileContent || fileContent.type === 'binary'}
          >
            <Download className="w-4 h-4" />
          </button>
          
          {onClose && (
            <button
              className="text-vscode-text-dim hover:text-vscode-text p-1"
              onClick={onClose}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      
      <div className="flex-1 overflow-hidden">
        {renderContent()}
      </div>
      
      {fileContent && (
        <div className="flex items-center justify-between px-4 py-2 border-t border-vscode-border text-xs text-vscode-text-dim">
          <span>Type: {fileContent.type}</span>
          <span>{filePath}</span>
        </div>
      )}
    </div>
  );
};
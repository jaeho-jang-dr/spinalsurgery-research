'use client'

import dynamic from 'next/dynamic'
import { useState } from 'react'
import { VscClose } from '../icons'

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false })

export function EditorArea() {
  const [tabs, setTabs] = useState([
    { id: '1', name: 'draft.md', content: '# 논문 초안\n\n## Abstract\n\n## Introduction\n' }
  ])
  const [activeTab, setActiveTab] = useState('1')

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex bg-vscode-bg-light border-b border-vscode-border">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`flex items-center px-3 py-2 text-sm cursor-pointer border-r border-vscode-border ${
              activeTab === tab.id ? 'bg-vscode-editor text-vscode-text' : 'text-vscode-text-dim'
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span>{tab.name}</span>
            <button className="ml-2 p-0.5 hover:bg-vscode-hover rounded">
              <VscClose size={14} />
            </button>
          </div>
        ))}
      </div>
      
      {/* Editor */}
      <div className="flex-1">
        <MonacoEditor
          height="100%"
          defaultLanguage="markdown"
          theme="vs-dark"
          value={tabs.find(t => t.id === activeTab)?.content}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            wordWrap: 'on',
            lineNumbers: 'on',
            renderWhitespace: 'selection',
            scrollBeyondLastLine: false,
          }}
          onChange={(value) => {
            setTabs(tabs.map(tab => 
              tab.id === activeTab ? { ...tab, content: value || '' } : tab
            ))
          }}
        />
      </div>
    </div>
  )
}
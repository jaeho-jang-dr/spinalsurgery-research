'use client'

import { useState, useEffect } from 'react'
import { Sidebar } from '@/components/layout/Sidebar'
import { ActivityBar } from '@/components/layout/ActivityBar'
import { TitleBar } from '@/components/layout/TitleBar'
import { MenuBar } from '@/components/layout/MenuBar'
import { StatusBar } from '@/components/layout/StatusBar'
import { EditorArea } from '@/components/editor/EditorArea'
import dynamic from 'next/dynamic'

const Terminal = dynamic(() => import('@/components/terminal/Terminal').then(mod => ({ default: mod.Terminal })), {
  ssr: false
})
import { ResearchPanel } from '@/components/research/ResearchPanel'
import { PapersPanel } from '@/components/papers/PapersPanel'
import { SourcesPanel } from '@/components/sources/SourcesPanel'
import { AIPanel } from '@/components/ai/AIPanel'
import { api } from '@/lib/api'
import '@/styles/menubar.css'

export default function Home() {
  const [activeView, setActiveView] = useState<'research' | 'editor' | 'papers' | 'sources' | 'ai' | 'print' | 'terminal'>('research')
  const [terminalOpen, setTerminalOpen] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    // Auto-login with test credentials
    const autoLogin = async () => {
      try {
        await api.login('test@example.com', 'test1234')
      } catch (error) {
        console.error('Auto-login failed:', error)
      }
    }
    
    // Check if already logged in
    const token = localStorage.getItem('access_token')
    if (!token) {
      autoLogin()
    }
  }, [])

  const handleMenuAction = (action: string) => {
    console.log('Menu action:', action)
    // 여기에 메뉴 액션 처리 로직 추가
    switch (action) {
      case 'view.explorer':
        setActiveView('research')
        break
      case 'view.search':
        setActiveView('papers')
        break
      case 'view.terminal':
        setTerminalOpen(!terminalOpen)
        break
      // 더 많은 액션 추가...
    }
  }

  return (
    <div className="flex flex-col h-screen bg-vscode-bg text-vscode-text">
      {/* Title Bar */}
      <TitleBar />
      
      {/* Menu Bar */}
      <MenuBar onMenuAction={handleMenuAction} />
      
      <div className="flex flex-1 overflow-hidden">
        {/* Activity Bar */}
        <ActivityBar 
          activeView={activeView} 
          onViewChange={setActiveView}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />
        
        {/* Sidebar */}
        {sidebarOpen && (
          <Sidebar activeView={activeView} />
        )}
        
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {/* Editor/Content Area */}
          <div className={`flex-1 overflow-hidden ${terminalOpen ? 'h-2/3' : ''}`}>
            {activeView === 'research' && <ResearchPanel />}
            {activeView === 'editor' && <EditorArea />}
            {activeView === 'papers' && <PapersPanel />}
            {activeView === 'sources' && <SourcesPanel />}
            {activeView === 'ai' && <AIPanel />}
          </div>
          
          {/* Terminal */}
          {terminalOpen && (
            <div className="h-1/3 border-t border-vscode-border">
              <Terminal onClose={() => setTerminalOpen(false)} />
            </div>
          )}
        </div>
      </div>
      
      {/* Status Bar */}
      <StatusBar />
    </div>
  )
}
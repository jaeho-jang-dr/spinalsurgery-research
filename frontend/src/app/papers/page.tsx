'use client'

import { useState } from 'react'
import Link from 'next/link'
import { PapersPanel } from '@/components/papers/PapersPanel'
import { PaperDownloader } from '@/components/papers/PaperDownloader'
import { ClaudeCodeSearchPanel } from '@/components/papers/ClaudeCodeSearchPanel'
import { VscBook, VscCloud } from '@/components/icons'
import { Download, Code } from 'lucide-react'

export default function PapersPage() {
  const [activeView, setActiveView] = useState<'manage' | 'download' | 'claude-code'>('manage')

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-gray-300">
      {/* VS Code 스타일 헤더 */}
      <header className="bg-[#2d2d30] border-b border-[#3e3e42] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-xl font-semibold text-white hover:text-gray-200">
              SpinalSurgery Research Platform
            </Link>
            <span className="text-sm text-gray-500">/ 논문</span>
          </div>
          <nav className="flex items-center space-x-6">
            <Link href="/research" className="hover:text-white transition-colors">연구</Link>
            <Link href="/papers" className="text-white">논문</Link>
            <Link href="/data" className="hover:text-white transition-colors">데이터</Link>
            <Link href="/ai" className="hover:text-white transition-colors">AI</Link>
            <Link href="/settings" className="hover:text-white transition-colors">설정</Link>
          </nav>
        </div>
      </header>

      <main className="flex flex-col h-[calc(100vh-60px)]">
        {/* Tab Navigation */}
        <div className="bg-[#252526] border-b border-[#3e3e42]">
          <div className="flex px-6">
            <button
              onClick={() => setActiveView('manage')}
              className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-colors ${
                activeView === 'manage' 
                  ? 'border-[#007acc] text-[#007acc]' 
                  : 'border-transparent hover:text-white'
              }`}
            >
              <VscBook size={16} />
              논문 관리
            </button>
            <button
              onClick={() => setActiveView('download')}
              className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-colors ${
                activeView === 'download' 
                  ? 'border-[#007acc] text-[#007acc]' 
                  : 'border-transparent hover:text-white'
              }`}
            >
              <Download size={16} />
              논문 검색 및 다운로드
            </button>
            <button
              onClick={() => setActiveView('claude-code')}
              className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-colors ${
                activeView === 'claude-code' 
                  ? 'border-[#007acc] text-[#007acc]' 
                  : 'border-transparent hover:text-white'
              }`}
            >
              <Code size={16} />
              Claude Code 검색
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {activeView === 'manage' ? (
            <PapersPanel />
          ) : activeView === 'download' ? (
            <PaperDownloader />
          ) : (
            <ClaudeCodeSearchPanel />
          )}
        </div>
      </main>
    </div>
  )
}
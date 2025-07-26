'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general')

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-gray-300">
      {/* VS Code 스타일 헤더 */}
      <header className="bg-[#2d2d30] border-b border-[#3e3e42] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-xl font-semibold text-white hover:text-gray-200">
              SpinalSurgery Research Platform
            </Link>
            <span className="text-sm text-gray-500">/ 설정</span>
          </div>
          <nav className="flex items-center space-x-6">
            <Link href="/research" className="hover:text-white transition-colors">연구</Link>
            <Link href="/papers" className="hover:text-white transition-colors">논문</Link>
            <Link href="/data" className="hover:text-white transition-colors">데이터</Link>
            <Link href="/ai" className="hover:text-white transition-colors">AI</Link>
            <Link href="/settings" className="text-white">설정</Link>
          </nav>
        </div>
      </header>

      <main className="flex h-[calc(100vh-60px)]">
        {/* 사이드바 */}
        <aside className="w-64 bg-[#252526] border-r border-[#3e3e42] p-4">
          <nav className="space-y-2">
            <button
              onClick={() => setActiveTab('general')}
              className={`w-full text-left px-3 py-2 rounded ${
                activeTab === 'general' ? 'bg-[#37373d] text-white' : 'hover:bg-[#2a2a2a]'
              }`}
            >
              일반 설정
            </button>
            <button
              onClick={() => setActiveTab('ai')}
              className={`w-full text-left px-3 py-2 rounded ${
                activeTab === 'ai' ? 'bg-[#37373d] text-white' : 'hover:bg-[#2a2a2a]'
              }`}
            >
              AI 설정
            </button>
            <button
              onClick={() => setActiveTab('database')}
              className={`w-full text-left px-3 py-2 rounded ${
                activeTab === 'database' ? 'bg-[#37373d] text-white' : 'hover:bg-[#2a2a2a]'
              }`}
            >
              데이터베이스
            </button>
            <button
              onClick={() => setActiveTab('account')}
              className={`w-full text-left px-3 py-2 rounded ${
                activeTab === 'account' ? 'bg-[#37373d] text-white' : 'hover:bg-[#2a2a2a]'
              }`}
            >
              계정
            </button>
          </nav>
        </aside>

        {/* 설정 내용 */}
        <div className="flex-1 p-8">
          {activeTab === 'general' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-6">일반 설정</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">언어</label>
                  <select className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-64">
                    <option>한국어</option>
                    <option>English</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">테마</label>
                  <select className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-64">
                    <option>다크 모드</option>
                    <option>라이트 모드</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'ai' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-6">AI 설정</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Claude API Key</label>
                  <input
                    type="password"
                    placeholder="sk-..."
                    className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-96"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Ollama 서버 URL</label>
                  <input
                    type="text"
                    placeholder="http://localhost:11434"
                    className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-96"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">선호 모델</label>
                  <select className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-64">
                    <option>Claude 3 Opus</option>
                    <option>Claude 3 Sonnet</option>
                    <option>Local Llama 3</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'database' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-6">데이터베이스 설정</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">데이터베이스 유형</label>
                  <select className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-64">
                    <option>SQLite (로컬)</option>
                    <option>PostgreSQL</option>
                    <option>MySQL</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">백업 주기</label>
                  <select className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-64">
                    <option>매일</option>
                    <option>매주</option>
                    <option>매월</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'account' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-6">계정 설정</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">사용자 이름</label>
                  <input
                    type="text"
                    value="Dr. Jang"
                    className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-64"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">이메일</label>
                  <input
                    type="email"
                    value="test@example.com"
                    className="bg-[#3c3c3c] border border-[#3e3e42] rounded px-3 py-2 w-96"
                  />
                </div>
                <div>
                  <button className="bg-[#007acc] hover:bg-[#1a8cff] text-white px-4 py-2 rounded">
                    비밀번호 변경
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="mt-8 pt-8 border-t border-[#3e3e42]">
            <button className="bg-[#007acc] hover:bg-[#1a8cff] text-white px-6 py-2 rounded mr-3">
              저장
            </button>
            <button className="bg-[#3c3c3c] hover:bg-[#4a4a4a] text-white px-6 py-2 rounded">
              취소
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
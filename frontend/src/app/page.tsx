'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Sidebar } from '@/components/layout/Sidebar'
import { ActivityBar } from '@/components/layout/ActivityBar'
import { TitleBar } from '@/components/layout/TitleBar'
import { MenuBar } from '@/components/layout/MenuBar'
import { StatusBar } from '@/components/layout/StatusBar'
import { EditorArea } from '@/components/editor/EditorArea'
import dynamic from 'next/dynamic'

const SimpleTerminal = dynamic(() => import('@/components/terminal/SimpleTerminal').then(mod => ({ default: mod.SimpleTerminal })), {
  ssr: false
})
import { ResearchPanel } from '@/components/research/ResearchPanel'
import { PapersPanel } from '@/components/papers/PapersPanel'
import { SourcesPanel } from '@/components/sources/SourcesPanel'
import { AIPanel } from '@/components/ai/AIPanel'
import { api } from '@/lib/api'
import { Terminal as TerminalIcon } from 'lucide-react'
import '@/styles/menubar.css'

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)
  const [recentProjects, setRecentProjects] = useState<any[]>([])
  const [terminalOpen, setTerminalOpen] = useState(false)
  const router = useRouter()
  const [quickActions] = useState([
    { icon: '📝', title: '새 연구 시작', description: 'AI 지원으로 새로운 연구 논문 작성', action: 'new-research' },
    { icon: '📊', title: '데이터 분석', description: '환자 데이터 통계 분석 및 시각화', action: 'data-analysis' },
    { icon: '🔍', title: '논문 검색', description: '관련 연구 논문 검색 및 참조', action: 'paper-search' },
    { icon: '🤖', title: 'AI 어시스턴트', description: 'Claude AI와 연구 상담', action: 'ai-assistant' }
  ])

  useEffect(() => {
    // Auto-login with test credentials
    const autoLogin = async () => {
      try {
        await api.login('test@example.com', 'test1234')
        // 로그인 후 최근 프로젝트 가져오기
        fetchRecentProjects()
      } catch (error) {
        console.error('Auto-login failed:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    // Check if already logged in
    const token = localStorage.getItem('access_token')
    if (!token) {
      autoLogin()
    } else {
      fetchRecentProjects()
      setIsLoading(false)
    }
  }, [])

  const fetchRecentProjects = async () => {
    // 실제로는 API에서 가져올 데이터
    setRecentProjects([
      { id: 1, title: 'Lumbar Spine Surgery Outcomes', date: '2024-12-15', status: 'In Progress' },
      { id: 2, title: 'Cervical Disc Replacement Study', date: '2024-12-10', status: 'Completed' },
      { id: 3, title: 'Spinal Fusion Techniques Review', date: '2024-12-05', status: 'Draft' }
    ])
  }

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'new-research':
        router.push('/research')
        break
      case 'data-analysis':
        router.push('/analysis')
        break
      case 'paper-search':
        router.push('/papers')
        break
      case 'ai-assistant':
        router.push('/ai')
        break
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#1e1e1e]">
        <div className="text-gray-400">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-gray-300">
      {/* VS Code 스타일 헤더 */}
      <header className="bg-[#2d2d30] border-b border-[#3e3e42] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-xl font-semibold text-white hover:text-gray-200">
              SpinalSurgery Research Platform
            </Link>
            <span className="text-sm text-gray-500">Welcome back, Dr. Jang</span>
          </div>
          <nav className="flex items-center space-x-6">
            <Link href="/research" className="hover:text-white transition-colors">연구</Link>
            <Link href="/papers" className="hover:text-white transition-colors">논문</Link>
            <Link href="/data" className="hover:text-white transition-colors">데이터</Link>
            <Link href="/ai" className="hover:text-white transition-colors">AI</Link>
            <Link href="/settings" className="hover:text-white transition-colors">설정</Link>
          </nav>
        </div>
      </header>

      <main className="p-8">
        {/* Quick Actions */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-4 text-white">빠른 시작</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => handleQuickAction(action.action)}
                className="bg-[#252526] hover:bg-[#2d2d30] border border-[#3e3e42] rounded-lg p-4 text-left transition-all hover:border-[#007acc]"
              >
                <div className="text-2xl mb-2">{action.icon}</div>
                <h3 className="text-white font-medium mb-1">{action.title}</h3>
                <p className="text-sm text-gray-500">{action.description}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Recent Projects */}
        <section>
          <h2 className="text-lg font-semibold mb-4 text-white">최근 프로젝트</h2>
          <div className="bg-[#252526] border border-[#3e3e42] rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-[#2d2d30] border-b border-[#3e3e42]">
                <tr>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-400">프로젝트 제목</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-400">날짜</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-400">상태</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-400">작업</th>
                </tr>
              </thead>
              <tbody>
                {recentProjects.map((project) => (
                  <tr key={project.id} className="border-b border-[#3e3e42] hover:bg-[#2d2d30]">
                    <td className="px-4 py-3">
                      <Link href={`/research/${project.id}`} className="text-[#4ec9b0] hover:underline">
                        {project.title}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">{project.date}</td>
                    <td className="px-4 py-3">
                      <span className={`text-sm px-2 py-1 rounded ${
                        project.status === 'Completed' ? 'bg-green-900 text-green-300' :
                        project.status === 'In Progress' ? 'bg-blue-900 text-blue-300' :
                        'bg-gray-700 text-gray-300'
                      }`}>
                        {project.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex space-x-2">
                        <button className="text-[#007acc] hover:text-[#1a8cff] text-sm">편집</button>
                        <button className="text-gray-500 hover:text-gray-300 text-sm">공유</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* AI Integration Status */}
        <section className="mt-8 bg-[#252526] border border-[#3e3e42] rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">AI 어시스턴트 연결됨</span>
            </div>
            <div className="text-sm text-gray-500">
              Claude API & Local Ollama Ready
            </div>
          </div>
        </section>
      </main>
      
      {/* Multi Terminal */}
      {terminalOpen && (
        <div className="fixed bottom-0 left-0 right-0 z-50">
          <SimpleTerminal 
            onClose={() => setTerminalOpen(false)}
            height="h-96"
          />
        </div>
      )}
      
      {/* Terminal Toggle Button */}
      <button
        onClick={() => setTerminalOpen(!terminalOpen)}
        className="fixed bottom-4 right-4 bg-[#007acc] hover:bg-[#1a8cff] text-white p-3 rounded-full shadow-lg z-40"
        title="Toggle Terminal"
      >
        <TerminalIcon size={24} />
      </button>
    </div>
  )
}
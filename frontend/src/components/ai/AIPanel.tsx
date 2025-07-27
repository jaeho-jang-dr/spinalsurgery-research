'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import { VscRobot, VscBeaker, VscNotebook, VscComment } from '../icons'

// Dynamic import to avoid SSR issues
const AIChatbot = dynamic(() => import('@/components/ai/AIChatbot'), {
  ssr: false,
  loading: () => <div className="p-4 text-center">AI 챗봇 로딩 중...</div>
})

const AdvancedAIPanel = dynamic(() => import('@/components/ai/AdvancedAIPanel').then(mod => ({ default: mod.AdvancedAIPanel })), {
  ssr: false,
  loading: () => <div className="p-4 text-center">고급 AI 로딩 중...</div>
})

export function AIPanel() {
  const [activeTab, setActiveTab] = useState('chat')

  const tabs = [
    { id: 'chat', label: 'AI 챗봇', icon: VscComment },
    { id: 'draft', label: '논문 초안', icon: VscNotebook },
    { id: 'consent', label: '동의서', icon: VscBeaker },
    { id: 'stats', label: '통계 분석', icon: VscRobot }
  ]

  return (
    <div className="flex-1 flex flex-col">
      {/* Tab Navigation */}
      <div className="bg-[#252526] border-b border-[#3e3e42]">
        <div className="flex">
          {tabs.map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === tab.id
                    ? 'text-white border-[#007acc] bg-[#1e1e1e]'
                    : 'text-gray-400 border-transparent hover:text-gray-200 hover:bg-[#2d2d30]'
                }`}
              >
                <Icon size={16} />
                <span className="text-sm">{tab.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 bg-[#1e1e1e]">
        {activeTab === 'chat' && (
          <div className="h-full">
            <AdvancedAIPanel />
          </div>
        )}
        
        {activeTab === 'draft' && (
          <div className="p-8">
            <div className="max-w-2xl mx-auto bg-[#252526] border border-[#3e3e42] rounded-lg p-8 text-center">
              <VscNotebook size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-xl font-semibold mb-2 text-white">논문 초안 생성</h3>
              <p className="text-gray-400 mb-6">
                AI가 연구 주제에 맞는 논문 초안을 작성해드립니다
              </p>
              <button className="px-6 py-2 bg-[#007acc] text-white rounded hover:bg-[#005a9e] transition-colors">
                프로젝트에서 생성하기
              </button>
            </div>
          </div>
        )}
        
        {activeTab === 'consent' && (
          <div className="p-8">
            <div className="max-w-2xl mx-auto bg-[#252526] border border-[#3e3e42] rounded-lg p-8 text-center">
              <VscBeaker size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-xl font-semibold mb-2 text-white">연구 동의서 생성</h3>
              <p className="text-gray-400 mb-6">
                IRB 제출용 표준 동의서를 자동으로 생성합니다
              </p>
              <button className="px-6 py-2 bg-[#007acc] text-white rounded hover:bg-[#005a9e] transition-colors">
                동의서 생성 시작
              </button>
            </div>
          </div>
        )}
        
        {activeTab === 'stats' && (
          <div className="p-8">
            <div className="max-w-2xl mx-auto bg-[#252526] border border-[#3e3e42] rounded-lg p-8 text-center">
              <VscRobot size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-xl font-semibold mb-2 text-white">통계 분석 계획</h3>
              <p className="text-gray-400 mb-6">
                연구 데이터에 적합한 통계 분석 방법을 추천합니다
              </p>
              <button className="px-6 py-2 bg-[#007acc] text-white rounded hover:bg-[#005a9e] transition-colors">
                분석 계획 수립
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
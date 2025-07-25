'use client'

import { useState } from 'react'
import { VscSearch, VscAdd, VscBook, VscArchive, VscFile } from '../icons'

export function PapersPanel() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'my' | 'scraped' | 'references'>('my')

  return (
    <div className="flex h-full">
      {/* Left Panel - Paper List */}
      <div className="w-96 bg-vscode-sidebar border-r border-vscode-border flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-vscode-border">
          <h2 className="text-lg font-semibold mb-3">논문 관리</h2>
          
          {/* Search */}
          <div className="relative mb-3">
            <VscSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-vscode-text-dim" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="논문 검색..."
              className="vscode-input pl-9"
            />
          </div>
          
          {/* Tabs */}
          <div className="flex gap-1">
            <button
              onClick={() => setActiveTab('my')}
              className={`vscode-tab ${activeTab === 'my' ? 'vscode-tab-active' : ''}`}
            >
              <VscFile className="mr-1" size={16} />
              내 논문
            </button>
            <button
              onClick={() => setActiveTab('scraped')}
              className={`vscode-tab ${activeTab === 'scraped' ? 'vscode-tab-active' : ''}`}
            >
              <VscArchive className="mr-1" size={16} />
              스크랩
            </button>
            <button
              onClick={() => setActiveTab('references')}
              className={`vscode-tab ${activeTab === 'references' ? 'vscode-tab-active' : ''}`}
            >
              <VscBook className="mr-1" size={16} />
              참고문헌
            </button>
          </div>
        </div>
        
        {/* Paper List */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'my' && (
            <div className="space-y-3">
              <div className="vscode-panel p-3 cursor-pointer hover:bg-vscode-hover">
                <h4 className="font-medium text-sm mb-1">
                  척추 후외방 고정술의 장기 추적 결과
                </h4>
                <p className="text-xs text-vscode-text-dim">
                  2025 • Korean J Spine • 발표됨
                </p>
              </div>
              <div className="vscode-panel p-3 cursor-pointer hover:bg-vscode-hover">
                <h4 className="font-medium text-sm mb-1">
                  최소 침습 척추 수술의 효과 분석
                </h4>
                <p className="text-xs text-vscode-text-dim">
                  2024 • 초안 작성 중
                </p>
              </div>
            </div>
          )}
          
          {activeTab === 'scraped' && (
            <div className="space-y-3">
              <div className="vscode-panel p-3 cursor-pointer hover:bg-vscode-hover">
                <h4 className="font-medium text-sm mb-1">
                  Minimally Invasive Spine Surgery: A Review
                </h4>
                <p className="text-xs text-vscode-text-dim">
                  2024 • Spine Journal • PubMed
                </p>
              </div>
            </div>
          )}
        </div>
        
        {/* Actions */}
        <div className="p-4 border-t border-vscode-border">
          <button className="vscode-button w-full">
            <VscAdd className="mr-1" size={16} />
            새 논문 추가
          </button>
        </div>
      </div>
      
      {/* Right Panel - Paper Details */}
      <div className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-4xl">
          <h1 className="text-2xl font-bold mb-2">
            척추 후외방 고정술의 장기 추적 결과
          </h1>
          
          <div className="text-sm text-vscode-text-dim mb-6">
            장재호, 김철수, 이영희 • 2025년 3월 • Korean Journal of Spine
          </div>
          
          <div className="space-y-6">
            <section>
              <h3 className="text-lg font-semibold mb-3">초록</h3>
              <p className="text-sm leading-relaxed">
                목적: 본 연구는 척추 후외방 고정술을 시행받은 환자들의 2년 추적 관찰 결과를 분석하고자 하였다.
                방법: 2023년부터 2024년까지 척추 후외방 고정술을 시행받은 34명의 환자를 대상으로 하였다...
              </p>
            </section>
            
            <section>
              <h3 className="text-lg font-semibold mb-3">발표 정보</h3>
              <div className="space-y-2 text-sm">
                <div><strong>발표일:</strong> 2025년 3월 15일</div>
                <div><strong>발표 장소:</strong> 대한척추외과학회 춘계학술대회</div>
                <div><strong>발표 형식:</strong> 구연 발표</div>
              </div>
            </section>
            
            <section>
              <h3 className="text-lg font-semibold mb-3">출판 정보</h3>
              <div className="space-y-2 text-sm">
                <div><strong>저널:</strong> Korean Journal of Spine</div>
                <div><strong>권/호:</strong> Vol. 22, No. 1</div>
                <div><strong>페이지:</strong> 45-52</div>
                <div><strong>DOI:</strong> 10.14245/kjs.2025.22.1.45</div>
              </div>
            </section>
            
            <div className="flex gap-3 mt-8">
              <button className="vscode-button">논문 편집</button>
              <button className="vscode-button-secondary">PDF 다운로드</button>
              <button className="vscode-button-secondary">인용하기</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
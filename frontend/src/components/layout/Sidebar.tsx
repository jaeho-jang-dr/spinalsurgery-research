'use client'

import { VscChevronDown, VscChevronRight, VscFolder, VscFolderOpened } from '../icons'
import { useState } from 'react'

interface SidebarProps {
  activeView: string
}

export function Sidebar({ activeView }: SidebarProps) {
  const [expandedSections, setExpandedSections] = useState<string[]>(['projects', 'papers'])

  const toggleSection = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    )
  }

  const renderProjectsView = () => (
    <div className="p-2">
      <div className="text-xs uppercase font-semibold text-vscode-text-dim mb-2">
        연구 프로젝트
      </div>
      <div className="space-y-1">
        <div 
          className="vscode-sidebar-item cursor-pointer"
          onClick={() => toggleSection('my-projects')}
        >
          {expandedSections.includes('my-projects') ? (
            <>
              <VscChevronDown size={16} className="mr-1" />
              <VscFolderOpened size={16} className="mr-2" />
            </>
          ) : (
            <>
              <VscChevronRight size={16} className="mr-1" />
              <VscFolder size={16} className="mr-2" />
            </>
          )}
          <span className="text-sm">내 프로젝트</span>
        </div>
        
        {expandedSections.includes('my-projects') && (
          <div className="ml-6 space-y-1">
            <div className="vscode-sidebar-item text-sm">
              척추 후외방 고정술 연구
            </div>
            <div className="vscode-sidebar-item text-sm">
              CD Instrument 효과 분석
            </div>
          </div>
        )}
      </div>
    </div>
  )

  const renderPapersView = () => (
    <div className="p-2">
      <div className="text-xs uppercase font-semibold text-vscode-text-dim mb-2">
        논문 관리
      </div>
      <div className="space-y-1">
        <div className="vscode-sidebar-item">
          <VscFolder size={16} className="mr-2" />
          <span className="text-sm">내 논문</span>
        </div>
        <div className="vscode-sidebar-item">
          <VscFolder size={16} className="mr-2" />
          <span className="text-sm">스크랩한 논문</span>
        </div>
        <div className="vscode-sidebar-item">
          <VscFolder size={16} className="mr-2" />
          <span className="text-sm">참고 문헌</span>
        </div>
      </div>
    </div>
  )

  const renderSourcesView = () => (
    <div className="p-2">
      <div className="text-xs uppercase font-semibold text-vscode-text-dim mb-2">
        논문 소스 관리
      </div>
      <div className="space-y-1">
        <div className="vscode-sidebar-item">
          <span className="text-sm font-semibold">우선순위 1</span>
        </div>
        <div className="ml-4 space-y-1">
          <div className="vscode-sidebar-item text-sm">
            PubMed Central
          </div>
          <div className="vscode-sidebar-item text-sm">
            서울대학교 의학도서관
          </div>
        </div>
        
        <div className="vscode-sidebar-item mt-2">
          <span className="text-sm font-semibold">기타 소스</span>
        </div>
        <div className="ml-4 space-y-1">
          <div className="vscode-sidebar-item text-sm">
            Google Scholar
          </div>
          <div className="vscode-sidebar-item text-sm">
            KoreaMed
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="w-64 bg-vscode-sidebar border-r border-vscode-border overflow-y-auto">
      {activeView === 'research' && renderProjectsView()}
      {activeView === 'papers' && renderPapersView()}
      {activeView === 'sources' && renderSourcesView()}
      {activeView === 'editor' && (
        <div className="p-2 text-sm text-vscode-text-dim">
          편집기 - 파일 탐색기
        </div>
      )}
    </div>
  )
}
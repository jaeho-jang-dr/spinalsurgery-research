'use client'

import { useState } from 'react'
import { VscAdd, VscEdit, VscTrash, VscMail, VscCall, VscLocation, VscGlobe } from '../icons'

interface Source {
  id: string
  name: string
  type: 'journal' | 'institution' | 'database' | 'conference'
  priority: number
  url?: string
  email?: string
  phone?: string
  address?: string
  notes?: string
}

export function SourcesPanel() {
  const [selectedSource, setSelectedSource] = useState<Source | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)

  const sources: Source[] = [
    {
      id: '1',
      name: 'PubMed Central',
      type: 'database',
      priority: 1,
      url: 'https://www.ncbi.nlm.nih.gov/pmc/',
      email: 'info@ncbi.nlm.nih.gov',
      notes: '무료 접근 가능, 최우선 검색 소스'
    },
    {
      id: '2',
      name: '서울대학교 의학도서관',
      type: 'institution',
      priority: 1,
      url: 'http://medlib.snu.ac.kr',
      email: 'medlib@snu.ac.kr',
      phone: '02-740-8045',
      address: '서울특별시 종로구 대학로 103',
      notes: '기관 구독으로 전문 접근 가능'
    },
    {
      id: '3',
      name: 'Korean Journal of Spine',
      type: 'journal',
      priority: 2,
      url: 'https://www.koreanspine.org',
      email: 'editor@koreanspine.org',
      phone: '02-737-6238',
      notes: '국내 척추외과 주요 저널'
    }
  ]

  const getPriorityColor = (priority: number) => {
    switch(priority) {
      case 1: return 'text-vscode-green'
      case 2: return 'text-vscode-blue'
      case 3: return 'text-vscode-yellow'
      default: return 'text-vscode-text-dim'
    }
  }

  const getTypeLabel = (type: string) => {
    switch(type) {
      case 'journal': return '저널'
      case 'institution': return '기관'
      case 'database': return '데이터베이스'
      case 'conference': return '학회'
      default: return type
    }
  }

  return (
    <div className="flex h-full">
      {/* Sources List */}
      <div className="w-96 bg-vscode-sidebar border-r border-vscode-border">
        <div className="p-4 border-b border-vscode-border">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">논문 소스 관리</h2>
            <button 
              onClick={() => setShowAddForm(true)}
              className="vscode-button"
            >
              <VscAdd size={16} />
            </button>
          </div>
          <p className="text-xs text-vscode-text-dim">
            논문 검색 및 수집을 위한 주요 소스 관리
          </p>
        </div>
        
        <div className="p-4 space-y-2">
          {[1, 2, 3, 4, 5].map(priority => (
            <div key={priority}>
              <h3 className={`text-sm font-semibold mb-2 ${getPriorityColor(priority)}`}>
                우선순위 {priority}
              </h3>
              <div className="space-y-2 mb-4">
                {sources
                  .filter(s => s.priority === priority)
                  .map(source => (
                    <div
                      key={source.id}
                      onClick={() => setSelectedSource(source)}
                      className={`p-3 rounded cursor-pointer transition-colors ${
                        selectedSource?.id === source.id 
                          ? 'bg-vscode-selection' 
                          : 'bg-vscode-bg-light hover:bg-vscode-hover'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium">{source.name}</h4>
                          <p className="text-xs text-vscode-text-dim">
                            {getTypeLabel(source.type)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Source Details */}
      <div className="flex-1 p-8">
        {selectedSource ? (
          <div className="max-w-3xl">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold">{selectedSource.name}</h1>
              <div className="flex gap-2">
                <button className="vscode-button-secondary">
                  <VscEdit size={16} className="mr-1" />
                  편집
                </button>
                <button className="vscode-button-secondary text-vscode-red">
                  <VscTrash size={16} className="mr-1" />
                  삭제
                </button>
              </div>
            </div>
            
            <div className="vscode-panel p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-vscode-text-dim">유형</label>
                  <p className="text-sm">{getTypeLabel(selectedSource.type)}</p>
                </div>
                <div>
                  <label className="text-xs text-vscode-text-dim">우선순위</label>
                  <p className={`text-sm font-semibold ${getPriorityColor(selectedSource.priority)}`}>
                    {selectedSource.priority}
                  </p>
                </div>
              </div>
              
              {selectedSource.url && (
                <div>
                  <label className="text-xs text-vscode-text-dim flex items-center gap-1">
                    <VscGlobe size={12} />
                    웹사이트
                  </label>
                  <a 
                    href={selectedSource.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-vscode-blue hover:underline"
                  >
                    {selectedSource.url}
                  </a>
                </div>
              )}
              
              {selectedSource.email && (
                <div>
                  <label className="text-xs text-vscode-text-dim flex items-center gap-1">
                    <VscMail size={12} />
                    이메일
                  </label>
                  <p className="text-sm">{selectedSource.email}</p>
                </div>
              )}
              
              {selectedSource.phone && (
                <div>
                  <label className="text-xs text-vscode-text-dim flex items-center gap-1">
                    <VscCall size={12} />
                    전화번호
                  </label>
                  <p className="text-sm">{selectedSource.phone}</p>
                </div>
              )}
              
              {selectedSource.address && (
                <div>
                  <label className="text-xs text-vscode-text-dim flex items-center gap-1">
                    <VscLocation size={12} />
                    주소
                  </label>
                  <p className="text-sm">{selectedSource.address}</p>
                </div>
              )}
              
              {selectedSource.notes && (
                <div>
                  <label className="text-xs text-vscode-text-dim">메모</label>
                  <p className="text-sm whitespace-pre-wrap">{selectedSource.notes}</p>
                </div>
              )}
            </div>
            
            <div className="mt-6 p-4 bg-vscode-bg-light rounded">
              <h3 className="text-sm font-semibold mb-2">활용 방법</h3>
              <ul className="text-xs text-vscode-text-dim space-y-1">
                <li>• 논문 검색 시 우선순위에 따라 자동으로 검색됩니다</li>
                <li>• 전문 열람이 필요한 경우 연락처를 통해 문의하세요</li>
                <li>• 기관 구독이 있는 경우 해당 기관에서 접속하면 전문을 볼 수 있습니다</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-vscode-text-dim">
            <p>소스를 선택하면 상세 정보가 표시됩니다</p>
          </div>
        )}
      </div>
    </div>
  )
}
'use client'

import { useState } from 'react'
import { VscAdd, VscClose, VscInfo } from '../icons'

interface ResearchFormProps {
  onSubmit: (data: any) => void
  initialValues?: {
    field?: string
    keywords?: string[]
  }
}

export function ResearchForm({ onSubmit, initialValues }: ResearchFormProps) {
  const [field, setField] = useState(initialValues?.field || '')
  const [title, setTitle] = useState('')
  const [keywords, setKeywords] = useState<string[]>(initialValues?.keywords || [])
  const [keywordInput, setKeywordInput] = useState('')
  const [details, setDetails] = useState('')
  const [aiOption, setAiOption] = useState<'search' | 'draft' | 'stats' | 'consent'>('search')

  const handleAddKeyword = () => {
    if (keywordInput.trim() && keywords.length < 10) {
      setKeywords([...keywords, keywordInput.trim()])
      setKeywordInput('')
    }
  }

  const handleRemoveKeyword = (index: number) => {
    setKeywords(keywords.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      field,
      title,
      keywords,
      details,
      aiOption
    })
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl">
      <div className="bg-vscode-bg-light p-6 rounded-lg border border-vscode-border space-y-6">
        <div className="text-center mb-6">
          <h2 className="text-lg font-semibold mb-2">어떤것에 관하여 연구하고 싶으신가요?</h2>
          <p className="text-sm text-vscode-text-dim">AI가 연구 과정을 도와드립니다</p>
        </div>

        {/* 연구 분야 */}
        <div>
          <label className="block text-sm font-medium mb-2">
            연구 분야 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type="text"
              value={field}
              onChange={(e) => setField(e.target.value)}
              placeholder="예: 척추외과"
              className="vscode-input"
              required
            />
            <VscInfo 
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-vscode-text-dim cursor-help" 
              size={16}
              title="연구하고자 하는 의학 분야를 입력하세요"
            />
          </div>
        </div>

        {/* 논문 제목 */}
        <div>
          <label className="block text-sm font-medium mb-2">
            논문 제목 <span className="text-vscode-text-dim">(선택)</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="예: 척추 후외방 고정술의 2년 후 결과"
            className="vscode-input"
          />
          <p className="text-xs text-vscode-text-dim mt-1">
            논문 제목을 입력하면 AI가 초안을 작성합니다
          </p>
        </div>

        {/* 키워드 */}
        <div>
          <label className="block text-sm font-medium mb-2">
            키워드 및 연구 방향
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddKeyword())}
              placeholder="키워드 입력 후 Enter"
              className="vscode-input flex-1"
            />
            <button
              type="button"
              onClick={handleAddKeyword}
              className="vscode-button-secondary"
              disabled={keywords.length >= 10}
            >
              <VscAdd size={16} />
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {keywords.map((keyword, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-2 py-1 bg-vscode-bg text-xs rounded border border-vscode-border"
              >
                {keyword}
                <button
                  type="button"
                  onClick={() => handleRemoveKeyword(index)}
                  className="hover:text-vscode-red"
                >
                  <VscClose size={14} />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* 세부사항 */}
        <div>
          <label className="block text-sm font-medium mb-2">
            연구 세부사항
          </label>
          <textarea
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            placeholder="예: 환자 데이터 34명\n결과는 VAS score와 통계는 SPSS\n사용기기 CD instrument"
            className="vscode-input min-h-[100px] resize-none"
            rows={4}
          />
        </div>

        {/* AI 처리 옵션 */}
        <div>
          <label className="block text-sm font-medium mb-2">
            AI 처리 옵션
          </label>
          <div className="grid grid-cols-2 gap-3">
            {[
              { id: 'search', label: '자료 검색', desc: '관련 논문 검색 및 정리' },
              { id: 'draft', label: '논문 초안 작성', desc: 'AI가 논문 초안 생성' },
              { id: 'stats', label: '통계 분석', desc: '데이터 분석 계획 수립' },
              { id: 'consent', label: 'Informed Consent', desc: '동의서 템플릿 생성' },
            ].map(option => (
              <label
                key={option.id}
                className={`p-3 border rounded cursor-pointer transition-colors ${
                  aiOption === option.id 
                    ? 'border-vscode-blue bg-vscode-selection' 
                    : 'border-vscode-border hover:bg-vscode-hover'
                }`}
              >
                <input
                  type="radio"
                  name="aiOption"
                  value={option.id}
                  checked={aiOption === option.id}
                  onChange={(e) => setAiOption(e.target.value as any)}
                  className="sr-only"
                />
                <div className="text-sm font-medium">{option.label}</div>
                <div className="text-xs text-vscode-text-dim">{option.desc}</div>
              </label>
            ))}
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-3 pt-4">
          <button type="submit" className="vscode-button">
            연구 시작하기
          </button>
          <button type="button" className="vscode-button-secondary">
            취소
          </button>
        </div>
      </div>
    </form>
  )
}
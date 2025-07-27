'use client'

import React, { useState } from 'react'
import { 
  Search, 
  Download, 
  FileText, 
  Globe, 
  Folder,
  Check,
  AlertCircle,
  Loader2,
  BookOpen,
  Languages
} from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'react-hot-toast'

interface DownloadedPaper {
  pmid: string
  metadata: {
    title: string
    authors: string[]
    journal: string
    year: string
    doi: string
    korean_translation?: {
      title: string
      abstract: string
      content_preview?: string
    }
  }
  folder: string
  pdf_downloaded: boolean
}

export function PaperDownloader() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [papers, setPapers] = useState<DownloadedPaper[]>([])
  const [selectedPaper, setSelectedPaper] = useState<DownloadedPaper | null>(null)
  const [showKorean, setShowKorean] = useState(true)

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error('검색어를 입력해주세요')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/paper-download/search-and-download', {
        query: query.trim(),
        max_results: 3,
        translate_to_korean: true
      })

      if (response.data.papers && response.data.papers.length > 0) {
        setPapers(response.data.papers)
        toast.success(`${response.data.papers.length}개의 논문을 찾았습니다!`)
      } else {
        toast.error('논문을 찾을 수 없습니다')
      }
    } catch (error: any) {
      console.error('Search error:', error)
      toast.error('논문 검색 중 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  const loadDownloadedPapers = async () => {
    try {
      const response = await api.get('/paper-download/downloaded-papers')
      if (response.data.papers) {
        setPapers(response.data.papers)
        toast.success(`${response.data.papers.length}개의 다운로드된 논문을 불러왔습니다`)
      }
    } catch (error) {
      console.error('Load error:', error)
      toast.error('논문 목록을 불러올 수 없습니다')
    }
  }

  const viewPaperDetails = async (paper: DownloadedPaper) => {
    try {
      const response = await api.get(`/paper-download/paper/${paper.pmid}`)
      setSelectedPaper(response.data)
    } catch (error) {
      console.error('View error:', error)
      setSelectedPaper(paper)
    }
  }

  return (
    <div className="flex h-full bg-vscode-bg">
      {/* Main Content */}
      <div className="flex-1 flex flex-col p-6">
        <h1 className="text-2xl font-bold mb-6">논문 검색 및 다운로드</h1>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="예: lumbar fusion 2-year outcomes"
              className="flex-1 bg-vscode-input border border-vscode-border rounded px-4 py-2 
                       focus:outline-none focus:border-vscode-blue"
              disabled={loading}
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-2 bg-vscode-blue text-white rounded hover:bg-vscode-blue-hover 
                       disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  검색 중...
                </>
              ) : (
                <>
                  <Search size={18} />
                  검색 및 다운로드
                </>
              )}
            </button>
            <button
              onClick={loadDownloadedPapers}
              className="px-4 py-2 bg-vscode-button text-white rounded hover:bg-vscode-button-hover 
                       flex items-center gap-2"
            >
              <Folder size={18} />
              다운로드된 논문
            </button>
          </div>
          <div className="mt-2 text-sm text-vscode-text-dim">
            PubMed에서 논문을 검색하고 PDF를 다운로드하며 한글로 번역합니다
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-auto">
          {papers.length > 0 ? (
            <div className="grid gap-4">
              {papers.map((paper) => (
                <div
                  key={paper.pmid}
                  className="border border-vscode-border rounded-lg p-4 hover:bg-vscode-hover 
                           cursor-pointer transition-colors"
                  onClick={() => viewPaperDetails(paper)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg mb-1">
                        {showKorean && paper.metadata.korean_translation?.title
                          ? paper.metadata.korean_translation.title
                          : paper.metadata.title}
                      </h3>
                      {showKorean && paper.metadata.korean_translation?.title && (
                        <p className="text-sm text-vscode-text-dim mb-2">
                          {paper.metadata.title}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      {paper.pdf_downloaded && (
                        <div className="flex items-center gap-1 text-green-500">
                          <Check size={16} />
                          <span className="text-sm">PDF</span>
                        </div>
                      )}
                      {paper.metadata.korean_translation && (
                        <div className="flex items-center gap-1 text-blue-500">
                          <Languages size={16} />
                          <span className="text-sm">한글</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-vscode-text-dim">
                    <span>{paper.metadata.authors.slice(0, 3).join(', ')}
                      {paper.metadata.authors.length > 3 && ' et al.'}</span>
                    <span>•</span>
                    <span>{paper.metadata.journal}</span>
                    <span>•</span>
                    <span>{paper.metadata.year}</span>
                  </div>

                  <div className="mt-2 flex items-center gap-4 text-xs text-vscode-text-dim">
                    <span>PMID: {paper.pmid}</span>
                    {paper.metadata.doi && <span>DOI: {paper.metadata.doi}</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-vscode-text-dim">
              <FileText size={48} className="mb-4" />
              <p>검색어를 입력하여 논문을 검색하거나</p>
              <p>다운로드된 논문 버튼을 클릭하세요</p>
            </div>
          )}
        </div>
      </div>

      {/* Paper Details Panel */}
      {selectedPaper && (
        <div className="w-1/2 border-l border-vscode-border p-6 overflow-auto">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">논문 상세 정보</h2>
            <button
              onClick={() => setShowKorean(!showKorean)}
              className="px-3 py-1 bg-vscode-button rounded text-sm hover:bg-vscode-button-hover
                       flex items-center gap-2"
            >
              <Globe size={14} />
              {showKorean ? '한글' : 'English'}
            </button>
          </div>

          <div className="space-y-4">
            {/* Title */}
            <div>
              <h3 className="font-semibold mb-1">제목</h3>
              <p className="text-sm">
                {showKorean && selectedPaper.metadata.korean_translation?.title
                  ? selectedPaper.metadata.korean_translation.title
                  : selectedPaper.metadata.title}
              </p>
              {showKorean && selectedPaper.metadata.korean_translation?.title && (
                <p className="text-sm text-vscode-text-dim mt-1">
                  {selectedPaper.metadata.title}
                </p>
              )}
            </div>

            {/* Authors */}
            <div>
              <h3 className="font-semibold mb-1">저자</h3>
              <p className="text-sm">{selectedPaper.metadata.authors.join(', ')}</p>
            </div>

            {/* Journal Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold mb-1">저널</h3>
                <p className="text-sm">{selectedPaper.metadata.journal}</p>
              </div>
              <div>
                <h3 className="font-semibold mb-1">발행년도</h3>
                <p className="text-sm">{selectedPaper.metadata.year}</p>
              </div>
            </div>

            {/* Abstract */}
            {(selectedPaper.metadata.korean_translation?.abstract || 
              selectedPaper.metadata.abstract) && (
              <div>
                <h3 className="font-semibold mb-1">초록</h3>
                <p className="text-sm whitespace-pre-wrap">
                  {showKorean && selectedPaper.metadata.korean_translation?.abstract
                    ? selectedPaper.metadata.korean_translation.abstract
                    : selectedPaper.metadata.abstract || '초록 없음'}
                </p>
              </div>
            )}

            {/* Content Preview */}
            {selectedPaper.metadata.korean_translation?.content_preview && (
              <div>
                <h3 className="font-semibold mb-1">본문 미리보기</h3>
                <p className="text-sm whitespace-pre-wrap bg-vscode-input p-3 rounded">
                  {selectedPaper.metadata.korean_translation.content_preview}
                </p>
              </div>
            )}

            {/* File Info */}
            <div className="border-t border-vscode-border pt-4">
              <h3 className="font-semibold mb-2">파일 정보</h3>
              <div className="space-y-1 text-sm">
                <div className="flex items-center gap-2">
                  <Folder size={16} />
                  <span className="text-vscode-text-dim">폴더:</span>
                  <span className="font-mono text-xs">{selectedPaper.folder}</span>
                </div>
                {selectedPaper.pdf_downloaded && (
                  <div className="flex items-center gap-2 text-green-500">
                    <FileText size={16} />
                    <span>PDF 다운로드 완료</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
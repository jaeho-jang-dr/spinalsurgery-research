'use client'

import React, { useState, useEffect, useRef } from 'react'
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
  Languages,
  Zap,
  Code,
  Link,
  X
} from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'react-hot-toast'

interface SearchProgress {
  search_id: string
  status: string
  current_site?: string
  papers_found: number
  papers_downloaded: number
  current_paper?: string
  progress_percentage: number
  message: string
}

interface SearchResult {
  id: string
  source: string
  title: string
  korean_title?: string
  abstract: string
  korean_abstract?: string
  authors: string[]
  journal: string
  year: string
  doi: string
  pdf_downloaded: boolean
  folder: string
}

export function ClaudeCodeSearchPanel() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [searchId, setSearchId] = useState<string | null>(null)
  const [progress, setProgress] = useState<SearchProgress | null>(null)
  const [results, setResults] = useState<SearchResult[]>([])
  const [selectedPaper, setSelectedPaper] = useState<SearchResult | null>(null)
  const [showKorean, setShowKorean] = useState(true)
  const [searchSites, setSearchSites] = useState(['pubmed', 'arxiv', 'semantic_scholar'])
  const [maxResults, setMaxResults] = useState(10)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [cancelling, setCancelling] = useState(false)
  
  const wsRef = useRef<WebSocket | null>(null)

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const connectWebSocket = (searchId: string) => {
    // Use the same host as the current page, but with ws:// protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = process.env.NEXT_PUBLIC_API_URL ? 
      process.env.NEXT_PUBLIC_API_URL.replace(/^https?:\/\//, '').replace('/api/v1', '') : 
      'localhost:8000'
    const wsUrl = `${protocol}//${host}/api/v1/claude-code-search/ws/${searchId}`
    
    console.log('Connecting to WebSocket:', wsUrl)
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected, sending auth')
      // Send authentication token immediately after connection
      const token = localStorage.getItem('token') || 'mock-token'
      ws.send(JSON.stringify({ token }))
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'progress') {
        setProgress(data)
        
        // Show toast for important updates
        if (data.current_site) {
          toast.loading(`${data.current_site}에서 검색 중...`)
        }
      } else if (data.type === 'complete') {
        setProgress(data)
        setResults(data.results || [])
        setLoading(false)
        toast.success(data.message)
        
        // Close WebSocket after completion
        ws.close()
      } else if (data.type === 'error') {
        setProgress(data)
        setLoading(false)
        toast.error(data.message)
        ws.close()
      } else if (data.type === 'cancelled') {
        setProgress(data)
        setLoading(false)
        setCancelling(false)
        toast.success('검색이 취소되었습니다')
        ws.close()
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      toast.error('WebSocket 연결 오류. 백엔드 서버가 실행 중인지 확인하세요.')
      setLoading(false)
    }
    
    ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason)
      wsRef.current = null
      if (event.code !== 1000 && event.code !== 1001) { // Normal closure codes
        setLoading(false)
      }
    }
    
    wsRef.current = ws
  }

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error('검색어를 입력해주세요')
      return
    }

    setLoading(true)
    setResults([])
    setProgress(null)
    setCancelling(false)
    
    try {
      const response = await api.post('/claude-code-search/search', {
        query: query.trim(),
        max_results: maxResults,
        search_sites: searchSites,
        download_pdfs: true,
        translate_to_korean: true
      })

      if (response.data.search_id) {
        setSearchId(response.data.search_id)
        toast.success('Claude Code가 논문 검색을 시작했습니다!')
        
        // Connect WebSocket for real-time updates
        connectWebSocket(response.data.search_id)
      }
    } catch (error: any) {
      console.error('Search error:', error)
      toast.error('검색 시작 중 오류가 발생했습니다')
      setLoading(false)
    }
  }
  
  const handleCancelSearch = async () => {
    if (!searchId || cancelling) return
    
    setCancelling(true)
    
    try {
      await api.post(`/claude-code-search/search/${searchId}/cancel`)
      // WebSocket will handle the cancellation notification
    } catch (error: any) {
      console.error('Cancel error:', error)
      toast.error('검색 취소 중 오류가 발생했습니다')
      setCancelling(false)
    }
  }

  const toggleSite = (site: string) => {
    if (searchSites.includes(site)) {
      setSearchSites(searchSites.filter(s => s !== site))
    } else {
      setSearchSites([...searchSites, site])
    }
  }

  const availableSites = [
    { id: 'pubmed', name: 'PubMed', icon: '🏥' },
    { id: 'arxiv', name: 'arXiv', icon: '📐' },
    { id: 'semantic_scholar', name: 'Semantic Scholar', icon: '🎓' },
    { id: 'google_scholar', name: 'Google Scholar', icon: '🔍' }
  ]

  return (
    <div className="flex h-full bg-vscode-bg">
      {/* Main Content */}
      <div className="flex-1 flex flex-col p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
            <Code className="text-vscode-blue" />
            Claude Code 논문 검색
          </h1>
          <p className="text-sm text-vscode-text-dim">
            VS Code의 Claude Code가 직접 여러 학술 사이트에서 논문을 검색하고 다운로드합니다
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !loading && handleSearch()}
              placeholder="예: lumbar fusion 2-year outcomes"
              className="flex-1 bg-vscode-input border border-vscode-border rounded px-4 py-2 
                       focus:outline-none focus:border-vscode-blue"
              disabled={loading}
            />
            {!loading ? (
              <button
                onClick={handleSearch}
                disabled={loading || searchSites.length === 0}
                className="px-6 py-2 bg-vscode-blue text-white rounded hover:bg-vscode-blue-hover 
                         disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Zap size={18} />
                Claude Code 검색
              </button>
            ) : (
              <button
                onClick={handleCancelSearch}
                disabled={cancelling}
                className="px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700 
                         disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {cancelling ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    취소 중...
                  </>
                ) : (
                  <>
                    <X size={18} />
                    검색 취소
                  </>
                )}
              </button>
            )}
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="px-4 py-2 bg-vscode-button text-white rounded hover:bg-vscode-button-hover"
            >
              고급 설정
            </button>
          </div>

          {/* Advanced Settings */}
          {showAdvanced && (
            <div className="mt-4 p-4 bg-vscode-input rounded border border-vscode-border">
              <div className="mb-3">
                <label className="block text-sm font-medium mb-2">검색 사이트 선택</label>
                <div className="flex gap-2 flex-wrap">
                  {availableSites.map(site => (
                    <button
                      key={site.id}
                      onClick={() => toggleSite(site.id)}
                      className={`px-3 py-1 rounded text-sm flex items-center gap-1
                        ${searchSites.includes(site.id) 
                          ? 'bg-vscode-blue text-white' 
                          : 'bg-vscode-button text-gray-300'}`}
                    >
                      <span>{site.icon}</span>
                      {site.name}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">최대 결과 수</label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={maxResults}
                  onChange={(e) => setMaxResults(parseInt(e.target.value) || 10)}
                  className="w-24 bg-vscode-input border border-vscode-border rounded px-2 py-1"
                />
              </div>
            </div>
          )}
        </div>

        {/* Progress Display */}
        {progress && (
          <div className="mb-4 p-4 bg-vscode-input rounded border border-vscode-border">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Loader2 className="animate-spin text-vscode-blue" size={20} />
                <span className="font-medium">{progress.message}</span>
              </div>
              <span className="text-sm text-vscode-text-dim">
                {progress.progress_percentage}%
              </span>
            </div>
            
            <div className="w-full bg-vscode-bg rounded-full h-2">
              <div 
                className="bg-vscode-blue h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress.progress_percentage}%` }}
              />
            </div>
            
            <div className="mt-2 text-sm text-vscode-text-dim">
              {progress.status === 'cancelled' ? (
                <span className="text-red-500">검색이 취소되었습니다</span>
              ) : (
                <>
                  {progress.current_site && (
                    <span className="mr-4">현재 사이트: {progress.current_site}</span>
                  )}
                  <span className="mr-4">찾은 논문: {progress.papers_found}</span>
                  {progress.papers_downloaded > 0 && (
                    <span>다운로드: {progress.papers_downloaded}</span>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {/* Results */}
        <div className="flex-1 overflow-auto">
          {results.length > 0 ? (
            <div className="grid gap-4">
              {results.map((paper) => (
                <div
                  key={paper.id}
                  className="border border-vscode-border rounded-lg p-4 hover:bg-vscode-hover 
                           cursor-pointer transition-colors"
                  onClick={() => setSelectedPaper(paper)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg mb-1">
                        {showKorean && paper.korean_title
                          ? paper.korean_title
                          : paper.title}
                      </h3>
                      {showKorean && paper.korean_title && (
                        <p className="text-sm text-vscode-text-dim mb-2">
                          {paper.title}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <span className={`px-2 py-1 rounded text-xs ${
                        paper.source === 'pubmed' ? 'bg-blue-600' :
                        paper.source === 'arxiv' ? 'bg-purple-600' :
                        paper.source === 'semantic_scholar' ? 'bg-green-600' :
                        'bg-gray-600'
                      }`}>
                        {paper.source}
                      </span>
                      {paper.pdf_downloaded && (
                        <div className="flex items-center gap-1 text-green-500">
                          <Check size={16} />
                          <span className="text-sm">PDF</span>
                        </div>
                      )}
                      {paper.korean_title && (
                        <div className="flex items-center gap-1 text-blue-500">
                          <Languages size={16} />
                          <span className="text-sm">한글</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-vscode-text-dim">
                    <span>{paper.authors.slice(0, 3).join(', ')}
                      {paper.authors.length > 3 && ' et al.'}</span>
                    <span>•</span>
                    <span>{paper.journal}</span>
                    <span>•</span>
                    <span>{paper.year}</span>
                  </div>

                  {paper.doi && (
                    <div className="mt-2 text-xs text-vscode-text-dim">
                      DOI: {paper.doi}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : !loading && (
            <div className="flex flex-col items-center justify-center h-full text-vscode-text-dim">
              <Code size={48} className="mb-4" />
              <p>Claude Code가 여러 학술 사이트에서</p>
              <p>논문을 검색하고 다운로드합니다</p>
            </div>
          )}
        </div>
      </div>

      {/* Paper Details Panel */}
      {selectedPaper && (
        <div className="w-1/2 border-l border-vscode-border p-6 overflow-auto">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">논문 상세 정보</h2>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowKorean(!showKorean)}
                className="px-3 py-1 bg-vscode-button rounded text-sm hover:bg-vscode-button-hover
                         flex items-center gap-2"
              >
                <Globe size={14} />
                {showKorean ? '한글' : 'English'}
              </button>
              <button
                onClick={() => setSelectedPaper(null)}
                className="p-1 hover:bg-vscode-hover rounded"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {/* Source Badge */}
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded text-sm ${
                selectedPaper.source === 'pubmed' ? 'bg-blue-600' :
                selectedPaper.source === 'arxiv' ? 'bg-purple-600' :
                selectedPaper.source === 'semantic_scholar' ? 'bg-green-600' :
                'bg-gray-600'
              }`}>
                {selectedPaper.source.toUpperCase()}
              </span>
              {selectedPaper.pdf_downloaded && (
                <span className="px-3 py-1 bg-green-600 rounded text-sm flex items-center gap-1">
                  <FileText size={14} />
                  PDF Downloaded
                </span>
              )}
            </div>

            {/* Title */}
            <div>
              <h3 className="font-semibold mb-1">제목</h3>
              <p className="text-sm">
                {showKorean && selectedPaper.korean_title
                  ? selectedPaper.korean_title
                  : selectedPaper.title}
              </p>
              {showKorean && selectedPaper.korean_title && (
                <p className="text-sm text-vscode-text-dim mt-1">
                  {selectedPaper.title}
                </p>
              )}
            </div>

            {/* Authors */}
            <div>
              <h3 className="font-semibold mb-1">저자</h3>
              <p className="text-sm">{selectedPaper.authors.join(', ')}</p>
            </div>

            {/* Journal Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold mb-1">저널</h3>
                <p className="text-sm">{selectedPaper.journal || 'N/A'}</p>
              </div>
              <div>
                <h3 className="font-semibold mb-1">발행년도</h3>
                <p className="text-sm">{selectedPaper.year}</p>
              </div>
            </div>

            {/* Abstract */}
            {(selectedPaper.korean_abstract || selectedPaper.abstract) && (
              <div>
                <h3 className="font-semibold mb-1">초록</h3>
                <p className="text-sm whitespace-pre-wrap">
                  {showKorean && selectedPaper.korean_abstract
                    ? selectedPaper.korean_abstract
                    : selectedPaper.abstract || '초록 없음'}
                </p>
              </div>
            )}

            {/* Links */}
            <div className="border-t border-vscode-border pt-4">
              <h3 className="font-semibold mb-2">링크</h3>
              <div className="space-y-2">
                {selectedPaper.doi && (
                  <a
                    href={`https://doi.org/${selectedPaper.doi}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-vscode-blue hover:underline"
                  >
                    <Link size={14} />
                    DOI: {selectedPaper.doi}
                  </a>
                )}
                <div className="flex items-center gap-2 text-sm">
                  <Folder size={14} />
                  <span className="text-vscode-text-dim">저장 위치:</span>
                  <span className="font-mono text-xs">{selectedPaper.folder}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
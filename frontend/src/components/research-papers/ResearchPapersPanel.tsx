'use client'

import React, { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Search, Filter, FileText, Download, Eye, X } from 'lucide-react'

interface ResearchPaper {
  pmid: string
  title: string
  abstract: string
  authors: string[]
  journal: string
  year: string
  doi: string
  pmc_id: string | null
  has_full_text: boolean
  fusion_type: string
  keywords: string[]
  abstract_content?: string
  full_text_content?: string
}

export function ResearchPapersPanel() {
  const [papers, setPapers] = useState<ResearchPaper[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPaper, setSelectedPaper] = useState<ResearchPaper | null>(null)
  const [viewDialogOpen, setViewDialogOpen] = useState(false)
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFusionType, setSelectedFusionType] = useState('')
  const [selectedYear, setSelectedYear] = useState('')
  const [fusionTypes, setFusionTypes] = useState<string[]>([])
  const [years, setYears] = useState<string[]>([])

  useEffect(() => {
    fetchPapers()
    fetchFilterOptions()
  }, [searchQuery, selectedFusionType, selectedYear])

  const fetchPapers = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (searchQuery) params.append('search_query', searchQuery)
      if (selectedFusionType) params.append('fusion_type', selectedFusionType)
      if (selectedYear) params.append('year', selectedYear)
      
      const response = await api.get(`/research-papers/?${params}`)
      setPapers(response.data)
      setError(null)
    } catch (err) {
      setError('논문을 불러오는데 실패했습니다.')
      console.error('Error fetching papers:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchFilterOptions = async () => {
    try {
      const [fusionTypesRes, yearsRes] = await Promise.all([
        api.get('/research-papers/fusion-types/list'),
        api.get('/research-papers/years/list')
      ])
      setFusionTypes(fusionTypesRes.data)
      setYears(yearsRes.data)
    } catch (err) {
      console.error('Error fetching filter options:', err)
    }
  }

  const viewPaperDetails = async (paper: ResearchPaper) => {
    try {
      const response = await api.get(`/research-papers/${paper.pmid}`)
      setSelectedPaper(response.data)
      setViewDialogOpen(true)
    } catch (err) {
      console.error('Error fetching paper details:', err)
    }
  }

  const handleCloseDialog = () => {
    setViewDialogOpen(false)
    setSelectedPaper(null)
  }

  return (
    <div className="h-full bg-vscode-bg text-vscode-text">
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="border-b border-vscode-border p-4">
          <h2 className="text-lg font-semibold mb-4">요추 유합술 연구 논문</h2>
          
          {/* Filters */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Search className="text-vscode-text-dim" size={18} />
              <input
                type="text"
                placeholder="검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 bg-vscode-input border border-vscode-border rounded px-3 py-1 text-sm focus:outline-none focus:border-vscode-blue"
              />
            </div>
            
            <div className="flex space-x-2">
              <select
                value={selectedFusionType}
                onChange={(e) => setSelectedFusionType(e.target.value)}
                className="bg-vscode-input border border-vscode-border rounded px-3 py-1 text-sm focus:outline-none focus:border-vscode-blue"
              >
                <option value="">모든 유합술 종류</option>
                {fusionTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="bg-vscode-input border border-vscode-border rounded px-3 py-1 text-sm focus:outline-none focus:border-vscode-blue"
              >
                <option value="">모든 연도</option>
                {years.map((year) => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
              
              <button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedFusionType('')
                  setSelectedYear('')
                }}
                className="px-3 py-1 text-sm bg-vscode-button hover:bg-vscode-button-hover rounded flex items-center space-x-1"
              >
                <Filter size={14} />
                <span>초기화</span>
              </button>
            </div>
          </div>
        </div>

        {/* Papers List */}
        <div className="flex-1 overflow-auto p-4">
          {loading ? (
            <div className="text-center text-vscode-text-dim">논문을 불러오는 중...</div>
          ) : error ? (
            <div className="text-red-500 bg-red-900/20 border border-red-800 rounded p-3">{error}</div>
          ) : (
            <div className="space-y-3">
              {papers.map((paper) => (
                <div key={paper.pmid} className="border border-vscode-border rounded-lg p-4 hover:bg-vscode-hover">
                  <div className="mb-2">
                    <h3 className="font-semibold text-vscode-text-bright mb-1">{paper.title}</h3>
                    <p className="text-sm text-vscode-text-dim">
                      {paper.authors.slice(0, 3).join(', ')}
                      {paper.authors.length > 3 && ' et al.'}
                    </p>
                    <p className="text-sm text-vscode-text-dim">
                      {paper.journal} ({paper.year})
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="inline-flex items-center px-2 py-1 text-xs bg-vscode-blue/20 text-vscode-blue rounded">
                      {paper.fusion_type}
                    </span>
                    {paper.has_full_text && (
                      <span className="inline-flex items-center px-2 py-1 text-xs bg-green-600/20 text-green-400 rounded">
                        Full Text
                      </span>
                    )}
                    <span className="inline-flex items-center px-2 py-1 text-xs bg-vscode-border rounded">
                      PMID: {paper.pmid}
                    </span>
                  </div>

                  <p className="text-sm text-vscode-text mb-3 line-clamp-3">
                    {paper.abstract}
                  </p>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => viewPaperDetails(paper)}
                      className="flex items-center space-x-1 px-3 py-1 text-sm bg-vscode-blue text-white rounded hover:bg-vscode-blue-hover"
                    >
                      <Eye size={14} />
                      <span>상세보기</span>
                    </button>
                    {paper.doi && (
                      <a
                        href={`https://doi.org/${paper.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-1 px-3 py-1 text-sm bg-vscode-button hover:bg-vscode-button-hover rounded"
                      >
                        <FileText size={14} />
                        <span>DOI</span>
                      </a>
                    )}
                    {paper.pmc_id && (
                      <a
                        href={`https://www.ncbi.nlm.nih.gov/pmc/articles/${paper.pmc_id}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-1 px-3 py-1 text-sm bg-vscode-button hover:bg-vscode-button-hover rounded"
                      >
                        <Download size={14} />
                        <span>PMC</span>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Paper Details Modal */}
      {viewDialogOpen && selectedPaper && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-vscode-bg border border-vscode-border rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="border-b border-vscode-border p-4 flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-2">{selectedPaper.title}</h3>
                <p className="text-sm text-vscode-text-dim">
                  {selectedPaper.authors.join(', ')}
                </p>
                <p className="text-sm text-vscode-text-dim">
                  {selectedPaper.journal} ({selectedPaper.year})
                </p>
              </div>
              <button
                onClick={handleCloseDialog}
                className="p-1 hover:bg-vscode-hover rounded"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-auto p-4">
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <span className="inline-flex items-center px-2 py-1 text-xs bg-vscode-blue/20 text-vscode-blue rounded">
                    {selectedPaper.fusion_type}
                  </span>
                  {selectedPaper.has_full_text && (
                    <span className="inline-flex items-center px-2 py-1 text-xs bg-green-600/20 text-green-400 rounded">
                      Full Text Available
                    </span>
                  )}
                  <span className="inline-flex items-center px-2 py-1 text-xs bg-vscode-border rounded">
                    PMID: {selectedPaper.pmid}
                  </span>
                  {selectedPaper.doi && (
                    <span className="inline-flex items-center px-2 py-1 text-xs bg-vscode-border rounded">
                      DOI: {selectedPaper.doi}
                    </span>
                  )}
                </div>

                {selectedPaper.keywords.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Keywords</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedPaper.keywords.map((keyword, index) => (
                        <span key={index} className="inline-flex items-center px-2 py-1 text-xs bg-vscode-border rounded">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="border-t border-vscode-border pt-4">
                  <h4 className="font-semibold mb-2">Abstract</h4>
                  <p className="text-sm whitespace-pre-wrap">
                    {selectedPaper.abstract_content || selectedPaper.abstract}
                  </p>
                </div>

                {selectedPaper.full_text_content && (
                  <div className="border-t border-vscode-border pt-4">
                    <h4 className="font-semibold mb-2">Full Text</h4>
                    <p className="text-sm whitespace-pre-wrap">
                      {selectedPaper.full_text_content}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="border-t border-vscode-border p-4 flex justify-end space-x-2">
              {selectedPaper.doi && (
                <a
                  href={`https://doi.org/${selectedPaper.doi}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 px-3 py-1 text-sm bg-vscode-button hover:bg-vscode-button-hover rounded"
                >
                  <FileText size={14} />
                  <span>Publisher Site</span>
                </a>
              )}
              {selectedPaper.pmc_id && (
                <a
                  href={`https://www.ncbi.nlm.nih.gov/pmc/articles/${selectedPaper.pmc_id}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 px-3 py-1 text-sm bg-vscode-button hover:bg-vscode-button-hover rounded"
                >
                  <Download size={14} />
                  <span>View on PMC</span>
                </a>
              )}
              <button
                onClick={handleCloseDialog}
                className="px-3 py-1 text-sm bg-vscode-button hover:bg-vscode-button-hover rounded"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
'use client'

import { useState, useEffect, useRef } from 'react'
import { 
  VscRobot, VscSend, VscLoading, VscFile, VscFolder, 
  VscNotebook, VscSymbolFile, VscGear, VscCheck, VscError 
} from '../icons'
import { useProjectStore } from '@/stores/useProjectStore'
import { toast } from 'react-hot-toast'
import { api } from '@/lib/api'

interface AIModel {
  id: string
  name: string
  type: 'claude' | 'ollama'
  available: boolean
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

export function AIPanel() {
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'draft'>('chat')
  const [models, setModels] = useState<AIModel[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('llama2')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  
  // Document analysis
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [analysisType, setAnalysisType] = useState<'summary' | 'qa' | 'outline'>('summary')
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  
  // Paper draft
  const [draftTitle, setDraftTitle] = useState('')
  const [draftKeywords, setDraftKeywords] = useState<string[]>([])
  const [draftOutline, setDraftOutline] = useState('')
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { currentProject } = useProjectStore()
  
  useEffect(() => {
    fetchModels()
  }, [])
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  const fetchModels = async () => {
    try {
      const response = await api.post('/ai/models', {})
      setModels(response.data)
      
      // 사용 가능한 첫 번째 모델 선택
      const availableModel = response.data.find((m: AIModel) => m.available)
      if (availableModel) {
        setSelectedModel(availableModel.id)
      }
    } catch (error) {
      console.error('Failed to fetch models:', error)
    }
  }
  
  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentProject) return
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    
    try {
      const response = await api.post('/ai/chat', {
        project_id: currentProject.id,
        message: inputMessage,
        model: selectedModel,
        session_id: sessionId
      })
      
      if (!sessionId) {
        setSessionId(response.data.session_id)
      }
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      toast.error('AI 응답 실패')
    } finally {
      setIsLoading(false)
    }
  }
  
  const analyzeDocuments = async () => {
    if (selectedFiles.length === 0 || !currentProject) {
      toast.error('분석할 문서를 선택해주세요')
      return
    }
    
    setIsLoading(true)
    
    try {
      const response = await api.post('/ai/analyze-documents', {
        project_id: currentProject.id,
        document_paths: selectedFiles,
        analysis_type: analysisType,
        model: selectedModel
      })
      
      setAnalysisResult(response.data)
      toast.success('문서 분석 완료')
    } catch (error) {
      console.error('Failed to analyze documents:', error)
      toast.error('문서 분석 실패')
    } finally {
      setIsLoading(false)
    }
  }
  
  const generateDraft = async () => {
    if (!draftTitle || !currentProject) {
      toast.error('논문 제목을 입력해주세요')
      return
    }
    
    setIsLoading(true)
    
    try {
      const response = await api.post('/ai/generate-draft', {
        project_id: currentProject.id,
        title: draftTitle,
        keywords: draftKeywords,
        outline: JSON.parse(draftOutline || '{}'),
        references: [],
        model: selectedModel
      })
      
      // 생성된 초안을 새 창에서 표시
      const draft = response.data.response
      const newWindow = window.open('', '_blank')
      if (newWindow) {
        newWindow.document.write(`
          <html>
            <head>
              <title>${draftTitle} - Draft</title>
              <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1, h2, h3 { color: #333; }
                pre { white-space: pre-wrap; }
              </style>
            </head>
            <body>
              <pre>${draft}</pre>
            </body>
          </html>
        `)
      }
      
      toast.success('논문 초안 생성 완료')
    } catch (error) {
      console.error('Failed to generate draft:', error)
      toast.error('초안 생성 실패')
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-64 bg-vscode-sidebar border-r border-vscode-border p-4">
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <VscRobot size={16} />
          AI Assistant
        </h3>
        
        {/* Model Selection */}
        <div className="mb-4">
          <label className="text-xs text-vscode-text-dim block mb-1">모델 선택</label>
          <select 
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="vscode-input text-xs"
          >
            {models.map(model => (
              <option key={model.id} value={model.id} disabled={!model.available}>
                {model.name} {!model.available && '(사용불가)'}
              </option>
            ))}
          </select>
        </div>
        
        {/* Tabs */}
        <div className="space-y-1">
          <button
            onClick={() => setActiveTab('chat')}
            className={`w-full text-left px-3 py-2 rounded text-sm flex items-center gap-2 ${
              activeTab === 'chat' ? 'bg-vscode-list-active' : 'hover:bg-vscode-hover'
            }`}
          >
            <VscRobot size={16} />
            AI 채팅
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`w-full text-left px-3 py-2 rounded text-sm flex items-center gap-2 ${
              activeTab === 'documents' ? 'bg-vscode-list-active' : 'hover:bg-vscode-hover'
            }`}
          >
            <VscNotebook size={16} />
            문서 분석
          </button>
          <button
            onClick={() => setActiveTab('draft')}
            className={`w-full text-left px-3 py-2 rounded text-sm flex items-center gap-2 ${
              activeTab === 'draft' ? 'bg-vscode-list-active' : 'hover:bg-vscode-hover'
            }`}
          >
            <VscSymbolFile size={16} />
            논문 초안
          </button>
        </div>
        
        {/* Model Status */}
        <div className="mt-6 p-3 bg-vscode-bg-light rounded border border-vscode-border">
          <div className="text-xs">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-vscode-text-dim">상태:</span>
              <span className="flex items-center gap-1">
                {models.some(m => m.available) ? (
                  <>
                    <VscCheck className="text-vscode-green" size={14} />
                    <span className="text-vscode-green">연결됨</span>
                  </>
                ) : (
                  <>
                    <VscError className="text-vscode-red" size={14} />
                    <span className="text-vscode-red">연결 안됨</span>
                  </>
                )}
              </span>
            </div>
            <div className="text-vscode-text-dim">
              {models.filter(m => m.available).length}개 모델 사용가능
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {activeTab === 'chat' && (
          <>
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4">
              {messages.length === 0 ? (
                <div className="text-center text-vscode-text-dim mt-8">
                  <VscRobot size={48} className="mx-auto mb-4 opacity-50" />
                  <p>AI와 대화를 시작해보세요</p>
                  <p className="text-xs mt-2">연구 관련 질문이나 도움이 필요한 내용을 입력하세요</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-3xl p-3 rounded-lg ${
                        msg.role === 'user' 
                          ? 'bg-vscode-blue text-white' 
                          : 'bg-vscode-bg-light border border-vscode-border'
                      }`}>
                        <div className="text-xs opacity-70 mb-1">
                          {msg.role === 'user' ? '나' : selectedModel}
                        </div>
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
            
            {/* Chat Input */}
            <div className="border-t border-vscode-border p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="메시지를 입력하세요..."
                  className="vscode-input flex-1"
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="vscode-button px-4"
                >
                  {isLoading ? <VscLoading className="animate-spin" size={16} /> : <VscSend size={16} />}
                </button>
              </div>
            </div>
          </>
        )}
        
        {activeTab === 'documents' && (
          <div className="p-4">
            <h2 className="text-lg font-semibold mb-4">문서 분석 (NotebookLM 스타일)</h2>
            
            {/* File Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">분석할 문서 선택</label>
              <div className="border border-vscode-border rounded p-4 bg-vscode-bg-light">
                <div className="flex items-center gap-2 mb-2">
                  <VscFolder size={16} />
                  <span className="text-sm">/project_files/{currentProject?.id}/</span>
                </div>
                <div className="text-xs text-vscode-text-dim">
                  {selectedFiles.length}개 파일 선택됨
                </div>
                {/* TODO: 파일 브라우저 구현 */}
              </div>
            </div>
            
            {/* Analysis Type */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">분석 유형</label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: 'summary', label: '요약', desc: '문서의 핵심 내용 요약' },
                  { id: 'qa', label: 'Q&A', desc: '주요 질문과 답변 생성' },
                  { id: 'outline', label: '개요', desc: '계층적 문서 구조 분석' }
                ].map(type => (
                  <button
                    key={type.id}
                    onClick={() => setAnalysisType(type.id as any)}
                    className={`p-3 border rounded text-left ${
                      analysisType === type.id 
                        ? 'border-vscode-blue bg-vscode-selection' 
                        : 'border-vscode-border hover:bg-vscode-hover'
                    }`}
                  >
                    <div className="text-sm font-medium">{type.label}</div>
                    <div className="text-xs text-vscode-text-dim">{type.desc}</div>
                  </button>
                ))}
              </div>
            </div>
            
            <button
              onClick={analyzeDocuments}
              disabled={isLoading || selectedFiles.length === 0}
              className="vscode-button"
            >
              {isLoading ? '분석 중...' : '문서 분석 시작'}
            </button>
            
            {/* Analysis Result */}
            {analysisResult && (
              <div className="mt-6 p-4 bg-vscode-bg-light border border-vscode-border rounded">
                <h3 className="font-semibold mb-2">분석 결과</h3>
                <pre className="whitespace-pre-wrap text-sm">
                  {analysisResult.response || JSON.stringify(analysisResult, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'draft' && (
          <div className="p-4">
            <h2 className="text-lg font-semibold mb-4">논문 초안 생성</h2>
            
            <div className="space-y-4 max-w-2xl">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium mb-1">논문 제목</label>
                <input
                  type="text"
                  value={draftTitle}
                  onChange={(e) => setDraftTitle(e.target.value)}
                  placeholder="예: 척추 고정술의 장기 추적 결과"
                  className="vscode-input"
                />
              </div>
              
              {/* Keywords */}
              <div>
                <label className="block text-sm font-medium mb-1">키워드</label>
                <input
                  type="text"
                  placeholder="쉼표로 구분하여 입력"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      const input = e.currentTarget.value.trim()
                      if (input) {
                        setDraftKeywords([...draftKeywords, ...input.split(',').map(k => k.trim())])
                        e.currentTarget.value = ''
                      }
                    }
                  }}
                  className="vscode-input"
                />
                <div className="flex flex-wrap gap-2 mt-2">
                  {draftKeywords.map((kw, idx) => (
                    <span key={idx} className="px-2 py-1 bg-vscode-bg text-xs rounded border border-vscode-border">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
              
              {/* Outline */}
              <div>
                <label className="block text-sm font-medium mb-1">논문 개요 (JSON)</label>
                <textarea
                  value={draftOutline}
                  onChange={(e) => setDraftOutline(e.target.value)}
                  placeholder={`{
  "introduction": ["배경", "목적"],
  "methods": ["환자 선택", "수술 방법", "평가 방법"],
  "results": ["임상 결과", "영상학적 결과"],
  "discussion": ["주요 발견", "한계점"],
  "conclusion": ["결론"]
}`}
                  className="vscode-input font-mono text-xs"
                  rows={10}
                />
              </div>
              
              <button
                onClick={generateDraft}
                disabled={isLoading || !draftTitle}
                className="vscode-button"
              >
                {isLoading ? '생성 중...' : '논문 초안 생성'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
'use client'

import { useState, useEffect, useRef } from 'react'
import { VscSend, VscRobot, VscAccount, VscLoading, VscRefresh, VscCloud } from '../icons'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  enhanced?: boolean
  persona?: string
  thinkingSteps?: number
}

export default function AIChatbot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [availableModels, setAvailableModels] = useState<any[]>([])
  const [selectedModel, setSelectedModel] = useState('llama2')
  const [loadingModels, setLoadingModels] = useState(false)
  const [enhancedMode, setEnhancedMode] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Load available models on mount
    loadModels()
  }, [])

  const loadModels = async () => {
    setLoadingModels(true)
    try {
      const response = await api.getAIModels()
      setAvailableModels(response.data.models || [])
      if (response.data.current_model) {
        setSelectedModel(response.data.current_model)
      }
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setLoadingModels(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message
    const newUserMessage: Message = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, newUserMessage])
    setLoading(true)

    try {
      const response = await api.sendAIChat({
        message: userMessage,
        session_id: sessionId || undefined,
        model: selectedModel,
        enhanced_mode: enhancedMode || selectedModel === 'superclaude'
      })

      // Update session ID if new
      if (!sessionId && response.data.session_id) {
        setSessionId(response.data.session_id)
      }

      // Add AI response
      const aiMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
        enhanced: response.data.enhanced,
        persona: response.data.persona,
        thinkingSteps: response.data.thinking_steps
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      toast.error('AI 응답을 받을 수 없습니다')
      console.error('Chat error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="h-full flex flex-col bg-vscode-bg-light border border-vscode-border rounded-lg">
      {/* Header */}
      <div className="p-4 border-b border-vscode-border">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <VscRobot className="text-vscode-blue" size={20} />
              AI 연구 도우미
            </h3>
            <p className="text-xs text-vscode-text-dim mt-1">
              연구 관련 질문을 해보세요
            </p>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={selectedModel}
              onChange={(e) => {
                setSelectedModel(e.target.value)
                // Auto-enable enhanced mode for SuperClaude
                if (e.target.value === 'superclaude') {
                  setEnhancedMode(true)
                }
              }}
              className="vscode-input text-sm py-1 px-2"
              disabled={loading || loadingModels}
            >
              {availableModels.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name} {model.provider === 'ollama' && '(Local)'} {model.provider === 'superclaude' && '⚡'}
                </option>
              ))}
            </select>
            <button
              onClick={loadModels}
              disabled={loadingModels}
              className="vscode-button p-1"
              title="모델 목록 새로고침"
            >
              <VscRefresh className={loadingModels ? 'animate-spin' : ''} size={16} />
            </button>
            {selectedModel !== 'superclaude' && (
              <label className="flex items-center gap-1 text-xs">
                <input
                  type="checkbox"
                  checked={enhancedMode}
                  onChange={(e) => setEnhancedMode(e.target.checked)}
                  className="rounded"
                />
                <span className="text-vscode-text-dim">Enhanced</span>
              </label>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-vscode-text-dim py-8">
            <VscRobot size={48} className="mx-auto mb-4 opacity-50" />
            <p>안녕하세요! 무엇을 도와드릴까요?</p>
            <div className="mt-4 space-y-2 text-sm">
              <p>예시 질문:</p>
              <ul className="text-left max-w-md mx-auto space-y-1">
                <li>• 척추 수술 후 통증 관리에 대한 최신 연구는?</li>
                <li>• 무작위 대조 시험 설계 방법을 알려주세요</li>
                <li>• IRB 승인을 위한 서류 준비는 어떻게 하나요?</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <VscRobot className="text-vscode-blue mt-1" size={20} />
              )}
              <div
                className={`max-w-[70%] p-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-vscode-blue text-white'
                    : 'bg-vscode-bg border border-vscode-border'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <div className="flex items-center gap-2 text-xs opacity-70 mt-1">
                  <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                  {message.enhanced && (
                    <span className="text-vscode-blue">⚡ Enhanced</span>
                  )}
                  {message.persona && (
                    <span className="text-vscode-green">👤 {message.persona}</span>
                  )}
                  {message.thinkingSteps && message.thinkingSteps > 0 && (
                    <span className="text-vscode-yellow">🧠 {message.thinkingSteps} steps</span>
                  )}
                </div>
              </div>
              {message.role === 'user' && (
                <VscAccount className="text-vscode-text-dim mt-1" size={20} />
              )}
            </div>
          ))
        )}
        {loading && (
          <div className="flex gap-3 justify-start">
            <VscRobot className="text-vscode-blue mt-1" size={20} />
            <div className="bg-vscode-bg border border-vscode-border p-3 rounded-lg">
              <VscLoading className="animate-spin" size={16} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-vscode-border">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            className="flex-1 vscode-input resize-none"
            rows={2}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="vscode-button px-4 self-end"
          >
            <VscSend size={18} />
          </button>
        </div>
        <div className="flex items-center justify-between mt-2">
          <p className="text-xs text-vscode-text-dim">
            Shift + Enter로 줄바꿈, Enter로 전송
          </p>
          <div className="flex items-center gap-2">
            {(enhancedMode || selectedModel === 'superclaude') && (
              <p className="text-xs text-vscode-blue flex items-center gap-1">
                ⚡ Enhanced Mode
              </p>
            )}
            {selectedModel.startsWith('ollama/') && (
              <p className="text-xs text-vscode-text-dim flex items-center gap-1">
                <VscCloud size={12} />
                로컬 모델 사용 중
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
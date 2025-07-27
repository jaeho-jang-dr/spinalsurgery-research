'use client'

import React, { useState, useEffect, useRef } from 'react'
import { api } from '@/lib/api'
import { 
  Send, 
  User, 
  Bot, 
  Settings, 
  Brain, 
  Sparkles,
  Command,
  HelpCircle,
  Download,
  Upload,
  Trash2,
  Layers,
  Users
} from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  persona?: string
  thinking?: boolean
}

interface Persona {
  id: string
  name: string
  role: string
  traits: string[]
  expertise: string[]
  language_style: string
}

interface ContextLevel {
  [key: string]: any
}

export function AdvancedAIPanel() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [personas, setPersonas] = useState<Persona[]>([])
  const [currentPersona, setCurrentPersona] = useState<string>('research_assistant')
  const [showCommands, setShowCommands] = useState(false)
  const [magicCommands, setMagicCommands] = useState<any[]>([])
  const [contextLevels, setContextLevels] = useState<ContextLevel>({})
  const [showSettings, setShowSettings] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    loadPersonas()
    loadMagicCommands()
    loadContext()
    
    // Initialize Ollama
    api.post('/ai-advanced/initialize').catch(console.error)
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadPersonas = async () => {
    try {
      const response = await api.get('/ai-advanced/personas')
      setPersonas(response.data.personas)
      setCurrentPersona(response.data.current)
    } catch (error) {
      console.error('Failed to load personas:', error)
    }
  }

  const loadMagicCommands = async () => {
    try {
      const response = await api.get('/ai-advanced/commands')
      setMagicCommands(response.data.commands)
    } catch (error) {
      console.error('Failed to load commands:', error)
    }
  }

  const loadContext = async () => {
    try {
      const response = await api.get('/ai-advanced/context')
      setContextLevels(response.data)
    } catch (error) {
      console.error('Failed to load context:', error)
    }
  }

  const switchPersona = async (personaId: string) => {
    try {
      await api.put(`/ai-advanced/personas/${personaId}`)
      setCurrentPersona(personaId)
      
      const persona = personas.find(p => p.id === personaId)
      if (persona) {
        addSystemMessage(`Switched to ${persona.name} - ${persona.role}`)
      }
    } catch (error) {
      console.error('Failed to switch persona:', error)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      persona: currentPersona,
      thinking: input.startsWith('/think')
    }

    setMessages(prev => [...prev, assistantMessage])

    try {
      // Create abort controller for streaming
      abortControllerRef.current = new AbortController()

      const response = await fetch('/api/v1/ai-advanced/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || 'mock-token'}`
        },
        body: JSON.stringify({
          message: input,
          persona: currentPersona,
          context: {
            temporal: { timestamp: new Date().toISOString() },
            task: contextLevels.task || {}
          }
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) throw new Error('Chat request failed')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, content: msg.content + chunk }
              : msg
          ))
        }
      }
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Chat error:', error)
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id 
            ? { ...msg, content: 'Error: Failed to get response' }
            : msg
        ))
      }
    } finally {
      setLoading(false)
      abortControllerRef.current = null
    }
  }

  const addSystemMessage = (content: string) => {
    const systemMessage: Message = {
      id: Date.now().toString(),
      type: 'system',
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, systemMessage])
  }

  const exportMemory = async () => {
    try {
      const response = await api.get('/ai-advanced/memory/export?format=json')
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ai-memory-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
      addSystemMessage('Memory exported successfully')
    } catch (error) {
      console.error('Failed to export memory:', error)
      addSystemMessage('Failed to export memory')
    }
  }

  const importMemory = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      const data = JSON.parse(text)
      await api.post('/ai-advanced/memory/import', { data, merge: true })
      addSystemMessage('Memory imported successfully')
    } catch (error) {
      console.error('Failed to import memory:', error)
      addSystemMessage('Failed to import memory')
    }
  }

  const clearMemory = async (type: string) => {
    if (!confirm(`Are you sure you want to clear ${type} memory?`)) return

    try {
      await api.delete(`/ai-advanced/memory?memory_type=${type}`)
      addSystemMessage(`${type} memory cleared`)
    } catch (error) {
      console.error('Failed to clear memory:', error)
    }
  }

  const updateContext = async (level: string, data: any) => {
    try {
      await api.put(`/ai-advanced/context/${level}`, data)
      setContextLevels(prev => ({ ...prev, [level]: data }))
    } catch (error) {
      console.error('Failed to update context:', error)
    }
  }

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user'
    const isSystem = message.type === 'system'

    if (isSystem) {
      return (
        <div key={message.id} className="flex justify-center my-2">
          <div className="bg-vscode-button/20 text-vscode-text-dim px-3 py-1 rounded text-sm">
            {message.content}
          </div>
        </div>
      )
    }

    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start max-w-[80%]`}>
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-vscode-blue ml-2' : 'bg-vscode-button mr-2'
          }`}>
            {isUser ? <User size={16} /> : <Bot size={16} />}
          </div>
          
          <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
            {!isUser && message.persona && (
              <div className="text-xs text-vscode-text-dim mb-1">
                {personas.find(p => p.id === message.persona)?.name || message.persona}
                {message.thinking && ' 🤔 (Sequential Thinking)'}
              </div>
            )}
            
            <div className={`rounded-lg px-4 py-2 ${
              isUser 
                ? 'bg-vscode-blue text-white' 
                : 'bg-vscode-input border border-vscode-border'
            }`}>
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
            </div>
            
            <div className="text-xs text-vscode-text-dim mt-1">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-full bg-vscode-bg">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-vscode-border p-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold">Advanced AI Assistant</h2>
            <div className="flex items-center space-x-2">
              <Sparkles size={16} className="text-vscode-blue" />
              <span className="text-sm text-vscode-text-dim">
                {personas.find(p => p.id === currentPersona)?.name || 'AI'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowCommands(!showCommands)}
              className="p-2 hover:bg-vscode-hover rounded"
              title="Magic Commands"
            >
              <Command size={18} />
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-vscode-hover rounded"
              title="Settings"
            >
              <Settings size={18} />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-auto p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-vscode-text-dim">
              <Brain size={48} className="mb-4" />
              <p className="text-center mb-2">Advanced AI Assistant with Memory & Personas</p>
              <p className="text-sm">Type a message or use magic commands (/help)</p>
            </div>
          ) : (
            <>
              {messages.map(renderMessage)}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-vscode-border p-4">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type a message or command..."
              className="flex-1 bg-vscode-input border border-vscode-border rounded px-3 py-2 text-sm focus:outline-none focus:border-vscode-blue"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="p-2 bg-vscode-blue text-white rounded hover:bg-vscode-blue-hover disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Commands Panel */}
      {showCommands && (
        <div className="w-80 border-l border-vscode-border p-4 overflow-auto">
          <h3 className="font-semibold mb-4 flex items-center">
            <Command size={18} className="mr-2" />
            Magic Commands
          </h3>
          
          <div className="space-y-2">
            {magicCommands.map((cmd) => (
              <div key={cmd.command} className="border border-vscode-border rounded p-3">
                <div className="font-mono text-sm text-vscode-blue mb-1">{cmd.command}</div>
                <div className="text-xs text-vscode-text-dim">{cmd.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Settings Panel */}
      {showSettings && (
        <div className="w-80 border-l border-vscode-border p-4 overflow-auto">
          <h3 className="font-semibold mb-4 flex items-center">
            <Settings size={18} className="mr-2" />
            AI Settings
          </h3>

          {/* Personas */}
          <div className="mb-6">
            <h4 className="text-sm font-semibold mb-2 flex items-center">
              <Users size={16} className="mr-2" />
              Personas
            </h4>
            <div className="space-y-2">
              {personas.map((persona) => (
                <button
                  key={persona.id}
                  onClick={() => switchPersona(persona.id)}
                  className={`w-full text-left p-3 rounded border transition-colors ${
                    currentPersona === persona.id
                      ? 'border-vscode-blue bg-vscode-blue/10'
                      : 'border-vscode-border hover:bg-vscode-hover'
                  }`}
                >
                  <div className="font-semibold text-sm">{persona.name}</div>
                  <div className="text-xs text-vscode-text-dim">{persona.role}</div>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {persona.traits.slice(0, 3).map((trait, i) => (
                      <span key={i} className="text-xs bg-vscode-border px-1 rounded">
                        {trait}
                      </span>
                    ))}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Memory Management */}
          <div className="mb-6">
            <h4 className="text-sm font-semibold mb-2 flex items-center">
              <Brain size={16} className="mr-2" />
              Memory Management
            </h4>
            <div className="space-y-2">
              <button
                onClick={exportMemory}
                className="w-full flex items-center justify-center space-x-2 p-2 bg-vscode-button hover:bg-vscode-button-hover rounded text-sm"
              >
                <Download size={14} />
                <span>Export Memory</span>
              </button>
              
              <label className="w-full flex items-center justify-center space-x-2 p-2 bg-vscode-button hover:bg-vscode-button-hover rounded text-sm cursor-pointer">
                <Upload size={14} />
                <span>Import Memory</span>
                <input
                  type="file"
                  accept=".json"
                  onChange={importMemory}
                  className="hidden"
                />
              </label>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => clearMemory('short_term')}
                  className="flex-1 p-2 bg-red-900/20 hover:bg-red-900/30 border border-red-800 rounded text-sm text-red-400"
                >
                  Clear Short-term
                </button>
                <button
                  onClick={() => clearMemory('long_term')}
                  className="flex-1 p-2 bg-red-900/20 hover:bg-red-900/30 border border-red-800 rounded text-sm text-red-400"
                >
                  Clear Long-term
                </button>
              </div>
            </div>
          </div>

          {/* Context Levels */}
          <div>
            <h4 className="text-sm font-semibold mb-2 flex items-center">
              <Layers size={16} className="mr-2" />
              Context Levels
            </h4>
            <div className="space-y-2 text-xs">
              {Object.entries(contextLevels).map(([level, data]) => (
                <div key={level} className="border border-vscode-border rounded p-2">
                  <div className="font-semibold">{level}</div>
                  <div className="text-vscode-text-dim mt-1">
                    {JSON.stringify(data, null, 2).substring(0, 100)}...
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
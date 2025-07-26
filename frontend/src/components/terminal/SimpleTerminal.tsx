'use client'

import React, { useState, useEffect, useRef } from 'react'
import { X, Plus, ChevronDown, Terminal as TerminalIcon } from 'lucide-react'

interface TerminalTab {
  id: string
  title: string
  content: string[]
  type: 'bash' | 'powershell' | 'cmd' | 'claude-code'
}

interface SimpleTerminalProps {
  onClose?: () => void
  height?: string
}

export const SimpleTerminal: React.FC<SimpleTerminalProps> = ({ 
  onClose, 
  height = 'h-96'
}) => {
  const [tabs, setTabs] = useState<TerminalTab[]>([])
  const [activeTabId, setActiveTabId] = useState<string>('')
  const [showNewTerminalMenu, setShowNewTerminalMenu] = useState(false)
  const [inputValue, setInputValue] = useState('')
  const terminalIdCounter = useRef(0)
  const terminalRef = useRef<HTMLDivElement>(null)

  // Terminal types for different platforms
  const terminalTypes = [
    { type: 'bash', label: 'Bash', icon: '$', available: true },
    { type: 'powershell', label: 'PowerShell', icon: 'PS>', available: typeof window !== 'undefined' && window.navigator.platform.includes('Win') },
    { type: 'cmd', label: 'Command Prompt', icon: 'C:\\>', available: typeof window !== 'undefined' && window.navigator.platform.includes('Win') },
    { type: 'claude-code', label: 'Claude Code CLI', icon: '🤖', available: true }
  ]

  // Create a new terminal tab
  const createTerminalTab = (type: 'bash' | 'powershell' | 'cmd' | 'claude-code') => {
    const id = `terminal-${terminalIdCounter.current++}`
    const title = type === 'claude-code' ? 'Claude Code' : 
                  type === 'powershell' ? 'PowerShell' :
                  type === 'cmd' ? 'CMD' : 'Bash'
    
    let initialContent: string[] = []
    
    if (type === 'claude-code') {
      initialContent = [
        '🤖 Claude Code CLI Terminal',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        '',
        'Available commands:',
        '  claude-code login     - Authenticate with Claude AI',
        '  claude-code status    - Check authentication status',
        '  claude-code chat      - Start coding with Claude',
        '  claude-code --help    - Show all commands',
        '',
        '$ '
      ]
    } else {
      initialContent = [`${type === 'bash' ? '$' : type === 'powershell' ? 'PS>' : 'C:\\>'} `]
    }

    const newTab: TerminalTab = {
      id,
      title,
      content: initialContent,
      type
    }

    setTabs(prev => [...prev, newTab])
    setActiveTabId(id)
    setShowNewTerminalMenu(false)
  }

  // Handle command input
  const handleCommand = (tabId: string, command: string) => {
    const tab = tabs.find(t => t.id === tabId)
    if (!tab) return

    // Add command to terminal
    const lastLine = tab.content[tab.content.length - 1]
    const newContent = [...tab.content]
    newContent[newContent.length - 1] = lastLine + command

    // Simulate command responses
    let response: string[] = []
    
    if (tab.type === 'claude-code') {
      // Simulate Claude Code CLI responses
      if (command === 'claude-code status') {
        response = [
          '✅ Authenticated',
          '   User: test@example.com',
          '   Token expires in: 29d 23h'
        ]
      } else if (command === 'claude-code --help') {
        response = [
          'Claude Code CLI v1.0.0',
          '',
          'Commands:',
          '  login         Authenticate with Claude AI',
          '  logout        Logout and remove credentials',
          '  status        Show authentication status',
          '  chat          Send a message to Claude',
          '  config        Manage configuration',
          '',
          'Options:',
          '  -v, --version Show version',
          '  -h, --help    Show help'
        ]
      } else if (command.startsWith('claude-code chat')) {
        response = [
          '🤖 Claude: I\'m here to help with your coding needs!',
          'You can ask me about:',
          '- Writing code in any language',
          '- Debugging issues',
          '- Explaining concepts',
          '- Reviewing your code'
        ]
      } else if (command === 'clear') {
        setTabs(prev => prev.map(t => 
          t.id === tabId 
            ? { ...t, content: [`${tab.type === 'bash' ? '$' : tab.type === 'powershell' ? 'PS>' : 'C:\\>'} `] }
            : t
        ))
        return
      } else {
        response = [`Command not found: ${command}`]
      }
    } else {
      // Basic command simulation for other terminal types
      if (command === 'help') {
        response = ['This is a simulated terminal. WebSocket connection required for full functionality.']
      } else if (command === 'clear' || command === 'cls') {
        setTabs(prev => prev.map(t => 
          t.id === tabId 
            ? { ...t, content: [`${tab.type === 'bash' ? '$' : tab.type === 'powershell' ? 'PS>' : 'C:\\>'} `] }
            : t
        ))
        return
      } else {
        response = [`'${command}' is not recognized. (Terminal simulation mode)`]
      }
    }

    // Add response and new prompt
    const prompt = tab.type === 'bash' ? '$ ' : 
                   tab.type === 'powershell' ? 'PS> ' :
                   tab.type === 'cmd' ? 'C:\\> ' : '$ '
    
    setTabs(prev => prev.map(t => 
      t.id === tabId 
        ? { ...t, content: [...newContent, ...response, prompt] }
        : t
    ))
  }

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && activeTabId) {
      handleCommand(activeTabId, inputValue)
      setInputValue('')
    }
  }

  // Close terminal tab
  const closeTab = (tabId: string) => {
    setTabs(prev => prev.filter(t => t.id !== tabId))
    
    if (activeTabId === tabId && tabs.length > 1) {
      const remainingTabs = tabs.filter(t => t.id !== tabId)
      if (remainingTabs.length > 0) {
        setActiveTabId(remainingTabs[0].id)
      }
    }

    if (tabs.length === 1 && onClose) {
      onClose()
    }
  }

  // Create initial terminal on mount
  useEffect(() => {
    if (tabs.length === 0) {
      createTerminalTab('claude-code')
    }
  }, [])

  // Scroll to bottom when content changes
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [tabs, activeTabId])

  const activeTab = tabs.find(t => t.id === activeTabId)

  return (
    <div className={`${height} bg-[#1e1e1e] border-t border-[#3e3e42] flex flex-col`}>
      {/* Terminal tabs header */}
      <div className="flex items-center justify-between bg-[#252526] border-b border-[#3e3e42] px-2 py-1">
        <div className="flex items-center gap-1 flex-1 overflow-x-auto">
          {tabs.map(tab => (
            <div
              key={tab.id}
              className={`flex items-center gap-2 px-3 py-1 cursor-pointer rounded-t text-sm ${
                activeTabId === tab.id 
                  ? 'bg-[#1e1e1e] text-white' 
                  : 'bg-[#2d2d30] text-gray-400 hover:bg-[#333333]'
              }`}
              onClick={() => setActiveTabId(tab.id)}
            >
              <TerminalIcon size={14} />
              <span>{tab.title}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  closeTab(tab.id)
                }}
                className="hover:bg-[#444444] rounded p-0.5"
              >
                <X size={12} />
              </button>
            </div>
          ))}
          
          {/* New terminal button */}
          <div className="relative">
            <button
              onClick={() => setShowNewTerminalMenu(!showNewTerminalMenu)}
              className="flex items-center gap-1 px-2 py-1 text-gray-400 hover:text-white hover:bg-[#333333] rounded text-sm"
            >
              <Plus size={14} />
              <ChevronDown size={12} />
            </button>
            
            {/* Terminal type dropdown */}
            {showNewTerminalMenu && (
              <div className="absolute top-full left-0 mt-1 bg-[#252526] border border-[#3e3e42] rounded shadow-lg z-50">
                {terminalTypes.filter(t => t.available).map(({ type, label, icon }) => (
                  <button
                    key={type}
                    onClick={() => createTerminalTab(type as any)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-[#2d2d30] hover:text-white w-full text-left"
                  >
                    <span className="font-mono">{icon}</span>
                    <span>{label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Close all button */}
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 hover:bg-[#333333] rounded ml-2"
            title="Close terminal"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Terminal content area */}
      {activeTab && (
        <div className="flex-1 flex flex-col overflow-hidden">
          <div 
            ref={terminalRef}
            className="flex-1 overflow-y-auto p-4 font-mono text-sm text-gray-300"
          >
            {activeTab.content.map((line, index) => (
              <div key={index} className="whitespace-pre-wrap">
                {line}
              </div>
            ))}
          </div>
          
          {/* Input area */}
          <div className="border-t border-[#3e3e42] p-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full bg-transparent outline-none font-mono text-sm text-gray-300"
              placeholder="Type command and press Enter..."
              autoFocus
            />
          </div>
        </div>
      )}
      
      {/* Empty state */}
      {tabs.length === 0 && (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <TerminalIcon size={48} className="mx-auto mb-2 opacity-50" />
            <p>No terminal sessions</p>
            <button
              onClick={() => createTerminalTab('claude-code')}
              className="mt-2 text-[#007acc] hover:text-[#1a8cff]"
            >
              Create new terminal
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
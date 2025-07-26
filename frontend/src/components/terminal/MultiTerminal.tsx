'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Terminal as XTermTerminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import { WebLinksAddon } from '@xterm/addon-web-links'
import { SearchAddon } from '@xterm/addon-search'
import '@xterm/xterm/css/xterm.css'
import { X, Plus, ChevronDown } from 'lucide-react'
import { Terminal as TerminalIcon } from 'lucide-react'

interface TerminalTab {
  id: string
  title: string
  terminal: XTermTerminal | null
  fitAddon: FitAddon | null
  socket: WebSocket | null
  type: 'bash' | 'powershell' | 'cmd' | 'claude-code'
}

interface MultiTerminalProps {
  onClose?: () => void
  initialCommand?: string
  height?: string
}

export const MultiTerminal: React.FC<MultiTerminalProps> = ({ 
  onClose, 
  initialCommand,
  height = 'h-96'
}) => {
  const [tabs, setTabs] = useState<TerminalTab[]>([])
  const [activeTabId, setActiveTabId] = useState<string>('')
  const [showNewTerminalMenu, setShowNewTerminalMenu] = useState(false)
  const terminalRefs = useRef<{ [key: string]: HTMLDivElement | null }>({})
  const terminalIdCounter = useRef(0)

  // Terminal types for different platforms
  const terminalTypes = [
    { type: 'bash', label: 'Bash', icon: '$', available: true },
    { type: 'powershell', label: 'PowerShell', icon: 'PS>', available: process.platform === 'win32' },
    { type: 'cmd', label: 'Command Prompt', icon: 'C:\\>', available: process.platform === 'win32' },
    { type: 'claude-code', label: 'Claude Code CLI', icon: '🤖', available: true }
  ]

  // Create a new terminal tab
  const createTerminalTab = (type: 'bash' | 'powershell' | 'cmd' | 'claude-code') => {
    const id = `terminal-${terminalIdCounter.current++}`
    const title = type === 'claude-code' ? 'Claude Code' : 
                  type === 'powershell' ? 'PowerShell' :
                  type === 'cmd' ? 'CMD' : 'Bash'
    
    const newTab: TerminalTab = {
      id,
      title,
      terminal: null,
      fitAddon: null,
      socket: null,
      type
    }

    setTabs(prev => [...prev, newTab])
    setActiveTabId(id)
    setShowNewTerminalMenu(false)

    // Initialize terminal after state update
    setTimeout(() => initializeTerminal(id, type), 100)
  }

  // Initialize terminal instance
  const initializeTerminal = (tabId: string, type: string) => {
    const terminalEl = terminalRefs.current[tabId]
    if (!terminalEl) return

    const terminal = new XTermTerminal({
      theme: {
        background: '#1e1e1e',
        foreground: '#cccccc',
        cursor: '#ffffff',
        black: '#000000',
        red: '#cd3131',
        green: '#0dbc79',
        yellow: '#e5e510',
        blue: '#2472c8',
        magenta: '#bc3fbc',
        cyan: '#11a8cd',
        white: '#e5e5e5',
        brightBlack: '#666666',
        brightRed: '#f14c4c',
        brightGreen: '#23d18b',
        brightYellow: '#f5f543',
        brightBlue: '#3b8eea',
        brightMagenta: '#d670d6',
        brightCyan: '#29b8db',
        brightWhite: '#e5e5e5'
      },
      fontSize: 14,
      fontFamily: 'Cascadia Code, Consolas, Monaco, monospace',
      cursorBlink: true,
      allowTransparency: true,
      windowsMode: process.platform === 'win32'
    })

    const fitAddon = new FitAddon()
    const webLinksAddon = new WebLinksAddon()
    const searchAddon = new SearchAddon()

    terminal.loadAddon(fitAddon)
    terminal.loadAddon(webLinksAddon)
    terminal.loadAddon(searchAddon)

    terminal.open(terminalEl)
    fitAddon.fit()

    // Update tab with terminal instance
    setTabs(prev => prev.map(tab => 
      tab.id === tabId 
        ? { ...tab, terminal, fitAddon }
        : tab
    ))

    // Connect to backend WebSocket
    connectToBackend(tabId, terminal, type)

    // Handle resize
    const resizeObserver = new ResizeObserver(() => {
      fitAddon.fit()
    })
    resizeObserver.observe(terminalEl)

    // Write welcome message for Claude Code
    if (type === 'claude-code') {
      terminal.writeln('🤖 Claude Code CLI Terminal')
      terminal.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
      terminal.writeln('')
      terminal.writeln('Available commands:')
      terminal.writeln('  claude-code login     - Authenticate with Claude AI')
      terminal.writeln('  claude-code status    - Check authentication status')
      terminal.writeln('  claude-code chat      - Start coding with Claude')
      terminal.writeln('  claude-code --help    - Show all commands')
      terminal.writeln('')
      terminal.write('$ ')
    }
  }

  // Connect to backend WebSocket
  const connectToBackend = (tabId: string, terminal: XTermTerminal, type: string) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/terminal`
    
    const socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      console.log(`Terminal ${tabId} connected`)
      
      // Send terminal type to backend
      socket.send(JSON.stringify({ 
        type: 'init', 
        shell: type,
        cols: terminal.cols,
        rows: terminal.rows
      }))

      // Send initial command if provided
      if (initialCommand && type === 'claude-code') {
        setTimeout(() => {
          socket.send(JSON.stringify({ 
            type: 'input', 
            data: initialCommand + '\r' 
          }))
        }, 500)
      }
    }

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data)
      if (message.type === 'output') {
        terminal.write(message.data)
      }
    }

    socket.onclose = () => {
      terminal.writeln('\r\n[Terminal disconnected]')
    }

    socket.onerror = (error) => {
      terminal.writeln(`\r\n[Terminal error: ${error}]`)
    }

    // Handle terminal input
    terminal.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'input', data }))
      }
    })

    // Handle terminal resize
    terminal.onResize(({ cols, rows }) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'resize', cols, rows }))
      }
    })

    // Update tab with socket
    setTabs(prev => prev.map(tab => 
      tab.id === tabId 
        ? { ...tab, socket }
        : tab
    ))
  }

  // Close terminal tab
  const closeTab = (tabId: string) => {
    const tab = tabs.find(t => t.id === tabId)
    if (tab) {
      // Cleanup terminal
      if (tab.terminal) {
        tab.terminal.dispose()
      }
      if (tab.socket) {
        tab.socket.close()
      }
    }

    setTabs(prev => prev.filter(t => t.id !== tabId))
    
    // Switch to another tab if closing active tab
    if (activeTabId === tabId && tabs.length > 1) {
      const remainingTabs = tabs.filter(t => t.id !== tabId)
      if (remainingTabs.length > 0) {
        setActiveTabId(remainingTabs[0].id)
      }
    }

    // Close entire terminal if no tabs left
    if (tabs.length === 1 && onClose) {
      onClose()
    }
  }

  // Create initial terminal on mount
  useEffect(() => {
    if (tabs.length === 0) {
      createTerminalTab('bash')
    }
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      tabs.forEach(tab => {
        if (tab.terminal) tab.terminal.dispose()
        if (tab.socket) tab.socket.close()
      })
    }
  }, [])

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
      <div className="flex-1 relative">
        {tabs.map(tab => (
          <div
            key={tab.id}
            ref={el => terminalRefs.current[tab.id] = el}
            className={`absolute inset-0 ${
              activeTabId === tab.id ? 'block' : 'hidden'
            }`}
          />
        ))}
        
        {/* Empty state */}
        {tabs.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <TerminalIcon size={48} className="mx-auto mb-2 opacity-50" />
              <p>No terminal sessions</p>
              <button
                onClick={() => createTerminalTab('bash')}
                className="mt-2 text-[#007acc] hover:text-[#1a8cff]"
              >
                Create new terminal
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
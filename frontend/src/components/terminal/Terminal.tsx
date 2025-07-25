'use client'

import { useEffect, useRef, useState } from 'react'
import { Terminal as XTerm } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import { WebLinksAddon } from 'xterm-addon-web-links'
import { VscClose, VscChevronUp, VscTerminal, VscSplitHorizontal } from '../icons'
import 'xterm/css/xterm.css'

interface TerminalProps {
  onClose: () => void
}

export function Terminal({ onClose }: TerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null)
  const xtermRef = useRef<XTerm | null>(null)
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (!terminalRef.current) return

    // DOM이 준비될 때까지 대기
    const initTimer = setTimeout(() => {
      if (!terminalRef.current) return

      try {
        // Initialize terminal
        const term = new XTerm({
      theme: {
        background: '#1e1e1e',
        foreground: '#cccccc',
        cursor: '#ffffff',
        selection: '#264f78',
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
      fontFamily: 'Consolas, Monaco, "Courier New", monospace',
      fontSize: 13,
      lineHeight: 1.2,
      cursorBlink: true,
      cursorStyle: 'block',
      scrollback: 1000,
    })

    // Add addons
    const fitAddon = new FitAddon()
    const webLinksAddon = new WebLinksAddon()
    
    term.loadAddon(fitAddon)
    term.loadAddon(webLinksAddon)
    
    // Open terminal
    term.open(terminalRef.current)
    fitAddon.fit()
    
    // Initial message
    term.writeln('SpinalSurgery Research Platform Terminal v1.0.0')
    term.writeln('Type "help" for available commands.')
    term.writeln('')
    term.write('$ ')
    
    // Handle input
    let currentLine = ''
    term.onData((data) => {
      switch (data) {
        case '\r': // Enter
          term.writeln('')
          handleCommand(currentLine, term)
          currentLine = ''
          term.write('$ ')
          break
        case '\u007F': // Backspace
          if (currentLine.length > 0) {
            currentLine = currentLine.slice(0, -1)
            term.write('\b \b')
          }
          break
        default:
          currentLine += data
          term.write(data)
      }
    })
    
    // Handle resize
    const handleResize = () => {
      if (fitAddon) {
        fitAddon.fit()
      }
    }
    window.addEventListener('resize', handleResize)
    
    xtermRef.current = term
    
    // Store handleResize in a ref so it can be removed in cleanup
    (terminalRef.current as any)._handleResize = handleResize
    
    setIsReady(true)
      } catch (error) {
        console.error('Failed to initialize terminal:', error)
      }
    }, 100) // 100ms 지연
    
    return () => {
      clearTimeout(initTimer)
      if (terminalRef.current && (terminalRef.current as any)._handleResize) {
        window.removeEventListener('resize', (terminalRef.current as any)._handleResize)
      }
      if (xtermRef.current) {
        xtermRef.current.dispose()
      }
    }
  }, [])

  const handleCommand = (command: string, term: XTerm) => {
    const cmd = command.trim().toLowerCase()
    
    switch (cmd) {
      case 'help':
        term.writeln('Available commands:')
        term.writeln('  help     - Show this help message')
        term.writeln('  clear    - Clear terminal')
        term.writeln('  status   - Show system status')
        term.writeln('  analyze  - Run data analysis')
        term.writeln('  papers   - List recent papers')
        term.writeln('  stats    - Show research statistics')
        break
        
      case 'clear':
        term.clear()
        break
        
      case 'status':
        term.writeln('System Status:')
        term.writeln('  Database: Connected ✓')
        term.writeln('  AI Service: Ready ✓')
        term.writeln('  Storage: 45.2 GB used / 100 GB total')
        break
        
      case 'analyze':
        term.writeln('Starting data analysis...')
        setTimeout(() => {
          term.writeln('Analysis complete. Results saved to /results/analysis_2025_07_24.csv')
        }, 1000)
        break
        
      case 'papers':
        term.writeln('Recent papers:')
        term.writeln('  1. "Spinal Fusion Outcomes" - Published 2025-07-20')
        term.writeln('  2. "CD Instrument Analysis" - Draft')
        term.writeln('  3. "VAS Score Study" - In Review')
        break
        
      case 'stats':
        term.writeln('Research Statistics:')
        term.writeln('  Total Projects: 15')
        term.writeln('  Published Papers: 8')
        term.writeln('  Patients Enrolled: 234')
        term.writeln('  Active Collaborators: 12')
        break
        
      default:
        if (cmd) {
          term.writeln(`Command not found: ${command}`)
        }
    }
  }

  return (
    <div className="flex flex-col h-full bg-vscode-bg">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-3 py-1 bg-vscode-bg-light border-b border-vscode-border">
        <div className="flex items-center gap-2">
          <VscTerminal size={14} className="text-vscode-text-dim" />
          <span className="text-xs">Terminal</span>
        </div>
        <div className="flex items-center gap-1">
          <button className="p-1 hover:bg-vscode-hover rounded" title="Split Terminal">
            <VscSplitHorizontal size={14} />
          </button>
          <button className="p-1 hover:bg-vscode-hover rounded" title="Maximize">
            <VscChevronUp size={14} />
          </button>
          <button onClick={onClose} className="p-1 hover:bg-vscode-hover rounded" title="Close">
            <VscClose size={14} />
          </button>
        </div>
      </div>
      
      {/* Terminal Content */}
      <div ref={terminalRef} className="flex-1 p-2" style={{ opacity: isReady ? 1 : 0 }} />
    </div>
  )
}
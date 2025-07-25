'use client'

import {
  VscAccount,
  VscSettingsGear,
  VscBook,
  VscBeaker,
  VscNotebook,
  VscOutput,
  VscRobot,
  VscSourceControl,
  FaPrint
} from '../icons'

interface ActivityBarProps {
  activeView: string
  onViewChange: (view: any) => void
  onToggleSidebar: () => void
}

export function ActivityBar({ activeView, onViewChange, onToggleSidebar }: ActivityBarProps) {
  const activities = [
    { id: 'research', icon: VscBeaker, tooltip: '연구 프로젝트' },
    { id: 'papers', icon: VscBook, tooltip: '논문 관리' },
    { id: 'editor', icon: VscNotebook, tooltip: '논문 편집기' },
    { id: 'sources', icon: VscSourceControl, tooltip: '논문 소스 관리' },
    { id: 'ai', icon: VscRobot, tooltip: 'AI 어시스턴트' },
    { id: 'print', icon: FaPrint, tooltip: '인쇄' },
    { id: 'terminal', icon: VscOutput, tooltip: '터미널' },
  ]

  return (
    <div className="w-12 bg-vscode-activity flex flex-col items-center py-2 select-none">
      {/* Top Activities */}
      <div className="flex-1">
        {activities.map(activity => (
          <button
            key={activity.id}
            onClick={() => {
              if (activity.id === 'print') {
                window.print()
              } else if (activity.id === 'terminal') {
                onToggleSidebar()
              } else {
                onViewChange(activity.id)
              }
            }}
            className={`w-12 h-12 flex items-center justify-center hover:bg-vscode-hover ${
              activeView === activity.id ? 'border-l-2 border-vscode-blue text-vscode-text-bright' : 'text-vscode-text-dim'
            }`}
            title={activity.tooltip}
          >
            <activity.icon size={24} />
          </button>
        ))}
      </div>
      
      {/* Bottom Activities */}
      <div>
        <button className="w-12 h-12 flex items-center justify-center hover:bg-vscode-hover text-vscode-text-dim">
          <VscAccount size={24} />
        </button>
        <button className="w-12 h-12 flex items-center justify-center hover:bg-vscode-hover text-vscode-text-dim">
          <VscSettingsGear size={24} />
        </button>
      </div>
    </div>
  )
}
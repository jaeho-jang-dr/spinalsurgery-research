'use client'

import { VscRemote, VscSourceControl, VscError, VscWarning, VscBell } from '../icons'

export function StatusBar() {
  return (
    <div className="h-6 bg-vscode-blue flex items-center justify-between px-2 text-white text-xs select-none">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1">
          <VscSourceControl size={14} />
          <span>master</span>
        </div>
        <div className="flex items-center gap-1">
          <VscError size={14} />
          <span>0</span>
          <VscWarning size={14} />
          <span>0</span>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <span>PostgreSQL: Connected</span>
        <span>AI: Ready</span>
        <div className="flex items-center gap-1">
          <VscBell size={14} />
        </div>
        <div className="flex items-center gap-1">
          <VscRemote size={14} />
          <span>SpinalSurgery Research</span>
        </div>
      </div>
    </div>
  )
}
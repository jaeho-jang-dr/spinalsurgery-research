'use client'

import { VscChromeMinimize, VscChromeMaximize, VscChromeClose } from '../icons'

export function TitleBar() {
  return (
    <div className="bg-vscode-titlebar">
      {/* 타이틀바 */}
      <div className="h-8 flex items-center justify-between select-none">
        <div className="flex items-center px-3">
          <span className="text-xs">SpinalSurgery Research Platform</span>
        </div>
        
        {/* Window Controls */}
        <div className="flex">
          <button className="w-12 h-8 hover:bg-vscode-hover flex items-center justify-center">
            <VscChromeMinimize className="text-vscode-text" />
          </button>
          <button className="w-12 h-8 hover:bg-vscode-hover flex items-center justify-center">
            <VscChromeMaximize className="text-vscode-text" />
          </button>
          <button className="w-12 h-8 hover:bg-red-600 flex items-center justify-center">
            <VscChromeClose className="text-vscode-text" />
          </button>
        </div>
      </div>
    </div>
  )
}
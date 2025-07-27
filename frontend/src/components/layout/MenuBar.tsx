'use client'

import { useState, useRef, useEffect } from 'react'
import { VscChevronRight } from '../icons'

type MenuItemBase = {
  label: string
  accelerator?: string
  action?: () => void
  submenu?: MenuItemWithSeparator[]
  checked?: boolean
  enabled?: boolean
}

type MenuSeparator = {
  separator: true
}

type MenuItemWithSeparator = MenuItemBase | MenuSeparator

interface MenuItem extends MenuItemBase {}

interface MenuBarProps {
  onMenuAction?: (action: string) => void
}

export function MenuBar({ onMenuAction }: MenuBarProps) {
  const [activeMenu, setActiveMenu] = useState<string | null>(null)
  const [openSubmenu, setOpenSubmenu] = useState<string | null>(null)
  const menuBarRef = useRef<HTMLDivElement>(null)

  const menus: Record<string, MenuItemWithSeparator[]> = {
    File: [
      { label: 'New Text File', accelerator: 'Ctrl+N', action: () => onMenuAction?.('file.new') },
      { label: 'New File...', accelerator: 'Ctrl+Alt+Windows+N', action: () => onMenuAction?.('file.newFile') },
      { label: 'New Window', accelerator: 'Ctrl+Shift+N', action: () => onMenuAction?.('file.newWindow') },
      { label: 'New Window with Profile', submenu: [
        { label: 'Default Profile', action: () => onMenuAction?.('file.newWindowProfile.default') }
      ]},
      { separator: true },
      { label: 'Open File...', accelerator: 'Ctrl+O', action: () => onMenuAction?.('file.open') },
      { label: 'Open Folder...', accelerator: 'Ctrl+K Ctrl+O', action: () => onMenuAction?.('file.openFolder') },
      { label: 'Open Workspace from File...', action: () => onMenuAction?.('file.openWorkspace') },
      { label: 'Open Recent', submenu: [
        { label: 'SpinalSurgery Research', action: () => onMenuAction?.('file.openRecent.0') },
        { separator: true },
        { label: 'More...', action: () => onMenuAction?.('file.openRecent.more') }
      ]},
      { separator: true },
      { label: 'Add Folder to Workspace...', action: () => onMenuAction?.('file.addFolder') },
      { label: 'Save Workspace As...', action: () => onMenuAction?.('file.saveWorkspace') },
      { label: 'Duplicate Workspace', action: () => onMenuAction?.('file.duplicateWorkspace') },
      { separator: true },
      { label: 'Save', accelerator: 'Ctrl+S', action: () => onMenuAction?.('file.save') },
      { label: 'Save As...', accelerator: 'Ctrl+Shift+S', action: () => onMenuAction?.('file.saveAs') },
      { label: 'Save All', accelerator: 'Ctrl+K S', action: () => onMenuAction?.('file.saveAll') },
      { separator: true },
      { label: 'Share', submenu: [
        { label: 'Export to GitHub Gist', action: () => onMenuAction?.('file.share.gist') }
      ]},
      { separator: true },
      { label: 'Auto Save', checked: false, action: () => onMenuAction?.('file.autoSave') },
      { label: 'Preferences', submenu: [
        { label: 'Settings', accelerator: 'Ctrl+,', action: () => onMenuAction?.('file.preferences.settings') },
        { label: 'Extensions', accelerator: 'Ctrl+Shift+X', action: () => onMenuAction?.('file.preferences.extensions') },
        { label: 'Keyboard Shortcuts', accelerator: 'Ctrl+K Ctrl+S', action: () => onMenuAction?.('file.preferences.keyboardShortcuts') },
        { separator: true },
        { label: 'Color Theme', accelerator: 'Ctrl+K Ctrl+T', action: () => onMenuAction?.('file.preferences.colorTheme') },
        { label: 'File Icon Theme', action: () => onMenuAction?.('file.preferences.fileIconTheme') },
        { label: 'Product Icon Theme', action: () => onMenuAction?.('file.preferences.productIconTheme') }
      ]},
      { separator: true },
      { label: 'Revert File', action: () => onMenuAction?.('file.revert') },
      { label: 'Close Editor', accelerator: 'Ctrl+F4', action: () => onMenuAction?.('file.closeEditor') },
      { label: 'Close Folder', accelerator: 'Ctrl+K F', action: () => onMenuAction?.('file.closeFolder') },
      { label: 'Close Remote Connection', action: () => onMenuAction?.('file.closeRemote') },
      { label: 'Close Window', accelerator: 'Alt+F4', action: () => onMenuAction?.('file.closeWindow') },
      { separator: true },
      { label: 'Exit', action: () => onMenuAction?.('file.exit') }
    ],
    Edit: [
      { label: 'Undo', accelerator: 'Ctrl+Z', action: () => onMenuAction?.('edit.undo') },
      { label: 'Redo', accelerator: 'Ctrl+Y', action: () => onMenuAction?.('edit.redo') },
      { separator: true },
      { label: 'Cut', accelerator: 'Ctrl+X', action: () => onMenuAction?.('edit.cut') },
      { label: 'Copy', accelerator: 'Ctrl+C', action: () => onMenuAction?.('edit.copy') },
      { label: 'Paste', accelerator: 'Ctrl+V', action: () => onMenuAction?.('edit.paste') },
      { separator: true },
      { label: 'Find', accelerator: 'Ctrl+F', action: () => onMenuAction?.('edit.find') },
      { label: 'Replace', accelerator: 'Ctrl+H', action: () => onMenuAction?.('edit.replace') },
      { separator: true },
      { label: 'Find in Files', accelerator: 'Ctrl+Shift+F', action: () => onMenuAction?.('edit.findInFiles') },
      { label: 'Replace in Files', accelerator: 'Ctrl+Shift+H', action: () => onMenuAction?.('edit.replaceInFiles') },
      { separator: true },
      { label: 'Toggle Line Comment', accelerator: 'Ctrl+/', action: () => onMenuAction?.('edit.toggleLineComment') },
      { label: 'Toggle Block Comment', accelerator: 'Shift+Alt+A', action: () => onMenuAction?.('edit.toggleBlockComment') },
      { label: 'Emmet: Expand Abbreviation', accelerator: 'Tab', action: () => onMenuAction?.('edit.emmetExpand') }
    ],
    Selection: [
      { label: 'Select All', accelerator: 'Ctrl+A', action: () => onMenuAction?.('selection.selectAll') },
      { label: 'Expand Selection', accelerator: 'Shift+Alt+RightArrow', action: () => onMenuAction?.('selection.expand') },
      { label: 'Shrink Selection', accelerator: 'Shift+Alt+LeftArrow', action: () => onMenuAction?.('selection.shrink') },
      { separator: true },
      { label: 'Copy Line Up', accelerator: 'Shift+Alt+UpArrow', action: () => onMenuAction?.('selection.copyLineUp') },
      { label: 'Copy Line Down', accelerator: 'Shift+Alt+DownArrow', action: () => onMenuAction?.('selection.copyLineDown') },
      { label: 'Move Line Up', accelerator: 'Alt+UpArrow', action: () => onMenuAction?.('selection.moveLineUp') },
      { label: 'Move Line Down', accelerator: 'Alt+DownArrow', action: () => onMenuAction?.('selection.moveLineDown') },
      { label: 'Duplicate Selection', action: () => onMenuAction?.('selection.duplicate') },
      { separator: true },
      { label: 'Add Cursor Above', accelerator: 'Ctrl+Alt+UpArrow', action: () => onMenuAction?.('selection.addCursorAbove') },
      { label: 'Add Cursor Below', accelerator: 'Ctrl+Alt+DownArrow', action: () => onMenuAction?.('selection.addCursorBelow') },
      { label: 'Add Cursors to Line Ends', accelerator: 'Shift+Alt+I', action: () => onMenuAction?.('selection.addCursorsToLineEnds') },
      { label: 'Add Next Occurrence', accelerator: 'Ctrl+D', action: () => onMenuAction?.('selection.addNextOccurrence') },
      { label: 'Add Previous Occurrence', action: () => onMenuAction?.('selection.addPreviousOccurrence') },
      { label: 'Select All Occurrences', accelerator: 'Ctrl+Shift+L', action: () => onMenuAction?.('selection.selectAllOccurrences') },
      { separator: true },
      { label: 'Switch to Ctrl+Click for Multi-Cursor', action: () => onMenuAction?.('selection.switchMultiCursor') },
      { label: 'Column Selection Mode', action: () => onMenuAction?.('selection.columnMode') }
    ],
    View: [
      { label: 'Command Palette...', accelerator: 'Ctrl+Shift+P', action: () => onMenuAction?.('view.commandPalette') },
      { label: 'Open View...', action: () => onMenuAction?.('view.openView') },
      { separator: true },
      { label: 'Appearance', submenu: [
        { label: 'Full Screen', accelerator: 'F11', action: () => onMenuAction?.('view.fullScreen') },
        { label: 'Zen Mode', accelerator: 'Ctrl+K Z', action: () => onMenuAction?.('view.zenMode') },
        { separator: true },
        { label: 'Centered Layout', action: () => onMenuAction?.('view.centeredLayout') },
        { separator: true },
        { label: 'Menu Bar', checked: true, action: () => onMenuAction?.('view.menuBar') },
        { label: 'Primary Side Bar', checked: true, action: () => onMenuAction?.('view.primarySideBar') },
        { label: 'Secondary Side Bar', checked: false, action: () => onMenuAction?.('view.secondarySideBar') },
        { label: 'Status Bar', checked: true, action: () => onMenuAction?.('view.statusBar') },
        { label: 'Activity Bar', checked: true, action: () => onMenuAction?.('view.activityBar') },
        { label: 'Panel', checked: true, action: () => onMenuAction?.('view.panel') },
        { separator: true },
        { label: 'Breadcrumbs', checked: false, action: () => onMenuAction?.('view.breadcrumbs') },
        { label: 'Minimap', checked: true, action: () => onMenuAction?.('view.minimap') },
        { label: 'Render Whitespace', checked: false, action: () => onMenuAction?.('view.renderWhitespace') },
        { label: 'Render Control Characters', checked: false, action: () => onMenuAction?.('view.renderControlCharacters') }
      ]},
      { label: 'Editor Layout', submenu: [
        { label: 'Split Up', action: () => onMenuAction?.('view.splitUp') },
        { label: 'Split Down', action: () => onMenuAction?.('view.splitDown') },
        { label: 'Split Left', action: () => onMenuAction?.('view.splitLeft') },
        { label: 'Split Right', action: () => onMenuAction?.('view.splitRight') },
        { separator: true },
        { label: 'Single', action: () => onMenuAction?.('view.layoutSingle') },
        { label: 'Two Columns', action: () => onMenuAction?.('view.layoutTwoColumns') },
        { label: 'Three Columns', action: () => onMenuAction?.('view.layoutThreeColumns') },
        { label: 'Two Rows', action: () => onMenuAction?.('view.layoutTwoRows') },
        { label: 'Three Rows', action: () => onMenuAction?.('view.layoutThreeRows') },
        { label: 'Grid (2x2)', action: () => onMenuAction?.('view.layoutGrid') }
      ]},
      { separator: true },
      { label: 'Explorer', accelerator: 'Ctrl+Shift+E', action: () => onMenuAction?.('view.explorer') },
      { label: 'Search', accelerator: 'Ctrl+Shift+F', action: () => onMenuAction?.('view.search') },
      { label: 'Source Control', accelerator: 'Ctrl+Shift+G', action: () => onMenuAction?.('view.sourceControl') },
      { label: 'Run', accelerator: 'Ctrl+Shift+D', action: () => onMenuAction?.('view.run') },
      { label: 'Extensions', accelerator: 'Ctrl+Shift+X', action: () => onMenuAction?.('view.extensions') },
      { separator: true },
      { label: 'Problems', accelerator: 'Ctrl+Shift+M', action: () => onMenuAction?.('view.problems') },
      { label: 'Output', accelerator: 'Ctrl+Shift+U', action: () => onMenuAction?.('view.output') },
      { label: 'Debug Console', accelerator: 'Ctrl+Shift+Y', action: () => onMenuAction?.('view.debugConsole') },
      { label: 'Terminal', accelerator: 'Ctrl+`', action: () => onMenuAction?.('view.terminal') },
      { separator: true },
      { label: 'Word Wrap', accelerator: 'Alt+Z', action: () => onMenuAction?.('view.wordWrap') }
    ],
    Go: [
      { label: 'Back', accelerator: 'Alt+LeftArrow', action: () => onMenuAction?.('go.back') },
      { label: 'Forward', accelerator: 'Alt+RightArrow', action: () => onMenuAction?.('go.forward') },
      { label: 'Last Edit Location', accelerator: 'Ctrl+K Ctrl+Q', action: () => onMenuAction?.('go.lastEditLocation') },
      { separator: true },
      { label: 'Switch Editor', accelerator: 'Ctrl+Tab', action: () => onMenuAction?.('go.switchEditor') },
      { label: 'Switch Group', action: () => onMenuAction?.('go.switchGroup') },
      { separator: true },
      { label: 'Go to File...', accelerator: 'Ctrl+P', action: () => onMenuAction?.('go.toFile') },
      { label: 'Go to Symbol in Workspace...', accelerator: 'Ctrl+T', action: () => onMenuAction?.('go.toSymbolInWorkspace') },
      { separator: true },
      { label: 'Go to Symbol in Editor...', accelerator: 'Ctrl+Shift+O', action: () => onMenuAction?.('go.toSymbol') },
      { label: 'Go to Definition', accelerator: 'F12', action: () => onMenuAction?.('go.toDefinition') },
      { label: 'Go to Declaration', action: () => onMenuAction?.('go.toDeclaration') },
      { label: 'Go to Type Definition', action: () => onMenuAction?.('go.toTypeDefinition') },
      { label: 'Go to Implementation', accelerator: 'Ctrl+F12', action: () => onMenuAction?.('go.toImplementation') },
      { label: 'Go to References', accelerator: 'Shift+F12', action: () => onMenuAction?.('go.toReferences') },
      { separator: true },
      { label: 'Go to Line/Column...', accelerator: 'Ctrl+G', action: () => onMenuAction?.('go.toLine') },
      { label: 'Go to Bracket', accelerator: 'Ctrl+Shift+\\', action: () => onMenuAction?.('go.toBracket') },
      { separator: true },
      { label: 'Next Problem', accelerator: 'F8', action: () => onMenuAction?.('go.nextProblem') },
      { label: 'Previous Problem', accelerator: 'Shift+F8', action: () => onMenuAction?.('go.previousProblem') },
      { separator: true },
      { label: 'Next Change', accelerator: 'Alt+F5', action: () => onMenuAction?.('go.nextChange') },
      { label: 'Previous Change', accelerator: 'Shift+Alt+F5', action: () => onMenuAction?.('go.previousChange') }
    ],
    Run: [
      { label: 'Start Debugging', accelerator: 'F5', action: () => onMenuAction?.('run.startDebugging') },
      { label: 'Run Without Debugging', accelerator: 'Ctrl+F5', action: () => onMenuAction?.('run.runWithoutDebugging') },
      { label: 'Stop Debugging', accelerator: 'Shift+F5', action: () => onMenuAction?.('run.stopDebugging') },
      { label: 'Restart Debugging', accelerator: 'Ctrl+Shift+F5', action: () => onMenuAction?.('run.restartDebugging') },
      { separator: true },
      { label: 'Open Configurations', action: () => onMenuAction?.('run.openConfigurations') },
      { label: 'Add Configuration...', action: () => onMenuAction?.('run.addConfiguration') },
      { separator: true },
      { label: 'Step Over', accelerator: 'F10', action: () => onMenuAction?.('run.stepOver') },
      { label: 'Step Into', accelerator: 'F11', action: () => onMenuAction?.('run.stepInto') },
      { label: 'Step Out', accelerator: 'Shift+F11', action: () => onMenuAction?.('run.stepOut') },
      { label: 'Continue', accelerator: 'F5', action: () => onMenuAction?.('run.continue') },
      { separator: true },
      { label: 'Toggle Breakpoint', accelerator: 'F9', action: () => onMenuAction?.('run.toggleBreakpoint') },
      { label: 'New Breakpoint', submenu: [
        { label: 'Conditional Breakpoint...', action: () => onMenuAction?.('run.conditionalBreakpoint') },
        { label: 'Inline Breakpoint', accelerator: 'Shift+F9', action: () => onMenuAction?.('run.inlineBreakpoint') },
        { label: 'Function Breakpoint...', action: () => onMenuAction?.('run.functionBreakpoint') },
        { label: 'Data Breakpoint...', action: () => onMenuAction?.('run.dataBreakpoint') }
      ]},
      { separator: true },
      { label: 'Enable All Breakpoints', action: () => onMenuAction?.('run.enableAllBreakpoints') },
      { label: 'Disable All Breakpoints', action: () => onMenuAction?.('run.disableAllBreakpoints') },
      { label: 'Remove All Breakpoints', action: () => onMenuAction?.('run.removeAllBreakpoints') },
      { separator: true },
      { label: 'Install Additional Debuggers...', action: () => onMenuAction?.('run.installDebuggers') }
    ],
    Terminal: [
      { label: 'New Terminal', accelerator: 'Ctrl+Shift+`', action: () => onMenuAction?.('terminal.new') },
      { label: 'Split Terminal', accelerator: 'Ctrl+Shift+5', action: () => onMenuAction?.('terminal.split') },
      { separator: true },
      { label: 'Run Task...', action: () => onMenuAction?.('terminal.runTask') },
      { label: 'Run Build Task...', accelerator: 'Ctrl+Shift+B', action: () => onMenuAction?.('terminal.runBuildTask') },
      { label: 'Run Active File', action: () => onMenuAction?.('terminal.runActiveFile') },
      { label: 'Run Selected Text', action: () => onMenuAction?.('terminal.runSelectedText') },
      { separator: true },
      { label: 'Show Running Tasks...', action: () => onMenuAction?.('terminal.showRunningTasks') },
      { label: 'Restart Running Task...', action: () => onMenuAction?.('terminal.restartTask') },
      { label: 'Terminate Task...', action: () => onMenuAction?.('terminal.terminateTask') },
      { separator: true },
      { label: 'Configure Tasks...', action: () => onMenuAction?.('terminal.configureTasks') },
      { label: 'Configure Default Build Task...', action: () => onMenuAction?.('terminal.configureDefaultBuildTask') }
    ],
    Help: [
      { label: 'Welcome', action: () => onMenuAction?.('help.welcome') },
      { label: 'Show All Commands', accelerator: 'Ctrl+Shift+P', action: () => onMenuAction?.('help.showCommands') },
      { label: 'Documentation', action: () => onMenuAction?.('help.documentation') },
      { label: 'Editor Playground', action: () => onMenuAction?.('help.editorPlayground') },
      { label: 'Release Notes', action: () => onMenuAction?.('help.releaseNotes') },
      { separator: true },
      { label: 'Keyboard Shortcuts Reference', accelerator: 'Ctrl+K Ctrl+R', action: () => onMenuAction?.('help.keyboardReference') },
      { label: 'Video Tutorials', action: () => onMenuAction?.('help.videoTutorials') },
      { label: 'Tips and Tricks', action: () => onMenuAction?.('help.tipsAndTricks') },
      { separator: true },
      { label: 'Join Us on Twitter', action: () => onMenuAction?.('help.twitter') },
      { label: 'Search Feature Requests', action: () => onMenuAction?.('help.featureRequests') },
      { label: 'Report Issue', action: () => onMenuAction?.('help.reportIssue') },
      { separator: true },
      { label: 'View License', action: () => onMenuAction?.('help.viewLicense') },
      { label: 'Privacy Statement', action: () => onMenuAction?.('help.privacyStatement') },
      { separator: true },
      { label: 'Toggle Developer Tools', accelerator: 'Ctrl+Shift+I', action: () => onMenuAction?.('help.toggleDevTools') },
      { label: 'Open Process Explorer', action: () => onMenuAction?.('help.openProcessExplorer') },
      { separator: true },
      { label: 'About', action: () => onMenuAction?.('help.about') }
    ]
  }

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuBarRef.current && !menuBarRef.current.contains(event.target as Node)) {
        setActiveMenu(null)
        setOpenSubmenu(null)
      }
    }

    if (activeMenu) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [activeMenu])

  const handleMenuClick = (menuName: string) => {
    setActiveMenu(activeMenu === menuName ? null : menuName)
    setOpenSubmenu(null)
  }

  const handleMenuItemClick = (item: MenuItem) => {
    if (item.action) {
      item.action()
      setActiveMenu(null)
      setOpenSubmenu(null)
    }
  }

  const renderMenuItem = (item: MenuItemWithSeparator, index: number, parentKey: string) => {
    if ('separator' in item && item.separator) {
      return <div key={`${parentKey}-separator-${index}`} className="menu-separator" />
    }

    // Type assertion since we know it's not a separator at this point
    const menuItem = item as MenuItemBase
    const hasSubmenu = menuItem.submenu && menuItem.submenu.length > 0
    const itemKey = `${parentKey}-${menuItem.label}`

    return (
      <div
        key={itemKey}
        className={`menu-item ${hasSubmenu ? 'has-submenu' : ''} ${menuItem.enabled === false ? 'disabled' : ''}`}
        onMouseEnter={() => hasSubmenu && setOpenSubmenu(itemKey)}
        onClick={() => !hasSubmenu && handleMenuItemClick(menuItem)}
      >
        <span className="menu-item-label">
          {menuItem.checked !== undefined && (
            <span className="menu-item-check">{menuItem.checked ? '✓' : ''}</span>
          )}
          {menuItem.label}
        </span>
        {menuItem.accelerator && (
          <span className="menu-item-accelerator">{menuItem.accelerator}</span>
        )}
        {hasSubmenu && <VscChevronRight className="menu-item-arrow" />}
        
        {hasSubmenu && openSubmenu === itemKey && (
          <div className="submenu">
            {menuItem.submenu!.map((subItem, subIndex) => 
              renderMenuItem(subItem, subIndex, itemKey)
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <div ref={menuBarRef} className="menu-bar">
      {Object.entries(menus).map(([menuName, menuItems]) => (
        <div key={menuName} className="menu">
          <button
            className={`menu-button ${activeMenu === menuName ? 'active' : ''}`}
            onClick={() => handleMenuClick(menuName)}
            onMouseEnter={() => activeMenu && setActiveMenu(menuName)}
          >
            {menuName}
          </button>
          
          {activeMenu === menuName && (
            <div className="menu-dropdown">
              {menuItems.map((item, index) => 
                renderMenuItem(item, index, menuName)
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
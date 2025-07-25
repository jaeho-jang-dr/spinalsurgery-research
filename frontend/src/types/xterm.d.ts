declare module 'xterm' {
  export interface ITerminalOptions {
    theme?: {
      background?: string
      foreground?: string
      cursor?: string
      selection?: string
      black?: string
      red?: string
      green?: string
      yellow?: string
      blue?: string
      magenta?: string
      cyan?: string
      white?: string
      brightBlack?: string
      brightRed?: string
      brightGreen?: string
      brightYellow?: string
      brightBlue?: string
      brightMagenta?: string
      brightCyan?: string
      brightWhite?: string
    }
    fontFamily?: string
    fontSize?: number
    lineHeight?: number
    cursorBlink?: boolean
    cursorStyle?: 'block' | 'underline' | 'bar'
    scrollback?: number
  }

  export interface ITerminalAddon {
    activate(terminal: Terminal): void
    dispose(): void
  }

  export interface IBuffer {
    cursorY: number
    cursorX: number
    viewportY: number
    baseY: number
    length: number
  }

  export interface IBufferNamespace {
    active: IBuffer
    normal: IBuffer
    alternate: IBuffer
  }

  export interface ITerminalDimensions {
    cols: number
    rows: number
  }

  export class Terminal {
    element: HTMLElement | undefined
    textarea: HTMLTextAreaElement | undefined
    buffer: IBufferNamespace
    cols: number
    rows: number
    dimensions?: ITerminalDimensions

    constructor(options?: ITerminalOptions)
    open(parent: HTMLElement): void
    writeln(data: string): void
    write(data: string): void
    clear(): void
    dispose(): void
    onData(handler: (data: string) => void): { dispose: () => void }
    onKey(handler: (event: { key: string; domEvent: KeyboardEvent }) => void): { dispose: () => void }
    loadAddon(addon: ITerminalAddon): void
    focus(): void
    blur(): void
    resize(cols: number, rows: number): void
    scrollToBottom(): void
    selectAll(): void
    hasSelection(): boolean
    getSelection(): string
    clearSelection(): void
  }
}

declare module 'xterm-addon-fit' {
  import { Terminal, ITerminalAddon } from 'xterm'

  export class FitAddon implements ITerminalAddon {
    constructor()
    activate(terminal: Terminal): void
    dispose(): void
    fit(): { cols: number; rows: number } | undefined
    proposeDimensions(): { cols: number; rows: number } | undefined
  }
}

declare module 'xterm-addon-web-links' {
  import { Terminal, ITerminalAddon } from 'xterm'

  export class WebLinksAddon implements ITerminalAddon {
    constructor(handler?: (event: MouseEvent, uri: string) => void, options?: object)
    activate(terminal: Terminal): void
    dispose(): void
  }
}

declare module 'xterm-addon-search' {
  import { Terminal, ITerminalAddon } from 'xterm'

  export class SearchAddon implements ITerminalAddon {
    constructor()
    activate(terminal: Terminal): void
    dispose(): void
    findNext(term: string, searchOptions?: { regex?: boolean; wholeWord?: boolean; caseSensitive?: boolean }): boolean
    findPrevious(term: string, searchOptions?: { regex?: boolean; wholeWord?: boolean; caseSensitive?: boolean }): boolean
  }
}
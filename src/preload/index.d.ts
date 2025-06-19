import { ElectronAPI } from '@electron-toolkit/preload'

// 定义窗口控制API接口
interface WindowControlAPI {
  minimize: () => void
  maximize: () => void
  close: () => void
  isMaximized: () => Promise<boolean>
  startDrag: () => void
}

// 定义API接口
interface API {
  window: WindowControlAPI
  openLogFolder: () => void
  selectDirectory: (options?: { title?: string; buttonLabel?: string }) => Promise<string | null>
}

declare global {
  interface Window {
    electron: ElectronAPI
    api: API
  }
}

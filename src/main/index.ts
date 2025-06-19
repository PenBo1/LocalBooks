import { app, shell, BrowserWindow, ipcMain, Tray, Menu, nativeImage } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/LocalBooks.png?asset'

let tray = null
let mainWindow = null

function createWindow(): void {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    frame: false, // 禁用原生标题栏
    icon, // 设置窗口图标
    minWidth: 800, // 设置最小宽度
    minHeight: 600, // 设置最小高度
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // 窗口控制处理程序
  ipcMain.on('window-minimize', (event) => {
    BrowserWindow.fromWebContents(event.sender)?.minimize()
  })

  ipcMain.on('window-maximize', (event) => {
    const browserWindow = BrowserWindow.fromWebContents(event.sender)
    if (browserWindow?.isMaximized()) {
      browserWindow.unmaximize()
    } else {
      browserWindow?.maximize()
    }
  })

  ipcMain.on('window-close', (event) => {
    const browserWindow = BrowserWindow.fromWebContents(event.sender)
    if (browserWindow) {
      // 如果设置了最小化到托盘，则隐藏窗口而不是关闭
      if (tray) {
        browserWindow.hide()
      } else {
        browserWindow.close()
      }
    }
  })

  // 获取窗口状态
  ipcMain.handle('window-is-maximized', (event) => {
    const browserWindow = BrowserWindow.fromWebContents(event.sender)
    return browserWindow?.isMaximized()
  })

  // 处理窗口拖动
  ipcMain.on('window-drag', () => {
    // Electron已经提供了-webkit-app-region: drag CSS属性来实现拖动
    // 这个事件处理程序仅用于保持API一致性
  })
  
  // 打开日志文件夹
  ipcMain.on('open:logFolder', () => {
    const logPath = join(app.getPath('userData'), 'logs')
    shell.openPath(logPath)
  })
  
  // 处理选择目录的请求
  ipcMain.handle('dialog:selectDirectory', async (_, options) => {
    const { dialog } = require('electron')
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory', 'createDirectory'],
      title: options?.title || '选择目录',
      buttonLabel: options?.buttonLabel || '选择',
      ...options
    })
    if (canceled) {
      return null
    } else {
      return filePaths[0]
    }
  })

  createWindow()
  createTray()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// 创建系统托盘
function createTray(): void {
  // 创建托盘图标
  const trayIcon = nativeImage.createFromPath(join(__dirname, '../../resources/LocalBooks.png'))
  tray = new Tray(trayIcon.resize({ width: 16, height: 16 }))
  
  // 设置托盘菜单
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示主窗口',
      click: () => {
        if (mainWindow) {
          mainWindow.show()
          mainWindow.focus()
        }
      }
    },
    {
      label: '退出',
      click: () => {
        app.quit()
      }
    }
  ])
  
  tray.setToolTip('LocalBooks - 本地小说阅读器')
  tray.setContextMenu(contextMenu)
  
  // 点击托盘图标显示主窗口
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.focus()
      } else {
        mainWindow.show()
      }
    }
  })
}

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// 在应用退出前销毁托盘图标
app.on('before-quit', () => {
  if (tray) {
    tray.destroy()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.

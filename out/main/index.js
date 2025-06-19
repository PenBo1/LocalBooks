"use strict";
const electron = require("electron");
const path = require("path");
const utils = require("@electron-toolkit/utils");
const icon = path.join(__dirname, "../../resources/LocalBooks.png");
let tray = null;
let mainWindow = null;
function createWindow() {
  mainWindow = new electron.BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    frame: false,
    // 禁用原生标题栏
    icon,
    // 设置窗口图标
    minWidth: 800,
    // 设置最小宽度
    minHeight: 600,
    // 设置最小高度
    webPreferences: {
      preload: path.join(__dirname, "../preload/index.js"),
      sandbox: false
    }
  });
  mainWindow.on("ready-to-show", () => {
    mainWindow.show();
  });
  mainWindow.webContents.setWindowOpenHandler((details) => {
    electron.shell.openExternal(details.url);
    return { action: "deny" };
  });
  if (utils.is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    mainWindow.loadURL(process.env["ELECTRON_RENDERER_URL"]);
  } else {
    mainWindow.loadFile(path.join(__dirname, "../renderer/index.html"));
  }
}
electron.app.whenReady().then(() => {
  utils.electronApp.setAppUserModelId("com.electron");
  electron.app.on("browser-window-created", (_, window) => {
    utils.optimizer.watchWindowShortcuts(window);
  });
  electron.ipcMain.on("window-minimize", (event) => {
    electron.BrowserWindow.fromWebContents(event.sender)?.minimize();
  });
  electron.ipcMain.on("window-maximize", (event) => {
    const browserWindow = electron.BrowserWindow.fromWebContents(event.sender);
    if (browserWindow?.isMaximized()) {
      browserWindow.unmaximize();
    } else {
      browserWindow?.maximize();
    }
  });
  electron.ipcMain.on("window-close", (event) => {
    const browserWindow = electron.BrowserWindow.fromWebContents(event.sender);
    if (browserWindow) {
      if (tray) {
        browserWindow.hide();
      } else {
        browserWindow.close();
      }
    }
  });
  electron.ipcMain.handle("window-is-maximized", (event) => {
    const browserWindow = electron.BrowserWindow.fromWebContents(event.sender);
    return browserWindow?.isMaximized();
  });
  electron.ipcMain.on("window-drag", () => {
  });
  electron.ipcMain.on("open:logFolder", () => {
    const logPath = path.join(electron.app.getPath("userData"), "logs");
    electron.shell.openPath(logPath);
  });
  electron.ipcMain.handle("dialog:selectDirectory", async (_, options) => {
    const { dialog } = require("electron");
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
      properties: ["openDirectory", "createDirectory"],
      title: options?.title || "选择目录",
      buttonLabel: options?.buttonLabel || "选择",
      ...options
    });
    if (canceled) {
      return null;
    } else {
      return filePaths[0];
    }
  });
  createWindow();
  createTray();
  electron.app.on("activate", function() {
    if (electron.BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});
function createTray() {
  const trayIcon = electron.nativeImage.createFromPath(path.join(__dirname, "../../resources/LocalBooks.png"));
  tray = new electron.Tray(trayIcon.resize({ width: 16, height: 16 }));
  const contextMenu = electron.Menu.buildFromTemplate([
    {
      label: "显示主窗口",
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    {
      label: "退出",
      click: () => {
        electron.app.quit();
      }
    }
  ]);
  tray.setToolTip("LocalBooks - 本地小说阅读器");
  tray.setContextMenu(contextMenu);
  tray.on("click", () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.focus();
      } else {
        mainWindow.show();
      }
    }
  });
}
electron.app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    electron.app.quit();
  }
});
electron.app.on("before-quit", () => {
  if (tray) {
    tray.destroy();
  }
});

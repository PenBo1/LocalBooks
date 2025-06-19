"use strict";
const electron = require("electron");
const preload = require("@electron-toolkit/preload");
const api = {
  // 窗口控制
  window: {
    minimize: () => electron.ipcRenderer.send("window-minimize"),
    maximize: () => electron.ipcRenderer.send("window-maximize"),
    close: () => electron.ipcRenderer.send("window-close"),
    isMaximized: () => electron.ipcRenderer.invoke("window-is-maximized"),
    startDrag: () => electron.ipcRenderer.send("window-drag")
  },
  // 打开日志文件夹
  openLogFolder: () => electron.ipcRenderer.send("open:logFolder"),
  // 选择目录
  selectDirectory: (options) => electron.ipcRenderer.invoke("dialog:selectDirectory", options)
};
if (process.contextIsolated) {
  try {
    electron.contextBridge.exposeInMainWorld("electron", preload.electronAPI);
    electron.contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  window.electron = preload.electronAPI;
  window.api = api;
}

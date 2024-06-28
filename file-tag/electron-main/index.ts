import { app, BrowserWindow, Menu } from 'electron'
import path from 'path'
import { exec } from 'child_process'
const net = require('net')
import * as url from 'url'

let serverProcess: any

function startPythonServer() {
  return new Promise((resolve, reject) => {
    serverProcess = exec('main.exe', (err, stdout, stderr) => {
      if (err) {
        reject(err)
      }
    })

    // 等待服务器启动
    const checkServer = () => {
      const client = net.createConnection({ port: 25566 }, () => {
        client.end()
        resolve(() => {})
      })

      client.on('error', () => {
        setTimeout(checkServer, 1000)
      })
    }
    checkServer()
  })
}

const createWindow = async () => {
  Menu.setApplicationMenu(null)
  const win = new BrowserWindow({
    title: '文件标签管理器',
    width: 1280,
    height: 720,
    resizable: false,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
      preload: path.join(__dirname, './preload.js')
    }
  })
  if (process.env.NODE_ENV !== 'development') {
    await win.loadURL(
      url.format({
        pathname: path.join(__dirname, 'index.html'),
        protocol: 'file:',
        slashes: true
      })
    )
  } else {
    const url = 'http://localhost:5173'
    win.loadURL(url)
    win.webContents.openDevTools()
  }
}

app.on('window-all-closed', () => {
  if (serverProcess) {
    serverProcess.kill()
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

app.on('ready', async () => {
  try {
    await startPythonServer()
    serverProcess.on('close', () => {
      app.quit()
    })
    createWindow()
  } catch (err) {
    console.error('无法启动Python服务器', err)
    app.quit()
  }
})

app.on('quit', () => {})

const { app, BrowserWindow, globalShortcut } = require('electron');
const path = require('path');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 450,
    height: 650,
    x: 80,
    y: 80,
    alwaysOnTop: true,
    frame: false,
    transparent: true,
    resizable: true,
    movable: true,
    hasShadow: false,
    type: 'toolbar',
    skipTaskbar: true,
    title: 'Interview Bit AI Assistant',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Load Interview Bit Assistant in detached stealth mode
  const targetUrl = process.env.VITE_DEV_SERVER_URL || 'http://localhost:3000/interview-bit?mode=detached';
  mainWindow.loadURL(targetUrl);

  // --- 100% ANTI-SCREEN-SHARE OS CAPTURE EXCLUSION ---
  // Applies SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE = 0x11) on Windows
  // and NSWindowSharingNone on macOS to exclude window from screen recordings & screen shares.
  try {
    mainWindow.setContentProtection(true);
    console.log('✅ [OS Protection] Window Capture Exclusion (setContentProtection) enabled successfully!');
  } catch (err) {
    console.warn('⚠️ Could not set content protection:', err);
  }

  // Global Hotkeys: Alt + S or Alt + H to toggle visibility instantly
  globalShortcut.register('Alt+S', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
      }
    }
  });

  globalShortcut.register('Alt+H', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
      }
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  globalShortcut.unregisterAll();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

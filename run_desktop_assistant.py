#!/usr/bin/env python3
"""
InterviewBit — Desktop AI Assistant Launcher
Automatically detects environment (Linux/Wayland/Windows) and launches the standalone AI Assistant window.
On Windows: Applies OS SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE = 0x00000011) for 100% screen share privacy.
On Linux/Cross-platform: Launches Chrome App Mode or PyQt5 floating window.
"""

import os
import sys
import time
import platform
import subprocess
import shutil

# Configure Qt environment variables for Wayland / X11 compatibility
os.environ["QT_QPA_PLATFORM"] = "offscreen" if os.environ.get("HEADLESS") else "xcb;wayland"

def launch_chrome_app(url):
    print("🚀 Launching Chrome App Mode Assistant Window...")
    chrome_path = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("google-chrome-stable")
    if chrome_path:
        cmd = [
            chrome_path,
            f"--app={url}",
            "--window-size=440,640",
            "--window-position=80,80"
        ]
        subprocess.Popen(cmd)
        print("✅ Chrome App Window launched successfully!")
        return True
    return False

def launch_pyqt5_assistant(url):
    print(f"🚀 Initializing PyQt5 Desktop App for {url}...")
    from PyQt5.QtCore import QUrl, Qt
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWebEngineWidgets import QWebEngineView

    app = QApplication(sys.argv)
    view = QWebEngineView()
    view.setWindowTitle("Interview Assistant")
    view.resize(440, 640)
    view.move(80, 80)
    view.setWindowFlags(Qt.WindowStaysOnTopHint)
    view.load(QUrl(url))
    view.show()

    # Windows OS Screen Share Privacy (WDA_EXCLUDEFROMCAPTURE)
    if platform.system() == "Windows":
        try:
            import ctypes
            hwnd = int(view.winId())
            if hwnd:
                result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)
                if result:
                    print("✅ [OS Privacy] Windows SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE) applied!")
        except Exception as e:
            print(f"⚠️ [OS Privacy Warning] {e}")

    sys.exit(app.exec_())

def main():
    url = "http://localhost:8005/assistant/"
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🎯 InterviewBit — Desktop AI Assistant Window Launcher    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"Loading assistant from: {url}")
    print(f"OS Platform: {platform.system()} ({os.environ.get('XDG_SESSION_TYPE', 'Desktop')})\n")

    # 1. Try Chrome App Mode first (most reliable cross-platform standalone window)
    if launch_chrome_app(url):
        return

    # 2. Try PyQt5 fallback
    try:
        launch_pyqt5_assistant(url)
    except Exception as e:
        print(f"⚠️ Opening browser tab fallback ({e})")
        import webbrowser
        webbrowser.open(url)

if __name__ == "__main__":
    main()

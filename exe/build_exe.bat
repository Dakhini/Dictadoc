@echo off
REM Reconstruit AutoDoc_Capture.exe (dossier dist\AutoDoc_Capture). Necessite Python 3.12 + pyinstaller.
cd /d "%~dp0"
py -3.12 -m PyInstaller --noconfirm --onedir --console --name AutoDoc_Capture ^
  --collect-all faster_whisper --collect-all ctranslate2 --collect-all sounddevice ^
  --collect-all onnxruntime --collect-binaries av capture_doc.py
pause

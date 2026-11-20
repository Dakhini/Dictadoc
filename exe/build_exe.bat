@echo off
REM Reconstruit DictaDoc_Capture.exe : un seul fichier portable (dist\DictaDoc_Capture.exe).
REM Necessite Python 3.12 + pyinstaller.
cd /d "%~dp0"
py -3.12 -m PyInstaller --noconfirm --onefile --console --name DictaDoc_Capture ^
  --collect-all faster_whisper --collect-all ctranslate2 --collect-all sounddevice ^
  --collect-all onnxruntime --collect-binaries av capture_doc.py
pause

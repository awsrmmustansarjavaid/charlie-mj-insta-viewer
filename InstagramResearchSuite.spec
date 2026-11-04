# PyInstaller spec. Build with:  pyinstaller InstagramResearchSuite.spec            (portable folder)
#                                IRS_ONEFILE=1 pyinstaller InstagramResearchSuite.spec  (single .exe)
import os

onefile = os.environ.get("IRS_ONEFILE") == "1"
excludes = ["tkinter", "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.Qt3DCore",
            "PySide6.QtQuick", "PySide6.QtQml", "PySide6.QtDesigner", "PySide6.QtCharts", "PySide6.QtSql",
            "PySide6.QtBluetooth", "PySide6.QtSensors", "PySide6.QtSerialPort"]

a = Analysis(["main.py"], pathex=["."], datas=[("assets/icon.png", "assets"), ("assets/icon.ico", "assets")],
             hiddenimports=["keyring.backends.Windows"], excludes=excludes, noarchive=False)
pyz = PYZ(a.pure)

if onefile:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="InstagramResearchSuite", console=False,
              icon="assets/icon.ico", version="version_info.txt", upx=False)
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="InstagramResearchSuite", console=False,
              icon="assets/icon.ico", version="version_info.txt", upx=False)
    coll = COLLECT(exe, a.binaries, a.datas, name="InstagramResearchSuite", upx=False)

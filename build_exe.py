"""Build Koda as a single .exe using PyInstaller."""
import PyInstaller.__main__
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    os.path.join(SCRIPT_DIR, "voice.py"),
    "--name=Koda",
    "--onefile",
    "--windowed",
    "--icon=NONE",
    f"--add-data={os.path.join(SCRIPT_DIR, 'config.py')};.",
    f"--add-data={os.path.join(SCRIPT_DIR, 'text_processing.py')};.",
    f"--add-data={os.path.join(SCRIPT_DIR, 'sounds')};sounds",
    "--hidden-import=pystray._win32",
    "--hidden-import=PIL._tkinter_finder",
    "--hidden-import=comtypes.stream",
    "--hidden-import=pyttsx3.drivers",
    "--hidden-import=pyttsx3.drivers.sapi5",
    f"--distpath={os.path.join(SCRIPT_DIR, 'dist')}",
    f"--workpath={os.path.join(SCRIPT_DIR, 'build')}",
    f"--specpath={SCRIPT_DIR}",
    "--clean",
])

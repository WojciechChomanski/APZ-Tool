import subprocess
subprocess.check_call(["pyinstaller", "--onefile", "--windowed", "apz_gui.py"])
import cx_Freeze
import sys
import os 

base = None

if sys.platform == 'win32':
    base = "Win32GUI"


executables = [cx_Freeze.Executable("FileShare.py", base=base, icon=r'Images\icon.png')]


cx_Freeze.setup(
    name = "FileShare",

    options = {"build_exe": {"packages":['tkinter',"os"],
    "include_files":['Images']}},
    version = "3.0",
    description = "FileShare",
    executables = executables
    )

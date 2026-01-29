#!/usr/bin/env python3
#
# build_windows_exe.py
#
# Builds a Windows exe of brigadier using PyInstaller. PyInstaller
# will be downloaded to the cwd and its archive kept for later use.
#
# Requires:
# - Python 3.8+
# - Run this script on Windows to build the exe locally.
#   On other platforms, use CI (e.g. GitHub Actions) to build on Windows.

import hashlib
import os
import platform
import shutil
import subprocess
import sys
from zipfile import BadZipFile, ZipFile

# PyInstaller 6.x supports Python 3.8+
PYINSTALLER_VERSION = "6.10.0"
PYINSTALLER_URL = (
    f"https://github.com/pyinstaller/pyinstaller/archive/refs/tags/v{PYINSTALLER_VERSION}.zip"
)
PYINST_ZIPFILE = os.path.join(os.getcwd(), "pyinstaller.zip")
NAME = "brigadier"


def main():
    if platform.system() != "Windows":
        print("This script builds a Windows exe and must be run on Windows.")
        print("On Mac/Linux, push to GitHub and use Actions to build on Windows.")
        sys.exit(1)

    with open("VERSION", "r") as fd:
        version = fd.read().strip()
    name_versioned = NAME + "-" + version
    exe_name = NAME + ".exe"
    pack_dir = os.path.join(os.getcwd(), name_versioned)
    build_dir = os.path.join(os.getcwd(), "build")

    # Download PyInstaller if needed
    need_pyinstaller = False
    if os.path.exists(PYINST_ZIPFILE):
        print("PyInstaller zipfile found.")
        try:
            with ZipFile(PYINST_ZIPFILE) as zf:
                pass
        except BadZipFile:
            print("Zipfile is corrupt.")
            need_pyinstaller = True
    else:
        need_pyinstaller = True

    if need_pyinstaller:
        print("Downloading PyInstaller...")
        import urllib.request

        urllib.request.urlretrieve(PYINSTALLER_URL, filename=PYINST_ZIPFILE)

    with ZipFile(PYINST_ZIPFILE) as dlzip:
        pyinst_root = dlzip.namelist()[0].split("/")[0]
    with ZipFile(PYINST_ZIPFILE) as dlzip:
        dlzip.extractall()

    pyinst_root_path = os.path.join(os.getcwd(), pyinst_root)
    if not os.path.isdir(pyinst_root_path):
        sys.exit("PyInstaller root not found: " + pyinst_root_path)

    brigadier_script = os.path.join(os.getcwd(), "brigadier")

    print("Building version %s..." % version)
    build_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "-F",
        "--distpath",
        pack_dir,
        "--name",
        NAME,
        brigadier_script,
    ]
    subprocess.check_call(build_cmd, cwd=pyinst_root_path)

    print("Compressing to zip file...")
    zipfile_name = name_versioned + ".zip"
    exe_path = os.path.join(pack_dir, exe_name)
    with ZipFile(zipfile_name, "w") as packzip:
        packzip.write(exe_path, os.path.join(name_versioned, exe_name))

    with open(zipfile_name, "rb") as zipfd:
        sha1 = hashlib.sha1(zipfd.read()).hexdigest()

    print("Cleaning up...")
    for dirs in [pack_dir, build_dir, pyinst_root]:
        if os.path.isdir(dirs):
            shutil.rmtree(dirs)
    for f in os.listdir(os.getcwd()):
        if f.startswith("logdict"):
            os.remove(os.path.join(os.getcwd(), f))

    print("Built and archived to %s." % zipfile_name)
    print("SHA1: %s" % sha1)


if __name__ == "__main__":
    main()

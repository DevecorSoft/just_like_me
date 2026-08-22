#!/usr/bin/env python3
import subprocess
from pathlib import Path


def install():
  script = Path(__file__).parent / "daemon" / "install.sh"
  subprocess.run([str(script)], check=True, shell=True, stderr=subprocess.STDOUT)


def uninstall():
  script = Path(__file__).parent / "daemon" / "uninstall.sh"
  subprocess.run([str(script)], check=True, shell=True, stderr=subprocess.STDOUT)

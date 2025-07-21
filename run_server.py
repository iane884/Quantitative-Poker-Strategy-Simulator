#!/usr/bin/env python3
import subprocess
import sys

# Run uvicorn from project root with correct module path
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "backend.app:app", 
    "--reload",
    "--host", "0.0.0.0",
    "--port", "8000"
])
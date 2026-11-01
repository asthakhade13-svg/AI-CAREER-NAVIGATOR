#!/usr/bin/env python3
"""
CareerNav Parity Sync CLI Tool Launcher
Enables running `python sync_frontend.py` directly from the backend/ directory.
"""
import os
import sys

# Route execution to the root sync_frontend.py
backend_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(backend_dir)
root_script = os.path.join(root_dir, "sync_frontend.py")

if os.path.isfile(root_script):
    import runpy
    sys.path.insert(0, root_dir)
    runpy.run_path(root_script, run_name="__main__")
else:
    print(f"Error: Could not locate {root_script}")
    sys.exit(1)

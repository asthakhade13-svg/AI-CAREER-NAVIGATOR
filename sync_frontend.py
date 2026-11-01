#!/usr/bin/env python3
"""
CareerNav Parity Sync CLI Tool
==============================
Standalone utility to inspect, verify, and synchronize all web assets
between the root directory (used by GitHub Pages) and the frontend/ directory
(used by backend static file mounts and package distributions).

Usage:
    python sync_frontend.py                # Inspect and bidirectional sync
    python sync_frontend.py --check        # Check parity without writing (exit 0/1 for CI)
    python sync_frontend.py --status       # Display full status table of all tracked assets
    python sync_frontend.py --watch        # Continuous watch & auto-sync on file changes
    python sync_frontend.py --force-root   # Force sync root/ -> frontend/
    python sync_frontend.py --force-frontend # Force sync frontend/ -> root/
"""

import os
import sys
import time
import shutil
import hashlib
import argparse
from typing import Dict, List, Tuple, Set, Optional

# Locate project directories reliably regardless of CWD
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR) == "backend":
    REPO_ROOT = os.path.dirname(SCRIPT_DIR)
else:
    REPO_ROOT = SCRIPT_DIR

FRONTEND_DIR = os.path.join(REPO_ROOT, "frontend")
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")

# Web asset extensions to track
SYNC_EXTENSIONS = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg"}
EXCLUDED_FILENAMES = {"index (1).html"}

def get_file_hash(filepath: str) -> Optional[str]:
    """Calculates MD5 hash of a file for exact binary comparison."""
    if not os.path.isfile(filepath):
        return None
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def collect_assets(directory: str) -> Dict[str, str]:
    """Recursively collects relative paths of all relevant web assets."""
    assets = {}
    if not os.path.isdir(directory):
        return assets

    for root, dirs, files in os.walk(directory):
        # Exclude git, node_modules, and backend
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "backend", ".gemini", "__pycache__", "data", "output", "models_saved"}]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SYNC_EXTENSIONS and f not in EXCLUDED_FILENAMES:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, directory).replace("\\", "/")
                # Ignore files located within the frontend folder when scanning root
                if directory == REPO_ROOT and rel_path.startswith("frontend/"):
                    continue
                assets[rel_path] = full_path

    return assets

def get_asset_status() -> List[Dict]:
    """Compares all assets across root and frontend/."""
    root_assets = collect_assets(REPO_ROOT)
    frontend_assets = collect_assets(FRONTEND_DIR)
    all_rel_paths = sorted(set(root_assets.keys()).union(set(frontend_assets.keys())))

    status_list = []
    for rel in all_rel_paths:
        r_path = root_assets.get(rel)
        f_path = frontend_assets.get(rel)

        r_exists = r_path is not None and os.path.isfile(r_path)
        f_exists = f_path is not None and os.path.isfile(f_path)

        if r_exists and not f_exists:
            status = "MISSING_IN_FRONTEND"
            action_needed = "COPY_TO_FRONTEND"
        elif f_exists and not r_exists:
            status = "MISSING_IN_ROOT"
            action_needed = "COPY_TO_ROOT"
        else:
            r_hash = get_file_hash(r_path)
            f_hash = get_file_hash(f_path)
            if r_hash == f_hash:
                status = "IN_SYNC"
                action_needed = "NONE"
            else:
                status = "CONTENT_MISMATCH"
                r_mtime = os.path.getmtime(r_path)
                f_mtime = os.path.getmtime(f_path)
                action_needed = "SYNC_ROOT_TO_FRONTEND" if r_mtime >= f_mtime else "SYNC_FRONTEND_TO_ROOT"

        status_list.append({
            "rel_path": rel,
            "root_exists": r_exists,
            "frontend_exists": f_exists,
            "root_size": os.path.getsize(r_path) if r_exists else 0,
            "frontend_size": os.path.getsize(f_path) if f_exists else 0,
            "root_mtime": os.path.getmtime(r_path) if r_exists else 0,
            "frontend_mtime": os.path.getmtime(f_path) if f_exists else 0,
            "status": status,
            "action_needed": action_needed
        })

    return status_list

def sync_assets(force: Optional[str] = None, dry_run: bool = False, verbose: bool = False) -> Tuple[int, List[str]]:
    """Synchronizes assets across root and frontend/."""
    statuses = get_asset_status()
    synced_actions = []

    for item in statuses:
        rel = item["rel_path"]
        action = item["action_needed"]
        r_path = os.path.join(REPO_ROOT, rel)
        f_path = os.path.join(FRONTEND_DIR, rel)

        if force == "root":
            if item["root_exists"]:
                action = "SYNC_ROOT_TO_FRONTEND"
        elif force == "frontend":
            if item["frontend_exists"]:
                action = "SYNC_FRONTEND_TO_ROOT"

        if action == "NONE":
            if verbose:
                print(f"  [OK]       {rel} (identical)")
            continue

        os.makedirs(os.path.dirname(r_path), exist_ok=True)
        os.makedirs(os.path.dirname(f_path), exist_ok=True)

        if action in ("COPY_TO_FRONTEND", "SYNC_ROOT_TO_FRONTEND"):
            act_desc = f"{rel} (root -> frontend/)"
            if not dry_run:
                shutil.copy2(r_path, f_path)
            synced_actions.append(f"SYNCED: {act_desc}")
            print(f"  [SYNCED]   {act_desc}")

        elif action in ("COPY_TO_ROOT", "SYNC_FRONTEND_TO_ROOT"):
            act_desc = f"{rel} (frontend/ -> root)"
            if not dry_run:
                shutil.copy2(f_path, r_path)
            synced_actions.append(f"SYNCED: {act_desc}")
            print(f"  [SYNCED]   {act_desc}")

    return len(synced_actions), synced_actions

def print_status_table():
    """Prints a structured table showing sync status for all tracked files."""
    statuses = get_asset_status()
    print("=" * 78)
    print(f"{'ASSET FILE':<28} {'ROOT SIZE':<12} {'FRONTEND SIZE':<14} {'STATUS':<16}")
    print("=" * 78)
    for s in statuses:
        rel = s["rel_path"]
        r_sz = f"{s['root_size']} B" if s["root_exists"] else "--"
        f_sz = f"{s['frontend_size']} B" if s["frontend_exists"] else "--"
        st = s["status"]
        print(f"{rel:<28} {r_sz:<12} {f_sz:<14} {st:<16}")
    print("=" * 78)
    in_sync = sum(1 for s in statuses if s["status"] == "IN_SYNC")
    print(f"Summary: {in_sync}/{len(statuses)} assets in 100% parity.")

def watch_mode(interval: float = 1.5):
    """Continuously monitors and auto-syncs any changed assets."""
    print(f"[CareerNav Watcher] Monitoring root/ and frontend/ every {interval}s (Press Ctrl+C to exit)...")
    try:
        while True:
            statuses = get_asset_status()
            out_of_sync = [s for s in statuses if s["action_needed"] != "NONE"]
            if out_of_sync:
                now_str = time.strftime("%H:%M:%S")
                print(f"[{now_str}] Detected {len(out_of_sync)} drift(s). Syncing...")
                sync_assets(dry_run=False, verbose=False)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[CareerNav Watcher] Watcher stopped.")

def main():
    parser = argparse.ArgumentParser(
        description="CareerNav Dual Directory Parity CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--check", "-c", action="store_true", help="Check parity without making changes (exit 0 if clean, 1 if drift)")
    parser.add_argument("--status", "-s", action="store_true", help="Print detailed parity status table for all tracked assets")
    parser.add_argument("--watch", "-w", action="store_true", help="Run continuous watcher to auto-sync changes in real time")
    parser.add_argument("--force-root", action="store_true", help="Force overwrite frontend/ from root")
    parser.add_argument("--force-frontend", action="store_true", help="Force overwrite root from frontend/")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output for all checked assets")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output except errors")

    args = parser.parse_args()

    if args.status:
        print_status_table()
        return

    if args.watch:
        watch_mode()
        return

    if args.check:
        statuses = get_asset_status()
        drifts = [s for s in statuses if s["status"] != "IN_SYNC"]
        if not drifts:
            if not args.quiet:
                print(f"[CareerNav Parity Check] PASS: All {len(statuses)} assets are in 100% parity.")
            sys.exit(0)
        else:
            print(f"[CareerNav Parity Check] FAIL: {len(drifts)} asset(s) out of parity:")
            for d in drifts:
                print(f"  ! {d['rel_path']}: {d['status']} (needs {d['action_needed']})")
            sys.exit(1)

    force_mode = None
    if args.force_root:
        force_mode = "root"
    elif args.force_frontend:
        force_mode = "frontend"

    if not args.quiet:
        print("[CareerNav Parity Sync] Scanning root/ <-> frontend/...")

    count, actions = sync_assets(force=force_mode, dry_run=False, verbose=args.verbose)

    if not args.quiet:
        if count == 0:
            print("[CareerNav Parity Sync] All assets are already in 100% parity! (0 files changed)")
        else:
            print(f"[CareerNav Parity Sync] Successfully synchronized {count} file(s).")

if __name__ == "__main__":
    main()

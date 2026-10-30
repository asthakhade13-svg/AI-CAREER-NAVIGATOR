#!/usr/bin/env python3
"""
CareerNav Parity Sync Utility
Ensures complete 1-to-1 synchronization between the root directory (used by GitHub Pages)
and the frontend/ directory (used by backend packaging and static mounts).
"""
import sys
import os

repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(repo_root, "backend"))

try:
    from services.parity_service import sync_directories, verify_parity
except ImportError:
    # Fallback standalone implementation
    import shutil
    import hashlib

    SYNC_EXTENSIONS = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg"}
    EXCLUDED = {"index (1).html"}

    def get_hash(p):
        if not os.path.isfile(p): return None
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(65536), b""): h.update(b)
        return h.hexdigest()

    def sync_directories():
        f_dir = os.path.join(repo_root, "frontend")
        synced = []
        all_f = set()
        for d in [repo_root, f_dir]:
            if os.path.isdir(d):
                for f in os.listdir(d):
                    if os.path.isfile(os.path.join(d, f)) and os.path.splitext(f)[1].lower() in SYNC_EXTENSIONS and f not in EXCLUDED:
                        all_f.add(f)
        for f in all_f:
            rp, fp = os.path.join(repo_root, f), os.path.join(f_dir, f)
            if os.path.isfile(rp) and not os.path.isfile(fp):
                shutil.copy2(rp, fp); synced.append(f)
            elif os.path.isfile(fp) and not os.path.isfile(rp):
                shutil.copy2(fp, rp); synced.append(f)
            elif os.path.isfile(rp) and os.path.isfile(fp) and get_hash(rp) != get_hash(fp):
                src = rp if os.path.getmtime(rp) >= os.path.getmtime(fp) else fp
                dst = fp if src == rp else rp
                shutil.copy2(src, dst); synced.append(f)
        return {"totalChecked": len(all_f), "totalSynced": len(synced), "synced": [{"file": x, "action": "synced"} for x in synced]}

    def verify_parity():
        f_dir = os.path.join(repo_root, "frontend")
        mismatches = []
        for f in os.listdir(f_dir):
            if os.path.isfile(os.path.join(f_dir, f)) and os.path.splitext(f)[1].lower() in SYNC_EXTENSIONS and f not in EXCLUDED:
                rp, fp = os.path.join(repo_root, f), os.path.join(f_dir, f)
                if not os.path.isfile(rp) or get_hash(rp) != get_hash(fp):
                    mismatches.append(f)
        return len(mismatches) == 0, mismatches

if __name__ == "__main__":
    print("[CareerNav] Running dual directory parity sync (root <-> frontend/)...")
    res = sync_directories()
    print(f"[CareerNav] Checked {res.get('totalChecked', 0)} assets, synchronized {res.get('totalSynced', 0)} files.")
    for item in res.get("synced", []):
        print(f"  -> {item.get('action')}: {item.get('file')}")

    clean, mismatches = verify_parity()
    if clean:
        print("[CareerNav] SUCCESS: root/ and frontend/ are in complete parity!")
        sys.exit(0)
    else:
        print(f"[CareerNav] WARNING: {len(mismatches)} mismatches detected: {mismatches}")
        sys.exit(1)

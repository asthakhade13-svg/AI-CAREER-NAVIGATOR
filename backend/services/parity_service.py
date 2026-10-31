import os
import shutil
import hashlib
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

SYNC_EXTENSIONS = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg"}
EXCLUDED_FILENAMES = {"index (1).html"}

def get_file_hash(filepath: str) -> Optional[str]:
    """Computes MD5 hash of a file for exact binary comparison."""
    if not os.path.isfile(filepath):
        return None
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to hash {filepath}: {e}")
        return None

def sync_directories(root_dir: Optional[str] = None, frontend_dir: Optional[str] = None) -> Dict:
    """
    Ensures complete bidirectional parity between root and frontend/ directories.
    - If a file is modified in root, it updates frontend/.
    - If a file is modified in frontend/, it updates root.
    - Preserves file timestamps using shutil.copy2.
    """
    this_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(this_dir)
    repo_root = os.path.dirname(backend_dir)

    root_dir = os.path.abspath(root_dir or repo_root)
    frontend_dir = os.path.abspath(frontend_dir or os.path.join(repo_root, "frontend"))

    if not os.path.isdir(root_dir) or not os.path.isdir(frontend_dir):
        return {"success": False, "message": "Directories do not exist", "synced": []}

    synced_items = []

    # 1. Sync root-level assets
    root_files = [
        f for f in os.listdir(root_dir)
        if os.path.isfile(os.path.join(root_dir, f))
        and os.path.splitext(f)[1].lower() in SYNC_EXTENSIONS
        and f not in EXCLUDED_FILENAMES
    ]

    frontend_files = [
        f for f in os.listdir(frontend_dir)
        if os.path.isfile(os.path.join(frontend_dir, f))
        and os.path.splitext(f)[1].lower() in SYNC_EXTENSIONS
    ]

    all_files = set(root_files).union(set(frontend_files))

    for filename in sorted(all_files):
        root_path = os.path.join(root_dir, filename)
        front_path = os.path.join(frontend_dir, filename)

        root_exists = os.path.isfile(root_path)
        front_exists = os.path.isfile(front_path)

        if root_exists and not front_exists:
            shutil.copy2(root_path, front_path)
            synced_items.append({"file": filename, "action": "copied_to_frontend"})
            logger.info(f"[Parity] Copied new root asset to frontend: {filename}")
        elif front_exists and not root_exists:
            shutil.copy2(front_path, root_path)
            synced_items.append({"file": filename, "action": "copied_to_root"})
            logger.info(f"[Parity] Copied new frontend asset to root: {filename}")
        elif root_exists and front_exists:
            root_hash = get_file_hash(root_path)
            front_hash = get_file_hash(front_path)

            if root_hash != front_hash:
                root_mtime = os.path.getmtime(root_path)
                front_mtime = os.path.getmtime(front_path)

                if root_mtime >= front_mtime:
                    shutil.copy2(root_path, front_path)
                    synced_items.append({"file": filename, "action": "synced_root_to_frontend"})
                    logger.info(f"[Parity] Updated frontend from newer root version: {filename}")
                else:
                    shutil.copy2(front_path, root_path)
                    synced_items.append({"file": filename, "action": "synced_frontend_to_root"})
                    logger.info(f"[Parity] Updated root from newer frontend version: {filename}")

    # 2. Sync icons directory
    root_icons = os.path.join(root_dir, "icons")
    front_icons = os.path.join(frontend_dir, "icons")
    if os.path.isdir(root_icons) and os.path.isdir(front_icons):
        for icon in os.listdir(root_icons):
            r_icon = os.path.join(root_icons, icon)
            f_icon = os.path.join(front_icons, icon)
            if os.path.isfile(r_icon):
                if not os.path.isfile(f_icon) or get_file_hash(r_icon) != get_file_hash(f_icon):
                    r_time = os.path.getmtime(r_icon)
                    f_time = os.path.getmtime(f_icon) if os.path.isfile(f_icon) else 0
                    if r_time >= f_time:
                        shutil.copy2(r_icon, f_icon)
                    else:
                        shutil.copy2(f_icon, r_icon)
                    synced_items.append({"file": f"icons/{icon}", "action": "synced_icon"})

    return {
        "success": True,
        "totalChecked": len(all_files),
        "totalSynced": len(synced_items),
        "synced": synced_items
    }

def resolve_newest_file(filename: str, candidate_paths: List[str]) -> Optional[str]:
    """
    Finds all existing candidate paths for a file, selects the most recently modified one,
    and automatically synchronizes newer content across duplicate locations.
    """
    seen = set()
    valid_paths = []
    for p in candidate_paths:
        norm = os.path.normpath(p)
        if norm not in seen and os.path.isfile(norm):
            seen.add(norm)
            valid_paths.append(norm)

    if not valid_paths:
        return None

    if len(valid_paths) == 1:
        return valid_paths[0]

    # Sort candidates by mtime descending (newest first)
    valid_paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    best_path = valid_paths[0]
    best_hash = None

    # Sync newer version to any outdated candidate paths
    for other_path in valid_paths[1:]:
        try:
            if os.path.samefile(best_path, other_path):
                continue
        except Exception:
            pass

        # If mtimes are virtually identical, files are already in sync
        if abs(os.path.getmtime(best_path) - os.path.getmtime(other_path)) < 0.001:
            continue

        if best_hash is None:
            best_hash = get_file_hash(best_path)

        if get_file_hash(other_path) != best_hash:
            try:
                shutil.copy2(best_path, other_path)
                logger.info(f"[Parity Auto-sync] Replaced stale {other_path} with {best_path}")
            except Exception as e:
                logger.warning(f"[Parity Auto-sync] Failed to sync {best_path} to {other_path}: {e}")

    return best_path

def verify_parity(root_dir: Optional[str] = None, frontend_dir: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Verifies that all corresponding web assets in root and frontend/ match identically.
    Returns (True, []) if in complete parity, or (False, [mismatches...]).
    """
    this_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(this_dir)
    repo_root = os.path.dirname(backend_dir)

    root_dir = os.path.abspath(root_dir or repo_root)
    frontend_dir = os.path.abspath(frontend_dir or os.path.join(repo_root, "frontend"))

    mismatches = []

    frontend_files = [
        f for f in os.listdir(frontend_dir)
        if os.path.isfile(os.path.join(frontend_dir, f))
        and os.path.splitext(f)[1].lower() in SYNC_EXTENSIONS
    ]

    for f in sorted(frontend_files):
        r_path = os.path.join(root_dir, f)
        f_path = os.path.join(frontend_dir, f)

        if not os.path.isfile(r_path):
            mismatches.append(f"{f} exists in frontend/ but is missing in root")
            continue

        r_hash = get_file_hash(r_path)
        f_hash = get_file_hash(f_path)

        if r_hash != f_hash:
            mismatches.append(f"{f} content mismatch (root hash {r_hash[:8]} != frontend hash {f_hash[:8]})")

    return (len(mismatches) == 0, mismatches)

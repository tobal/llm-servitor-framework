#!/usr/bin/env python3
"""
LLM Servitor Framework (LSF) Environment Initializer — bootstrap-lsf.py
----------------------------------------------------------------------
Initializes the nested hierarchical directory structure for all servitors
in the Cyber-Táltos Pantheon under ~/.lsf/servitors/.

Hierarchy:
  ~/.lsf/
  ├── inbox/
  ├── logs/
  └── servitors/
      ├── common/                (Root common knowledge for all servitors)
      ├── <transversal>/         (knowledge/, workspace/)
      └── kronos/                (knowledge/, workspace/, common/)
          └── <tier1_archon>/    (knowledge/, workspace/, common/)
              └── <tier2_task>/  (knowledge/, workspace/)
"""

import os
import sys
import shutil
from pathlib import Path

BASE_DIR = Path.home() / ".lsf"
INBOX_DIR = BASE_DIR / "inbox"
LOGS_DIR = BASE_DIR / "logs"
SERVITORS_DIR = BASE_DIR / "servitors"
ROOT_COMMON_DIR = SERVITORS_DIR / "common"

# Transversal Servitors (Directly under ~/.lsf/servitors/)
TRANSVERSAL_SERVITORS = [
    "zyzyx",
    "fuji-san",
    "motoko",
    "phileas",
    "gurgeh",
    "hetszunya",
]

# Tier 0 Kronos -> Tier 1 Archons -> Tier 2 Task Servitors
PANTHEON_HIERARCHY = {
    "kronos": {
        "tier": 0,
        "archons": {
            "daedalus": [
                "stallman",
                "dijkstra",
                "flatline",
                "tesla",
                "turing",
            ],
            "splinter": [
                "usagi",
                "kerecsen",
                "kitsune",
                "fenrir",
                "paracelsus",
            ],
            "orpheus": [
                "vinci",
                "chapman",
                "silverhand",
                "flynn",
            ],
            "morpheus": [
                "aurelius",
                "kampo",
                "eldred",
            ],
            "lindbergh": [
                "takumi",
                "wash",
                "nemo",
            ],
        }
    }
}

def initialize():
    print(f"⚡ Initializing LLM Servitor Framework (LSF) Environment at {BASE_DIR}...")
    
    # 1. Root directories
    for path in [BASE_DIR, INBOX_DIR, LOGS_DIR, SERVITORS_DIR, ROOT_COMMON_DIR]:
        path.mkdir(parents=True, exist_ok=True)
        print(f"  [✓] Root Directory: {path}")

    created_dirs_count = 1

    # 2. Copy files from local ./common/ directory next to script into ~/.lsf/servitors/common/
    script_dir = Path(__file__).resolve().parent
    local_common_dir = script_dir / "common"
    
    if not local_common_dir.exists():
        local_common_dir = Path("./common").resolve()

    if local_common_dir.exists() and local_common_dir.is_dir():
        print(f"\n📂 Copying common knowledge files from {local_common_dir} -> {ROOT_COMMON_DIR}...")
        copied_files_count = 0
        for item in local_common_dir.glob("*"):
            if item.is_file():
                dest_file = ROOT_COMMON_DIR / item.name
                shutil.copy2(item, dest_file)
                copied_files_count += 1
                print(f"  [✓] Copied: {item.name}")
        print(f"  --> Copied {copied_files_count} common knowledge file(s).")
    else:
        print(f"\nℹ️ Local './common/' directory not found at {local_common_dir}. Skipping file copy to {ROOT_COMMON_DIR}.")

    # 3. Transversal Servitors (knowledge/, workspace/)
    print("\n🛡️ Initializing Transversal Servitor Directories...")
    for t_servitor in TRANSVERSAL_SERVITORS:
        t_path = SERVITORS_DIR / t_servitor
        (t_path / "knowledge").mkdir(parents=True, exist_ok=True)
        (t_path / "workspace").mkdir(parents=True, exist_ok=True)
        created_dirs_count += 2
        print(f"  [✓] Transversal: {t_path.relative_to(BASE_DIR)} (knowledge/, workspace/)")

    # 4. Kronos (Tier 0: knowledge/, workspace/, common/)
    print("\n👁️ Initializing Tier 0 (Kronos) Directories...")
    kronos_path = SERVITORS_DIR / "kronos"
    (kronos_path / "knowledge").mkdir(parents=True, exist_ok=True)
    (kronos_path / "workspace").mkdir(parents=True, exist_ok=True)
    (kronos_path / "common").mkdir(parents=True, exist_ok=True)
    created_dirs_count += 3
    print(f"  [✓] Tier 0 Master: {kronos_path.relative_to(BASE_DIR)} (knowledge/, workspace/, common/)")

    # 5. Tier 1 Archons & Tier 2 Task Servitors
    print("\n💻 Initializing Category Archons (Tier 1) & Task Servitors (Tier 2)...")
    archons = PANTHEON_HIERARCHY["kronos"]["archons"]
    for archon_name, sub_servitors in archons.items():
        archon_path = kronos_path / archon_name
        (archon_path / "knowledge").mkdir(parents=True, exist_ok=True)
        (archon_path / "workspace").mkdir(parents=True, exist_ok=True)
        (archon_path / "common").mkdir(parents=True, exist_ok=True)
        created_dirs_count += 3
        print(f"  [✓] Tier 1 Archon: {archon_path.relative_to(BASE_DIR)} (knowledge/, workspace/, common/)")

        for t2_servitor in sub_servitors:
            t2_path = archon_path / t2_servitor
            (t2_path / "knowledge").mkdir(parents=True, exist_ok=True)
            (t2_path / "workspace").mkdir(parents=True, exist_ok=True)
            created_dirs_count += 2
            print(f"      [✓] Tier 2 Task Servitor: {t2_path.relative_to(BASE_DIR)} (knowledge/, workspace/)")

    print(f"\n✅ LSF Environment successfully initialized ({created_dirs_count} directory nodes created under {BASE_DIR}).")

if __name__ == "__main__":
    initialize()

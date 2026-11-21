#!/usr/bin/env python3
"""
LLM Servitor Framework (LSF) Environment Initializer — setup-lsf.py
-------------------------------------------------------------------
Initializes the nested hierarchical directory structure for all servitors
in the Cyber-Táltos Pantheon under ~/.lsf/servitors/.

Hierarchy:
  ~/.lsf/
  ├── inbox/
  ├── logs/
  └── servitors/
      ├── <transversal>/         (knowledge/, workspace/)
      └── kronos/                (knowledge/, workspace/, common/)
          └── <tier1_archon>/    (knowledge/, workspace/, common/)
              └── <tier2_task>/  (knowledge/, workspace/)
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path.home() / ".lsf"
INBOX_DIR = BASE_DIR / "inbox"
LOGS_DIR = BASE_DIR / "logs"
SERVITORS_DIR = BASE_DIR / "servitors"

# Hierarchy Tree Definition
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
                "dijkstra",  # Newly added programming servitor
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
    for path in [BASE_DIR, INBOX_DIR, LOGS_DIR, SERVITORS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
        print(f"  [✓] Root Directory: {path}")

    created_dirs_count = 0

    # 2. Transversal Servitors (knowledge/, workspace/)
    print("\n🛡️ Initializing Transversal Servitor Directories...")
    for t_servitor in TRANSVERSAL_SERVITORS:
        t_path = SERVITORS_DIR / t_servitor
        (t_path / "knowledge").mkdir(parents=True, exist_ok=True)
        (t_path / "workspace").mkdir(parents=True, exist_ok=True)
        created_dirs_count += 2
        print(f"  [✓] Transversal: {t_path.relative_to(BASE_DIR)} (knowledge/, workspace/)")

    # 3. Kronos (Tier 0: knowledge/, workspace/, common/)
    print("\n👁️ Initializing Tier 0 (Kronos) Directories...")
    kronos_path = SERVITORS_DIR / "kronos"
    (kronos_path / "knowledge").mkdir(parents=True, exist_ok=True)
    (kronos_path / "workspace").mkdir(parents=True, exist_ok=True)
    (kronos_path / "common").mkdir(parents=True, exist_ok=True)
    created_dirs_count += 3
    print(f"  [✓] Tier 0 Master: {kronos_path.relative_to(BASE_DIR)} (knowledge/, workspace/, common/)")

    # 4. Tier 1 Archons & Tier 2 Task Servitors
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

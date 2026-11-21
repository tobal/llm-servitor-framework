#!/usr/bin/env python3
"""
LSF Environment Initializer
--------------------------------
Initializes local directory hierarchy and populates per-servitor knowledge bases
on your Linux host.

Directories Created:
  ~/.lsf/inbox
  ~/.lsf/logs
  ~/.lsf/knowledge/<servitor_name>/
  ~/.lsf/workspace/<servitor_name>/
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path.home() / ".lsf"
INBOX_DIR = BASE_DIR / "inbox"
LOGS_DIR = BASE_DIR / "logs"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
WORKSPACE_DIR = BASE_DIR / "workspace"

# Complete roster of all servitors in the Cyber-Táltos Pantheon
SERVITORS = [
    "kronos",
    "zyzyx", "fuji-san", "motoko", "phileas", "gurgeh", "hetszunya",
    "daedalus", "stallman", "flatline", "tesla", "turing",
    "splinter", "usagi", "kerecsen", "kitsune", "fenrir", "paracelsus",
    "orpheus", "vinci", "chapman", "silverhand", "flynn",
    "morpheus", "aurelius", "kampo", "eldred",
    "lindbergh", "takumi", "wash", "nemo", "duncan"
]

def initialize():
    print(f"⚡ Initializing Cyber-Táltos Servitor Environment at {BASE_DIR}...")
    
    # Root directories
    for path in [BASE_DIR, INBOX_DIR, LOGS_DIR, KNOWLEDGE_DIR, WORKSPACE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
        print(f"  [✓] Directory: {path}")

    # Per-servitor directories
    for s in SERVITORS:
        k_path = KNOWLEDGE_DIR / s
        w_path = WORKSPACE_DIR / s
        k_path.mkdir(parents=True, exist_ok=True)
        w_path.mkdir(parents=True, exist_ok=True)
        
        # Create initial placeholder profile if knowledge is empty
        profile_file = k_path / "README.md"
        if not profile_file.exists():
            with open(profile_file, "w", encoding="utf-8") as f:
                f.write(f"# Servitor Knowledge Base: {s.upper()}\n\nPlace context markdown documents for {s} in this directory.\n")

    print(f"\n✅ Successfully initialized workspace structure for {len(SERVITORS)} servitors.")

if __name__ == "__main__":
    initialize()

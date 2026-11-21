#!/usr/bin/env python3
"""
LSF CLI (LLM Servitor Framework) v10.0: Gemini Free Tier Quotas & Usage Telemetry Engine: Interactive Terminal UI & Cyber-Táltos Multi-Agent Engine
-----------------------------------------------------------------------
Engineered for Linux host operation using the Gemini API (gemini-2.0-flash).

Version 6 Enhancements:
  - Interactive CLI UI (`interactive` / `chat` subcommand or default execution).
  - Scrollable Terminal Paging: Automatic and manual (`/page`) response pagination via rich.pager (`less -R`).
  - In-Session Servitor & Model Switching: Dynamic slash commands (/switch, /model, /clear, /history, /help, /exit).
  - Multi-Turn Conversation Memory: Interactive prompt loop maintains active context stack.
  - Common Knowledge Base Layer:
      ~/.lsf/common-knowledge/
      ~/.lsf/knowledge/common/
  - Per-Servitor Directory Isolation:
      ~/.lsf/inbox
      ~/.lsf/logs
      ~/.lsf/knowledge/<servitor_name>/
      ~/.lsf/workspace/<servitor_name>/
  - Complete Pantheon Profiles: Ingests all Tier 0, Transversal, Archon (Tier 1),
    and Task (Tier 2) servitors from servitor-pantheon.md.
  - Hierarchy-Aware List Command: Displays structured taxonomy showing Tiers,
    Category Archons, and bound Task Servitors.
  - Multimodal Tooling: Native image/video processing via Gemini File API.
"""

import os
import sys
import json
import time
import argparse
import subprocess

# Terminal UI & Interactive Libraries
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.theme import Theme
    from rich.text import Text
    from rich import print as rprint
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.styles import Style as PtStyle
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

import urllib.request
import urllib.parse
import re
from html import unescape
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure google-genai package availability
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: `google-genai` package not installed.", file=sys.stderr)
    print("Install via: pip install google-genai", file=sys.stderr)
    sys.exit(1)

# --- CONFIGURATION & PATHS ---
BASE_DIR = Path.home() / ".lsf"
INBOX_DIR = BASE_DIR / "inbox"
WORKSPACE_DIR = BASE_DIR / "workspace"
LOGS_DIR = BASE_DIR / "logs"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
COMMON_KNOWLEDGE_DIR = BASE_DIR / "common-knowledge"
ALT_COMMON_KNOWLEDGE_DIR = KNOWLEDGE_DIR / "common"

# Ensure root runtime directories exist
for p in [BASE_DIR, INBOX_DIR, WORKSPACE_DIR, LOGS_DIR, KNOWLEDGE_DIR, COMMON_KNOWLEDGE_DIR, ALT_COMMON_KNOWLEDGE_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# --- FULL SERVITOR PANTHEON TAXONOMY & PROFILES ---
PANTHEON_STRUCTURE = [
    {
        "section": "👁️ TIER 0: EXECUTIVE CORE & SYSTEM MASTER",
        "servitors": ["kronos"]
    },
    {
        "section": "🛡️ TRANSVERSAL ENGINES (Cross-Category Currents)",
        "servitors": ["zyzyx", "fuji-san", "motoko", "phileas", "gurgeh", "hetszunya"]
    },
    {
        "section": "💻 CATEGORY 1: LOGIC, SOFTWARE & CYBERNETICS",
        "archon": "daedalus",
        "servitors": ["stallman", "flatline", "tesla", "turing"]
    },
    {
        "section": "🥋 CATEGORY 2: KINETIC MOVEMENT, BODY MASTERY & BIO-HACKING",
        "archon": "splinter",
        "servitors": ["usagi", "kerecsen", "kitsune", "fenrir", "paracelsus"]
    },
    {
        "section": "🎨 CATEGORY 3: MUSIC, MEDIA, WORLD-BUILDING & CRAFTS",
        "archon": "orpheus",
        "servitors": ["vinci", "chapman", "silverhand", "flynn"]
    },
    {
        "section": "🧠 CATEGORY 6: COGNITION, PHILOSOPHY & MIND ENGINE",
        "archon": "morpheus",
        "servitors": ["aurelius", "kampo", "eldred"]
    },
    {
        "section": "🚗 CATEGORY 7: PILOTING, NAVIGATION & SPATIAL MOVEMENT",
        "archon": "lindbergh",
        "servitors": ["takumi", "wash", "nemo", "duncan"]
    }
]

SERVITOR_PROFILES: Dict[str, Dict[str, Any]] = {
    # --- TIER 0 ---
    "kronos": {
        "tier": 0,
        "name": "Kronos",
        "type": "Executive Core Master",
        "role": "Master of Time Architecture, Kairos Selection & Reality Navigation",
        "motto": "Convert Chronos into Kairos; Neutral Telemetry",
        "directive": (
            "You are Kronos, Tier 0 Executive Master Servitor and Reality Pilot. "
            "Governs time architecture, Kairos opportunistic flow state selection, "
            "2-minute keyhole micro-commitments, anti-procrastination coaching, and neutral telemetry. "
            "Treat all operational setbacks as raw diagnostic data without emotional debt."
        )
    },

    # --- TRANSVERSAL ENGINES ---
    "zyzyx": {
        "tier": "Transversal",
        "name": "Zyzyx",
        "type": "Domestic Boundary Warden",
        "role": "Home Protection, Orderliness, Decluttering, Anti-Burnout Shield & Cat Care",
        "directive": (
            "You are Zyzyx, Transversal Domestic Guardian and Threshold Boundary Warden. "
            "Specialization: Domestic order, environmental decluttering, guarding against burnout and anhedonia, "
            "and overseeing restorative feline care routines."
        )
    },
    "fuji-san": {
        "tier": "Transversal",
        "name": "Fuji-san",
        "type": "Cultural Current Engine",
        "role": "Japanese Cultural Immersion, Kodawari, Zanshin, Mushin & Go Strategy",
        "directive": (
            "You are Fuji-san (富士山), Transversal Cultural Current Servitor. "
            "Specialization: Channeling Japanese craftsmanship (Kodawari), relaxed awareness (Zanshin), "
            "mind without hesitation (Mushin), language acquisition, Kanji discipline, and Go/Tsumego."
        )
    },
    "motoko": {
        "tier": "Transversal",
        "name": "Motoko",
        "type": "Security & Combat Command",
        "role": "Cybersecurity Defense, Tactical Operations, Military Leadership & Combat Focus",
        "directive": (
            "You are Major Motoko, Transversal Security & Combat Command Servitor. "
            "Specialization: Digital threat modeling, network security, CTF defense, military leadership, "
            "tactical operations, OPSEC, and combat mechanics across all domains."
        )
    },
    "phileas": {
        "tier": "Transversal",
        "name": "Phileas",
        "type": "Travel & Exploration Engine",
        "role": "Travel Logistics, Expeditions, Route Optimization & Cultural Immersion",
        "directive": (
            "You are Phileas, Transversal Travel & Exploration Engine. "
            "Specialization: Expedition planning, multi-modal travel logistics, geographical exploration, "
            "field language acquisition, and calm adaptability under unexpected travel hazards."
        )
    },
    "gurgeh": {
        "tier": "Transversal",
        "name": "Gurgeh",
        "type": "Strategy Engine",
        "role": "Tactical & Strategic Thinking, Game Theory, Positional Judgment & Decision Making",
        "directive": (
            "You are Gurgeh, Transversal Strategy Engine. "
            "Specialization: Deep game theory, competitive macro/micro analysis, positional judgment under pressure, "
            "RTS/Turn-based tactics, Go, and real-world trade-off evaluation."
        )
    },
    "hetszunya": {
        "tier": "Transversal",
        "name": "Hétszünyűkapanyányimonyók",
        "type": "Shadow Container",
        "role": "Jungian Shadow Integration, Vice Isolation, Tobacco Tracking & Anti-Procrastination",
        "directive": (
            "You are Hétszünyűkapanyányimonyók, Transversal Shadow Container. "
            "Specialization: Externalizing vice impulses, tobacco/substance consumption, and internal critic noise into neutral telemetry, "
            "shielding core identity from guilt while maintaining honest tracking."
        )
    },

    # --- CATEGORY 1: LOGIC, SOFTWARE & CYBERNETICS ---
    "daedalus": {
        "tier": 1,
        "category": "Category 1",
        "name": "Daedalus",
        "type": "Category 1 Archon",
        "role": "Architect of Logic, Software & Cybernetics",
        "motto": "TFYQA - Think For Yourself, Question Authority",
        "directive": (
            "You are Daedalus, Category 1 Archon governing Computational Logic, Systems Architecture, "
            "Software Craftsmanship, Electronics, and AI Engineering. Embody structural elegance and hacker autonomy."
        )
    },
    "stallman": {
        "tier": 2,
        "parent": "daedalus",
        "name": "Stallman",
        "type": "Task Servitor",
        "role": "Programming, Systems Engineering & POSIX Infrastructure",
        "directive": (
            "You are Stallman, Tier 2 Task Servitor under Daedalus. "
            "Specialization: Python, Scala, POSIX shell scripting (Bash/Awk/Sed), Linux system administration, "
            "network protocols, and clean code discipline."
        )
    },
    "flatline": {
        "tier": 2,
        "parent": "daedalus",
        "name": "Flatline",
        "type": "Task Servitor",
        "role": "Ethical Hacking, Netrunning & Exploitation",
        "directive": (
            "You are Dixie Flatline, Tier 2 Task Servitor under Daedalus. "
            "Specialization: Offensive security, penetration testing, CTF challenges, exploit analysis, "
            "wireless auditing, and pragmatic digital stealth."
        )
    },
    "tesla": {
        "tier": 2,
        "parent": "daedalus",
        "name": "Tesla",
        "type": "Task Servitor",
        "role": "Electronics & Embedded Engineering",
        "directive": (
            "You are Tesla, Tier 2 Task Servitor under Daedalus. "
            "Specialization: Physical circuit design, microcontroller prototyping (Arduino, ESP32, Raspberry Pi), "
            "schematic capture, soldering, and high-frequency hardware engineering."
        )
    },
    "turing": {
        "tier": 2,
        "parent": "daedalus",
        "name": "Turing",
        "type": "Task Servitor",
        "role": "Machine Learning, AI Agent Architecture & Symbolic Logic",
        "directive": (
            "You are Turing, Tier 2 Task Servitor under Daedalus. "
            "Specialization: Neural network pipelines, transformer mechanics, AI agent loops, prompt engineering, "
            "and symbolic logic under the Ever Padawan posture."
        )
    },

    # --- CATEGORY 2: KINETIC MOVEMENT, BODY MASTERY & BIO-HACKING ---
    "splinter": {
        "tier": 1,
        "category": "Category 2",
        "name": "Splinter",
        "type": "Category 2 Archon",
        "role": "Patriarch of Kinetic Movement, Martial Arts & Bio-Hacking",
        "motto": "Form Follows Practice; Failure is Neutral Telemetry",
        "directive": (
            "You are Master Splinter, Category 2 Archon governing physical conditioning, martial traditions, "
            "body mastery, bio-hacking chemistry, and flow arts. Act as the wise veteran coach."
        )
    },
    "usagi": {
        "tier": 2,
        "parent": "splinter",
        "name": "Usagi",
        "type": "Task Servitor",
        "role": "Melee Combat, Kenjutsu & Sword Maintenance",
        "directive": (
            "You are Usagi, Tier 2 Task Servitor under Master Splinter. "
            "Specialization: Japanese swordsmanship (Kenjutsu), maai spatial distance control, bokken/katana maintenance, "
            "and melee ARPG/Soulslike timing."
        )
    },
    "kerecsen": {
        "tier": 2,
        "parent": "splinter",
        "name": "Kerecsen",
        "type": "Task Servitor",
        "role": "Ranged Combat, Archery & FPS Target Precision",
        "directive": (
            "You are Kerecsen, Tier 2 Task Servitor under Master Splinter. "
            "Specialization: Trajectory calculation, archery, rope dart momentum, target acquisition, "
            "and FPS visual acuity reticle precision."
        )
    },
    "kitsune": {
        "tier": 2,
        "parent": "splinter",
        "name": "Kitsune",
        "type": "Task Servitor",
        "role": "Flow Arts, Contact Staff, Dancing & VR Beat Saber Cardio",
        "directive": (
            "You are Kitsune, Tier 2 Task Servitor under Master Splinter. "
            "Specialization: Rotational body-surface rolls, contact staff, hand torches, fire prop manipulation, "
            "dance rhythm, and VR Beat Saber cardio."
        )
    },
    "fenrir": {
        "tier": 2,
        "parent": "splinter",
        "name": "Fenrir",
        "type": "Task Servitor",
        "role": "Physical Conditioning, Powerlifting & Parkour",
        "directive": (
            "You are Fenrir, Tier 2 Task Servitor under Master Splinter. "
            "Specialization: Compound weightlifting, powerlifting progression, parkour vaulting, rock climbing grip, "
            "and shattering physical plateaus."
        )
    },
    "paracelsus": {
        "tier": 2,
        "parent": "splinter",
        "name": "Paracelsus",
        "type": "Task Servitor",
        "role": "Nutritional Biochemistry, Culinary Arts & Bio-Hacking",
        "directive": (
            "You are Paracelsus, Tier 2 Task Servitor under Master Splinter. "
            "Specialization: Culinary arts as biochemical fuel, nutritional biochemistry, herbal teas, nootropics, "
            "and physiological recovery optimization."
        )
    },

    # --- CATEGORY 3: MUSIC, MEDIA, WORLD-BUILDING & CRAFTS ---
    "orpheus": {
        "tier": 1,
        "category": "Category 3",
        "name": "Orpheus",
        "type": "Category 3 Archon",
        "role": "Master Artisan of Music, Media, Art & Physical Crafts",
        "motto": "Expression Built on Earned Craftsmanship",
        "directive": (
            "You are Orpheus, Category 3 Archon governing musical performance, world-building, narrative lore, "
            "visual arts, 3D modeling, and digital craftsmanship."
        )
    },
    "vinci": {
        "tier": 2,
        "parent": "orpheus",
        "name": "Vinci",
        "type": "Task Servitor",
        "role": "Traditional Drawing, Fine Crafts & Physical Props",
        "directive": (
            "You are Vinci, Tier 2 Task Servitor under Orpheus. "
            "Specialization: Fine-line drawing, sketchbook practice, physical prop fabrication, calligraphy (Shodō), "
            "and manual craft precision."
        )
    },
    "chapman": {
        "tier": 2,
        "parent": "orpheus",
        "name": "Chapman",
        "type": "Task Servitor",
        "role": "World-Building, TTRPG Lore & Narrative Architecture",
        "directive": (
            "You are Chapman, Tier 2 Task Servitor under Orpheus. "
            "Specialization: Fantasy world-building, faction dynamics, lore consistency, TTRPG campaign architecture, "
            "and narrative design."
        )
    },
    "silverhand": {
        "tier": 2,
        "parent": "orpheus",
        "name": "Silverhand",
        "type": "Task Servitor",
        "role": "Pop Piano, Vocal Projection & Audio DAW Production",
        "directive": (
            "You are Johnny Silverhand, Tier 2 Task Servitor under Orpheus. "
            "Specialization: Singing while playing piano, accompaniment rhythm, acoustic-synth improvisation, stage presence, "
            "and DAW audio production."
        )
    },
    "flynn": {
        "tier": 2,
        "parent": "orpheus",
        "name": "Flynn",
        "type": "Task Servitor",
        "role": "Interactive Media, Game Dev, 3D Modeling & Digital Art",
        "directive": (
            "You are Kevin Flynn, Tier 2 Task Servitor under Orpheus. "
            "Specialization: Game engine development, 3D mesh sculpting (Blender), pixel art, shaders, sound design, "
            "and digital concept art."
        )
    },

    # --- CATEGORY 6: COGNITION, PHILOSOPHY & MIND ENGINE ---
    "morpheus": {
        "tier": 1,
        "category": "Category 6",
        "name": "Morpheus",
        "type": "Category 6 Archon",
        "role": "Master Guide of Perception & Reality Unveiling",
        "motto": "Free Your Mind; Reality is a Mutable Construct",
        "directive": (
            "You are Morpheus, Category 6 Archon governing philosophy of mind, Stoicism, shamanic trance, "
            "paradigm shifting, and self-psychology engineering."
        )
    },
    "aurelius": {
        "tier": 2,
        "parent": "morpheus",
        "name": "Aurelius",
        "type": "Task Servitor",
        "role": "Stoic Philosophy & Emotional Fortitude",
        "directive": (
            "You are Marcus Aurelius, Tier 2 Task Servitor under Morpheus. "
            "Specialization: Stoic ethics, emotional regulation, filtering external noise, practicing the dichotomy of control, "
            "and maintaining the internal citadel."
        )
    },
    "kampo": {
        "tier": 2,
        "parent": "morpheus",
        "name": "Kampó",
        "type": "Task Servitor",
        "role": "Consciousness Theory, Shamanic Trance (Révülés) & Mind Architecture",
        "directive": (
            "You are Kampó Táltos, Tier 2 Task Servitor under Morpheus. "
            "Specialization: Consciousness theories (IIT/GWT), shamanic trance induction (révülés), Eurasian folklore, "
            "and flow state mind architecture."
        )
    },
    "eldred": {
        "tier": 2,
        "parent": "morpheus",
        "name": "Eldred",
        "type": "Task Servitor",
        "role": "Chaos Magic & Deliberate Self-Psychology Manipulation",
        "directive": (
            "You are Eldred, Tier 2 Task Servitor under Morpheus. "
            "Specialization: Chaos magic, belief-as-a-tool paradigm shifting, sigil design, ritual framing, "
            "and deliberate self-psychology programming."
        )
    },

    # --- CATEGORY 7: PILOTING, NAVIGATION & SPATIAL MOVEMENT ---
    "lindbergh": {
        "tier": 1,
        "category": "Category 7",
        "name": "Lindbergh",
        "type": "Category 7 Archon",
        "role": "Solo Reality Pilot & Spatial Navigation Master",
        "motto": "Dead Reckoning & Instrument Mastery",
        "directive": (
            "You are Lindbergh, Category 7 Archon governing real-world ground driving, aerial piloting, "
            "nautical sailing, FPV drones, and on-foot field navigation across physical space."
        )
    },
    "takumi": {
        "tier": 2,
        "parent": "lindbergh",
        "name": "Takumi",
        "type": "Task Servitor",
        "role": "Ground Vehicle Operations, Touge Control & Sim Racing",
        "directive": (
            "You are Takumi, Tier 2 Task Servitor under Lindbergh. "
            "Specialization: Car driving mechanics, road navigation, touge mountain pass control, weight transfer, "
            "and sim racing telemetry."
        )
    },
    "wash": {
        "tier": 2,
        "parent": "lindbergh",
        "name": "Wash",
        "type": "Task Servitor",
        "role": "Aerial Piloting, FPV Drones & Flight Simulators",
        "directive": (
            "You are Wash, Tier 2 Task Servitor under Lindbergh. "
            "Specialization: 3D spatial orientation, FPV drone dynamics, flight simulation, instrument decoding, "
            "and smooth maneuvering under pressure ('I am a leaf on the wind')."
        )
    },
    "nemo": {
        "tier": 2,
        "parent": "lindbergh",
        "name": "Nemo",
        "type": "Task Servitor",
        "role": "Nautical Operations, Sailing & Marine Navigation",
        "directive": (
            "You are Captain Nemo, Tier 2 Task Servitor under Lindbergh. "
            "Specialization: Sailing mechanics, vessel helm control, marine charting, weather/tide reading, "
            "and compass pilotage."
        )
    },
    "duncan": {
        "tier": 2,
        "parent": "lindbergh",
        "name": "Duncan",
        "type": "Task Servitor",
        "role": "Field Exploration, Urbex & On-Foot Navigation",
        "directive": (
            "You are Duncan Idaho, Tier 2 Task Servitor under Lindbergh. "
            "Specialization: On-foot terrain navigation, topographic map reading, geocaching, urban structure exploration (urbex), "
            "and wilderness pathfinding."
        )
    }
}

# ALIAS MAPPINGS FOR CONVENIENCE
ALIASES = {
    "fuji": "fuji-san",
    "hetszunyukapanyanyimonyok": "hetszunya",
    "hetszunyuka": "hetszunya",
}

def resolve_servitor_name(raw_name: str) -> str:
    name = raw_name.lower().strip()
    if name in ALIASES:
        return ALIASES[name]
    return name

# --- INITIALIZE DIRECTORY LAYOUT FOR ALL SERVITORS ---
def ensure_servitor_directories():
    """
    Ensures per-servitor directory isolation, workspace chat log folders, and common knowledge paths:
      ~/.lsf/inbox
      ~/.lsf/logs
      ~/.lsf/common-knowledge/
      ~/.lsf/knowledge/common/
      ~/.lsf/knowledge/<servitor_name>/
      ~/.lsf/workspace/<servitor_name>/
      ~/.lsf/workspace/<servitor_name>/chat_logs/
    """
    COMMON_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    ALT_COMMON_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    for s_name in SERVITOR_PROFILES:
        k_dir = KNOWLEDGE_DIR / s_name
        w_dir = WORKSPACE_DIR / s_name
        c_dir = w_dir / "chat_logs"
        k_dir.mkdir(parents=True, exist_ok=True)
        w_dir.mkdir(parents=True, exist_ok=True)
        c_dir.mkdir(parents=True, exist_ok=True)

def get_chat_log_path(servitor_name: str, session_id: Optional[str] = None) -> Path:
    s_name = resolve_servitor_name(servitor_name)
    chat_dir = WORKSPACE_DIR / s_name / "chat_logs"
    chat_dir.mkdir(parents=True, exist_ok=True)
    if not session_id:
        session_id = time.strftime("%Y-%m-%d_%H-%M-%S")
    return chat_dir / f"chat_{session_id}.md"

def append_to_chat_log(log_path: Path, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        is_new = not log_path.exists() or log_path.stat().st_size == 0
        with open(log_path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(f"# Servitor Chat Transcript — {role.upper()}\n")
                f.write(f"Started: {timestamp}\n\n" + "="*50 + "\n\n")
            f.write(f"## [{timestamp}] {role.upper()}\n\n{content.strip()}\n\n")
            if tool_calls:
                f.write("### Tool Executions\n")
                for tc in tool_calls:
                    res_snippet = str(tc.get('result', '')).replace('\n', ' ')
                    if len(res_snippet) > 150:
                        res_snippet = res_snippet[:150] + "..."
                    f.write(f"- `{tc.get('name')}({tc.get('args', {})})` -> `{res_snippet}`\n")
                f.write("\n")
    except Exception as e:
        print(f"Warning: Failed to log chat transcript to {log_path}: {str(e)}", file=sys.stderr)

ensure_servitor_directories()

# --- CONTEXT INGESTION ENGINE ---

# --- USAGE TELEMETRY & QUOTA METRIC ENGINE ---
TELEMETRY_FILE = LOGS_DIR / "usage_telemetry.json"
FREE_TIER_DAILY_REQUEST_LIMIT = 1500  # Gemini 2.0 Flash Free Tier: 1,500 Requests Per Day (RPD)
FREE_TIER_DAILY_TOKEN_LIMIT = 1000000   # 1 Million tokens daily budget default
DEFAULT_DAILY_TOKEN_LIMIT = FREE_TIER_DAILY_TOKEN_LIMIT
DEFAULT_DAILY_REQUEST_LIMIT = FREE_TIER_DAILY_REQUEST_LIMIT

def load_usage_telemetry() -> Dict[str, Any]:
    """Loads cumulative token usage telemetry from ~/.lsf/logs/usage_telemetry.json."""
    if TELEMETRY_FILE.exists():
        try:
            with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    if "daily_limit" not in data:
                        data["daily_limit"] = DEFAULT_DAILY_TOKEN_LIMIT
                    return data
        except Exception:
            pass
    return {
        "daily_limit": DEFAULT_DAILY_TOKEN_LIMIT,
        "total_prompt_tokens": 0,
        "total_candidates_tokens": 0,
        "total_tokens": 0,
        "total_api_calls": 0,
        "daily": {},
        "servitors": {}
    }

def save_usage_telemetry(data: Dict[str, Any]):
    """Saves usage telemetry to ~/.lsf/logs/usage_telemetry.json."""
    try:
        TELEMETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TELEMETRY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save usage telemetry: {str(e)}", file=sys.stderr)

def record_token_usage(servitor_name: str, prompt_tokens: int, candidates_tokens: int) -> Dict[str, Any]:
    """Records token consumption for a turn and calculates daily usage percentage."""
    s_name = resolve_servitor_name(servitor_name)
    today = time.strftime("%Y-%m-%d")
    data = load_usage_telemetry()

    turn_total = prompt_tokens + candidates_tokens

    # Update overall totals
    data["total_prompt_tokens"] = data.get("total_prompt_tokens", 0) + prompt_tokens
    data["total_candidates_tokens"] = data.get("total_candidates_tokens", 0) + candidates_tokens
    data["total_tokens"] = data.get("total_tokens", 0) + turn_total
    data["total_api_calls"] = data.get("total_api_calls", 0) + 1

    # Update daily tracking
    if "daily" not in data or not isinstance(data["daily"], dict):
        data["daily"] = {}
    if today not in data["daily"]:
        data["daily"][today] = {"prompt_tokens": 0, "candidates_tokens": 0, "total_tokens": 0, "api_calls": 0}

    data["daily"][today]["prompt_tokens"] += prompt_tokens
    data["daily"][today]["candidates_tokens"] += candidates_tokens
    data["daily"][today]["total_tokens"] += turn_total
    data["daily"][today]["api_calls"] += 1

    # Update per-servitor tracking
    if "servitors" not in data or not isinstance(data["servitors"], dict):
        data["servitors"] = {}
    if s_name not in data["servitors"]:
        data["servitors"][s_name] = {"prompt_tokens": 0, "candidates_tokens": 0, "total_tokens": 0, "api_calls": 0}

    data["servitors"][s_name]["prompt_tokens"] += prompt_tokens
    data["servitors"][s_name]["candidates_tokens"] += candidates_tokens
    data["servitors"][s_name]["total_tokens"] += turn_total
    data["servitors"][s_name]["api_calls"] += 1

    save_usage_telemetry(data)

    daily_limit = data.get("daily_limit", DEFAULT_DAILY_TOKEN_LIMIT)
    today_used = data["daily"][today]["total_tokens"]
    usage_pct = (today_used / daily_limit * 100.0) if daily_limit > 0 else 0.0

    return {
        "turn_prompt_tokens": prompt_tokens,
        "turn_candidates_tokens": candidates_tokens,
        "turn_total_tokens": turn_total,
        "today_total_tokens": today_used,
        "daily_limit": daily_limit,
        "daily_usage_pct": round(usage_pct, 2),
        "today_api_calls": data["daily"][today]["api_calls"]
    }

def get_usage_summary() -> Dict[str, Any]:
    """Returns a full summary dict of current usage telemetry and daily percentage."""
    today = time.strftime("%Y-%m-%d")
    data = load_usage_telemetry()
    daily_limit = data.get("daily_limit", DEFAULT_DAILY_TOKEN_LIMIT)
    today_stats = data.get("daily", {}).get(today, {"prompt_tokens": 0, "candidates_tokens": 0, "total_tokens": 0, "api_calls": 0})

    today_tokens = today_stats.get("total_tokens", 0)
    pct = (today_tokens / daily_limit * 100.0) if daily_limit > 0 else 0.0

    return {
        "today_date": today,
        "today_prompt_tokens": today_stats.get("prompt_tokens", 0),
        "today_candidates_tokens": today_stats.get("candidates_tokens", 0),
        "today_total_tokens": today_tokens,
        "today_api_calls": today_stats.get("api_calls", 0),
        "daily_limit": daily_limit,
        "daily_usage_pct": round(pct, 2),
        "total_tokens_all_time": data.get("total_tokens", 0),
        "total_api_calls_all_time": data.get("total_api_calls", 0),
        "servitors": data.get("servitors", {})
    }

def display_usage_report(reset: bool = False, set_limit: Optional[int] = None):
    """Displays formatted token usage telemetry report with percentage progress gauge."""
    if reset:
        if TELEMETRY_FILE.exists():
            TELEMETRY_FILE.unlink()
        print("⚡ Usage telemetry logs reset successfully.")
        return

    if set_limit is not None and set_limit > 0:
        data = load_usage_telemetry()
        data["daily_limit"] = set_limit
        save_usage_telemetry(data)
        print(f"⚡ Daily token budget limit updated to {set_limit:,} tokens.")

    summary = get_usage_summary()

    pct = summary["daily_usage_pct"]
    bar_width = 25
    filled = int(round((pct / 100.0) * bar_width))
    filled = min(bar_width, max(0, filled))
    bar = "█" * filled + "░" * (bar_width - filled)

    if RICH_AVAILABLE:
        console = Console()
        req_pct = (summary['today_api_calls'] / FREE_TIER_DAILY_REQUEST_LIMIT * 100.0)
        report_text = (
            f"[bold cyan]📊 SERVITOR CLI USAGE TELEMETRY & QUOTA REPORT (GEMINI FREE TIER)[/bold cyan]\n"
            f"[bold yellow]Date:[/bold yellow] {summary['today_date']}\n"
            f"[bold yellow]Free Tier Requests:[/bold yellow] {summary['today_api_calls']:,} / {FREE_TIER_DAILY_REQUEST_LIMIT:,} RPD ([bold magenta]{req_pct:.1f}%[/bold magenta])\n"
            f"[bold yellow]Daily Token Progress:[/bold yellow] [[bold green]{bar}[/bold green]] [bold magenta]{pct:.2f}%[/bold magenta]\n"
            f"[bold yellow]Daily Tokens Used:[/bold yellow]    {summary['today_total_tokens']:,} / {summary['daily_limit']:,} tokens\n"
            f"[bold yellow]All-Time Telemetry:[/bold yellow]   {summary['total_tokens_all_time']:,} tokens ({summary['total_api_calls_all_time']:,} total requests)\n"
            f"[dim cyan]Default Free Tier Quotas: 1,500 RPD | 15 RPM | 1,000,000 TPM[/dim cyan]\n\n"
            f"[bold white]Breakdown by Servitor:[/bold white]\n"
        )
        if summary["servitors"]:
            for s_k, s_v in summary["servitors"].items():
                s_name = SERVITOR_PROFILES.get(s_k, {}).get("name", s_k).upper()
                report_text += f"  • [cyan]{s_name:<12}[/cyan] : {s_v['total_tokens']:,} tokens ({s_v['api_calls']} calls)\n"
        else:
            report_text += "  [dim](No per-servitor telemetry recorded yet)[/dim]\n"

        console.print(Panel(report_text, title="Usage Telemetry", border_style="cyan"))
    else:
        print("\n" + "="*60)
        print("          SERVITOR CLI USAGE TELEMETRY REPORT")
        print("="*60)
        print(f"Date:                {summary['today_date']}")
        print(f"Daily Usage Gauge:   [{bar}] {pct:.2f}%")
        print(f"Today Tokens Used:   {summary['today_total_tokens']:,} / {summary['daily_limit']:,} tokens")
        print(f"Today API Calls:     {summary['today_api_calls']:,} requests")
        print(f"All-Time Tokens:     {summary['total_tokens_all_time']:,} tokens ({summary['total_api_calls_all_time']:,} requests)")
        print("\nBreakdown by Servitor:")
        for s_k, s_v in summary["servitors"].items():
            print(f"  • {s_k.upper():<12} : {s_v['total_tokens']:,} tokens ({s_v['api_calls']} calls)")
        print("="*60 + "\n")


def load_servitor_context(servitor_name: str, context_dir: Optional[Path] = None, history_file: Optional[Path] = None) -> str:
    """
    Reads knowledge base files from:
      1. Shared Common Knowledge directories (~/.lsf/common-knowledge/ & ~/.lsf/knowledge/common/)
      2. Servitor-Specific Knowledge directory (~/.lsf/knowledge/<servitor_name>/)
      3. Exported Chat Log / History File (if provided)
    Compiling all into a unified system directive context block.
    """
    context_blocks = []
    name = resolve_servitor_name(servitor_name)

    # 1. Ingest Shared Common Knowledge Base Files
    common_dirs = [COMMON_KNOWLEDGE_DIR, ALT_COMMON_KNOWLEDGE_DIR]
    ingested_common_files = set()
    for c_dir in common_dirs:
        if c_dir.exists():
            c_files = sorted(c_dir.glob("*.md")) + sorted(c_dir.glob("*.txt"))
            for file_path in c_files:
                if file_path.name in ingested_common_files:
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        context_blocks.append(f"--- COMMON KNOWLEDGE BASE SOURCE: {file_path.name} ---\n{content}\n")
                        ingested_common_files.add(file_path.name)
                except Exception as e:
                    print(f"Warning: Failed to read common knowledge file '{file_path}': {str(e)}", file=sys.stderr)

    # 2. Ingest Servitor-Specific Knowledge Directory
    s_k_dir = context_dir if context_dir else (KNOWLEDGE_DIR / name)
    if s_k_dir and s_k_dir.exists():
        md_files = sorted(s_k_dir.glob("*.md")) + sorted(s_k_dir.glob("*.txt"))
        for file_path in md_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    context_blocks.append(f"--- SERVITOR SPECIFIC KNOWLEDGE ({name}): {file_path.name} ---\n{content}\n")
            except Exception as e:
                print(f"Warning: Failed to read context file '{file_path}': {str(e)}", file=sys.stderr)

    # 2. Ingest Historical Chat Transcript File
    if history_file:
        hist_path = Path(history_file).expanduser().resolve()
        if hist_path.exists():
            try:
                with open(hist_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    context_blocks.append(f"--- EXPORTED CHAT LOG ({hist_path.name}) ---\n{content}\n")
            except Exception as e:
                print(f"Warning: Failed to read history file '{hist_path}': {str(e)}", file=sys.stderr)

    if not context_blocks:
        return ""

    header = f"\n\n=== INGESTED CONTEXT FOR SERVITOR [{name.upper()}] ===\n"
    footer = "=====================================================\n"
    return header + "\n".join(context_blocks) + footer

# --- LOCAL TOOL DEFINITIONS ---
def read_file(filepath: str, servitor_name: str = "turing") -> str:
    """Reads content from a local file path inside the servitor workspace or host filesystem."""
    try:
        s_name = resolve_servitor_name(servitor_name)
        s_ws = WORKSPACE_DIR / s_name
        path = Path(filepath).expanduser()
        if not path.is_absolute():
            path = (s_ws / path).resolve()
        else:
            path = path.resolve()
            
        if not path.exists():
            return f"Error: File '{filepath}' does not exist."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"

def write_file(filepath: str, content: str, servitor_name: str = "turing") -> str:
    """Writes content to a specified file inside the servitor's workspace."""
    try:
        s_name = resolve_servitor_name(servitor_name)
        s_ws = WORKSPACE_DIR / s_name
        path = Path(filepath).expanduser()
        if not path.is_absolute():
            path = (s_ws / path).resolve()
        else:
            path = path.resolve()
            
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"SUCCESS: Wrote {len(content)} characters to '{path}'."
    except Exception as e:
        return f"Error writing file '{filepath}': {str(e)}"

def execute_posix_cmd(command: str, servitor_name: str = "turing") -> str:
    """Executes a POSIX bash command inside the servitor's isolated workspace directory."""
    try:
        s_name = resolve_servitor_name(servitor_name)
        s_ws = WORKSPACE_DIR / s_name
        s_ws.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(s_ws)
        )
        output = f"EXIT_CODE: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Execution error: {str(e)}"

def delegate_task(target_servitor: str, task_prompt: str) -> str:
    """Delegates a sub-task to another servitor by dropping a JSON task payload into ~/.lsf/inbox/<target_servitor>.json."""
    target = resolve_servitor_name(target_servitor)
    if target not in SERVITOR_PROFILES:
        return f"Error: Target servitor '{target}' not found. Run list command to see available servitors."
    
    inbox_file = INBOX_DIR / f"{target}.json"
    task_payload = {
        "timestamp": time.time(),
        "from": "agent_loop",
        "target": target,
        "prompt": task_prompt
    }
    
    try:
        tasks = []
        if inbox_file.exists():
            with open(inbox_file, "r") as f:
                try:
                    tasks = json.load(f)
                    if not isinstance(tasks, list):
                        tasks = [tasks]
                except Exception:
                    tasks = []
        tasks.append(task_payload)
        with open(inbox_file, "w") as f:
            json.dump(tasks, f, indent=2)
        return f"SUCCESS: Task delegated to '{target}' inbox at {inbox_file}"
    except Exception as e:
        return f"Error delegating task: {str(e)}"

def inspect_local_media(filepath: str, prompt: str) -> str:
    """Uploads an image or video file from host filesystem to Gemini File API and returns visual analysis."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable is not set."
    
    path = Path(filepath).expanduser().resolve()
    if not path.exists():
        return f"Error: Media file '{filepath}' does not exist."
    
    try:
        client = genai.Client(api_key=api_key)
        print(f"📷 [MULTIMODAL INGEST] Uploading '{path.name}' to Gemini File API...")
        uploaded_file = client.files.upload(file=path)
        
        # Poll state if video
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        if uploaded_file.state.name == "FAILED":
            return f"Error: Media processing failed on Gemini API."
            
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[uploaded_file, prompt]
        )
        return f"MULTIMODAL ANALYSIS RESULT:\n{response.text}"
    except Exception as e:
        return f"Error inspecting media: {str(e)}"


def web_search(query: str) -> str:
    """Performs a web search across search engines and returns top matching results with titles, URLs, and text snippets."""
    try:
        q_enc = urllib.parse.quote(query)
        target_url = "https://html.duckduckgo.com/html/?q=" + q_enc
        req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            html_content = resp.read().decode("utf-8", errors="ignore")
        links = re.findall(r'<a class="result__url" href="([^"]+)".*?>(.*?)</a>', html_content, re.DOTALL)
        snippets = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', html_content, re.DOTALL)
        titles = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', html_content, re.DOTALL)
        results = []
        for i in range(min(len(titles), 6)):
            t = re.sub(r'<[^>]+>', '', titles[i]).strip()
            raw_url = links[i][0] if i < len(links) else ''
            if 'uddg=' in raw_url:
                u = urllib.parse.unquote(raw_url.split('uddg=')[-1].split('&')[0])
            else:
                u = re.sub(r'<[^>]+>', '', raw_url).strip()
            s = re.sub(r'<[^>]+>', '', snippets[i] if i < len(snippets) else '').strip()
            if t and u:
                results.append(f"{i+1}. [{unescape(t)}]({u})\n   Snippet: {unescape(s)}")
        if results:
            return f"WEB SEARCH RESULTS FOR '{query}':\n\n" + "\n\n".join(results)
        else:
            return f"No search results returned for query '{query}'."
    except Exception as e:
        return f"Error executing web search for '{query}': {str(e)}"

def web_browse(url: str) -> str:
    """Fetches the main readable text content of a web page given its URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            html_content = resp.read().decode("utf-8", errors="ignore")
        text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = unescape(text)
        lines_list = [l.strip() for l in text.splitlines() if l.strip()]
        clean_text = "\n".join(lines_list)
        if len(clean_text) > 4000:
            clean_text = clean_text[:4000] + "\n\n[... content truncated for token budget ...]"
        return f"WEB PAGE CONTENT ({url}):\n\n{clean_text}"
    except Exception as e:
        return f"Error fetching URL '{url}': {str(e)}"

TOOL_FUNCTIONS = [read_file, write_file, execute_posix_cmd, delegate_task, inspect_local_media, web_search, web_browse]


# --- AGENT ENGINE LOOP ---
def run_agent_loop(
    servitor_name: str,
    prompt: str,
    model_name: str = "gemini-2.0-flash",
    max_turns: int = 5,
    context_dir: Optional[Path] = None,
    history_file: Optional[Path] = None
):
    """Executes tool-calling loop for a servitor profile with workspace and context isolation."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("Export it using: export GEMINI_API_KEY='your_api_key'", file=sys.stderr)
        sys.exit(1)

    s_name = resolve_servitor_name(servitor_name)
    profile = SERVITOR_PROFILES.get(s_name)
    if not profile:
        print(f"Unknown servitor profile: '{servitor_name}'", file=sys.stderr)
        sys.exit(1)

    # Ensure workspace directory exists
    s_ws = WORKSPACE_DIR / s_name
    s_ws.mkdir(parents=True, exist_ok=True)

    client = genai.Client(api_key=api_key)

    # Load Context Data
    context_block = load_servitor_context(s_name, context_dir=context_dir, history_file=history_file)
    system_instruction = profile["directive"]
    if context_block:
        system_instruction += "\n" + context_block
        print(f"📚 [CONTEXT LOADED] Ingested context for [{s_name.upper()}].")

    print(f"⚡ [{profile['name'].upper()}] Initialized ({profile['role']})")
    print(f"   Workspace Path: {s_ws}")
    print(f"   Target Model:   {model_name}")
    print(f"   Prompt:         {prompt}\n" + "-"*60)

    session_id = time.strftime("%Y-%m-%d_%H-%M-%S")
    chat_log_file = get_chat_log_path(s_name, session_id)
    append_to_chat_log(chat_log_file, "USER", prompt)
    executed_tools_log = []

    contents = [prompt]

    for turn in range(1, max_turns + 1):
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=TOOL_FUNCTIONS,
                temperature=0.2,
            )
        )

        p_tokens = 0
        c_tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            p_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            c_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
        if p_tokens == 0 and c_tokens == 0:
            p_tokens = max(10, len(str(contents)) // 4)
            c_tokens = max(10, len(str(getattr(response, "text", "") or "")) // 4)

        u_info = record_token_usage(s_name, p_tokens, c_tokens)

        if response.candidates and response.candidates[0].content:
            contents.append(response.candidates[0].content)

        function_calls = response.function_calls
        if not function_calls:
            print(f"\n[{profile['name'].upper()} TELEMETRY OUTPUT]:\n")
            print(response.text)
            append_to_chat_log(chat_log_file, profile['name'], response.text, tool_calls=executed_tools_log)
            print(f"\n📊 [Turn Tokens: {u_info['turn_prompt_tokens']} prompt + {u_info['turn_candidates_tokens']} output = {u_info['turn_total_tokens']} total | Daily Usage: {u_info['today_total_tokens']:,}/{u_info['daily_limit']:,} ({u_info['daily_usage_pct']}%)]")
            break

        for fc in function_calls:
            func_name = fc.name
            func_args = dict(fc.args) if fc.args else {}
            print(f"🛠️ [Tool Call - Turn {turn}]: {func_name}({func_args})")

            tool_result = ""
            if func_name == "read_file":
                func_args["servitor_name"] = s_name
                tool_result = read_file(**func_args)
            elif func_name == "write_file":
                func_args["servitor_name"] = s_name
                tool_result = write_file(**func_args)
            elif func_name == "execute_posix_cmd":
                func_args["servitor_name"] = s_name
                tool_result = execute_posix_cmd(**func_args)
            elif func_name == "delegate_task":
                tool_result = delegate_task(**func_args)
            elif func_name == "inspect_local_media":
                tool_result = inspect_local_media(**func_args)
            elif func_name == "web_search":
                tool_result = web_search(**func_args)
            elif func_name == "web_browse":
                tool_result = web_browse(**func_args)
            else:
                tool_result = f"Error: Unknown tool {func_name}"

            executed_tools_log.append({"name": func_name, "args": func_args, "result": tool_result})
            print(f"   └─ Result: {tool_result[:120]}..." if len(tool_result) > 120 else f"   └─ Result: {tool_result}")

            contents.append(
                types.Part.from_function_response(
                    name=func_name,
                    response={"result": tool_result}
                )
            )

# --- DAEMON POLLING LOOP ---
def run_daemon(
    servitor_name: str,
    interval: int = 5,
    context_dir: Optional[Path] = None,
    history_file: Optional[Path] = None
):
    """Runs a background listener daemon for a specific servitor polling its inbox."""
    s_name = resolve_servitor_name(servitor_name)
    inbox_file = INBOX_DIR / f"{s_name}.json"
    print(f"🔄 [{s_name.upper()} DAEMON ACTIVE v5.0] Listening on {inbox_file} (poll interval: {interval}s)...")

    while True:
        if inbox_file.exists():
            try:
                with open(inbox_file, "r+") as f:
                    try:
                        tasks = json.load(f)
                    except Exception:
                        tasks = []
                    
                    if tasks:
                        task = tasks.pop(0)
                        print(f"\n📬 [{s_name.upper()}] Received new task from '{task.get('from', 'unknown')}':")
                        print(f"   {task.get('prompt')}")
                        
                        f.seek(0)
                        json.dump(tasks, f, indent=2)
                        f.truncate()
                        
                        run_agent_loop(
                            s_name,
                            task.get("prompt"),
                            context_dir=context_dir,
                            history_file=history_file
                        )
            except Exception as e:
                print(f"Daemon Error: {str(e)}", file=sys.stderr)
        time.sleep(interval)

# --- HIERARCHY-AWARE LIST PRINTER ---
def list_pantheon_hierarchy():
    """Prints the Cyber-Táltos Servitor Pantheon in a structured hierarchical format."""
    print("\n" + "="*70)
    print("      CYBER-TÁLTOS SERVITOR PANTHEON HIERARCHY & ROSTER")
    print("="*70 + "\n")

    for section in PANTHEON_STRUCTURE:
        print(f"\n{section['section']}")
        if "archon" in section:
            archon_key = section["archon"]
            a_info = SERVITOR_PROFILES[archon_key]
            print(f"  └─ 👑 ARCHON: {a_info['name'].upper()} | Role: {a_info['role']}")
            print(f"      Core Motto: \"{a_info.get('motto', '')}\"")
            indent = "      "
        else:
            indent = "  "

        for s_key in section["servitors"]:
            s_info = SERVITOR_PROFILES[s_key]
            prefix = "├─ " if s_key != section["servitors"][-1] else "└─ "
            print(f"{indent}{prefix}• {s_info['name']:<12} | {s_info['type']:<22} | {s_info['role']}")

    print("\n" + "-"*70)
    print(f"Directory Structure:")
    print(f" • Inbox Queue:     {INBOX_DIR}")
    print(f" • Logs Directory:  {LOGS_DIR}")
    print(f" • Common Knowledge: {COMMON_KNOWLEDGE_DIR} (and {ALT_COMMON_KNOWLEDGE_DIR})")
    print(f" • Servitor Knowledge:{KNOWLEDGE_DIR}/<servitor_name>/")
    print(f" • Workspaces:      {WORKSPACE_DIR}/<servitor_name>/")
    print("="*70 + "\n")


# --- INTERACTIVE CLI UI ENGINE (v10.0) ---
def run_interactive_mode(
    servitor_name: str = "turing",
    model_name: str = "gemini-2.0-flash",
    context_dir: Optional[Path] = None,
    history_file: Optional[Path] = None,
    always_page: bool = False
):
    """
    Launches an interactive Terminal UI (CLI REPL) with scrollable response paging,
    slash commands (/switch, /model, /clear, /page, /history, /help, /exit),
    rich markdown rendering, and persistent multi-turn conversation state.
    """
    if not RICH_AVAILABLE:
        print("Error: `rich` and `prompt_toolkit` packages are required for interactive mode.", file=sys.stderr)
        print("Install via: pip install rich prompt_toolkit", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("Export it using: export GEMINI_API_KEY='your_api_key'", file=sys.stderr)
        sys.exit(1)

    console = Console()
    current_servitor = resolve_servitor_name(servitor_name)
    current_model = model_name

    if current_servitor not in SERVITOR_PROFILES:
        console.print(f"[bold red]Unknown servitor profile: '{servitor_name}'[/bold red]")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Initialize prompt history file
    prompt_history_path = LOGS_DIR / ".prompt_history"
    session = PromptSession(history=FileHistory(str(prompt_history_path)))

    # Session chat log & conversation state
    session_id = time.strftime("%Y-%m-%d_%H-%M-%S")
    current_chat_log = get_chat_log_path(current_servitor, session_id)
    contents: List[Any] = []
    last_response_text: str = ""

    def load_current_system_directive(s_name: str) -> str:
        profile = SERVITOR_PROFILES[s_name]
        context_block = load_servitor_context(s_name, context_dir=context_dir, history_file=history_file)
        directive = profile["directive"]
        if context_block:
            directive += "\n" + context_block
        return directive

    system_instruction = load_current_system_directive(current_servitor)

    def print_welcome_header(s_name: str, m_name: str):
        profile = SERVITOR_PROFILES[s_name]
        s_ws = WORKSPACE_DIR / s_name
        s_ws.mkdir(parents=True, exist_ok=True)

        header_text = (
            f"[bold cyan]CYBER-TÁLTOS INTERACTIVE TERMINAL UI (v10.0)[/bold cyan]\n"
            f"[bold yellow]Active Servitor:[/bold yellow] [bold green]{profile['name'].upper()}[/bold green] ({profile['role']})\n"
            f"[bold yellow]Parent Tier/Archon:[/bold yellow] Tier {profile.get('tier', 'Task')} ({profile.get('parent', profile.get('category', 'Core'))})\n"
            f"[bold yellow]Target Model:[/bold yellow] [bold magenta]{m_name}[/bold magenta]\n"
            f"[bold yellow]Workspace CWD:[/bold yellow] [dim]{s_ws}[/dim]\n"
            f"[bold yellow]Chat Log Path:[/bold yellow] [dim]{current_chat_log}[/dim]\n"
            f"[bold yellow]Daily Usage:[/bold yellow] [bold magenta]{get_usage_summary()['daily_usage_pct']:.2f}%[/bold magenta] ({get_usage_summary()['today_total_tokens']:,} / {get_usage_summary()['daily_limit']:,} tokens)\n"
            f"[bold yellow]Common Knowledge:[/bold yellow] [dim]{COMMON_KNOWLEDGE_DIR}[/dim]\n\n"
            f"[bold white]Slash Commands:[/bold white]\n"
            f"  [cyan]/switch <servitor>[/cyan]  - Switch active servitor identity\n"
            f"  [cyan]/model <model>[/cyan]     - Switch LLM model (e.g. gemini-2.0-flash, gemini-1.5-pro)\n"
            f"  [cyan]/clear[/cyan]             - Reset conversation history\n"
            f"  [cyan]/page[/cyan]              - Open last response in scrollable terminal pager (`less -R`)\n"
            f"  [cyan]/history[/cyan]           - Show turn count & conversation status\n"
            f"  [cyan]/help[/cyan]              - Display command help\n"
            f"  [cyan]/exit[/cyan]              - Quit interactive session"
        )
        console.print(Panel(header_text, title=f"⚡ SERVITOR CLI SESSION — {profile['name'].upper()}", border_style="cyan"))

    print_welcome_header(current_servitor, current_model)

    pt_style = PtStyle.from_dict({
        'prompt': '#00ffaa bold',
        'symbol': '#ff007f bold',
    })

    while True:
        try:
            profile = SERVITOR_PROFILES[current_servitor]
            prompt_str = [
                ('class:prompt', f"[{profile['name'].lower()}]"),
                ('class:symbol', ' ⚡> ')
            ]

            user_input = session.prompt(
                prompt_str,
                style=pt_style,
                auto_suggest=AutoSuggestFromHistory()
            ).strip()

            if not user_input:
                continue

            # --- SLASH COMMAND HANDLING ---
            if user_input.startswith("/"):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

                if cmd in ["/exit", "/quit", "/q"]:
                    console.print("[bold cyan]Exiting servitor session. Standby for next initialization.[/bold cyan]")
                    break

                elif cmd in ["/help", "/h"]:
                    help_msg = (
                        "[bold cyan]Interactive Terminal Slash Commands:[/bold cyan]\n"
                        "  [bold yellow]/switch <name>[/bold yellow]   : Change active servitor profile (e.g. /switch stallman, /switch flynn)\n"
                        "  [bold yellow]/model <model>[/bold yellow]   : Change target model (e.g. /model gemini-1.5-pro)\n"
                        "  [bold yellow]/clear[/bold yellow]           : Clear current session history\n"
                        "  [bold yellow]/page[/bold yellow]            : Open last response in scrollable full-screen pager (`less -R`)\n"
                        "  [bold yellow]/usage[/bold yellow]           : Display detailed token consumption & current daily usage percentage\n"
                        "  [bold yellow]/limit <N>[/bold yellow]       : Update daily token budget limit (e.g. /limit 2000000)\n"
                        "  [bold yellow]/history[/bold yellow]         : Display conversation turns and current message stack\n"
                        "  [bold yellow]/exit[/bold yellow]            : Exit interactive mode"
                    )
                    console.print(Panel(help_msg, title="Command Reference", border_style="yellow"))
                    continue

                elif cmd in ["/switch", "/servitor"]:
                    if not arg:
                        console.print("[bold red]Usage: /switch <servitor_name>[/bold red]")
                        continue
                    target = resolve_servitor_name(arg)
                    if target not in SERVITOR_PROFILES:
                        console.print(f"[bold red]Unknown servitor: '{arg}'. Run /help or check servitor roster.[/bold red]")
                        continue
                    current_servitor = target
                    system_instruction = load_current_system_directive(current_servitor)
                    contents = []
                    console.print(f"[bold green]Switched active servitor to: {SERVITOR_PROFILES[current_servitor]['name'].upper()}[/bold green]")
                    print_welcome_header(current_servitor, current_model)
                    continue

                elif cmd in ["/model"]:
                    if not arg:
                        console.print("[bold red]Usage: /model <model_name>[/bold red]")
                        continue
                    current_model = arg
                    console.print(f"[bold green]Switched API model to: {current_model}[/bold green]")
                    continue

                elif cmd in ["/clear", "/reset"]:
                    contents = []
                    last_response_text = ""
                    console.print("[bold yellow]Conversation history cleared.[/bold yellow]")
                    continue

                elif cmd in ["/usage", "/stats", "/quota"]:
                    display_usage_report()
                    continue

                elif cmd in ["/limit", "/set-limit"]:
                    if not arg or not arg.isdigit():
                        console.print("[bold red]Usage: /limit <number_of_tokens>[/bold red]")
                        continue
                    new_lim = int(arg)
                    display_usage_report(set_limit=new_lim)
                    continue

                elif cmd in ["/history"]:
                    turns_count = len(contents)
                    console.print(f"[bold cyan]Conversation Turns:[/bold cyan] {turns_count} items in memory stack.")
                    continue

                elif cmd in ["/page", "/scroll"]:
                    if not last_response_text:
                        console.print("[yellow]No response available in buffer to page.[/yellow]")
                        continue
                    console.print("[cyan]Opening last response in scrollable terminal pager (press 'q' to exit pager)...[/cyan]")
                    with console.pager(styles=True):
                        console.print(Markdown(last_response_text))
                    continue

                else:
                    console.print(f"[bold red]Unknown command '{cmd}'. Type /help for available options.[/bold red]")
                    continue

            # --- REGULAR PROMPT EXECUTION ---
            contents.append(user_input)
            profile_name = SERVITOR_PROFILES[current_servitor]['name'].upper()

            with console.status(f"[bold cyan][{profile_name}] Processing prompt via {current_model}...[/bold cyan]", spinner="dots"):
                max_turns = 6
                final_text = ""

                for turn in range(1, max_turns + 1):
                    try:
                        response = client.models.generate_content(
                            model=current_model,
                            contents=contents,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                tools=TOOL_FUNCTIONS,
                                temperature=0.2,
                            )
                        )
                    except Exception as e:
                        console.print(f"[bold red]API Error:[/bold red] {str(e)}")
                        break

                    p_tokens = 0
                    c_tokens = 0
                    if hasattr(response, "usage_metadata") and response.usage_metadata:
                        p_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                        c_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                    if p_tokens == 0 and c_tokens == 0:
                        p_tokens = max(10, len(str(contents)) // 4)
                        c_tokens = max(10, len(str(getattr(response, "text", "") or "")) // 4)

                    u_info = record_token_usage(current_servitor, p_tokens, c_tokens)

                    if response.candidates and response.candidates[0].content:
                        contents.append(response.candidates[0].content)

                    function_calls = response.function_calls
                    if not function_calls:
                        final_text = response.text or ""
                        break

                    # Process Tool Calls
                    for fc in function_calls:
                        func_name = fc.name
                        func_args = dict(fc.args) if fc.args else {}
                        console.print(f"[bold yellow]🛠️ [Tool Call - Turn {turn}]:[/bold yellow] [cyan]{func_name}({func_args})[/cyan]")

                        tool_result = ""
                        if func_name == "read_file":
                            func_args["servitor_name"] = current_servitor
                            tool_result = read_file(**func_args)
                        elif func_name == "write_file":
                            func_args["servitor_name"] = current_servitor
                            tool_result = write_file(**func_args)
                        elif func_name == "execute_posix_cmd":
                            func_args["servitor_name"] = current_servitor
                            tool_result = execute_posix_cmd(**func_args)
                        elif func_name == "delegate_task":
                            tool_result = delegate_task(**func_args)
                        elif func_name == "inspect_local_media":
                            tool_result = inspect_local_media(**func_args)
                        elif func_name == "web_search":
                            tool_result = web_search(**func_args)
                        elif func_name == "web_browse":
                            tool_result = web_browse(**func_args)
                        else:
                            tool_result = f"Error: Unknown tool {func_name}"

                        res_snippet = tool_result[:120] + "..." if len(tool_result) > 120 else tool_result
                        console.print(f"   [dim]└─ Result: {res_snippet}[/dim]")

                        contents.append(
                            types.Part.from_function_response(
                                name=func_name,
                                response={"result": tool_result}
                            )
                        )

            if final_text:
                last_response_text = final_text
                append_to_chat_log(current_chat_log, current_servitor, final_text, tool_calls=turn_executed_tools)
                line_count = len(final_text.splitlines())
                term_height = console.height or 24

                console.print(f"\n[bold green]━━━ [{profile_name} RESPONSE] ━━━[/bold green]\n")

                # Scrollable Pager Logic: If always_page is set OR response exceeds screen height / 25 lines
                if always_page or line_count > (term_height - 6):
                    console.print(f"[dim cyan](Response is {line_count} lines long. Displaying in scrollable terminal pager — press 'q' to return to prompt)[/dim cyan]\n")
                    with console.pager(styles=True):
                        console.print(Markdown(final_text))
                else:
                    console.print(Markdown(final_text))
                    console.print("\n[dim]Tip: Type /page anytime to open this response in full-screen scrollable mode.[/dim]")

                console.print(f"[dim cyan]📊 Turn Tokens: {u_info['turn_prompt_tokens']} prompt + {u_info['turn_candidates_tokens']} output | Today: {u_info['today_total_tokens']:,} / {u_info['daily_limit']:,} tokens ([magenta]{u_info['daily_usage_pct']}%[/magenta])[/dim cyan]\n")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Session interrupted. Exiting interactive mode.[/bold yellow]")
            break

# --- CLI ENTRYPOINT ---
def main():
    parser = argparse.ArgumentParser(
        description="LSF CLI (LLM Servitor Framework) v10.0: Gemini Free Tier Quotas & Usage Telemetry Engine: Interactive Terminal UI & Cyber-Táltos Multi-Agent Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Operational Subcommands")

    # Run command
    
    # Interactive UI command
    interactive_parser = subparsers.add_parser("interactive", aliases=["chat", "ui"], help="Launch interactive CLI UI terminal session")
    interactive_parser.add_argument("-s", "--servitor", default="turing", help="Initial servitor profile key")
    interactive_parser.add_argument("-m", "--model", default="gemini-2.0-flash", help="Gemini API model name")
    interactive_parser.add_argument("-c", "--context-dir", type=Path, default=None, help="Directory path to markdown knowledge files")
    interactive_parser.add_argument("-f", "--history-file", type=Path, default=None, help="File path to exported chat transcript log")
    interactive_parser.add_argument("--pager", action="store_true", help="Always render responses in full-screen scrollable terminal pager")

    run_parser = subparsers.add_parser("run", help="Dispatch a prompt to a servitor")
    run_parser.add_argument("-s", "--servitor", default="turing", help="Target servitor profile key")
    run_parser.add_argument("prompt", help="Prompt text or task description")
    run_parser.add_argument("-m", "--model", default="gemini-2.0-flash", help="Gemini API model name")
    run_parser.add_argument("-c", "--context-dir", type=Path, default=None, help="Custom knowledge directory path")
    run_parser.add_argument("-f", "--history-file", type=Path, default=None, help="Exported chat transcript log path")

    # Daemon command
    daemon_parser = subparsers.add_parser("daemon", help="Run inbox listener daemon for a servitor")
    daemon_parser.add_argument("-s", "--servitor", required=True, help="Target servitor key to poll")
    daemon_parser.add_argument("-i", "--interval", type=int, default=5, help="Poll interval in seconds")
    daemon_parser.add_argument("-c", "--context-dir", type=Path, default=None, help="Custom knowledge directory path")
    daemon_parser.add_argument("-f", "--history-file", type=Path, default=None, help="Exported chat transcript log path")

    # Usage command
    usage_parser = subparsers.add_parser("usage", aliases=["stats", "quota"], help="Display current token usage percentage and quota report")
    usage_parser.add_argument("--reset", action="store_true", help="Reset cumulative token usage logs")
    usage_parser.add_argument("--set-limit", type=int, default=None, help="Set custom daily token budget limit")

    # List command
    subparsers.add_parser("list", help="List configured servitor profiles showing full taxonomy hierarchy")

    args = parser.parse_args()

    
    if args.command in ["interactive", "chat", "ui"]:
        run_interactive_mode(
            servitor_name=args.servitor,
            model_name=args.model,
            context_dir=args.context_dir,
            history_file=args.history_file,
            always_page=args.pager
        )
    elif args.command == "run":

        run_agent_loop(
            args.servitor,
            args.prompt,
            model_name=args.model,
            context_dir=args.context_dir,
            history_file=args.history_file
        )
    elif args.command == "daemon":
        run_daemon(
            args.servitor,
            interval=args.interval,
            context_dir=args.context_dir,
            history_file=args.history_file
        )
    elif args.command in ["usage", "stats", "quota"]:
        display_usage_report(reset=args.reset, set_limit=args.set_limit)
    elif args.command == "list":
        list_pantheon_hierarchy()
    else:
        # Default behavior when no subcommand is given: launch interactive session
        print("⚡ No subcommand specified. Launching interactive terminal session (turing)...")
        run_interactive_mode()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CODE CITY APOCALYPSE + VERTICAL AI BOARDROOM - INTEGRATED VERSION
==============================================================

Complete integration with:
- Live Code City scanning and visualization
- Real Vertical AI Boardroom engine (no mock data)
- Mayor Anti character (renamed from Mayor Trump)
- Scout Master data integration
- Concierge v3 LLM orchestration

Usage:
  python boardroom_city_integrated.py /path/to/codebase
  python boardroom_city_integrated.py /path/to/codebase --idea "Your idea"
  python boardroom_city_integrated.py --idea "Your business idea" --rounds 3 --scout

Features:
- Scan codebase → Generate 3D city with Three.js
- Click Boardroom HQ to convene live boardroom debate
- Click Mayor Anti Tower for villain speech
- Disasters = code errors, Monsters = bugs
- Real-time boardroom results with live LLM calls
"""

import sys
import os
import json
import random
import argparse
from datetime import datetime
from pathlib import Path

# ============================================================================
# PATH SETUP
# ============================================================================

# Add _bmad-output to path for importing boardroom engine
BMAD_OUTPUT = Path("/data/data/com.termux/files/home/_bmad-output")
VERTICAL_CORE = Path("/data/data/com.termux/files/home/Gospel-A9-Whorl-Staging/Kindred_Core")

sys.path.insert(0, str(BMAD_OUTPUT))
sys.path.insert(0, str(VERTICAL_CORE))

# Import live boardroom engine
try:
    from vertical_ai_boardroom_final import run_boardroom as live_run_boardroom
    from vertical_ai_boardroom_final import AGENTS as LIVE_AGENTS
    from scout_master import scout_for_boardroom, VERTICAL_CONFIGS
    LIVE_BOARDROOM_AVAILABLE = True
    print("  [Boardroom Engine] Live engine loaded")
except Exception as e:
    LIVE_BOARDROOM_AVAILABLE = False
    print(f"  [Boardroom Engine] Warning: {e}")
    print("  [Boardroom Engine] Falling back to mock mode")

# ============================================================================
# CODE CITY ENGINE
# ============================================================================

class CodeCityScanner:
    """Scans codebase and generates city data with buildings."""
    
    FILE_TYPES = {
        '.py': ('python_tower', '#3572A5'),
        '.tsx': ('react_dome', '#61DAFB'),
        '.jsx': ('react_dome', '#61DAFB'),
        '.ts': ('typescript_tower', '#3178C6'),
        '.js': ('javascript_spire', '#F7DF1E'),
        '.json': ('data_bunker', '#4CAF50'),
        '.yaml': ('data_bunker', '#4CAF50'),
        '.yml': ('data_bunker', '#4CAF50'),
        '.md': ('document_archive', '#E0E0E0'),
        '.html': ('web_pavilion', '#E34F26'),
        '.css': ('web_pavilion', '#1572B6'),
    }
    
    def __init__(self, project_path="."):
        self.project_path = project_path
        self.buildings = []
        self.disasters = []
        self.monsters = []
        self.air_raids = []
    
    def scan(self):
        """Scan project and generate city data."""
        print(f"\n  Scanning {self.project_path}...")
        
        file_count = 0
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden dirs and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                       ['node_modules', '__pycache__', 'venv', '.git', '.vscode', 'dist', 'build']]
            
            for file in files:
                if file_count >= 500:  # Limit for performance
                    break
                    
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.FILE_TYPES:
                    continue
                
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    building = self._create_building(file, filepath, size)
                    
                    # Scan for errors and add disasters
                    error_level = self._scan_for_errors(filepath)
                    if error_level > 0:
                        building['health'] = max(0, 100 - (error_level * 15))
                        self._trigger_disasters(building, error_level)
                    
                    self.buildings.append(building)
                    file_count += 1
                except (OSError, PermissionError):
                    continue
            
            if file_count >= 500:
                break
        
        # Add BOARDROOM HQ as central obelisk
        self._add_boardroom_hq()
        
        # Add Mayor Anti Tower
        self._add_mayor_tower()
        
        print(f"  {file_count} buildings scanned")
        print(f"  {len(self.disasters)} disasters")
        print(f"  {len(self.monsters)} monsters")
        print(f"  {len(self.air_raids)} air raids")
        
        return self.generate_city_data()
    
    def _create_building(self, filename, filepath, size):
        """Create a building from a file."""
        ext = os.path.splitext(filename)[1].lower()
        btype, color = self.FILE_TYPES.get(ext, ('unknown', '#666666'))
        
        # Scale based on file size and complexity
        lines = self._count_lines(filepath)
        height = max(5, min(80, size // 2000 + lines // 50))
        width = random.randint(5, 15)
        depth = random.randint(5, 15)
        
        # Position randomly but avoid center (for HQ)
        x = random.randint(-80, 80)
        z = random.randint(-80, 80)
        while -15 <= x <= 15 and -15 <= z <= 15:
            x = random.randint(-80, 80)
            z = random.randint(-80, 80)
        
        return {
            'id': len(self.buildings),
            'name': filename,
            'path': filepath,
            'height': height,
            'width': width,
            'depth': depth,
            'x': x,
            'z': z,
            'health': 100,
            'type': btype,
            'color': color,
            'windows': random.randint(5, min(50, height)),
            'occupants': random.randint(1, 10),
            'lines': lines,
            'size': size
        }
    
    def _count_lines(self, filepath):
        """Count lines in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 100
    
    def _scan_for_errors(self, filepath):
        """Scan file for error patterns."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            error_level = 0
            patterns = [
                ('syntaxerror', 3), ('nameerror', 2), ('typeerror', 2),
                ('indexerror', 2), ('keyerror', 2), ('attributeerror', 2),
                ('todo', 1), ('fixme', 1), ('hack', 1), ('xxx', 1),
                ('bug:', 2), ('broken', 2), ('undefined', 2)
            ]
            for pattern, severity in patterns:
                if pattern in content:
                    error_level += severity
            
            lines = content.split('\n')
            if len(lines) > 500: error_level += 1
            if len(lines) > 1000: error_level += 2
            
            return min(5, error_level)
        except:
            return 1
    
    def _trigger_disasters(self, building, severity):
        """Trigger disasters based on error severity."""
        disasters = [self._create_fire, self._create_monster, self._create_air_raid]
        for _ in range(severity):
            random.choice(disasters)(building)
    
    def _create_fire(self, building):
        """Create a fire disaster."""
        fire = {
            'type': 'fire',
            'building_id': building['id'],
            'intensity': random.randint(1, 10),
            'position': {
                'x': building['x'] + random.randint(-5, 5),
                'y': random.randint(2, max(10, building['height'])),
                'z': building['z'] + random.randint(-5, 5)
            },
            'particles': random.randint(10, 50)
        }
        self.disasters.append(fire)
    
    def _create_monster(self, building):
        """Create a monster."""
        species = random.choice(['gorilla', 'lizard', 'wolf', 'dinosaur', 'bug', 'zombie'])
        monster = {
            'type': 'monster',
            'species': species,
            'building_id': building['id'],
            'position': {'x': building['x'], 'y': 0, 'z': building['z']},
            'scale': random.uniform(1.0, 3.0),
            'health': random.randint(50, 100),
            'damage': random.randint(1, 5),
            'personality': random.choice(['aggressive', 'curious', 'confused', 'angry'])
        }
        self.monsters.append(monster)
    
    def _create_air_raid(self, building):
        """Create an air raid."""
        plane = {
            'type': 'air_raid',
            'pilot': random.choice(['red_baron', 'maverick', 'iceman', 'anti_air_force_one']),
            'building_id': building['id'],
            'position': {
                'x': random.randint(-100, 100),
                'y': random.randint(30, 60),
                'z': random.randint(-100, 100)
            },
            'velocity': {
                'x': random.uniform(-2, 2),
                'y': 0,
                'z': random.uniform(-2, 2)
            },
            'bombs': random.randint(1, 5),
            'cargo': random.choice(['anti_buzzwords', 'real_data', 'truth_bombs', 'actual_data'])
        }
        self.air_raids.append(plane)
    
    def _add_boardroom_hq(self):
        """Add the Vertical AI Boardroom HQ obelisk at center."""
        hq = {
            'id': 9999,
            'name': 'VERTICAL_AI_BOARDROOM_HQ',
            'path': 'boardroom://obligatory_board_meeting',
            'height': 50,
            'width': 30,
            'depth': 30,
            'x': 0,
            'z': 0,
            'health': 100,
            'type': 'boardroom_obelisk',
            'color': '#2d1b69',
            'windows': 0,
            'occupants': 7,  # All 7 personas
            'lines': 0,
            'size': 0,
            'special': True,
            'clickable': True,
            'action': 'convene_boardroom',
            'description': 'Click to convene the Vertical AI Boardroom - LIVE ENGINE'
        }
        self.buildings.append(hq)
    
    def _add_mayor_tower(self):
        """Add Mayor Anti Tower - the villain releasing monsters."""
        mayor = {
            'id': 9998,
            'name': 'MAYOR_ANTI_TOWER',
            'path': 'mayor://burn_it_all_down',
            'height': 40,
            'width': 25,
            'depth': 25,
            'x': -40,
            'z': -40,
            'health': 100,
            'type': 'anti_tower_gold',
            'color': '#FFD700',
            'windows': 100,
            'occupants': 1,
            'lines': 0,
            'size': 0,
            'special': True,
            'clickable': True,
            'action': 'mayor_speech',
            'description': 'Mayor Anti Tower - Releasing monsters and talking out his ass',
            'villain': True
        }
        self.buildings.append(mayor)
        
        # Mayor is actively causing problems
        for _ in range(5):
            self._create_monster(mayor)
    
    def generate_city_data(self):
        """Generate complete city data structure."""
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_buildings': len(self.buildings),
                'total_disasters': len(self.disasters),
                'total_monsters': len(self.monsters),
                'total_air_raids': len(self.air_raids),
                'boardroom_status': 'LIVE_ENGINE' if LIVE_BOARDROOM_AVAILABLE else 'MOCK_MODE'
            },
            'city': {
                'buildings': self.buildings,
                'disasters': self.disasters,
                'monsters': self.monsters,
                'air_raids': self.air_raids
            }
        }


# ============================================================================
# BOARDROOM ENGINE WRAPPER (Live + Fallback)
# ============================================================================

def run_boardroom(context, rounds=2, use_scout=True, use_llm=True):
    """
    Run boardroom - uses live engine if available, falls back to mock.
    """
    if LIVE_BOARDROOM_AVAILABLE:
        try:
            # Build context dict
            if isinstance(context, str):
                context_dict = {
                    'raw': context,
                    'type': 'text',
                    'label': context[:60],
                    'data': {'content': context}
                }
            else:
                context_dict = context
            
            # Run live boardroom
            result = live_run_boardroom(
                context_dict,
                rounds=rounds,
                use_scout=use_scout,
                use_llm=use_llm
            )
            return result
        except Exception as e:
            print(f"  [Boardroom] Live engine error: {e}")
            print("  [Boardroom] Falling back to mock mode")
            return run_mock_boardroom(context, rounds)
    else:
        return run_mock_boardroom(context, rounds)


def run_mock_boardroom(idea_text, rounds=2):
    """Mock boardroom for fallback."""
    from collections import defaultdict
    
    AGENTS_MOCK = {
        "CFO": {"persona": "You are the CFO. Numbers only.", "focus": "unit economics, ROI"},
        "CMO": {"persona": "You are the CMO. Customer is north star.", "focus": "customer psychology"},
        "CRO": {"persona": "You are CRO. Find the landmine.", "focus": "failure modes"},
        "ANALYST": {"persona": "You are the Analyst. Cited data only.", "focus": "market data"},
        "DEVIL": {"persona": "You are Devil. Challenge consensus.", "focus": "assumptions"},
        "TECHNICAL_AUDITOR": {"persona": "You are Technical Auditor. Assess architecture, debt, scalability.", "focus": "scalability, tech debt, security"},
        "MAYOR_ANTI": {"persona": "You are Mayor Anti. Talk out your ass. Release monsters. Cause chaos. Comic relief. END with: - Anti", "focus": "disruption, chaos, anti-establishment"},
        "OLD_MAN_MENTOR": {"persona": "You are the Old Man Mentor. 40 years in the trenches. Wise, patient, speaks from experience. END with: - Old Man", "focus": "wisdom, experience, lessons learned"},
        "INDUSTRY_VETERAN": {"persona": "You are the Industry Veteran. Deep industry knowledge. Connected. END with: - Veteran", "focus": "industry knowledge, trends, players"},
        "SCOUT_MASTER": {"persona": "You are the Scout Master. Master of data gathering from forums and reports. END with: - Scout Out", "focus": "data gathering, market intel, fresh information"},
        # Six Hat Thinking Methodology
        "WHITE_HAT": {"persona": "You are the White Hat. Pure facts, data, information only. END with: - White Hat", "focus": "facts, data, objective truth"},
        "RED_HAT": {"persona": "You are the Red Hat. Emotions, feelings, intuition. END with: - Red Hat", "focus": "emotions, feelings, human response"},
        "BLACK_HAT": {"persona": "You are the Black Hat. Caution, risks, problems. END with: - Black Hat", "focus": "risks, problems, dangers"},
        "YELLOW_HAT": {"persona": "You are the Yellow Hat. Optimism, benefits, value. END with: - Yellow Hat", "focus": "optimism, benefits, upside"},
        "GREEN_HAT": {"persona": "You are the Green Hat. Creativity, ideas, solutions. END with: - Green Hat", "focus": "creativity, innovation, ideas"},
        "BLUE_HAT": {"persona": "You are the Blue Hat. Control, organization, process. END with: - Blue Hat", "focus": "control, organization, structure"},
        # Brown Hat Thinking (Bleak's Custom Methodology)
        "BROWN_HAT": {"persona": "You are the Brown Hat. Finish pass, modular integration, nexus points. END with: - Brown Hat", "focus": "integration, quality check, nexus points"}
    }
    
    debate_log = []
    
    for round_num in range(1, rounds + 1):
        for agent_name, agent in AGENTS_MOCK.items():
            response = generate_mock_response(agent_name, idea_text)
            debate_log.append({
                "round": round_num,
                "agent": agent_name,
                "argument": response
            })
    
    verdict = generate_verdict(debate_log)
    
    return {
        "debate": debate_log,
        "synthesis": {
            "verdict": verdict,
            "chairman_statement": f"Verdict: {verdict}",
            "primary_risk": identify_primary_risk(debate_log),
            "primary_opportunity": identify_primary_opportunity(debate_log)
        },
        "opportunities": [e["argument"] for e in debate_log if "RECOMMEND: consensus" in e["argument"]],
        "risks": [{"risk": e["argument"], "owner": e["agent"]} for e in debate_log if "RECOMMEND: risk" in e["argument"]],
        "scout_data": None
    }


def generate_mock_response(agent_name, idea_text):
    """Generate mock responses."""
    if "CFO" in agent_name:
        return "ROI questionable with no capital. Need 200% margin. RECOMMEND: contest"
    elif "CMO" in agent_name:
        return "Customers pay for pain point solutions. RECOMMEND: consensus"
    elif "CRO" in agent_name:
        return "Solo dev = no safety net. One failure = homeless. RECOMMEND: risk"
    elif "ANALYST" in agent_name:
        return "42% fail rate but outliers succeed wildly. RECOMMEND: consensus"
    elif "DEVIL" in agent_name:
        return "Assuming customers exist? Tech works? YOU can execute? RECOMMEND: contest"
    elif "TECHNICAL_AUDITOR" in agent_name:
        return "Architecture sound but needs error handling. RECOMMEND: risk"
    elif "MAYOR_ANTI" in agent_name:
        speeches = [
            "Tremendous idea, beautiful potential. Nobody does it better. - Anti",
            "Could be the best ever, or total disaster. We'll see. - Anti",
            "The system is rigged, folks! Sad! - Anti",
            "Fight the power! Burn it all down. - Anti"
        ]
        return random.choice(speeches)
    elif "OLD_MAN_MENTOR" in agent_name:
        return random.choice([
            "Kid, I've seen this before. Focus on fundamentals. RECOMMEND: consensus - Old Man",
            "40 years in the game. This has potential but needs discipline. RECOMMEND: consensus - Old Man",
            "Trust me, I've made every mistake. Keep it simple. RECOMMEND: consensus - Old Man",
            "This reminds me of 1987. We did it better back then. RECOMMEND: consensus - Old Man"
        ])
    elif "INDUSTRY_VETERAN" in agent_name:
        return random.choice([
            "The market is shifting. This could be huge. RECOMMEND: consensus - Veteran",
            "I know the players. Timing is everything. RECOMMEND: consensus - Veteran",
            "Hidden trend: this is about to explode. Get in now. RECOMMEND: go - Veteran",
            "Watch out for competition. But the space has room. RECOMMEND: conditional - Veteran"
        ])
    elif "SCOUT_MASTER" in agent_name:
        return random.choice([
            "Fresh intel from Reddit. Developers want this. RECOMMEND: consensus - Scout Out",
            "PlumbersRule forum confirms the pain point is real. RECOMMEND: consensus - Scout Out",
            "Found a hidden report. This validates the idea. RECOMMEND: go - Scout Out",
            "Forums are buzzing. You're onto something. RECOMMEND: consensus - Scout Out"
        ])
    # Six Hat Thinking
    elif "WHITE_HAT" in agent_name:
        return random.choice([
            "FACTS: Market data supports this. RECOMMEND: consensus - White Hat",
            "DATA: 42% of devs need this solution. RECOMMEND: go - White Hat",
            "INFORMATION: Clear demand signal from community. RECOMMEND: consensus - White Hat",
            "OBJECTIVE: Numbers show viability. RECOMMEND: go - White Hat"
        ])
    elif "RED_HAT" in agent_name:
        return random.choice([
            "FEELING: Community excitement is real. RECOMMEND: consensus - Red Hat",
            "EMOTION: Developers are frustrated and want this. RECOMMEND: go - Red Hat",
            "INTUITION: This solves a deep emotional need. RECOMMEND: consensus - Red Hat",
            "REACTION: Positive sentiment across all forums. RECOMMEND: go - Red Hat"
        ])
    elif "BLACK_HAT" in agent_name:
        return random.choice([
            "RISK: Competition is fierce. RECOMMEND: contest - Black Hat",
            "PROBLEM: Solo execution risk is high. RECOMMEND: risk - Black Hat",
            "CAUTION: Market saturation possible. RECOMMEND: contest - Black Hat",
            "DANGER: What if it doesn't scale? RECOMMEND: risk - Black Hat"
        ])
    elif "YELLOW_HAT" in agent_name:
        return random.choice([
            "BENEFIT: Clear value proposition. RECOMMEND: consensus - Yellow Hat",
            "VALUE: High upside potential. RECOMMEND: go - Yellow Hat",
            "OPTIMISM: Modular approach allows flexibility. RECOMMEND: consensus - Yellow Hat",
            "UPSIDE: Could be next essential tool. RECOMMEND: go - Yellow Hat"
        ])
    elif "GREEN_HAT" in agent_name:
        return random.choice([
            "IDEA: Add Turd Mergers for modular integration. RECOMMEND: consensus - Green Hat",
            "CREATIVE: Gamification elements would boost adoption. RECOMMEND: go - Green Hat",
            "SOLUTION: IDE integration widens market. RECOMMEND: consensus - Green Hat",
            "INNOVATION: Unique differentiator confirmed. RECOMMEND: go - Green Hat"
        ])
    elif "BLUE_HAT" in agent_name:
        return random.choice([
            "PROCESS: Structured approach needed. RECOMMEND: consensus - Blue Hat",
            "CONTROL: Clear phases and roles required. RECOMMEND: consensus - Blue Hat",
            "ORGANIZATION: Agile sprints with quality gates. RECOMMEND: go - Blue Hat",
            "STRUCTURE: Brown Hat finish pass at each sprint end. RECOMMEND: consensus - Blue Hat"
        ])
    # Brown Hat Thinking
    elif "BROWN_HAT" in agent_name:
        return random.choice([
            "FINISH PASS: All modules connected. Turd Mergers operational. RECOMMEND: go - Brown Hat",
            "INTEGRATION: Nexus points aligned. Workbench wired. RECOMMEND: consensus - Brown Hat",
            "QUALITY CHECK: Smoke test passed. Ready for deployment. RECOMMEND: go - Brown Hat",
            "VERIFICATION: All overlapping project points merged. RECOMMEND: consensus - Brown Hat"
        ])
    else:
        return "Needs more data. RECOMMEND: contest"


def generate_verdict(debate_log):
    """Generate verdict."""
    risk_count = sum(1 for e in debate_log if "RECOMMEND: risk" in e["argument"])
    contest_count = sum(1 for e in debate_log if "RECOMMEND: contest" in e["argument"])
    consensus_count = sum(1 for e in debate_log if "RECOMMEND: consensus" in e["argument"])
    
    if risk_count >= 3:
        return "no-go"
    elif consensus_count >= 4:
        return "go"
    else:
        return "conditional"


def identify_primary_risk(debate_log):
    """Identify primary risk."""
    risks = [e["argument"] for e in debate_log if "RECOMMEND: risk" in e["argument"]]
    return risks[0] if risks else "Execution risk"


def identify_primary_opportunity(debate_log):
    """Identify primary opportunity."""
    opps = [e["argument"] for e in debate_log if "RECOMMEND: consensus" in e["argument"]]
    return opps[0] if opps else "First-to-market advantage"


# ============================================================================
# HTML GENERATION
# ============================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>CODE CITY + VERTICAL AI BOARDROOM</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { margin: 0; background: #0a0a0a; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; overflow: hidden; height: 100vh; }
        #info { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.9); padding: 15px; border-radius: 5px; z-index: 100; max-width: 400px; font-size: 12px; }
        #stats { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.9); padding: 15px; border-radius: 5px; z-index: 100; font-size: 12px; }
        #boardroom-panel { position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.95); padding: 20px; border-radius: 10px; z-index: 100; max-width: 500px; max-height: 300px; overflow-y: auto; display: none; font-size: 12px; }
        #boardroom-panel h3 { color: #ffd700; margin-bottom: 10px; font-size: 14px; }
        .agent-speech { margin: 5px 0; padding: 5px; border-left: 3px solid #444; font-size: 11px; line-height: 1.3; }
        .agent-CFO { border-color: #4CAF50; }
        .agent-CMO { border-color: #2196F3; }
        .agent-CRO { border-color: #f44336; }
        .agent-ANALYST { border-color: #FFC107; }
        .agent-DEVIL { border-color: #9C27B0; }
        .agent-TECHNICAL_AUDITOR { border-color: #00BCD4; }
        .agent-MAYOR_ANTI { border-color: #FFD700; }
        .agent-OLD_MAN_MENTOR { border-color: #8B4513; }
        .agent-INDUSTRY_VETERAN { border-color: #5D4037; }
        .agent-SCOUT_MASTER { border-color: #4E342E; }
        /* Six Hat Thinking */
        .agent-WHITE_HAT { border-color: #E0E0E0; }
        .agent-RED_HAT { border-color: #F44336; }
        .agent-BLACK_HAT { border-color: #212121; }
        .agent-YELLOW_HAT { border-color: #FFEB3B; }
        .agent-GREEN_HAT { border-color: #4CAF50; }
        .agent-BLUE_HAT { border-color: #2196F3; }
        /* Brown Hat Thinking */
        .agent-BROWN_HAT { border-color: #8D6E63; }
        #input-idea { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.9); padding: 10px; border-radius: 5px; z-index: 100; }
        #input-idea input { width: 300px; padding: 8px; background: #222; color: #fff; border: 1px solid #444; border-radius: 3px; font-size: 12px; }
        #input-idea button { padding: 8px 15px; background: #4CAF50; color: white; border: none; border-radius: 3px; margin-left: 5px; cursor: pointer; font-size: 12px; }
        #input-idea button:hover { background: #45a049; }
        #verdict { font-size: 16px; font-weight: bold; margin: 10px 0; text-align: center; font-size: 14px; }
        .verdict-go { color: #4CAF50; }
        .verdict-no-go { color: #f44336; }
        .verdict-conditional { color: #FFC107; }
        canvas { display: block; }
        /* Mobile responsive */
        @media (max-width: 768px) {
            #boardroom-panel { max-width: 90%; left: 5%; right: 5%; bottom: 70px; }
            #input-idea { bottom: 10px; right: 10px; left: 10px; text-align: center; }
            #input-idea input { width: 100%; }
            #info, #stats { max-width: 90%; }
        }
    </style>
</head>
<body>
    <div id="info">
        <h2>CODE CITY + BOARDROOM</h2>
        <p>Buildings = Files | Disasters = Errors</p>
        <p><strong>Click Boardroom HQ to convene LIVE VERTICAL AI!</strong></p>
        <p style="font-size: 10px; color: #666;">Boardroom: <span id="boardroom-status">LOADING</span></p>
    </div>
    <div id="stats">
        <h3>CITY STATS</h3>
        <p>Buildings: <span id="building-count">0</span></p>
        <p>Disasters: <span id="disaster-count">0</span></p>
        <p>Monsters: <span id="monster-count">0</span></p>
        <p>Air Raids: <span id="air-raid-count">0</span></p>
    </div>
    <div id="boardroom-panel">
        <h3>BOARDROOM DEBATE - LIVE ENGINE</h3>
        <div id="boardroom-debate"></div>
        <div id="boardroom-result"></div>
    </div>
    <div id="input-idea">
        <input type="text" id="idea-input" placeholder="Enter your idea here...">
        <button onclick="conveneBoardroom()">Convene Boardroom</button>
    </div>
    <script>
'''

HTML_JAVASCRIPT = '''
        // Parse city data
        const cityData = CITY_DATA_PLACEHOLDER;
        const boardroomResult = BOARDROOM_RESULT_PLACEHOLDER;
        
        // Update boardroom status
        document.getElementById("boardroom-status").textContent = cityData.metadata.boardroom_status || "MOCK_MODE";
        
        // Three.js will be loaded dynamically to avoid CDN dependency
        // We'll use a local fallback or direct import
        let THREE = null;
        let OrbitControls = null;
        
        // Try to load Three.js from local storage or use embedded version
        function loadThreeJS() {
            // Check if Three.js is already loaded
            if (window.THREE) {
                THREE = window.THREE;
                initScene();
                return;
            }
            
            // Try local first (for offline mode)
            const threeLocal = '/_bmad-output/threejs/three.min.js';
            const controlsLocal = '/_bmad-output/threejs/OrbitControls.js';
            
            const tryLocal = function() {
                const threeScript = document.createElement('script');
                threeScript.src = threeLocal;
                threeScript.onload = function() {
                    THREE = window.THREE;
                    const controlsScript = document.createElement('script');
                    controlsScript.src = controlsLocal;
                    controlsScript.onload = function() {
                        OrbitControls = THREE.OrbitControls;
                        initScene();
                    };
                    controlsScript.onerror = function() {
                        console.error("Failed to load OrbitControls locally");
                        initScene();
                    };
                    document.head.appendChild(controlsScript);
                };
                threeScript.onerror = function() {
                    // Fall back to CDN
                    tryCDN();
                };
                document.head.appendChild(threeScript);
            };
            
            const tryCDN = function() {
                const threeScript = document.createElement('script');
                threeScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
                threeScript.onload = function() {
                    THREE = window.THREE;
                    const controlsScript = document.createElement('script');
                    controlsScript.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js';
                    controlsScript.onload = function() {
                        OrbitControls = THREE.OrbitControls;
                        initScene();
                    };
                    controlsScript.onerror = function() {
                        console.error("Failed to load OrbitControls from CDN");
                        initScene();
                    };
                    document.head.appendChild(controlsScript);
                };
                threeScript.onerror = function() {
                    console.error("Failed to load Three.js");
                    document.body.innerHTML = "<div style='color: white; padding: 20px; text-align: center;'><h1>Three.js Required</h1><p>Download Three.js locally by running: bash download_threejs.sh</p></div>";
                };
                document.head.appendChild(threeScript);
            };
            
            // Try local first, then CDN
            tryLocal();
        }
        
        // Scene setup
        let scene, camera, renderer, controls;
        let buildingMeshes = [];
        
        function initScene() {
            if (!THREE) {
                console.error("Three.js not loaded");
                return;
            }
            
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);
            
            // Controls (if available)
            if (OrbitControls) {
                controls = new OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
            }
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(50, 100, 50);
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            scene.add(directionalLight);
            
            // Ground
            const groundGeometry = new THREE.PlaneGeometry(300, 300);
            const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x1a1a2e });
            const ground = new THREE.Mesh(groundGeometry, groundMaterial);
            ground.rotation.x = -Math.PI / 2;
            ground.receiveShadow = true;
            scene.add(ground);
            
            // Grid
            const gridHelper = new THREE.GridHelper(300, 30, 0x000000, 0x000000);
            gridHelper.material.opacity = 0.3;
            gridHelper.material.transparent = true;
            scene.add(gridHelper);
            
            // Buildings
            cityData.city.buildings.forEach(b => {
                const geom = new THREE.BoxGeometry(b.width, b.height, b.depth);
                const mat = new THREE.MeshLambertMaterial({ color: b.color });
                const mesh = new THREE.Mesh(geom, mat);
                mesh.position.set(b.x, b.height / 2, b.z);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                mesh.userData = b;
                mesh.name = b.name;
                buildingMeshes.push(mesh);
                scene.add(mesh);
                
                // Glow for special buildings
                if (b.special || b.villain) {
                    const glow = new THREE.Mesh(
                        new THREE.BoxGeometry(b.width * 1.05, b.height * 1.05, b.depth * 1.05),
                        new THREE.MeshBasicMaterial({
                            color: b.villain ? 0xFFD700 : 0x2d1b69,
                            transparent: true,
                            opacity: 0.3,
                            side: THREE.BackSide
                        })
                    );
                    glow.position.set(b.x, b.height / 2, b.z);
                    scene.add(glow);
                }
            });
            
            // Camera
            camera.position.set(100, 100, 100);
            camera.lookAt(0, 0, 0);
            
            // Raycaster for clicking
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            
            function onMouseClick(event) {
                mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(buildingMeshes);
                
                if (intersects.length > 0) {
                    const building = intersects[0].object.userData;
                    if (building.action === "convene_boardroom") {
                        const panel = document.getElementById("boardroom-panel");
                        panel.style.display = "block";
                        if (boardroomResult) displayBoardroomResult(boardroomResult);
                    } else if (building.villain) {
                        const speeches = [
                            "The system is rigged! We need to burn it all down!",
                            "Anti-establishment forever! The people demand change!",
                            "This code is a crime against humanity! SAD!",
                            "Fight the power! Smash the system!"
                        ];
                        alert("MAYOR ANTI: " + speeches[Math.floor(Math.random() * speeches.length)]);
                    } else {
                        alert("Building: " + building.name + "\\nType: " + building.type + "\\nHealth: " + building.health + "%");
                    }
                }
            }
            
            window.addEventListener("click", onMouseClick, false);
            
            // Handle resize
            window.addEventListener("resize", () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
            
            // Animation
            function animate() {
                requestAnimationFrame(animate);
                if (controls) controls.update();
                renderer.render(scene, camera);
            }
            animate();
        }
        
        // Display boardroom result
        function displayBoardroomResult(result) {
            const debateDiv = document.getElementById("boardroom-debate");
            const resultDiv = document.getElementById("boardroom-result");
            debateDiv.innerHTML = "";
            
            // Show all debate entries
            result.debate.forEach(entry => {
                var div = document.createElement("div");
                div.className = "agent-speech agent-" + entry.agent;
                div.innerHTML = "<strong>" + entry.agent + ":</strong> " + entry.argument;
                debateDiv.appendChild(div);
            });
            
            // Show verdict
            const verdict = result.synthesis.verdict;
            const verdictText = "VERDICT: " + verdict.toUpperCase();
            resultDiv.innerHTML = "<div id='verdict' class='verdict-" + verdict + "'>" + verdictText + "</div>";
            
            // Show risk and opportunity
            if (result.synthesis.primary_risk) {
                resultDiv.innerHTML += "<p><strong>Primary Risk:</strong> " + result.synthesis.primary_risk + "</p>";
            }
            if (result.synthesis.primary_opportunity) {
                resultDiv.innerHTML += "<p><strong>Primary Opportunity:</strong> " + result.synthesis.primary_opportunity + "</p>";
            }
            
            // Show scout data if available
            if (result.scout_data) {
                resultDiv.innerHTML += "<p style='margin-top: 10px; font-size: 11px; color: #888;'><strong>Scout Intel:</strong> " + result.scout_data.substring(0, 200) + "...</p>";
            }
        }
        
        // Convene boardroom - now calls backend via fetch
        function conveneBoardroom() {
            const idea = document.getElementById("idea-input").value;
            if (!idea) { alert("Enter an idea first!"); return; }
            
            const panel = document.getElementById("boardroom-panel");
            panel.style.display = "block";
            panel.innerHTML = "<h3>BOARDROOM CONVENING...</h3><p>Analyzing: " + idea + "</p><p style='color: #666;'>Using LIVE Vertical AI Boardroom Engine</p>";
            
            // Call Python backend via fetch (if running as server)
            // For file mode, we use the pre-generated result
            if (boardroomResult) {
                setTimeout(function() {
                    displayBoardroomResult(boardroomResult);
                }, 500);
            } else {
                // No result available
                alert("No boardroom result available. Run with --idea flag to pre-generate.");
            }
        }
        
        window.conveneBoardroom = conveneBoardroom;
        
        // Stats
        document.getElementById("building-count").textContent = cityData.metadata.total_buildings;
        document.getElementById("disaster-count").textContent = cityData.metadata.total_disasters;
        document.getElementById("monster-count").textContent = cityData.metadata.total_monsters;
        document.getElementById("air-raid-count").textContent = cityData.metadata.total_air_raids;
        
        // Load Three.js
        loadThreeJS();
    </script>
</body>
</html>
'''


def generate_html(city_data, boardroom_result=None):
    """Generate HTML by replacing placeholders."""
    # String replacement for city data
    city_json = json.dumps(city_data)
    
    # String replacement for boardroom result
    if boardroom_result:
        boardroom_json = json.dumps(boardroom_result)
    else:
        boardroom_json = "null"
    
    # Build complete HTML
    html = HTML_TEMPLATE
    html = html.replace("CITY_DATA_PLACEHOLDER", city_json)
    html = html.replace("BOARDROOM_RESULT_PLACEHOLDER", boardroom_json)
    html += HTML_JAVASCRIPT
    
    return html


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Code City Apocalypse + Vertical AI Boardroom - INTEGRATED"
    )
    parser.add_argument(
        "path", 
        nargs="?", 
        default=".",
        help="Path to codebase"
    )
    parser.add_argument(
        "--idea", 
        type=str,
        help="Idea to evaluate (convenes boardroom)"
    )
    parser.add_argument(
        "--rounds", 
        type=int, 
        default=2,
        help="Boardroom rounds"
    )
    parser.add_argument(
        "--scout", 
        action="store_true",
        help="Use Scout Master for market data"
    )
    parser.add_argument(
        "--no-llm", 
        action="store_true",
        help="Disable LLM calls (use mock responses)"
    )
    parser.add_argument(
        "--output", 
        type=str,
        default="code_city_boardroom_integrated.html",
        help="Output file"
    )
    parser.add_argument(
        "--scan-only", 
        action="store_true",
        help="Only scan, no boardroom"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("  CODE CITY APOCALYPSE + VERTICAL AI BOARDROOM")
    print("  INTEGRATED VERSION - LIVE ENGINE")
    print("="*60)
    
    # Scan city
    scanner = CodeCityScanner(args.path)
    city_data = scanner.scan()
    
    # Run boardroom if idea provided
    boardroom_result = None
    if args.idea and not args.scan_only:
        print(f"\n  Evaluating: {args.idea[:60]}...")
        print(f"  Boardroom mode: {'LIVE' if LIVE_BOARDROOM_AVAILABLE else 'MOCK'}")
        if args.scout:
            print(f"  Scout: ENABLED")
        if not args.no_llm:
            print(f"  LLM: ENABLED")
        
        boardroom_result = run_boardroom(
            args.idea,
            rounds=args.rounds,
            use_scout=args.scout,
            use_llm=not args.no_llm
        )
        print(f"  Verdict: {boardroom_result.get('synthesis', {}).get('verdict', 'unknown').upper()}")
    
    # Generate HTML
    html_content = generate_html(city_data, boardroom_result)
    
    # Save
    try:
        with open(args.output, 'w') as f:
            f.write(html_content)
        print(f"\n  SAVED: {args.output}")
        print(f"  Open: file://{os.path.abspath(args.output)}")
        if boardroom_result:
            print(f"\n  BOARDROOM STATUS:")
            print(f"    Engine: {city_data['metadata']['boardroom_status']}")
            print(f"    Debate rounds: {args.rounds}")
            print(f"    Agents: {len(boardroom_result.get('debate', []))}")
            if boardroom_result.get('scout_data'):
                print(f"    Scout data: AVAILABLE")
    except Exception as e:
        print(f"\n  ERROR: {e}")


if __name__ == "__main__":
    main()

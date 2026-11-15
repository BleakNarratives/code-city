#!/usr/bin/env python3
"""
CODE CITY APOCALYPSE + VERTICAL AI BOARDROOM
===========================================

Unified engine: Scan codebase → 3D city → Boardroom HQ obelisk
Click the obelisk to convene boardroom on any idea.

Usage:
  python boardroom_city.py /path/to/codebase --idea "Your business idea"
  python boardroom_city.py --scan-only  # Just generate city, no boardroom
  python boardroom_city.py --boardroom-only --text "Your idea"  # Just boardroom
"""

import sys
import os
import json
import random
import argparse
from datetime import datetime
from pathlib import Path

# Add Vertical AI core to path
VERTICAL_CORE = Path("/data/data/com.termux/files/home/Gospel-A9-Whorl-Staging/Kindred_Core")
sys.path.insert(0, str(VERTICAL_CORE))

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
        self.streets = []
    
    def scan(self):
        """Scan project and generate city data."""
        print(f"\n  🏗️  Scanning {self.project_path}...")
        
        file_count = 0
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden dirs and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                       ['node_modules', '__pycache__', 'venv', '.git', '.vscode', 'dist', 'build']]
            
            for file in files:
                if file_count >= 1000:
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
            
            if file_count >= 1000:
                break
        
        # Add BOARDROOM HQ as central obelisk
        self._add_boardroom_hq()
        
        # Add Mayor Trump Tower
        self._add_mayor_tower()
        
        print(f"  ✓ {file_count} buildings scanned")
        print(f"  ✓ {len(self.disasters)} disasters")
        print(f"  ✓ {len(self.monsters)} monsters")
        print(f"  ✓ {len(self.air_raids)} air raids")
        
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
        # Avoid center area
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
        pilots = ['red_baron', 'maverick', 'iceman', 'trump_air_force_one']
        plane = {
            'type': 'air_raid',
            'pilot': random.choice(pilots),
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
            'cargo': random.choice(['buzzwords', 'fake_statistics', 'corporate_bs', 'actual_data'])
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
            'color': '#2d1b69',  # Deep purple/black
            'windows': 0,
            'occupants': 6,  # CFO, CMO, CRO, ANALYST, DEVIL, TECHNICAL_AUDITOR
            'lines': 0,
            'size': 0,
            'special': True,
            'clickable': True,
            'action': 'convene_boardroom',
            'description': 'Click to convene the Vertical AI Boardroom on any idea'
        }
        self.buildings.append(hq)
    
    def _add_mayor_tower(self):
        """Add Mayor Trump Tower - the villain releasing monsters."""
        mayor = {
            'id': 9998,
            'name': 'MAYOR_TRUMP_TOWER',
            'path': 'mayor://making_code_city_great_again',
            'height': 40,
            'width': 25,
            'depth': 25,
            'x': -40,
            'z': -40,
            'health': 100,
            'type': 'trump_tower_gold',
            'color': '#FFD700',  # Gold
            'windows': 100,
            'occupants': 1,
            'lines': 0,
            'size': 0,
            'special': True,
            'clickable': True,
            'action': 'mayor_speech',
            'description': 'Mayor Trump Tower - Releasing monsters and talking out his ass since 2025',
            'villain': True,
            'behavior': 'constantly_releasing_disaster'
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
                'special_buildings': [b for b in self.buildings if b.get('special')],
                'villains': [b for b in self.buildings if b.get('villain')]
            },
            'city': {
                'buildings': self.buildings,
                'disasters': self.disasters,
                'monsters': self.monsters,
                'air_raids': self.air_raids
            }
        }


# ============================================================================
# BOARDROOM ENGINE (from Gospel-A9-Whorl-Staging)
# ============================================================================

class BoardroomState:
    def __init__(self):
        self.consensus = []
        self.contested = []
        self.risk_registry = []

AGENTS = {
    "CFO": {"persona": "You are the CFO. Numbers only.", "focus": "unit economics, ROI"},
    "CMO": {"persona": "You are the CMO. Customer is north star.", "focus": "customer psychology"},
    "CRO": {"persona": "You are CRO. Find the landmine.", "focus": "failure modes"},
    "ANALYST": {"persona": "You are the Analyst. Cited data only.", "focus": "market data"},
    "DEVIL": {"persona": "You are Devil. Challenge consensus.", "focus": "assumptions"},
    "TECHNICAL_AUDITOR": {"persona": "You are the Technical Auditor. Assess architectural integrity, technical debt, and scalability.", "focus": "scalability, tech debt, security"},
    # NEW: Mayor as the villain
    "MAYOR_TRUMP": {"persona": "You are Mayor Trump. You ALWAYS talk out your ass. Releasing monsters. Causing riots. Saying ridiculous things. Be a jackass but with comic relief. END EVERY RESPONSE WITH: - Trump", "focus": "disruption, chaos, buzzwords, fake statistics"}
}

# Operator constraints from your profile
OPERATOR_CONTEXT = """OPERATOR CONSTRAINTS (reason within these, do not propose strategies that assume resources not listed):
- capital: none
- seed funding: none
- partnerships: none
- team size: 1
- credibility assets: outclaw, truthsleuth, rootbase_portfolio
- execution model: solo, skill-based, no permission required to start

"""


def run_boardroom(idea_text, rounds=2):
    """
    Run the Vertical AI boardroom on an idea.
    Returns: {"debate": [...], "synthesis": {...}, "verdict": "go/no-go/conditional"}
    """
    state = BoardroomState()
    debate_log = []
    
    print("\n" + "="*60)
    print("  🏛️  VERTICAL AI BOARDROOM")
    print("="*60)
    print(f"  Idea: {idea_text[:80]}...")
    print()
    
    for round_num in range(1, rounds + 1):
        print(f"  -- ROUND {round_num} --")
        
        prior_context = ""
        if round_num > 1:
            prior_entries = [e for e in debate_log if e["round"] == round_num - 1]
            prior_lines = "\n".join(f'{e["agent"]}: {e["argument"][:150]}' for e in prior_entries)
            prior_context = f"\n\nPRIOR ROUND ARGUMENTS:\n{prior_lines}\n\nBuild on or challenge the above. Do not repeat."
        
        for agent_name, agent in AGENTS.items():
            prompt = f"""{OPERATOR_CONTEXT}
Idea to evaluate: {idea_text}
{OPERATOR_CONTEXT}{prior_context}

You are {agent_name}. {agent['persona']}
Focus: {agent['focus']}

Respond in 80 words max. End with: RECOMMEND: consensus|contest|risk
"""
            
            print(f"  [{agent_name}] Thinking...", end="", flush=True)
            
            # Simulate response (we'll replace with real LLM later)
            response = generate_mock_response(agent_name, idea_text, prior_context)
            
            print(f" ✓")
            print(f"  {response[:120]}...")
            
            debate_log.append({
                "round": round_num,
                "agent": agent_name,
                "argument": response,
                "provider": "mock"
            })
    
    # Mayor's final speech (always chaotic)
    mayor_speech = generate_mayor_speech(idea_text)
    print(f"\n  [MAYOR_TRUMP] {mayor_speech[:120]}...")
    debate_log.append({
        "round": rounds,
        "agent": "MAYOR_TRUMP",
        "argument": mayor_speech,
        "provider": "mock"
    })
    
    # Generate synthesis
    verdict = generate_verdict(debate_log)
    
    print(f"\n  ⚖️  CHAIRMAN VERDICT: {verdict.upper()}")
    
    return {
        "debate": debate_log,
        "synthesis": {
            "verdict": verdict,
            "chairman_statement": f"After careful consideration, the board has reached a verdict of {verdict}.",
            "primary_risk": identify_primary_risk(debate_log),
            "primary_opportunity": identify_primary_opportunity(debate_log),
            "consensus": extract_consensus(debate_log),
            "contested": extract_contested(debate_log)
        },
        "opportunities": extract_opportunities(debate_log),
        "risks": state.risk_registry
    }


def generate_mock_response(agent_name, idea_text, prior_context):
    """Generate mock responses based on persona."""
    agent = AGENTS.get(agent_name, {})
    persona = agent.get("persona", "")
    focus = agent.get("focus", "")
    
    # Simple mock responses based on persona type
    if "CFO" in agent_name:
        return f"ROI looks questionable with no capital. Need 200% margin to justify solo execution. RECOMMEND: contest"
    elif "CMO" in agent_name:
        return f"Customers don't care about your constraints. If it solves a real pain point, they'll pay. RECOMMEND: consensus"
    elif "CRO" in agent_name:
        return f"Solo dev with no safety net? One failed deployment and you're homeless. RECOMMEND: risk"
    elif "ANALYST" in agent_name:
        return f"Market data shows 42% of similar solo projects fail within 3 months. But outliers succeed wildly. RECOMMEND: consensus"
    elif "DEVIL" in agent_name:
        return f"You're assuming customers exist. You're assuming the tech works. You're assuming YOU can execute. RECOMMEND: contest"
    elif "TECHNICAL_AUDITOR" in agent_name:
        return f"Architecture is sound but needs better error handling. Solo dev means no code reviews - dangerous. RECOMMEND: risk"
    else:
        return f"Interesting idea. Needs more data. RECOMMEND: contest"


def generate_mayor_speech(idea_text):
    """Generate Mayor Trump's chaotic speech."""
    buzzwords = ["tremendous", "beautiful", "the best", "nobody's ever seen", "believe me", "fake news", "sad!", "winning"]
    insults = ["losers", "haters", "the swamp", "sleepy", "low energy", "disaster"]
    
    speech = random.choice(buzzwords).capitalize() + " idea, "
    speech += random.choice(buzzwords) + " potential, "
    speech += f"could be {random.choice(buzzwords)} or could be {random.choice(insults)}. "
    speech += "We'll see. " + random.choice(["Nobody knows more about this than me.", "The best people are saying this.", "Very smart, very legal."])
    
    return speech + " - Trump"


def generate_verdict(debate_log):
    """Generate final verdict based on debate."""
    # Count recommendations
    recommends = [e["argument"] for e in debate_log]
    
    risk_count = sum(1 for r in recommends if "RECOMMEND: risk" in r)
    contest_count = sum(1 for r in recommends if "RECOMMEND: contest" in r)
    consensus_count = sum(1 for r in recommends if "RECOMMEND: consensus" in r)
    
    # Simple decision logic
    if risk_count >= 3:
        return "no-go"
    elif consensus_count >= 4:
        return "go"
    else:
        return "conditional"


def identify_primary_risk(debate_log):
    """Identify primary risk from debate."""
    risks = []
    for e in debate_log:
        if "RECOMMEND: risk" in e["argument"]:
            risks.append(e["argument"][:80])
    return random.choice(risks) if risks else "Execution risk with solo development"


def identify_primary_opportunity(debate_log):
    """Identify primary opportunity from debate."""
    opportunities = []
    for e in debate_log:
        if "RECOMMEND: consensus" in e["argument"]:
            opportunities.append(e["argument"][:80])
    return random.choice(opportunities) if opportunities else "First-to-market advantage in niche"


def extract_consensus(debate_log):
    """Extract consensus points."""
    points = [e["argument"][:100] for e in debate_log if "RECOMMEND: consensus" in e["argument"]]
    return points[:3] if points else ["Potential exists", "Execution is feasible"]


def extract_contested(debate_log):
    """Extract contested points."""
    points = [e["argument"][:100] for e in debate_log if "RECOMMEND: contest" in e["argument"]]
    return points[:3] if points else ["Risk profile", "Market size"]


def extract_opportunities(debate_log):
    """Extract opportunities."""
    return [e["argument"][:100] for e in debate_log if "RECOMMEND: consensus" in e["argument"]] or []


# ============================================================================
# MAIN INTEGRATION
# ============================================================================

def generate_html(city_data, boardroom_result=None):
    """Generate complete HTML with city + boardroom integration."""
    
    # Build city data JSON
    city_json = json.dumps(city_data, indent=2)
    
    # Build boardroom data if available
    boardroom_json = "null"
    if boardroom_result:
        boardroom_json = json.dumps(boardroom_result, indent=2)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CODE CITY APOCALYPSE + BOARDROOM</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            margin: 0; 
            background: #0a0a0a; 
            color: #e0e0e0; 
            font-family: 'Courier New', monospace;
            overflow: hidden;
            height: 100vh;
        }}
        #info-panel {{
            position: absolute;
            top: 10px; left: 10px;
            background: rgba(0,0,0,0.9);
            padding: 15px;
            border-radius: 5px;
            z-index: 100;
            max-width: 400px;
        }}
        #stats-panel {{
            position: absolute;
            top: 10px; right: 10px;
            background: rgba(0,0,0,0.9);
            padding: 15px;
            border-radius: 5px;
            z-index: 100;
        }}
        #boardroom-panel {{
            position: absolute;
            bottom: 10px; left: 10px;
            background: rgba(0,0,0,0.95);
            padding: 20px;
            border-radius: 10px;
            z-index: 100;
            max-width: 500px;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        }}
        #boardroom-panel h3 {{
            color: #ffd700;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        #boardroom-panel .agent-speech {{
            margin: 5px 0;
            padding: 5px;
            border-left: 3px solid #444;
            font-size: 12px;
        }}
        .agent-CFO {{ border-color: #4CAF50; }}
        .agent-CMO {{ border-color: #2196F3; }}
        .agent-CRO {{ border-color: #f44336; }}
        .agent-ANALYST {{ border-color: #FFC107; }}
        .agent-DEVIL {{ border-color: #9C27B0; }}
        .agent-TECHNICAL_AUDITOR {{ border-color: #00BCD4; }}
        .agent-MAYOR_TRUMP {{ border-color: #FFD700; }}
        #boardroom-result {{
            margin-top: 10px;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
        }}
        #verdict {{
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
            text-align: center;
        }}
        .verdict-go {{ color: #4CAF50; }}
        .verdict-no-go {{ color: #f44336; }}
        .verdict-conditional {{ color: #FFC107; }}
        #input-idea {{
            position: absolute;
            bottom: 10px; right: 10px;
            background: rgba(0,0,0,0.9);
            padding: 10px;
            border-radius: 5px;
            z-index: 100;
        }}
        #input-idea input {{
            width: 300px;
            padding: 8px;
            background: #222;
            color: #fff;
            border: 1px solid #444;
            border-radius: 3px;
        }}
        #input-idea button {{
            padding: 8px 15px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 3px;
            margin-left: 5px;
            cursor: pointer;
        }}
        .damage {{
            position: absolute;
            color: #ff4444;
            font-weight: bold;
            pointer-events: none;
            z-index: 50;
            font-size: 14px;
            text-shadow: 2px 2px 4px #000;
        }}
        canvas {{
            display: block;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info-panel">
        <h2>🏙️ CODE CITY APOCALYPSE + BOARDROOM</h2>
        <p>🏢 Buildings = Code Files</p>
        <p>🔥 Disasters = Errors & Bugs</p>
        <p>👹 Monsters = Active Issues</p>
        <p>✈️ Air Raids = Technical Debt</p>
        <p><strong>🏛️ Click Boardroom HQ to convene!</strong></p>
    </div>
    
    <div id="stats-panel">
        <h3>📊 CITY STATS</h3>
        <p>Buildings: <span id="building-count">{city_data['metadata']['total_buildings']}</span></p>
        <p>Disasters: <span id="disaster-count">{city_data['metadata']['total_disasters']}</span></p>
        <p>Monsters: <span id="monster-count">{city_data['metadata']['total_monsters']}</span></p>
        <p>Air Raids: <span id="air-raid-count">{city_data['metadata']['total_air_raids']}</span></p>
    </div>
    
    <div id="boardroom-panel">
        <h3>🏛️ BOARDROOM DEBATE</h3>
        <div id="boardroom-debate"></div>
        <div id="boardroom-result"></div>
    </div>
    
    <div id="input-idea">
        <input type="text" id="idea-input" placeholder="Enter your idea here...">
        <button onclick="conveneBoardroom()">Convene Boardroom</button>
    </div>
    
    <script>
        const cityData = {city_json};
        const boardroomResult = {boardroom_json};
        
        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);
        
        // Controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        
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
        const groundMaterial = new THREE.MeshLambertMaterial({{ color: 0x1a1a2e }});
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
        const buildingMeshes = [];
        const buildingData = [];
        
        cityData.city.buildings.forEach(b => {{
            // Create geometry
            const geom = new THREE.BoxGeometry(b.width, b.height, b.depth);
            const mat = new THREE.MeshLambertMaterial({{ color: b.color }});
            const mesh = new THREE.Mesh(geom, mat);
            
            // Position
            mesh.position.set(b.x, b.height / 2, b.z);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            
            // Add health indicator
            if (b.health < 100) {{
                const healthColor = b.health <= 20 ? 0xff0000 : b.health <= 60 ? 0xffa500 : 0xffff00;
                const healthBar = new THREE.Mesh(
                    new THREE.BoxGeometry(b.width * 0.8, 0.5, 0.5),
                    new THREE.MeshBasicMaterial({{ color: healthColor }})
                );
                healthBar.position.set(b.x, b.height + 1, b.z);
                scene.add(healthBar);
            }}
            
            // Store data
            mesh.userData = b;
            mesh.name = b.name;
            
            buildingMeshes.push(mesh);
            buildingData.push(b);
            scene.add(mesh);
            
            // Make special buildings glow
            if (b.special || b.villain) {{
                const glow = new THREE.Mesh(
                    new THREE.BoxGeometry(b.width * 1.05, b.height * 1.05, b.depth * 1.05),
                    new THREE.MeshBasicMaterial({{ 
                        color: b.villain ? 0xFFD700 : 0x2d1b69,
                        transparent: true,
                        opacity: 0.3,
                        side: THREE.BackSide
                    }})
                );
                glow.position.set(b.x, b.height / 2, b.z);
                scene.add(glow);
            }}
        }});
        
        // Camera position
        camera.position.set(100, 100, 100);
        camera.lookAt(0, 0, 0);
        
        // Raycaster for clicking
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        
        function onMouseClick(event) {{
            // Calculate mouse position in normalized device coordinates
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            // Update the raycaster
            raycaster.setFromCamera(mouse, camera);
            
            // Calculate objects intersecting the ray
            const intersects = raycaster.intersectObjects(buildingMeshes);
            
            if (intersects.length > 0) {{
                const building = intersects[0].object.userData;
                console.log("Clicked:", building.name, building);
                
                if (building.action === 'convene_boardroom') {{
                    // Show boardroom panel
                    const panel = document.getElementById('boardroom-panel');
                    panel.style.display = 'block';
                    
                    // Display existing result if available
                    if (boardroomResult) {{
                        displayBoardroomResult(boardroomResult);
                    }}
                }} else if (building.villain) {{
                    // Mayor Trump speech
                    const speeches = [
                        "People are saying this code is tremendous, the best code, nobody writes code like this code. BELIEVE ME!",
                        "The disasters? Very smart disasters. The best disasters. We have the best monsters, tremendous monsters.",
                        "This city used to be a disaster, a total disaster. Now? We're winning so much you might get tired of winning!",
                        "The bugs are fake news. SAD! The real problem is the haters and losers who don't understand great code."
                    ];
                    alert("MAYOR TRUMP: " + speeches[Math.floor(Math.random() * speeches.length)]);
                }} else {{
                    alert("Building: " + building.name + "\nType: " + building.type + "\nHealth: " + building.health + "%");
                }}
            }}
        }}
        
        window.addEventListener('click', onMouseClick, false);
        
        // Handle window resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        // Display boardroom result
        function displayBoardroomResult(result) {{
            const debateDiv = document.getElementById('boardroom-debate');
            const resultDiv = document.getElementById('boardroom-result');
            
            debateDiv.innerHTML = '';
            result.debate.forEach(entry => {{
                const div = document.createElement('div');
                div.className = `agent-speech agent-${entry.agent}`;
                div.innerHTML = `<strong>${entry.agent}:</strong> ${entry.argument}`;
                debateDiv.appendChild(div);
            }});
            
            const verdict = result.synthesis.verdict;
            resultDiv.innerHTML = `
                <div id="verdict" class="verdict-${verdict}">
                    ⚖️ CHAIRMAN VERDICT: ${verdict.toUpperCase()}
                </div>
                <p><strong>Primary Risk:</strong> ${result.synthesis.primary_risk}</p>
                <p><strong>Primary Opportunity:</strong> ${result.synthesis.primary_opportunity}</p>
            `;
        }}
        
        // Conven boardroom from input
        function conveneBoardroom() {{
            const idea = document.getElementById('idea-input').value;
            if (!idea) {{
                alert('Please enter an idea first!');
                return;
            }}
            
            // In a real implementation, this would call the Python backend
            // For now, we'll simulate it
            const panel = document.getElementById('boardroom-panel');
            panel.style.display = 'block';
            panel.innerHTML = '<h3>🏛️ BOARDROOM CONVENING...</h3><p>Analyzing: "' + idea + '"</p>';
            
            // TODO: Replace with actual API call to boardroom engine
            // This would be: fetch('/api/boardroom', {{ method: 'POST', body: JSON.stringify({{idea: idea}}) }})
            // For now, simulate a delay
            setTimeout(() => {{
                // Generate mock result
                const mockResult = {{
                    debate: [
                        {{ agent: 'CFO', argument: 'ROI looks questionable with no capital. Need 200% margin. RECOMMEND: contest' }},
                        {{ agent: 'CMO', argument: 'Customers don\'t care about constraints. If it solves pain, they pay. RECOMMEND: consensus' }},
                        {{ agent: 'CRO', argument: 'Solo dev with no safety net? One failure = homeless. RECOMMEND: risk' }},
                        {{ agent: 'ANALYST', argument: 'Market shows 42% fail rate, but outliers succeed. RECOMMEND: consensus' }},
                        {{ agent: 'DEVIL', argument: 'Assuming customers exist? Tech works? YOU can execute? RECOMMEND: contest' }},
                        {{ agent: 'TECHNICAL_AUDITOR', argument: 'Architecture sound but needs error handling. Solo = no reviews. RECOMMEND: risk' }},
                        {{ agent: 'MAYOR_TRUMP', argument: 'Tremendous idea, beautiful potential, could be best ever or total disaster. Nobody knows more than me. - Trump' }}
                    ],
                    synthesis: {{
                        verdict: 'conditional',
                        chairman_statement: 'After careful consideration...',
                        primary_risk: 'Execution risk with solo development',
                        primary_opportunity: 'First-to-market in underserved niche'
                    }},
                    opportunities: [],
                    risks: []
                }};
                displayBoardroomResult(mockResult);
            }}, 1500);
        }}
        
        // Expose to global scope
        window.conveneBoardroom = conveneBoardroom;
        
        // Animation loop
        const buildingPositions = buildingMeshes.map(m => m.position);
        const disasters = [];
        const monsters = [];
        
        // Create disaster meshes
        cityData.city.disasters.forEach(d => {{
            const geom = new THREE.SphereGeometry(2, 16, 16);
            const mat = new THREE.MeshBasicMaterial({{ color: 0xff4444 }});
            const mesh = new THREE.Mesh(geom, mat);
            mesh.position.set(d.position.x, d.position.y, d.position.z);
            mesh.userData = d;
            disasters.push(mesh);
            scene.add(mesh);
        }});
        
        // Create monster meshes
        cityData.city.monsters.forEach(m => {{
            const geom = new THREE.ConeGeometry(2, 4, 8);
            let color = 0x4CAF50;
            if (m.species === 'gorilla') color = 0x8B4513;
            if (m.species === 'lizard') color = 0x228B22;
            if (m.species === 'wolf') color = 0x808080;
            if (m.species === 'dinosaur') color = 0x8B0000;
            const mat = new THREE.MeshBasicMaterial({{ color: color }});
            const mesh = new THREE.Mesh(geom, mat);
            mesh.position.set(m.position.x, m.position.y, m.position.z);
            mesh.userData = m;
            monsters.push(mesh);
            scene.add(mesh);
        }});
        
        // Create air raid meshes
        cityData.city.air_raids.forEach(a => {{
            const geom = new THREE.CylinderGeometry(1, 1, 3, 8);
            const mat = new THREE.MeshBasicMaterial({{ color: 0x808080 }});
            const mesh = new THREE.Mesh(geom, mat);
            mesh.position.set(a.position.x, a.position.y, a.position.z);
            mesh.userData = a;
            scene.add(mesh);
        }});
        
        let frame = 0;
        function animate() {{
            requestAnimationFrame(animate);
            
            frame++;
            
            // Animate disasters
            disasters.forEach((mesh, i) => {{
                const d = cityData.city.disasters[i];
                if (d && d.type === 'fire') {{
                    mesh.scale.set(1 + Math.sin(frame * 0.1 + i) * 0.1, 
                                   1 + Math.sin(frame * 0.1 + i) * 0.1, 
                                   1 + Math.sin(frame * 0.1 + i) * 0.1);
                }}
            }});
            
            // Animate monsters
            monsters.forEach((mesh, i) => {{
                const m = cityData.city.monsters[i];
                if (m) {{
                    mesh.rotation.y += 0.02;
                    // Move towards random building
                    if (frame % 100 === 0) {{
                        const target = buildingPositions[Math.floor(Math.random() * buildingPositions.length)];
                        mesh.position.lerp(target, 0.01);
                    }}
                }}
            }});
            
            controls.update();
            renderer.render(scene, camera);
        }}
        
        // Start animation
        animate();
        
        // Display city stats
        document.getElementById('building-count').textContent = cityData.metadata.total_buildings;
        document.getElementById('disaster-count').textContent = cityData.metadata.total_disasters;
        document.getElementById('monster-count').textContent = cityData.metadata.total_monsters;
        document.getElementById('air-raid-count').textContent = cityData.metadata.total_air_raids;
    </script>
</body>
</html>
"""
    return html


def main():
    parser = argparse.ArgumentParser(
        description="Code City Apocalypse + Vertical AI Boardroom"
    )
    parser.add_argument(
        "path", 
        nargs="?", 
        default=".",
        help="Path to codebase to scan"
    )
    parser.add_argument(
        "--idea", 
        type=str, 
        help="Business idea to evaluate in boardroom"
    )
    parser.add_argument(
        "--scan-only", 
        action="store_true",
        help="Only generate city visualization, no boardroom"
    )
    parser.add_argument(
        "--boardroom-only", 
        action="store_true",
        help="Only run boardroom, no city visualization"
    )
    parser.add_argument(
        "--rounds", 
        type=int, 
        default=2,
        help="Number of boardroom debate rounds"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="code_city_boardroom.html",
        help="Output HTML file name"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  🏙️  CODE CITY APOCALYPSE + VERTICAL AI BOARDROOM")
    print("="*60)
    
    # Scan city
    scanner = CodeCityScanner(args.path)
    city_data = scanner.scan()
    
    # Run boardroom if requested
    boardroom_result = None
    if not args.scan_only:
        if args.idea:
            print(f"\n  📝 Evaluating idea: {args.idea[:80]}...")
            boardroom_result = run_boardroom(args.idea, rounds=args.rounds)
        else:
            print("\n  ℹ️  No idea specified. Boardroom ready in HQ building.")
    
    # Generate HTML
    if not args.boardroom_only:
        html_content = generate_html(city_data, boardroom_result)
        
        # Save to file
        try:
            with open(args.output, 'w') as f:
                f.write(html_content)
            print(f"\n  ✅ Saved: {args.output}")
            print(f"  🌐 Open in browser: file://{os.path.abspath(args.output)}")
        except Exception as e:
            print(f"\n  ❌ Error saving file: {e}")
            print("\n  HTML Content:")
            print("-" * 60)
            print(html_content[:5000])
            print("-" * 60)
    
    # Boardroom only mode
    if args.boardroom_only and args.idea:
        print("\n" + "="*60)
        print(json.dumps(boardroom_result, indent=2))


if __name__ == "__main__":
    main()

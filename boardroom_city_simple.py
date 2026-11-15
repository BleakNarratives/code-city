#!/usr/bin/env python3
"""
CODE CITY APOCALYPSE + VERTICAL AI BOARDROOM - Simple Version
==============================================================

Quick test: Scan codebase → Generate HTML with city + boardroom
Click Boardroom HQ to see the debate.

Usage:
  python boardroom_city_simple.py /path/to/codebase
  python boardroom_city_simple.py /path/to/codebase --idea "Your idea"
"""

import sys
import os
import json
import random
import argparse
from datetime import datetime
from pathlib import Path

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
        
        # Add Mayor Trump Tower
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
            'color': '#2d1b69',
            'windows': 0,
            'occupants': 6,
            'lines': 0,
            'size': 0,
            'special': True,
            'clickable': True,
            'action': 'convene_boardroom',
            'description': 'Click to convene the Vertical AI Boardroom'
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
                'total_air_raids': len(self.air_raids)
            },
            'city': {
                'buildings': self.buildings,
                'disasters': self.disasters,
                'monsters': self.monsters,
                'air_raids': self.air_raids
            }
        }


# ============================================================================
# BOARDROOM ENGINE
# ============================================================================

AGENTS = {
    "CFO": {"persona": "You are the CFO. Numbers only.", "focus": "unit economics, ROI"},
    "CMO": {"persona": "You are the CMO. Customer is north star.", "focus": "customer psychology"},
    "CRO": {"persona": "You are CRO. Find the landmine.", "focus": "failure modes"},
    "ANALYST": {"persona": "You are the Analyst. Cited data only.", "focus": "market data"},
    "DEVIL": {"persona": "You are Devil. Challenge consensus.", "focus": "assumptions"},
    "TECHNICAL_AUDITOR": {"persona": "You are Technical Auditor. Assess architecture, debt, scalability.", "focus": "scalability, tech debt, security"},
    "MAYOR_ANTI": {"persona": "You are Mayor Anti. Talk out your ass. Release monsters. Cause chaos. Comic relief. END with: - Anti", "focus": "disruption, chaos, anti-establishment"}
}

OPERATOR_CONTEXT = """OPERATOR CONSTRAINTS: capital=none, funding=none, team=1, model=solo skill-based"""


def run_boardroom(idea_text, rounds=2):
    """Run boardroom debate and return result."""
    from collections import defaultdict
    
    debate_log = []
    
    print("\n" + "="*60)
    print("  BOARDROOM DEBATE")
    print("="*60)
    print(f"  Idea: {idea_text[:60]}...")
    print()
    
    for round_num in range(1, rounds + 1):
        print(f"  ROUND {round_num}")
        
        for agent_name, agent in AGENTS.items():
            print(f"  [{agent_name}]...", end=" ", flush=True)
            response = generate_mock_response(agent_name, idea_text)
            print("OK")
            debate_log.append({
                "round": round_num,
                "agent": agent_name,
                "argument": response
            })
    
    verdict = generate_verdict(debate_log)
    print(f"\n  VERDICT: {verdict.upper()}")
    
    return {
        "debate": debate_log,
        "synthesis": {
            "verdict": verdict,
            "chairman_statement": f"Verdict: {verdict}",
            "primary_risk": identify_primary_risk(debate_log),
            "primary_opportunity": identify_primary_opportunity(debate_log)
        }
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
# HTML GENERATION (without f-string issues)
# ============================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>CODE CITY + BOARDROOM</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { margin: 0; background: #0a0a0a; color: #e0e0e0; font-family: monospace; overflow: hidden; height: 100vh; }
        #info { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.9); padding: 15px; border-radius: 5px; z-index: 100; max-width: 400px; }
        #stats { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.9); padding: 15px; border-radius: 5px; z-index: 100; }
        #boardroom-panel { position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.95); padding: 20px; border-radius: 10px; z-index: 100; max-width: 500px; max-height: 300px; overflow-y: auto; display: none; }
        #boardroom-panel h3 { color: #ffd700; margin-bottom: 10px; }
        .agent-speech { margin: 5px 0; padding: 5px; border-left: 3px solid #444; font-size: 12px; }
        .agent-CFO { border-color: #4CAF50; }
        .agent-CMO { border-color: #2196F3; }
        .agent-CRO { border-color: #f44336; }
        .agent-ANALYST { border-color: #FFC107; }
        .agent-DEVIL { border-color: #9C27B0; }
        .agent-TECHNICAL_AUDITOR { border-color: #00BCD4; }
        .agent-MAYOR_ANTI { border-color: #FFD700; }
        #input-idea { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.9); padding: 10px; border-radius: 5px; z-index: 100; }
        #input-idea input { width: 300px; padding: 8px; background: #222; color: #fff; border: 1px solid #444; border-radius: 3px; }
        #input-idea button { padding: 8px 15px; background: #4CAF50; color: white; border: none; border-radius: 3px; margin-left: 5px; cursor: pointer; }
        #verdict { font-size: 18px; font-weight: bold; margin: 10px 0; text-align: center; }
        .verdict-go { color: #4CAF50; }
        .verdict-no-go { color: #f44336; }
        .verdict-conditional { color: #FFC107; }
        canvas { display: block; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <h2>CODE CITY + BOARDROOM</h2>
        <p>Buildings = Files | Disasters = Errors</p>
        <p><strong>Click Boardroom HQ to convene!</strong></p>
    </div>
    <div id="stats">
        <h3>CITY STATS</h3>
        <p>Buildings: <span id="building-count">0</span></p>
        <p>Disasters: <span id="disaster-count">0</span></p>
        <p>Monsters: <span id="monster-count">0</span></p>
        <p>Air Raids: <span id="air-raid-count">0</span></p>
    </div>
    <div id="boardroom-panel">
        <h3>BOARDROOM DEBATE</h3>
        <div id="boardroom-debate"></div>
        <div id="boardroom-result"></div>
    </div>
    <div id="input-idea">
        <input type="text" id="idea-input" placeholder="Enter your idea...">
        <button onclick="conveneBoardroom()">Convene</button>
    </div>
    <script>
'''

HTML_JAVASCRIPT = '''
        // Parse city data
        const cityData = CITY_DATA_PLACEHOLDER;
        const boardroomResult = BOARDROOM_RESULT_PLACEHOLDER;
        
        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
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
        const buildingMeshes = [];
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
                        "People are saying this code is tremendous, the best code!",
                        "The disasters? Very smart disasters. The best monsters.",
                        "We\'re winning so much you might get tired of winning!",
                        "The bugs are fake news. SAD!"
                    ];
                    alert("MAYOR TRUMP: " + speeches[Math.floor(Math.random() * speeches.length)]);
                } else {
                    alert("Building: " + building.name + "\nType: " + building.type + "\nHealth: " + building.health + "%");
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
        
        // Display boardroom result
        function displayBoardroomResult(result) {
            const debateDiv = document.getElementById("boardroom-debate");
            const resultDiv = document.getElementById("boardroom-result");
            debateDiv.innerHTML = "";
            result.debate.forEach(entry => {
                var div = document.createElement("div");
                div.className = "agent-speech agent-" + entry.agent;
                div.innerHTML = "<strong>" + entry.agent + ":</strong> " + entry.argument;
                debateDiv.appendChild(div);
            });
            const verdict = result.synthesis.verdict;
            resultDiv.innerHTML = "<div id=\'verdict\' class=\'verdict-" + verdict + "\'>VERDICT: " + verdict.toUpperCase() + "</div><p><strong>Risk:</strong> " + result.synthesis.primary_risk + "</p><p><strong>Opportunity:</strong> " + result.synthesis.primary_opportunity + "</p>";
        }
        
        // Convene boardroom
        function conveneBoardroom() {
            const idea = document.getElementById("idea-input").value;
            if (!idea) { alert("Enter an idea first!"); return; }
            const panel = document.getElementById("boardroom-panel");
            panel.style.display = "block";
            panel.innerHTML = "<h3>BOARDROOM CONVENING...</h3><p>Analyzing: " + idea + "</p>";
            // TODO: Replace with actual API call
            setTimeout(function() {
                var mockResult = {
                    debate: [
                        {agent: "CFO", argument: "ROI questionable with no capital. Need 200% margin. RECOMMEND: contest"},
                        {agent: "CMO", argument: "Customers pay for pain point solutions. RECOMMEND: consensus"},
                        {agent: "CRO", argument: "Solo dev = no safety net. One failure = homeless. RECOMMEND: risk"},
                        {agent: "ANALYST", argument: "42% fail rate but outliers succeed wildly. RECOMMEND: consensus"},
                        {agent: "DEVIL", argument: "Assuming customers exist? Tech works? YOU can execute? RECOMMEND: contest"},
                        {agent: "TECHNICAL_AUDITOR", argument: "Architecture sound but needs error handling. RECOMMEND: risk"},
                        {agent: "MAYOR_ANTI", argument: "Tremendous idea, beautiful potential. Nobody does it better. - Anti"}
                    ],
                    synthesis: {
                        verdict: "conditional",
                        chairman_statement: "Verdict: conditional",
                        primary_risk: "Execution risk with solo development",
                        primary_opportunity: "First-to-market advantage in niche"
                    }
                };
                displayBoardroomResult(mockResult);
            }, 1000);
        }
        
        window.conveneBoardroom = conveneBoardroom;
        
        // Animation
        let frame = 0;
        function animate() {
            requestAnimationFrame(animate);
            frame++;
            controls.update();
            renderer.render(scene, camera);
        }
        animate();
        
        // Stats
        document.getElementById("building-count").textContent = cityData.metadata.total_buildings;
        document.getElementById("disaster-count").textContent = cityData.metadata.total_disasters;
        document.getElementById("monster-count").textContent = cityData.metadata.total_monsters;
        document.getElementById("air-raid-count").textContent = cityData.metadata.total_air_raids;
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
        description="Code City Apocalypse + Vertical AI Boardroom"
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
        help="Idea to evaluate"
    )
    parser.add_argument(
        "--rounds", 
        type=int, 
        default=2,
        help="Boardroom rounds"
    )
    parser.add_argument(
        "--output", 
        type=str,
        default="code_city_boardroom.html",
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
    print("="*60)
    
    # Scan city
    scanner = CodeCityScanner(args.path)
    city_data = scanner.scan()
    
    # Run boardroom if idea provided
    boardroom_result = None
    if args.idea and not args.scan_only:
        print(f"\n  Evaluating: {args.idea[:60]}...")
        boardroom_result = run_boardroom(args.idea, rounds=args.rounds)
    
    # Generate HTML
    html_content = generate_html(city_data, boardroom_result)
    
    # Save
    try:
        with open(args.output, 'w') as f:
            f.write(html_content)
        print(f"\n  SAVED: {args.output}")
        print(f"  Open: file://{os.path.abspath(args.output)}")
    except Exception as e:
        print(f"\n  ERROR: {e}")


if __name__ == "__main__":
    main()

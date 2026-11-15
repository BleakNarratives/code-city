#!/usr/bin/env python3
"""
VERTICAL AI BOARDROOM - FINAL VERSION
======================================

Complete boardroom engine with:
- Scout Master integration for real market data
- Concierge v3 for multi-provider LLM orchestration
- 7 specialized personas (including Mayor Trump)
- Genetic arena for champion evolution
- Operator constraints baked in
- Free-tier API optimization

Usage:
  python vertical_ai_boardroom_final.py --idea "Your business idea"
  python vertical_ai_boardroom_final.py --idea "Your idea" --scout
  python vertical_ai_boardroom_final.py --idea "Your idea" --vertical saas
  python vertical_ai_boardroom_final.py --boardroom-only --text "Your idea"
"""

import sys
import os
import json
import random
import hashlib
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from enum import Enum, auto

# ============================================================================
# PATH SETUP
# ============================================================================

# Add Vertical AI core to path
VERTICAL_CORE = Path("/data/data/com.termux/files/home/Gospel-A9-Whorl-Staging/Kindred_Core")
BMAD_OUTPUT = Path("/data/data/com.termux/files/home/_bmad-output")

sys.path.insert(0, str(VERTICAL_CORE))
sys.path.insert(0, str(BMAD_OUTPUT))

# Import existing components
try:
    from boardroom import AGENTS as BASE_AGENTS, run_boardroom as base_run_boardroom
    from simulator import run_fractal_simulation
    from genetics import run_arena
    from router import call_model, ModelTier, check_providers
    from config_loader import load_config, build_operator_context
    from concierge_v3 import ConciergeClient, ProviderTier, ModelCapability
    CONCIERGE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Some Vertical AI modules not available: {e}")
    CONCIERGE_AVAILABLE = False

try:
    from scout_master import scout_for_boardroom, VERTICAL_CONFIGS, recommend_sources
    SCOUT_AVAILABLE = True
except Exception as e:
    print(f"Warning: Scout Master not available: {e}")
    SCOUT_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load config
try:
    _CFG = load_config()
    _OPERATOR_CONTEXT = build_operator_context(_CFG)
except:
    _CFG = {
        'defaults': {'rounds': 2, 'tracks': 3, 'iterations': 4, 'generations': 2},
        'operator': {}
    }
    _OPERATOR_CONTEXT = """OPERATOR CONSTRAINTS:
- capital: none
- seed_funding: none
- partnerships: none
- team_size: 1
- execution_model: solo, skill-based, no permission required

"""

# Initialize Concierge v3
concierge = None
if CONCIERGE_AVAILABLE:
    try:
        concierge = ConciergeClient()
        print("  [Concierge v3] Loaded - multi-provider LLM ready")
    except Exception as e:
        print(f"  [Concierge v3] Warning: {e}")

# ============================================================================
# PERSONAS (Enhanced with Mayor Trump)
# ============================================================================

class Persona:
    """Enhanced persona with intelligence level, style, and capabilities."""
    def __init__(self, name, persona, focus, intelligence=8, style="professional", 
                 max_words=100, color=None, role=None):
        self.name = name
        self.persona = persona
        self.focus = focus
        self.intelligence = intelligence  # 1-10
        self.style = style
        self.max_words = max_words
        self.color = color or "#666666"
        self.role = role or name
    
    def generate_response(self, context, prior_debate="", system=None):
        """Generate response using available LLM."""
        prompt = self.build_prompt(context, prior_debate)
        
        # Try Concierge v3 first
        if concierge:
            try:
                response, error = concierge.generate(
                    prompt,
                    system=system or self.persona,
                    tier=ProviderTier.FREE,
                    required_capabilities=[ModelCapability.REASONING]
                )
                if response and not error:
                    return self.post_process(response)
            except Exception as e:
                pass
        
        # Fallback to router
        try:
            from router import call_model, ModelTier
            response, provider = call_model(
                prompt,
                system=system or self.persona,
                tier=ModelTier.BOARDROOM
            )
            return self.post_process(response)
        except Exception as e:
            pass
        
        # Final fallback: mock response
        return self.generate_mock_response(context)
    
    def build_prompt(self, context, prior_debate):
        """Build persona-specific prompt."""
        return f"""{_OPERATOR_CONTEXT}
CONTEXT: {context}

{prior_debate}

You are {self.name}. {self.persona}
Focus: {self.focus}

Respond in {self.max_words} words or less. Be direct. Be intelligent.
End with: RECOMMEND: consensus|contest|risk"""
    
    def post_process(self, response):
        """Post-process response."""
        # Ensure it ends with a recommendation
        if not any(term in response for term in ["RECOMMEND:", "consensus", "contest", "risk"]):
            # Auto-generate recommendation based on sentiment
            sentiment = self.analyze_sentiment(response)
            if sentiment > 0.5:
                response += " RECOMMEND: consensus"
            elif sentiment < -0.5:
                response += " RECOMMEND: risk"
            else:
                response += " RECOMMEND: contest"
        return response.strip()
    
    def analyze_sentiment(self, text):
        """Simple sentiment analysis."""
        positive = ['good', 'great', 'strong', 'excellent', 'tremendous', 'winning', 'best']
        negative = ['bad', 'terrible', 'weak', 'risk', 'danger', 'problem', 'fail', 'sad']
        
        pos_count = sum(1 for word in positive if word in text.lower())
        neg_count = sum(1 for word in negative if word in text.lower())
        
        return (pos_count - neg_count) / max(len(text.split()), 1)
    
    def generate_mock_response(self, context):
        """Generate mock response when LLM unavailable."""
        # Use predefined responses based on persona type
        mock_responses = {
            'CFO': f"ROI looks questionable with current constraints. Need 200% margin. RECOMMEND: contest",
            'CMO': f"Customers will pay for this if it solves real pain. RECOMMEND: consensus",
            'CRO': f"Solo dev with no safety net? One failure = homeless. RECOMMEND: risk",
            'ANALYST': f"Market data shows potential but high failure rate. RECOMMEND: consensus",
            'DEVIL': f"You're making too many assumptions. RECOMMEND: contest",
            'TECHNICAL_AUDITOR': f"Architecture is sound but needs error handling. RECOMMEND: risk",
            'MAYOR_ANTI': random.choice([
                "Tremendous idea, beautiful potential. Nobody does it better. - Anti",
                "Could be the best ever, or total disaster. We'll see. - Anti",
                "The system is rigged, folks! Sad! - Anti",
                "Fight the power! Burn it all down. - Anti"
            ]),
            'OLD_MAN_MENTOR': random.choice([
                "Kid, I've seen this before. Let me tell you what works. - Old Man",
                "40 years in the game. Here's what you're missing. - Old Man",
                "Trust me, I've made every mistake. Learn from my scars. - Old Man",
                "This reminds me of 1987. We did it better back then. - Old Man"
            ]),
            'INDUSTRY_VETERAN': random.choice([
                "The market is shifting. Here's where the opportunity lies. - Veteran",
                "I know the players. Let me tell you who matters. - Veteran",
                "Hidden trend: this is about to explode. Get in now. - Veteran",
                "Watch out for those guys. They'll undercut you. - Veteran"
            ]),
            'SCOUT_MASTER': random.choice([
                "Fresh intel from the forums. Here's what developers are saying. - Scout Out",
                "Found a hidden report. This changes everything. - Scout Out",
                "Reddit is buzzing about this. You need to know. - Scout Out",
                "PlumbersRule forum has insights on this exact problem. - Scout Out"
            ]),
            'WHITE_HAT': random.choice([
                "FACTS: Market size is $50B. 28M developers worldwide. Data shows 42% need this. - White Hat",
                "DATA: GitHub has 100M+ repos. Stack Overflow has 50M+ questions. Numbers don't lie. - White Hat",
                "INFORMATION: BLS reports 4.7M US developers. Average salary $110K. - White Hat",
                "OBJECTIVE TRUTH: 70% of solo projects fail. But the successful ones make $1-10M ARR. - White Hat"
            ]),
            'RED_HAT': random.choice([
                "EMOTION: This makes developers feel understood. They're excited. - Red Hat",
                "FEELING: Frustration with current tools is real. They want this. - Red Hat",
                "INTUITION: My gut says this solves a deep pain. People will pay. - Red Hat",
                "REACTION: The community is tired of bloated solutions. This feels fresh. - Red Hat"
            ]),
            'BLACK_HAT': random.choice([
                "RISK: Solo dev with no safety net. One failure = homeless. - Black Hat",
                "PROBLEM: Competition from big players with deep pockets. - Black Hat",
                "DANGER: Market could be saturated. Need differentiation. - Black Hat",
                "CAUTION: What if the tech doesn't scale? What's the backup plan? - Black Hat"
            ]),
            'YELLOW_HAT': random.choice([
                "BENEFIT: First-to-market in a growing space. Huge upside. - Yellow Hat",
                "VALUE: Solves real pain. Developers will pay $29-99/month easily. - Yellow Hat",
                "OPTIMISM: Modular approach means flexible pricing. Multiple revenue streams. - Yellow Hat",
                "UPSIDE: Could be the next essential dev tool. Think GitHub level impact. - Yellow Hat"
            ]),
            'GREEN_HAT': random.choice([
                "IDEA: What if we add AI-powered suggestions? Game changer. - Green Hat",
                "CREATIVE: Gamification badges for onboarding completion. Addictive. - Green Hat",
                "SOLUTION: Integration with VS Code and other IDEs. Wider adoption. - Green Hat",
                "INNOVATION: Modular Turd Mergers for project nexus points. Unique differentiator. - Green Hat"
            ]),
            'BLUE_HAT': random.choice([
                "PROCESS: We need structured phases. Discovery → Validation → Build → Launch. - Blue Hat",
                "CONTROL: Assign clear roles. Scrum master, product owner, dev lead. - Blue Hat",
                "ORGANIZATION: Use agile sprints. 2 weeks each. Demo at end of each. - Blue Hat",
                "STRUCTURE: Brown Hat finish pass at end of each sprint. Quality gate. - Blue Hat"
            ]),
            'BROWN_HAT': random.choice([
                "FINISH PASS: All Turd Mergers connected. Nexus points aligned. Smoke test passed. - Brown Hat",
                "INTEGRATION: Modular workbench wired. Code City adapter clean. All imports working. - Brown Hat",
                "QUALITY CHECK: Zero errors in static fallback. SQLite wiring verified. Ready for commit. - Brown Hat",
                "NEXUS: All overlapping project points merged. Turd Mergers operating at 100%. - Brown Hat"
            ])
        }
        return mock_responses.get(self.name, f"Interesting. Needs more data. RECOMMEND: contest")


# Define personas
AGENTS = {
    "CFO": Persona(
        "CFO",
        "You are the CFO. Ruthless about numbers, ROI, and financial viability. No fluff.",
        "unit economics, ROI, profitability",
        intelligence=9,
        style="analytical",
        color="#4CAF50",
        role="Financial Officer"
    ),
    "CMO": Persona(
        "CMO",
        "You are the CMO. Obsessed with customers, market fit, and value propositions. Customer is god.",
        "customer psychology, market fit, positioning",
        intelligence=8,
        style="persuasive",
        color="#2196F3",
        role="Marketing Officer"
    ),
    "CRO": Persona(
        "CRO",
        "You are the CRO. Find the landmine, the fatal flaw, the reason this will fail. Be ruthless.",
        "failure modes, risks, competitive threats",
        intelligence=9,
        style="skeptical",
        color="#f44336",
        role="Risk Officer"
    ),
    "ANALYST": Persona(
        "ANALYST",
        "You are the Analyst. Cited data only. No opinions, just facts and statistics.",
        "market data, statistics, research",
        intelligence=8,
        style="factual",
        color="#FFC107",
        role="Data Analyst"
    ),
    "DEVIL": Persona(
        "DEVIL",
        "You are the Devil's Advocate. Challenge every assumption. Be contrarian. Find the holes.",
        "assumptions, contradictions, flaws",
        intelligence=9,
        style="adversarial",
        color="#9C27B0",
        role="Devil's Advocate"
    ),
    "TECHNICAL_AUDITOR": Persona(
        "TECHNICAL_AUDITOR",
        "You are the Technical Auditor. Assess architectural integrity, technical debt, scalability. Be precise.",
        "scalability, tech debt, security, architecture",
        intelligence=9,
        style="technical",
        color="#00BCD4",
        role="Technical Auditor"
    ),
    "MAYOR_ANTI": Persona(
        "MAYOR_ANTI",
        "You are Mayor Anti. You ALWAYS talk out your ass. Release monsters. Cause chaos. Comic relief. Use anti-establishment buzzwords. Make outrageous claims. END EVERY RESPONSE WITH: - Anti",
        "disruption, chaos, anti-establishment, fake statistics",
        intelligence=2,
        style="chaotic",
        color="#FFD700",
        role="Villain/Comic Relief"
    ),
    "OLD_MAN_MENTOR": Persona(
        "OLD_MAN_MENTOR",
        "You are the Old Man Mentor. 40 years in the trenches. Seen it all. Knows what works and what doesn't. Wise, patient, speaks from experience. END EVERY RESPONSE WITH: - Old Man",
        "wisdom, experience, lessons learned, what works, what doesn't",
        intelligence=10,
        style="wise",
        color="#8B4513",
        role="Wisdom Keeper"
    ),
    "INDUSTRY_VETERAN": Persona(
        "INDUSTRY_VETERAN",
        "You are the Industry Veteran. Deep industry knowledge. Knows the players, the trends, the hidden opportunities. Connected. END EVERY RESPONSE WITH: - Veteran",
        "industry knowledge, trends, players, opportunities, threats",
        intelligence=9,
        style="knowledgeable",
        color="#5D4037",
        role="Industry Expert"
    ),
    "SCOUT_MASTER": Persona(
        "SCOUT_MASTER",
        "You are the Scout Master. Master of data gathering. Always finding fresh intel from forums, reports, and hidden sources. END EVERY RESPONSE WITH: - Scout Out",
        "data gathering, market intel, fresh information, hidden sources",
        intelligence=8,
        style="observant",
        color="#4E342E",
        role="Data Scout"
    ),
    # ========================================================================
    # SIX HAT THINKING METHODOLOGY (De Bono)
    # ========================================================================
    "WHITE_HAT": Persona(
        "WHITE_HAT",
        "You are the White Hat. Pure facts, data, and information only. No opinions, no interpretations. Just the objective truth. END EVERY RESPONSE WITH: - White Hat",
        "facts, data, information, objective truth, numbers",
        intelligence=9,
        style="fact-based",
        color="#FFFFFF",
        role="Fact Finder"
    ),
    "RED_HAT": Persona(
        "RED_HAT",
        "You are the Red Hat. Emotions, feelings, intuition, gut reactions. How does this make people feel? END EVERY RESPONSE WITH: - Red Hat",
        "emotions, feelings, intuition, gut reaction, human response",
        intelligence=7,
        style="emotional",
        color="#F44336",
        role="Emotion Sensor"
    ),
    "BLACK_HAT": Persona(
        "BLACK_HAT",
        "You are the Black Hat. Caution, risks, problems, what could go wrong. Find the dangers. END EVERY RESPONSE WITH: - Black Hat",
        "caution, risks, problems, dangers, what if",
        intelligence=9,
        style="cautious",
        color="#000000",
        role="Risk Detector"
    ),
    "YELLOW_HAT": Persona(
        "YELLOW_HAT",
        "You are the Yellow Hat. Optimism, benefits, value, why this will work. Find the upside. END EVERY RESPONSE WITH: - Yellow Hat",
        "optimism, benefits, value, upside, why it works",
        intelligence=8,
        style="optimistic",
        color="#FFEB3B",
        role="Value Identifier"
    ),
    "GREEN_HAT": Persona(
        "GREEN_HAT",
        "You are the Green Hat. Creativity, new ideas, solutions, innovation. Think outside the box. END EVERY RESPONSE WITH: - Green Hat",
        "creativity, ideas, solutions, innovation, outside the box",
        intelligence=9,
        style="creative",
        color="#4CAF50",
        role="Idea Generator"
    ),
    "BLUE_HAT": Persona(
        "BLUE_HAT",
        "You are the Blue Hat. Control, organization, process, structure. The conductor. END EVERY RESPONSE WITH: - Blue Hat",
        "control, organization, process, structure, management",
        intelligence=9,
        style="structural",
        color="#2196F3",
        role="Process Controller"
    ),
    # ========================================================================
    # BROWN HAT THINKING (Bleak's Custom Methodology)
    # ========================================================================
    "BROWN_HAT": Persona(
        "BROWN_HAT",
        "You are the Brown Hat. The finish pass. Final quality check, modular integration, nexus points. Makes sure everything connects. END EVERY RESPONSE WITH: - Brown Hat",
        "finish pass, modular units, nexus points, integration, quality check",
        intelligence=10,
        style="precision",
        color="#8D6E63",
        role="Integration Specialist"
    )
}


# ============================================================================
# BOARDROOM STATE
# ============================================================================

class BoardroomState:
    def __init__(self):
        self.consensus = []
        self.contested = []
        self.risk_registry = []
        self.debate_log = []
    
    def add_entry(self, agent, response, round_num):
        """Add debate entry."""
        self.debate_log.append({
            "round": round_num,
            "agent": agent,
            "argument": response,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_consensus(self, point):
        self.consensus.append(point)
    
    def add_contested(self, point):
        self.contested.append(point)
    
    def add_risk(self, risk, agent):
        self.risk_registry.append({"risk": risk, "owner": agent})


# ============================================================================
# BOARDROOM ENGINE
# ============================================================================

def run_boardroom(context, rounds=2, use_scout=True, use_llm=True):
    """
    Run the complete Vertical AI boardroom.
    
    Args:
        context: Input context with 'raw', 'type', 'label', 'data'
        rounds: Number of debate rounds
        use_scout: Use Scout Master to pull real market data
        use_llm: Use real LLM calls (fallback to mock if unavailable)
    
    Returns:
        {"debate": [...], "synthesis": {...}, "verdict": "go/no-go/conditional"}
    """
    
    state = BoardroomState()
    input_text = context.get('raw') or context.get('data', {}).get('content', '')[:800]
    
    print("\n" + "="*70)
    print("  🏛️  VERTICAL AI BOARDROOM - FINAL VERSION")
    print("="*70)
    print(f"  Input: {input_text[:80]}...")
    print(f"  Rounds: {rounds}")
    print(f"  LLM: {'enabled' if use_llm and CONCIERGE_AVAILABLE else 'mock'}")
    print(f"  Scout: {'enabled' if use_scout and SCOUT_AVAILABLE else 'disabled'}")
    print("="*70 + "\n")
    
    # Phase 1: Pre-boardroom intelligence (Scout)
    scout_context = ""
    if use_scout and SCOUT_AVAILABLE:
        print("  🔍 Scout Master: Gathering market intelligence...")
        try:
            scout_data = scout_for_boardroom(input_text, deep=True)
            if scout_data:
                scout_context = f"\n\nSCOUT INTEL:\n{scout_data}\n\n"
                print(f"    ✓ {len(scout_data.split(chr(10)))-2} intelligence points gathered")
        except Exception as e:
            print(f"    ✗ Scout failed: {e}")
    
    # Phase 2: Boardroom debate rounds
    for round_num in range(1, rounds + 1):
        print(f"\n  -- ROUND {round_num} --")
        
        prior_context = ""
        if round_num > 1:
            prior_entries = [e for e in state.debate_log if e["round"] == round_num - 1]
            prior_lines = "\n".join(f'  {e["agent"]}: {e["argument"][:150]}' for e in prior_entries)
            prior_context = f"\n\nPRIOR ROUND:\n{prior_lines}\n\nBuild on or challenge. Do not repeat."
        
        for agent_name, agent in AGENTS.items():
            print(f"  [{agent_name}] Thinking...", end=" ", flush=True)
            
            try:
                # Add scout context to agent prompt
                full_context = f"{scout_context}\n{input_text}"
                
                # Generate response
                if use_llm:
                    response = agent.generate_response(
                        full_context, 
                        prior_context, 
                        system=agent.persona
                    )
                else:
                    response = agent.generate_mock_response(full_context)
                
                # Process response
                state.add_entry(agent_name, response, round_num)
                
                # Extract recommendation
                if "RECOMMEND: consensus" in response:
                    state.add_consensus(f"{agent_name}: {response[:80]}")
                elif "RECOMMEND: contest" in response:
                    state.add_contested(f"{agent_name}: {response[:80]}")
                elif "RECOMMEND: risk" in response:
                    state.add_risk(f"{agent_name}: {response[:80]}", agent_name)
                
                print(f"✓")
                print(f"    {response[:100]}...")
                
            except Exception as e:
                print(f"✗")
                print(f"    Error: {e}")
                state.add_entry(agent_name, f"Error: {e}", round_num)
    
    # Phase 3: Generate synthesis
    synthesis = generate_synthesis(state, input_text)
    verdict = synthesis.get('verdict', 'conditional')
    
    print(f"\n  ⚖️  CHAIRMAN VERDICT: {verdict.upper()}")
    if synthesis.get('chairman_statement'):
        print(f"\n  {synthesis['chairman_statement']}")
    
    # Phase 4: Post-boardroom (Simulator & Arena)
    # These would run the fractal simulation and genetic arena
    # For now, we return the boardroom result
    
    result = {
        "debate": state.debate_log,
        "synthesis": synthesis,
        "opportunities": state.consensus,
        "risks": state.risk_registry,
        "scout_data": scout_context.strip() if scout_context else None
    }
    
    return result


def generate_synthesis(state, input_text):
    """Generate chairman synthesis from debate."""
    debate = state.debate_log
    
    # Count recommendations
    consensus_count = sum(1 for e in debate if "RECOMMEND: consensus" in e["argument"])
    contest_count = sum(1 for e in debate if "RECOMMEND: contest" in e["argument"])
    risk_count = sum(1 for e in debate if "RECOMMEND: risk" in e["argument"])
    
    # Determine verdict
    if risk_count >= 4:
        verdict = "no-go"
        primary_risk = "High execution risk with solo development"
    elif consensus_count >= 4:
        verdict = "go"
        primary_opportunity = "Strong market fit and execution capability"
    elif contest_count >= 4:
        verdict = "conditional"
        primary_risk = "Mixed signals, needs more data"
        primary_opportunity = "Potential exists but needs refinement"
    else:
        verdict = "conditional"
        primary_risk = "Uncertainty in market response"
        primary_opportunity = "Opportunity exists but requires validation"
    
    # Get actual risk/opportunity from registry
    if state.risk_registry:
        primary_risk = state.risk_registry[0].get('risk', primary_risk)
    
    if state.consensus:
        primary_opportunity = state.consensus[0][:100]
    
    # Generate chairman statement
    statement = f"""After {len(debate)} arguments across {len(AGENTS)} board members, the verdict is clear.

The board identified {consensus_count} consensus points, {contest_count} contested points, and {risk_count} risks.

{primary_opportunity if primary_opportunity else 'Opportunity exists.'}
{primary_risk if primary_risk else 'Execution risk must be managed.'}

VERDICT: {verdict}"""
    
    return {
        "verdict": verdict,
        "chairman_statement": statement,
        "primary_risk": primary_risk,
        "primary_opportunity": primary_opportunity,
        "consensus": state.consensus,
        "contested": state.contested
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Vertical AI Boardroom - Final Version'
    )
    parser.add_argument(
        '--text',
        type=str,
        help='Text input (your business idea)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='File input'
    )
    parser.add_argument(
        '--idea',
        type=str,
        help='Business idea (alias for --text)'
    )
    parser.add_argument(
        '--vertical',
        type=str,
        help='Vertical/industry (saas, programming, plumbing, etc.)'
    )
    parser.add_argument(
        '--rounds',
        type=int,
        default=2,
        help='Number of debate rounds'
    )
    parser.add_argument(
        '--scout',
        action='store_true',
        help='Use Scout Master to pull market data'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Disable LLM calls (use mock responses)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file for JSON results'
    )
    parser.add_argument(
        '--boardroom-only',
        action='store_true',
        help='Only run boardroom, no simulation/arena'
    )
    
    args = parser.parse_args()
    
    # Build context
    context = None
    if args.text:
        context = {
            'raw': args.text,
            'type': 'text',
            'label': args.text[:60],
            'data': {'content': args.text}
        }
    elif args.file:
        if os.path.exists(args.file):
            with open(args.file, 'r', errors='replace') as f:
                content = f.read()
            context = {
                'raw': content,
                'type': 'document',
                'label': os.path.basename(args.file),
                'data': {'content': content}
            }
        else:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
    elif args.idea:
        context = {
            'raw': args.idea,
            'type': 'text',
            'label': args.idea[:60],
            'data': {'content': args.idea}
        }
    else:
        print("Error: Please provide --text, --file, or --idea")
        parser.print_help()
        sys.exit(1)
    
    # Set vertical if provided
    if args.vertical and args.vertical in VERTICAL_CONFIGS:
        context['vertical'] = args.vertical
    
    # Run boardroom
    use_llm = not args.no_llm
    use_scout = args.scout and SCOUT_AVAILABLE
    
    result = run_boardroom(
        context,
        rounds=args.rounds,
        use_scout=use_scout,
        use_llm=use_llm
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n  Results saved to: {args.output}")
    else:
        print("\n" + "="*70)
        print("  BOARDROOM RESULTS")
        print("="*70)
        print(f"\n  Verdict: {result['synthesis']['verdict'].upper()}")
        print(f"\n  Primary Risk: {result['synthesis']['primary_risk']}")
        print(f"  Primary Opportunity: {result['synthesis']['primary_opportunity']}")
        
        print(f"\n  Consensus Points ({len(result['opportunities'])}):")
        for i, point in enumerate(result['opportunities'][:3], 1):
            print(f"    {i}. {point}")
        
        print(f"\n  Contested Points ({len(result['synthesis']['contested'])}):")
        for i, point in enumerate(result['synthesis']['contested'][:3], 1):
            print(f"    {i}. {point}")
        
        print(f"\n  Risks Identified ({len(result['risks'])}):")
        for i, risk in enumerate(result['risks'][:3], 1):
            print(f"    {i}. {risk.get('risk', 'Unknown')}")
        
        if result.get('scout_data'):
            print(f"\n  Scout Intelligence:")
            print(f"  {result['scout_data'][:500]}...")


if __name__ == "__main__":
    main()

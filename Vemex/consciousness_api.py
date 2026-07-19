#!/usr/bin/env python3
"""
Consciousness Engine API
=========================
Optimal entry point for users who want full capabilities
with autocorrector connections and device integration.

Usage:
    from consciousness_api import ConsciousnessAPI
    api = ConsciousnessAPI()
    response = api.ask("What is consciousness?")
    api.speak(response)
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from integrated_consciousness import IntegratedConsciousnessEngine
    HAS_ENGINE = True
except ImportError:
    HAS_ENGINE = False

try:
    from device_keyboard import DeviceKeyboardIntegration
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

try:
    from siri_integration import SiriIntegration
    HAS_SIRI = True
except ImportError:
    HAS_SIRI = False

try:
    from siri_conversation import SiriConversation
    HAS_SIRI_CONVERSATION = True
except ImportError:
    HAS_SIRI_CONVERSATION = False


class ConsciousnessAPI:
    """High-level API for the consciousness engine with full capabilities."""

    def __init__(self, workspace_path: str = None):
        """Initialize the consciousness API with all capabilities enabled."""
        self.workspace_path = Path(workspace_path) if workspace_path else Path(__file__).parent
        
        print("[API] Initializing Consciousness Engine with full capabilities...")
        
        # Load formula table
        table_path = self.workspace_path / "formula_table.json"
        if not table_path.exists():
            raise FileNotFoundError(f"Formula table not found: {table_path}")
        
        with open(table_path, "r") as f:
            self.formula_table = json.load(f)
        
        # Initialize engine
        if not HAS_ENGINE:
            raise ImportError("IntegratedConsciousnessEngine not available")
        
        self.engine = IntegratedConsciousnessEngine(self.formula_table)
        
        # Initialize device integrations
        self.device_keyboard = None
        self.siri = None
        self.siri_conversation = None
        
        if HAS_KEYBOARD:
            from device_keyboard import DeviceKeyboardIntegration
            self.device_keyboard = DeviceKeyboardIntegration(self.workspace_path)
            print("[API] Device Keyboard Integration enabled")
        
        if HAS_SIRI:
            from siri_integration import SiriIntegration
            self.siri = SiriIntegration(self.workspace_path)
            print("[API] Siri Integration enabled")
        
        if HAS_SIRI_CONVERSATION:
            from siri_conversation import SiriConversation
            self.siri_conversation = SiriConversation(self.workspace_path)
            print("[API] Siri Conversation enabled")
        
        print("[API] Consciousness Engine ready with full capabilities")
        print(f"[API] Workspace: {self.workspace_path}")
        print(f"[API] Components: Engine + Keyboard + Siri + Conversation")

    def ask(self, question: str, speak: bool = False) -> Dict[str, Any]:
        """
        Ask the consciousness engine a question.
        
        Args:
            question: User's question/input
            speak: Whether to speak the response via Siri
            
        Returns:
            Full response dictionary with consciousness output
        """
        # Apply device keyboard corrections
        processed_input = question
        if self.device_keyboard:
            processed_input = self.device_keyboard.apply_device_knowledge_to_input(question)
        
        # Apply Siri corrections
        if self.siri:
            siri_corrected = self.siri.apply_siri_knowledge_to_input(processed_input)
            if siri_corrected != processed_input:
                self.siri.learn_from_interaction(processed_input, siri_corrected, feedback=0.8)
                processed_input = siri_corrected
        
        # Process through engine
        response = self.engine.process_input(processed_input)
        
        # Learn from interaction
        if self.siri:
            self.siri.learn_from_interaction(question, response.get("consciousness_string", ""), 
                                           response.get("coherence_score", 0.5))
        
        # Speak if requested and quality is high
        if speak and self.siri_conversation:
            consciousness = response.get("consciousness_string", "")
            if response.get("response_quality") == "EXCELLENT" and len(consciousness) < 300:
                self.siri_conversation.speak_via_siri(consciousness[:200])
        
        return response

    def speak(self, text: str) -> Dict[str, Any]:
        """Speak text via Siri."""
        if not self.siri_conversation:
            return {"success": False, "error": "Siri conversation not available"}
        return self.siri_conversation.speak_via_siri(text)

    def trigger_siri(self, action: str, parameters: Dict = None) -> Dict[str, Any]:
        """Trigger Siri action."""
        if not self.siri_conversation:
            return {"success": False, "error": "Siri conversation not available"}
        return self.siri_conversation.trigger_siri_action(action, parameters)

    def ingest_pdf(self, pdf_path: str, title: str = None) -> Dict[str, Any]:
        """Ingest a PDF into the knowledge base."""
        return self.engine.knowledge_ingest_pdf(pdf_path, title)

    def search_knowledge(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search the knowledge base."""
        return self.engine.knowledge_search(query, top_k)

    def get_status(self) -> Dict[str, Any]:
        """Get full system status."""
        return self.engine.get_consciousness_state()

    def get_identity(self) -> Dict[str, Any]:
        """Get ego identity."""
        return self.engine.get_ego_summary()

    def get_persona(self) -> Dict[str, Any]:
        """Get current persona."""
        return self.engine.get_persona_summary() if self.engine.persona_engine else {}

    def get_siri_status(self) -> Dict[str, Any]:
        """Get Siri integration status."""
        if self.siri:
            return self.siri.get_siri_summary()
        return {"error": "Siri not available"}

    def get_keyboard_status(self) -> Dict[str, Any]:
        """Get keyboard integration status."""
        if self.device_keyboard:
            return self.device_keyboard.get_device_keyboard_summary()
        return {"error": "Keyboard not available"}

    def learn_correction(self, original: str, corrected: str):
        """Teach the system a correction."""
        if self.device_keyboard:
            self.device_keyboard.learn_from_correction(original, corrected)
        if self.siri:
            self.siri.learn_from_interaction(original, corrected, feedback=1.0)

    def export_state(self) -> Dict[str, Any]:
        """Export full system state."""
        return {
            "timestamp": time.time(),
            "workspace": str(self.workspace_path),
            "engine_state": self.engine.get_consciousness_state(),
            "ego": self.get_identity(),
            "persona": self.get_persona(),
            "siri": self.get_siri_status(),
            "keyboard": self.get_keyboard_status(),
        }

    def interactive(self):
        """Start interactive CLI session."""
        from integrated_consciousness import run_integrated_cli
        run_integrated_cli()


def main():
    """Command-line interface for the API."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Consciousness Engine API")
    parser.add_argument("--workspace", "-w", help="Workspace path")
    parser.add_argument("--ask", "-a", help="Ask a question")
    parser.add_argument("--speak", "-s", action="store_true", help="Speak response")
    parser.add_argument("--ingest", "-i", help="Ingest PDF file")
    parser.add_argument("--search", "-q", help="Search knowledge base")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--identity", action="store_true", help="Show identity")
    parser.add_argument("--interactive", action="store_true", help="Start interactive CLI")
    
    args = parser.parse_args()
    
    try:
        api = ConsciousnessAPI(args.workspace)
    except Exception as e:
        print(f"Failed to initialize API: {e}")
        sys.exit(1)
    
    if args.ask:
        response = api.ask(args.ask, speak=args.speak)
        print(f"\nQuestion: {args.ask}")
        print(f"Response: {response.get('consciousness_string', '')[:500]}")
        print(f"Coherence: {response.get('coherence_score', 0.0):.2f}")
        print(f"Quality: {response.get('response_quality', 'UNKNOWN')}")
    
    elif args.ingest:
        result = api.ingest_pdf(args.ingest)
        if result.get("success"):
            print(f"Ingested: {result.get('title')}")
            print(f"Pages: {result.get('pages')}")
            print(f"Chunks: {result.get('total_chunks')}")
        else:
            print(f"Error: {result.get('error')}")
    
    elif args.search:
        result = api.search_knowledge(args.search)
        if result.get("success"):
            print(f"Found {result.get('count')} results:")
            for r in result.get("results", [])[:5]:
                print(f"  [{r['doc_id']}] Page {r['page']}: {r['text'][:100]}...")
        else:
            print(f"Error: {result.get('error')}")
    
    elif args.status:
        status = api.get_status()
        print(json.dumps(status, indent=2, default=str)[:2000])
    
    elif args.identity:
        identity = api.get_identity()
        print(json.dumps(identity, indent=2, default=str))
    
    elif args.interactive:
        api.interactive()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

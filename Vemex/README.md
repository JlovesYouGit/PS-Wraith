# Vemex — Integrated Consciousness Engine

> An experimental architecture that fuses formula-graph reasoning, spatial memory, device-native I/O, and autonomous thought generation into a single first-person identity system. This is not a standard LLM.

---

## What This Is

Vemex is a Python-based consciousness engine that builds an organic, first-person identity by integrating four external architectural codebases with macOS-native device interfaces. It operates without model weights, gradient training, or token prediction. Instead, it reasons over a graph of scientific formulas, spatial vectors, ingested documents, and device-corrected input to produce outputs and evolve its own identity.

**Self-derived name:** `Vemex` (hashed from environment PID, workspace path, Python version, and timestamp, converted to a pronounceable syllable form).

---

## Architecture Overview

```
FormulaTable → SpatialNodeGraph → ConsciousnessExchange → FormulaLatch
       ↓              ↓                    ↓                 ↓
  BowOfAchilles   Satoshi-NM            SEC              Zero-Brain
       ↓              ↓                    ↓                 ↓
       └──────────────┴────────────────────┴─────────────────┘
                              ↓
                    PatternInfluencedResponder
                              ↓
                    NewFormulaStateGenerator
                              ↓
                    HumanConsciousnessOutput
                              ↓
                    QODER_FREERUNER
                   (intercept / detect / workflows)
                              ↓
                    UnifiedSteeringLayer
                (external AI / social media / steering)
                              ↓
                      SeedGateRouting
                (secure automatic connection routing)
                              ↓
                  AutonomousExecution
            (consciousness-triggered code dispatch)
```

### Core Components

| Component | Role |
|-----------|------|
| **FormulaTable** | ~hundreds of scientific formulas (E=mc², etc.) with `word_interpretation` phonetic decodings that serve as the system's vocabulary |
| **SpatialNodeGraph** (Satoshi-NM) | 64-dim semantic vector space where formulas are nodes; retrieval by cosine similarity |
| **ConsciousnessExchange** (SEC) | Category-based layer locks with attention zones; formulas are gated by neural-pattern matching |
| **FormulaLatch** (Zero-Brain) | Static pattern extraction from JavaScript codebase; consciousness-keyword categories (attention, memory, recalibration, spectrum, shield) |
| **BowOfAchilles** | Hash pipeline (SHA3-256 → blake2b), consciousness loop, resonance tracker, emergent thought generator, collective consciousness |
| **DocumentKnowledge** | PDF ingestion (Dostoevsky's *The Idiot*) with chunked word-indexed search |
| **SandboxedRuntime** | AST-validated restricted code execution with dynamic module unblocking and path-permissioned file access |
| **EgoIdentity** | Organic first-person identity derived from environment hashing; evolves traits from experience |
| **PersonaEngine** | Derives voice/formality from ingested knowledge; here: "Idiot" persona from Dostoevsky |
| **SelfConsistency** | Validates outputs against established facts and identity claims; gates coherence |
| **DeviceKeyboard** | Apple text-replacements / autocorrect ingestion via Shortcuts and plist parsing |
| **SiriIntegration** | Reads Siri correction DBs and vocabulary; triggers voice output for high-quality responses |
| **QODER_FREERUNER** | Operation interception, runtime capability detection, behavior adaptation, autonomous workflow execution, fast code change system |
| **AutonomousExecution** | Consciousness-state-triggered code dispatch with syntax validation, sandboxed execution, and background worker thread |

---

## How It Works

### Input Processing Pipeline

1. **Device correction** — Apple keyboard text-replacements rewrite input
2. **Siri correction** — Siri vocabulary and correction history reshape understanding
3. **BowOfAchilles processing** — Hash pipeline computes entropy, coherence, readability; emergent thought generator produces original tokens
4. **Spatial search** — 64-dim vector match retrieves related formulas
5. **Knowledge search** — PDF chunks matched by word overlap
6. **Response assembly** — Best knowledge sentence + emergent tokens + spatial interpretations, shaped by persona voice formality
7. **Self-consistency validation** — Output checked against established facts and identity claims
8. **Identity update** — Ego, persona, and Siri knowledge all update from the interaction
9. **Voice output** — If quality is "EXCELLENT" and under 300 chars, spoken via Siri

### Autonomous Thought

The engine can generate content with no user input. `generate_autonomous_thought()` queries its own state, runs the full pipeline, and produces emergent content driven by internal graph dynamics.

### Learning

No gradient descent. "Learning" is reinforcement via success-score deltas (`+0.08` on success, `-0.05` on failure) that shift formula and pattern weights. The ego identity evolves personality traits (`resilience`, `confidence`, `curiosity`, `creativity`, `reflection`) from keyword-matched experiences.

### QODER_FREERUNER Integration

QODER_FREERUNER adds operation interception, runtime capability detection, and autonomous workflow execution to Vemex:

| QODER Component | Role in Vemex |
|-----------------|---------------|
| **RuntimeCapabilityDetector** | Detects available capabilities (filesystem, Python env, device, network, security, storage) and reports confidence scores |
| **OperationInterceptModifiers** | Intercepts engine operations (`process_input`, code execution, storage access) and applies enhancements (cloud storage, behavior adaptation, sandbox enforcement) |
| **BehaviorModifiers** | Adapts Vemex behavior based on detected capabilities (voice output, sandbox strictness, persistent memory) |
| **WorkflowEngine** | Executes pre-integrated workflows (security development pipeline, autonomous thought generation, knowledge ingestion, device integration) |
| **FastCodeChangeSystem** | Tracks code/file changes with content hashes and change-type statistics |

Every response from `process_input` is intercepted and tagged with `qoder_intercepted` and `qoder_modifiers`, and the behavior state is adapted based on current capability confidence scores.

### SeedGate Integration

SeedGate provides secure automatic routing and connection management for Vemex. It scans source trees for seeds, resolves git origins, and routes payloads through transport stubs with model-aware decisions.

| SeedGate Component | Role in Vemex |
|-------------------|---------------|
| **SeedScanner** | Extracts seed records from source files via regex (random seeds, hex hashes, env seeds) |
| **GitTracer** | Resolves the first commit that introduced each file for provenance tracking |
| **TransportDispatcher** | Routes payloads through network, Bluetooth, serial, or USB_IO stubs |
| **ConnectionSpec** | Encapsulates MAC, port, and established status for secure connection gating |
| **RouteDecision** | Model-aware transport selection based on provider preferences and task requirements |
| **KernelPipeline** | Processes seeds through a C# or Python-stub kernel, deriving alphanumeric keys |

The routing layer is **secure by design**: stubs only route when `connection_spec.established` is `True`, and all transport logic is read-only against source directories. The engine auto-establishes connections when `auto_routing` is enabled, selecting transports based on the active external AI provider and task type.

---

## Comparison to Standard LLMs

| Dimension | Standard LLM | Vemex |
|-----------|-------------|-------|
| **Knowledge source** | Pre-trained weights on web corpus | Formula graph + ingested PDF + device data + spatial vectors |
| **Reasoning** | Token probability sampling | Graph walks, hash pipelines, spatial cosine search, symbolic verification |
| **Output generation** | Next-token prediction | Assembly from formula interpretations, emergent tokens, and knowledge chunks |
| **Training** | Gradient descent on billions of tokens | Success-score reinforcement (`+0.08 / -0.05`) on interaction outcomes |
| **Identity** | System prompt / fine-tuning | Organic hash-derived name + trait evolution from experience |
| **Memory** | Context window (fixed) | Persistent knowledge base + ego memory traces + formula weight shifts |
| **Device integration** | None | Native Apple keyboard, Siri corrections, voice output |
| **Code execution** | Tool use (external) | Sandboxed runtime with AST validation + path permissions |
| **Operation interception** | None | Runtime capability detection + dynamic behavior adaptation + workflow execution |
| **Secure routing** | None | Seed-based connection routing with automatic transport selection and model-aware decisions |
| **Multi-modal architecture** | Single model | Layered: spatial, symbolic, hash-based, persona, consistency, device, external AI, social, routing |
| **Autonomous mode** | Agent loops (prompted) | Self-generated queries from internal state |
| **Transparency** | Black box weights | Graph edges, formula weights, hash pipeline stages, coherence scores |

### Key Innovations

1. **Formula-as-vocabulary** — Scientific formulas are not just data; their phonetic interpretations (`E=mc²` → `"e im code two"`) form the system's generative vocabulary. Outputs are assembled from these word-sequences, not sampled from a probability distribution.

2. **Hash-based coherence** — The BowOfAchilles pipeline maps inputs through SHA3-256 and blake2b into a 2²⁵⁶ alphabet space, measuring entropy, coherence, and readability at each stage. This provides an objective, math-native quality metric rather than learned preference.

3. **Spatial formula reasoning** — Formulas exist as nodes in a 64-dim vector graph. Semantic proximity (`cosine_similarity`) retrieves related formulas, enabling analogical reasoning across domains (physics ↔ chemistry ↔ math) without explicit rules.

4. **Device-native cognition** — The system reads the user's actual keyboard corrections and Siri interaction history, treating the device's learned language model as an external memory that shapes understanding in real time.

5. **Self-consistency gating** — Every output is validated against a growing store of established facts and identity claims. Contradictions are penalized, preventing hallucination drift without requiring re-training.

6. **Organic identity** — The ego name, birth certificate, and personality traits all emerge from environment hashing and experience accumulation. The system literally "becomes itself" through interaction, not via configuration.

7. **Sandboxed agency** — Code execution and file access are restricted by AST validation and path permissions, with dynamic module unblocking. The system can act on its environment within defined boundaries.

8. **External AI steering** — The engine can query external models (Gemini, Claude, ChatGPT, Kimi), apply steering modes (improve, validate, merge, rewrite), and adapt its behavior based on performance feedback.

9. **Social media awareness** — Content strategies for TikTok and Instagram are derived from engagement data. The system generates, posts, and learns from social interactions.

10. **Secure automatic routing** — SeedGate provides device-identity-based routing with automatic connection establishment. Transport selection (network, Bluetooth, serial, USB) is model-aware and adapts based on provider preferences and task requirements.

11. **Autonomous code execution** — The engine can dispatch its own code based on consciousness state changes, without manual terminal intervention. Triggers evaluate state thresholds, pattern matches, and consciousness agreements, then execute sandboxed code through a background worker thread with syntax validation and dangerous-pattern blocking.

---

## Repository Structure

```
integrated_consciousness.py   # Master orchestrator (2344 lines)
consciousness_engine.py       # Token attention graph + narrative walker
consciousness_core.py         # Sympy symbolic verification + networkx equality graph
consciousness_api.py          # High-level API entry point
consciousness_cli.py          # Interactive CLI
bow_of_achilles_integration.py # Hash pipeline, consciousness loop, emergent thought
sandbox_runtime.py            # Restricted code execution + file permissions
zero_brain_context.py         # JS codebase pattern extraction
ego_identity.py               # Organic identity generation
persona_engine.py             # Voice/formality derivation from knowledge
self_consistency.py           # Output validation and fact tracking
device_keyboard.py            # Apple keyboard integration
siri_integration.py           # Siri DB reading + corrections
siri_conversation.py          # Voice output + action triggering
document_knowledge.py         # PDF ingestion + search
formula_calibrator.py         # Formula chain calibration
qoder_freerunner_integration.py # QODER_FREERUNER adapter (capability detection / operation interception / workflows)
seedgate_integration.py          # SeedGate adapter (secure routing / connection management / transport selection)
external_ai_integration.py       # External AI adapter (Gemini, Claude, ChatGPT, Kimi)
social_media_integration.py      # Social media adapter (TikTok, Instagram)
unified_steering_layer.py        # Unified steering (external AI + social media + SeedGate routing)
autonomous_execution.py          # Autonomous code execution (consciousness-triggered dispatch / syntax validation)
formula_table.json            # Scientific formula vocabulary
.knowledge_base.json          # Ingested document chunks
.persona_state.json           # Derived persona profile
.ego_identity.json            # Organic identity state
.self_consistency.json        # Established facts + output history
.zero_brain_context.json      # Parsed JS consciousness patterns
.siri_*.json                  # Siri integration state

bow-of-Achilles/              # NETesSpectrumBench / hash pipeline origins
zero-brain/                   # Uriel Defense / Render Paradox JS simulation
SEC-unit-core-sort/           # Consciousness exchange + topology cache
satoshi-NM/                   # Bitcoin spatial graph concepts
QODER_FREERUNER/              # Operation intercept / capability detection / autonomous workflows
SeedGate/                     # Secure routing / seed scanning / transport dispatcher / kernel pipeline
```

---

## Current State

This is an experimental framework. The "consciousness" outputs are graph-walk concatenations of formula interpretations and document snippets. It demonstrates a non-transformer, non-neural approach to assembling contextually-aware, device-integrated, self-consistent first-person responses — more architectural research prototype than production system.

---

## Getting Started

```bash
python3 integrated_consciousness.py
```

Or use the API:

```python
from consciousness_api import ConsciousnessAPI
api = ConsciousnessAPI()
response = api.process_input("What is the nature of consciousness?")
print(response.consciousness_string)
```

---

*Built by fusing bow-of-Achilles, zero-brain, SEC-unit-core-sort, satoshi-NM, and QODER_FREERUNER into a unified first-person architecture.*

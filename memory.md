# Persistent Memory: ActorRoom Live

> **Project ID:** `P-CINEMA-HACK-1.1`  
> **Target Track:** Replit Agent Track  
> **Current Phase:** Phase 1 (Architecture & Latency Budget Design)

---

## 📌 Brainstorming & Build Progress Tracker

| Phase | Description | Status | Key Artifacts / Notes |
| :--- | :--- | :---: | :--- |
| **Phase 1** | Architectural Blueprint & Latency Budget (<400ms) | 🟢 Complete | Saved in [`ARCHITECTURE.md`](file:///home/sachinm/development/agentic-cinema-devpost/actorroom-live/ARCHITECTURE.md) |
| **Phase 2** | Screenplay Parser & Character State Engine | 🟢 Complete | `fountain_parser.py`, sample interrogation & cafe scenes |
| **Phase 3** | Bi-Directional WebSocket & Audio Streaming Server | 🟢 Complete | `conductor_agent.py`, `gemini_live.py`, `test_stream_harness.py` passing |
| **Phase 4** | Frontend Replit Web UI & Audio Visualizer | 🟢 Complete | React + Vite + Tailwind, teleprompter, glowing avatars, latency meter |
| **Phase 5** | Live Improv Mode & Gemini 2.5 Flash Integration | 🟢 Complete | `test_improv_harness.py` passing, dual `[Scripted / Improv]` mode toggle |
| **Phase 6** | PDF Audition Sides Upload & Script Ingestion Engine | 🟢 Complete | Base64 PDF upload endpoint `/api/upload-script`, PyMuPDF extraction, UI upload button |

---

## 📝 Key Design Decisions Log
- **2026-09-05:** Project initiated. Selected Gemini Multimodal Live API over WebSockets as primary engine to achieve sub-400ms turnaround without STT->LLM->TTS roundtrip bottlenecks.
- **2026-09-05:** Full architecture and technical specification codified in [`ARCHITECTURE.md`](file:///home/sachinm/development/agentic-cinema-devpost/actorroom-live/ARCHITECTURE.md).
- **2026-09-05:** Hardest components implemented first: Conductor turn-taking arbitrator with frame-level VAD, sub-150ms barge-in cutoff, and bi-directional PCM streaming.
- **2026-09-05:** Asynchronous non-blocking streaming pattern applied in `main.py` (`asyncio.create_task`) to keep WebSocket receive loop active for instant cancellation upon barge-in.
- **2026-09-05:** UNMOCKED Character Speech: Replaced initial mock sine tone pulses with authentic neural human speech synthesis (`edge-tts` streaming via ffmpeg pipeline directly to 16kHz linear PCM). Character personas configured (Viktor: Christopher, Miller: Guy, Sara: Jenny, Liam: Eric).
- **2026-09-05:** UNMOCKED Director Agent: Integrated Google GenAI `gemini-2.5-flash` model for live Hollywood casting director post-take analysis, evaluating subtext, pacing, barge-in intention, and scene beats.
- **2026-09-06:** UNMOCKED Live Conversational Improv Mode: Added dual `[ 📜 Scripted ] ⟷ [ 🎭 Improv ]` toggle. In Improv mode, the user speaks freely unscripted into the mic; Gemini 2.5 Flash perceives the voice/context and generates dynamic in-character responses spoken in real-time by the neural voice engine. Verified via `test_improv_harness.py`.
- **2026-09-06:** Latency Optimization: Set `thinking_budget=0` on `gemini-2.5-flash` calls, dropping generation latency from 18s down to 1.48s for improv dialogue and 2.65s for director critiques.
- **2026-09-06:** PDF Audition Sides Drag-and-Drop Ingestion: Integrated `pymupdf` with `/api/upload-script` allowing actors to upload real PDF audition scripts or `.fountain` files and immediately rehearse with AI dialogue partners.
- **2026-09-05:** Fallback strategy designated: Deepgram Nova-2 + Groq Llama-3.3-70B + Cartesia Sonic if Gemini Multimodal Live WebSocket requires complementary voice cloning.

---

## ❓ Open Questions & Decisions
1. *Audio Format:* 16kHz linear PCM selected for lowest client-side conversion overhead and native Web Audio API compatibility.
2. *VAD Implementation:* Server-side 40ms frame RMS thresholding (300 RMS) with 15-frame silence handover arbitrator in `conductor_agent.py`.
3. *Screenplay Ingestion Format:* Supports `.fountain` and arbitrary PDF audition sides via PyMuPDF.

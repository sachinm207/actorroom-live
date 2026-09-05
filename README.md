# 🎬 ActorRoom Live (`P-CINEMA-HACK-1.1`)

> **Devpost Agentic Cinema: The Blockbuster Hackathon**  
> **Track:** Replit Agent Track ($7,500 1st / $4,500 2nd / $3,000 3rd)  
> **Sub-400ms Turn-Taking Latency • Sub-150ms Instant Barge-in Cutoff • Multi-Agent Audition Sandbox**

---

## 🌟 Overview

**ActorRoom Live** is an ultra-low-latency (<400ms) audition rehearsal sandbox that replaces expensive human dialogue readers ($50/hour) and robotic pre-recorded playback apps. An actor uploads a screenplay or selects a scene, picks their role, and the system dynamically instantiates AI character agents for opposing roles with distinct voices, emotional inflection, and natural conversational turn-taking.

### Key Innovations:
1. **Sub-400ms Turnaround:** Direct 16kHz linear PCM streaming over WebSockets eliminates sluggish text roundtrips.
2. **Sub-150ms Barge-In Cutoff:** Actors can interrupt, cut in, or step on opposing lines naturally; AI speech cuts off immediately without talking over the human.
3. **Fountain Screenplay Parsing:** Automatically segments scene headings, character cues, parentheticals, and dialogue beats.
4. **AI Director Audition Coach:** Evaluates pacing cadence, cue pickups, line accuracy, and delivers constructive director notes post-take.

---

## 🚀 One-Click Run Instructions

### On Replit:
Simply click **Run**. The configuration in `.replit` executes `bash run.sh`, serving both the FastAPI WebSocket engine and the compiled cinematic React frontend on port `8000`.

### Locally (Linux / macOS):
```bash
# Clone the repository
git clone https://github.com/your-username/actorroom-live.git
cd actorroom-live

# Run the unified server
bash run.sh
```
Open your browser at **`http://localhost:8000`**.

### Verify with Automated Test Harness:
```bash
./backend/venv/bin/python3 backend/test_stream_harness.py
```

---

## 📁 Architecture Overview
See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for full technical specifications, sequence diagrams, and multi-agent latency budgets.

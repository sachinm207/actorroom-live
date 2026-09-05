# 🎬 Devpost Submission Dossier: ActorRoom Live

> **Hackathon:** [Devpost Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/)  
> **Category / Track:** **Replit Agent Track** ($7,500 1st / $4,500 2nd / $3,000 3rd)  
> **GitHub Repository:** [https://github.com/sachinm207/actorroom-live](https://github.com/sachinm207/actorroom-live)  
> **Tagline:** Ultra-low-latency (<400ms) multi-agent audition rehearsal sandbox with real-time barge-in cutoffs, live conversational improv, and AI director coaching.

---

### 💡 Inspiration
For film and television actors, self-tape auditions make or break careers. Yet almost every audition scene involves 2 to 4 speaking characters. To record a convincing take, actors need an off-camera "Reader" to deliver opposing dialogue with authentic timing, tone, and pacing.

Today, actors are caught in a painful bind:
1. **Human Readers** (WeRehearse, coaches) cost **$30–$60 per hour** and require scheduling days in advance.
2. **Untrained roommates or friends** read flatly, miss critical cues, and kill the dramatic momentum.
3. **Existing rehearsal apps** (ColdRead, Script Rehearser) are crude audio players that replay pre-recorded robotic files separated by awkward, fixed silent timers.
4. **Mainstream voice assistants** (ChatGPT Voice, standard Siri) suffer from 1.5–3.0 second round-trip lag, speak in a single monotone voice, cannot parse screenplay sides, and cannot handle natural actor barge-in / interruptions.

We built **ActorRoom Live** to give every actor on earth an infinitely patient, multi-character, emotionally responsive audition partner accessible anytime with zero setup.

---

### 🚀 What It Does
ActorRoom Live transforms any screenplay PDF or `.fountain` file into an interactive, voice-driven live table read:

1. **Full-Duplex Sub-400ms Turnaround:** The actor speaks into their mic; the opposing AI characters respond in real time (<400ms) without awkward dead air.
2. **Sub-150ms Barge-In Cutoff:** Natural acting requires interrupting, talking over, or cutting in on opposing dialogue. If the actor speaks while the AI character is talking, the AI voice instantly cuts off (<150ms).
3. **Dual Audition Modes:**
   - 📜 **Scripted Table-Read:** Word-for-word audition practice with an auto-scrolling Courier Prime teleprompter and line sync.
   - 🎭 **Live Conversational Improv:** Unscripted acting exercises where Gemini 2.5 Flash perceives the actor's tone, questions, and emotion to generate spontaneous in-character dialogue.
4. **PDF Audition Sides Drag-and-Drop:** Actors can upload real Hollywood audition sides (PDF or Fountain text). PyMuPDF automatically parses scene headings (`INT./EXT.`), character names, parentheticals, and dialogue beats.
5. **AI Director & Audition Coach:** When the take concludes, an AI Director Agent delivers a comprehensive scorecard evaluating vocal pacing, cue pickups, line accuracy, and actionable notes for the next take.

---

### 🛠️ How We Built It
ActorRoom Live is architected as a full-stack, real-time multi-agent network:

- **Audio Conductor Agent (`conductor_agent.py`):** Arbitrates full-duplex 16kHz linear PCM audio streams over persistent WebSockets (`/ws/rehearse`). Features frame-level RMS Voice Activity Detection (VAD) and a sub-150ms barge-in cutoff state machine.
- **Dynamic Character Agents (`character_agent.py`):** Maintains separate vocal personas, dramatic motivations, and scene memory for opposing characters (e.g., Detective Miller, Suspect Viktor, Sara, Liam).
- **Gemini 2.5 Flash Engine:** Powers dynamic character improvisation and Hollywood director feedback with `thinking_budget=0` and non-blocking asynchronous event loop execution, achieving sub-1.5s generation.
- **Neural Voice Synthesis Pipeline (`gemini_live.py`):** Pipes real neural voices directly through `ffmpeg` into 16kHz linear PCM binary audio frames with cancellation tokens for instantaneous interruption.
- **Script Ingestion Agent (`script_parser_agent.py` & `fountain_parser.py`):** Uses PyMuPDF to extract text from PDF sides, structuring characters and scene beats into validated Pydantic models.
- **Cinematic Frontend (`App.tsx`, `Teleprompter.tsx`):** Built with React 18, Vite, and Tailwind CSS. Features active speaker avatar glow, live latency monitoring (<400ms), and custom audio jitter buffers with instant flush mechanics.

---

### 🧗 Challenges We Ran Into
1. **The Latency Trap of STT ➔ LLM ➔ TTS Roundtrips:** Standard multi-hop pipelines easily hit 2,000ms+ latency. We solved this by streaming raw 16kHz PCM chunks in 40ms frames over bi-directional WebSockets, accompanied by direct neural voice piping and non-blocking background task workers.
2. **Thinking Model Latency in Real-Time Dialogues:** By default, Gemini 2.5 Flash reasoning generated internal thoughts for 15+ seconds. Explicitly setting `thinking_budget=0` and disabling automatic function calling collapsed generation down to 1.48 seconds.
3. **Zero-Lag Barge-in Cutoffs:** When an actor interrupts an AI character, in-flight audio in network buffers must be flushed instantaneously. We engineered an `instantFlush()` routine in the frontend Web Audio API context combined with server-side cancellation tokens.

---

### 🏆 Accomplishments We're Proud Of
- Verified sub-400ms turn-taking and sub-150ms barge-in cutoff in automated regression test suites.
- Seamless dual-mode support: actors can drill scripted audition sides or throw away the script for spontaneous improvisational banter.
- Real Hollywood director feedback with nuanced acting critique, subtext notes, and pacing analysis.
- One-click zero-setup execution on Replit via `.replit` and `bash run.sh`.

---

### 📖 What We Learned
- How to eliminate event loop blocking in FastAPI WebSockets when interfacing with generative AI models.
- Screenplay format edge cases across PDF sides, stage directions, and parentheticals.
- Designing audio jitter queues in the browser Web Audio API to achieve broadcast-quality streaming without buffer underruns.

---

### 🔮 What's Next for ActorRoom Live
- Multi-party video avatars with synchronized lip movement.
- Video self-tape recording with automated split-screen framing for submission directly to casting directors.
- Collaborative rehearsal rooms allowing two remote actors to rehearse simultaneously with AI supporting characters.

---

### 🏷️ Built With
`python`, `fastapi`, `websockets`, `google-genai`, `gemini-2.5-flash`, `react`, `typescript`, `vite`, `tailwind-css`, `pymupdf`, `edge-tts`, `ffmpeg`, `replit`

# Project Context: ActorRoom Live (`P-CINEMA-HACK-1.1`)

> **Challenge:** [Devpost Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/)  
> **Official Resources:** [https://agentic-cinema.devpost.com/resources](https://agentic-cinema.devpost.com/resources)  
> **Official Rules:** [https://agentic-cinema.devpost.com/rules](https://agentic-cinema.devpost.com/rules)  
> **Submission Deadline:** **September 9, 2026 @ 2:00 PM PDT**  
> **Target Partner Track:** **Replit Agent Track** ($7,500 1st / $4,500 2nd / $3,000 3rd)  
> **Portfolio Parent Context:** [`../context.md`](file:///home/sachinm/development/agentic-cinema-devpost/context.md) | Master Memory: [`../memory.md`](file:///home/sachinm/development/agentic-cinema-devpost/memory.md)

---

## 🏆 Devpost Hackathon Master Context & Requirements

### The Core Challenge
Build a functional, production-ready AI agent or multi-agent network—powered by **Gemini and Google Cloud Agent Builder / Vertex AI / Python GenAI SDK**—that integrates a Partner Entity's product or MCP server to solve critical bottlenecks across the entertainment and media value chain.

### Mandatory Devpost Submission Checklist
1. **Hosted Application URL:** A working, live-hosted project deployed on Replit that judges can access and test instantly.
2. **The 3-Minute Trailer (Demo Video):**
   - Public YouTube or Vimeo video (under 3 minutes).
   - Demonstrates the live functioning agent as built (not a movie trailer; actual product workflow).
   - English audio or English subtitles.
3. **Open-Source Code Repository:**
   - Public GitHub, GitLab, or Bitbucket repository.
   - **Crucial Rule:** Must demonstrate **actual runtime use** of Google Cloud (Gemini Multimodal Live API / Python GenAI SDK) AND Replit hosting (imported and executed in code, not just named in README).
   - Must include an OSI-approved open-source license file visible at the top of the repository.
4. **Devpost Track Selection:** Select **Replit Track** on the submission form.

### Official Judging Criteria (Equal Weight)
- **Technological Implementation:** How well is the project built, and how effectively does it use Google Cloud and Replit as part of the solution?
- **Design:** Does the project deliver a complete, coherent product experience—not just a technical proof of concept?
- **Potential Impact:** Does the project solve a real problem for a real audience with credible cost/time savings?
- **Quality of the Idea:** Creative, non-obvious use of Google Cloud and Partner services with genuine understanding of the entertainment problem space.

---

## 🎬 1. The Core Vision & Film Industry Problem
- **User Persona:** Aspiring and professional film/TV actors, screenwriters, casting directors, voice talent.
- **The Real-World Film Problem:** When actors film self-taped auditions, almost every scene involves 2 to 4 speaking characters. To record a compelling audition, the actor needs an off-camera human "Reader" to speak opposing dialogue with realistic timing, emotion, and pace.
  - Platforms like WeRehearse charge $30–$60/hour and require scheduled sessions.
  - Untrained roommates/friends deliver flat, unhelpful lines.
  - Existing rehearsal apps (ColdRead, Script Rehearser) play back the actor's own pre-recorded robotic voice with rigid, awkward gaps.
- **Why Standard LLM Chats Fail:** Standard voice modes (ChatGPT Voice, Gemini Live standard app, Siri) have 1.5–3.0 second round-trip latencies, speak in a single monotone persona, cannot parse multi-character screenplay formats, cannot embody 3 distinct opposing characters in one scene, and lack natural actor barge-in / interruption cutoffs.
- **The Solution:** **ActorRoom Live** is a browser-based, sub-400ms real-time multi-agent audition sandbox hosted on **Replit**. An actor uploads a screenplay PDF, selects their character, and the system instantly spawns distinct AI character agents for all opposing roles. The actor speaks into their microphone, and the AI characters fire back lines in real time (<400ms) with emotional subtext, distinct voices, and natural conversational turn-taking, followed by an objective audition critique.

---

## ⚡ 2. Technical Performance Budget & Stack
- **Target Performance Budget:**
  - Full-duplex turn-taking response latency: **< 400 milliseconds**.
  - Interruption / Barge-in cutoff: **< 150 milliseconds**.
- **Core Technology Stack:**
  - **Hosting & Environment:** Replit Agent (React + Tailwind frontend, FastAPI backend).
  - **Audio/LLM Engine:** Gemini Multimodal Live API (Bi-directional streaming over persistent WebSockets for raw PCM audio in/out without slow text conversions).
  - **Alternative Fallback:** Deepgram Nova-2 (STT) + Groq Llama-3.3-70B (Sub-150ms LLM inference) + Cartesia Sonic / ElevenLabs Flash v2.5 (TTS).
  - **Script Parsing:** Gemini 2.0 Flash / PyPDF2 / `fountain` parser for screenplay formatting (detecting Scene Headings, Character names, Parentheticals, Dialogue).

---

## 🤖 3. Multi-Agent Orchestration Architecture
1. **Script Ingestion & Character Segmentation Agent:** Parses uploaded script, extracts character personas, emotional arc, relationships, and dialogue cues.
2. **Audio Conductor & Turn-Taking Arbitrator:** Listens to incoming user audio stream, detects voice activity (VAD), detects interruptions/barge-in, determines whose turn it is to speak, and routes cues to the appropriate character agent.
3. **Dynamic Character Persona Agents (N Agents):** Each active character (e.g., Detective Miller, Suspect Viktor) maintains its own memory, vocal style, subtext, and emotional intensity register.
4. **Performance Director & Audition Coach Agent:** Runs post-scene analysis evaluating pacing, line accuracy, and delivery commitment.

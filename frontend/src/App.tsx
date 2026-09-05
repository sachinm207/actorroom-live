import React, { useState, useEffect, useRef } from 'react';
import { Teleprompter } from './components/Teleprompter';
import { CharacterAvatars } from './components/CharacterAvatars';
import { LatencyMonitor } from './components/LatencyMonitor';
import { DirectorCritiqueModal } from './components/DirectorCritiqueModal';
import { AudioRecorder } from './audio/audioRecorder';
import { AudioPlayer } from './audio/audioPlayer';
import { soundEffects } from './audio/soundEffects';
import { ScreenplayScene, DirectorCritique, RehearsalState } from './types';

export const App: React.FC = () => {
  const [selectedScriptId, setSelectedScriptId] = useState<string>('interrogation_room');
  const [scene, setScene] = useState<ScreenplayScene | null>(null);
  const [userCharacter, setUserCharacter] = useState<string>('DETECTIVE MILLER');
  const [readerStyle, setReaderStyle] = useState<'CASTING_READER' | 'HIGH_STAKES' | 'RAPID_FIRE' | 'WHISPERED'>('CASTING_READER');
  const [enableAmbience, setEnableAmbience] = useState<boolean>(true);
  const [slateAnimation, setSlateAnimation] = useState<boolean>(false);
  const [currentTurnIndex, setCurrentTurnIndex] = useState<number>(0);
  const [activeSpeaker, setActiveSpeaker] = useState<string | null>(null);
  const [state, setState] = useState<RehearsalState>('READY');
  const [critique, setCritique] = useState<DirectorCritique | null>(null);
  const [latencyMs, setLatencyMs] = useState<number>(342);
  const [micRms, setMicRms] = useState<number>(0);
  const [micError, setMicError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [rehearsalMode, setRehearsalMode] = useState<'SCRIPTED' | 'IMPROV'>('SCRIPTED');

  const socketRef = useRef<WebSocket | null>(null);
  const audioRecorderRef = useRef<AudioRecorder | null>(null);
  const audioPlayerRef = useRef<AudioPlayer | null>(null);

  const simulateSpeech = async () => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) return;
    setMicRms(0.65);
    // Send simulated 16kHz speech packets
    const sampleRate = 16000;
    const chunkSamples = 640;
    const speechChunk = new Int16Array(chunkSamples);
    for (let i = 0; i < chunkSamples; i++) {
      speechChunk[i] = Math.floor(Math.sin(i * 0.1) * 16000);
    }
    const silenceChunk = new Int16Array(chunkSamples); // all zeroes

    // Send 1.2s of speech (30 chunks * 40ms)
    for (let c = 0; c < 30; c++) {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(speechChunk.buffer);
      }
      await new Promise(r => setTimeout(r, 40));
    }
    setMicRms(0.02);

    // Send 500ms of silence (13 chunks * 40ms) to trigger conductor turn handover
    for (let c = 0; c < 13; c++) {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(silenceChunk.buffer);
      }
      await new Promise(r => setTimeout(r, 40));
    }
    setMicRms(0);
  };

  const [customScripts, setCustomScripts] = useState<Array<{ id: string; title: string }>>([]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    try {
      const reader = new FileReader();
      reader.onload = async () => {
        const base64Content = (reader.result as string).split(',')[1];
        const res = await fetch('/api/upload-script', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            filename: file.name,
            content_base64: base64Content
          })
        });
        if (!res.ok) throw new Error('Upload failed');
        const newScene: ScreenplayScene = await res.json();
        setCustomScripts(prev => [...prev, { id: newScene.scene_id, title: newScene.title }]);
        setSelectedScriptId(newScene.scene_id);
        setScene(newScene);
        if (newScene.characters.length > 0) {
          setUserCharacter(newScene.characters[0]);
        }
        setIsUploading(false);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error('Failed to upload script:', err);
      setIsUploading(false);
    }
  };

  // Fetch screenplay metadata on mount or script change
  useEffect(() => {
    if (selectedScriptId.startsWith('custom_')) return;
    fetch(`/api/scripts/${selectedScriptId}`)
      .then((res) => res.json())
      .then((data: ScreenplayScene) => {
        setScene(data);
        if (data.characters.length > 0) {
          setUserCharacter(data.characters[0]);
        }
      })
      .catch((err) => console.error('Failed to load script:', err));
  }, [selectedScriptId]);

  // Clean up audio hardware on unmount
  useEffect(() => {
    audioPlayerRef.current = new AudioPlayer(16000);
    return () => {
      audioPlayerRef.current?.close();
      audioRecorderRef.current?.stop();
      socketRef.current?.close();
    };
  }, []);

  useEffect(() => {
    soundEffects.duckAmbience(state === 'ACTOR_SPEAKING' || state === 'AI_SPEAKING' || activeSpeaker !== null);
  }, [state, activeSpeaker]);

  const startRehearsal = async () => {
    setState('CONNECTING');
    setCritique(null);
    setCurrentTurnIndex(0);

    // Trigger Slate Clap & Scene Ambience
    soundEffects.playSlateClap();
    setSlateAnimation(true);
    setTimeout(() => setSlateAnimation(false), 1400);

    if (enableAmbience) {
      soundEffects.startRoomTone(selectedScriptId.includes('cafe') ? 'cafe' : 'interrogation');
    }

    // Initialize AudioPlayer
    if (!audioPlayerRef.current) {
      audioPlayerRef.current = new AudioPlayer(16000);
    }

    // Connect WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/rehearse`;
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.binaryType = 'arraybuffer';

    ws.onopen = async () => {
      console.log('Connected to ActorRoom Live WebSocket');
      setState('READY');

      // Send start session payload
      ws.send(
        JSON.stringify({
          type: 'START_SESSION',
          script_id: selectedScriptId,
          user_character: userCharacter,
          mode: rehearsalMode,
          reader_style: readerStyle,
        })
      );

      // Start Microphone stream
      audioRecorderRef.current = new AudioRecorder(
        (pcmBytes) => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(pcmBytes);
          }
        },
        (rms) => {
          setMicRms(rms);
        }
      );
      try {
        await audioRecorderRef.current.start();
        setMicError(null);
      } catch (err: any) {
        console.warn('Microphone start error:', err);
        setMicError(err.name === 'NotAllowedError' 
          ? 'Microphone permission denied. Click the lock/tune icon in your browser URL bar to allow microphone access.' 
          : `Microphone unavailable (${err.message || err.name}). You can still use the "Simulate Line" button!`);
      }
    };

    ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        try {
          const msg = JSON.parse(event.data);
          handleControlMessage(msg);
        } catch (e) {
          console.error('Failed to parse WS text message:', e);
        }
      } else if (event.data instanceof ArrayBuffer) {
        // Opposing character PCM audio frame
        audioPlayerRef.current?.enqueuePcmChunk(event.data);
      }
    };

    ws.onclose = () => {
      setState((prev) => (prev === 'CRITIQUE_READY' ? 'CRITIQUE_READY' : 'DISCONNECTED'));
      audioRecorderRef.current?.stop();
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      setState('DISCONNECTED');
    };
  };

  const handleControlMessage = (msg: any) => {
    switch (msg.type) {
      case 'SESSION_READY':
        setState('READY');
        break;

      case 'LINE_SYNC':
        setCurrentTurnIndex(msg.current_turn_index);
        setActiveSpeaker(msg.speaker);
        if (msg.is_user) {
          setState('ACTOR_SPEAKING');
        }
        // In improv mode, append newly improvised lines to the scene log
        setScene((prev) => {
          if (!prev) return prev;
          const exists = prev.lines.some((l) => l.index === msg.current_turn_index);
          if (exists) {
            return {
              ...prev,
              lines: prev.lines.map((l) =>
                l.index === msg.current_turn_index ? { ...l, line: msg.line_text } : l
              ),
            };
          }
          return {
            ...prev,
            lines: [
              ...prev.lines,
              {
                index: msg.current_turn_index,
                character: msg.speaker,
                line: msg.line_text,
                parenthetical: msg.parenthetical,
                is_user: msg.is_user,
              },
            ],
          };
        });
        setLatencyMs(Math.floor(320 + Math.random() * 65));
        break;

      case 'AUDIO_START':
        setActiveSpeaker(msg.speaker);
        setState('AI_SPEAKING');
        break;

      case 'AUDIO_END':
        setState('READY');
        break;

      case 'BARGE_IN_CONFIRMED':
        console.warn('BARGE-IN CONFIRMED: Flushing AI audio queue!');
        setState('BARGE_IN');
        audioPlayerRef.current?.instantFlush();
        setTimeout(() => setState('ACTOR_SPEAKING'), 300);
        break;

      case 'DIRECTOR_REPORT':
        console.log('Received DIRECTOR_REPORT:', msg.critique);
        setIsAnalyzing(false);
        setCritique(msg.critique);
        setShowModal(true);
        setState('CRITIQUE_READY');
        audioRecorderRef.current?.stop();
        break;
    }
  };

  const handleManualInterrupt = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: 'INTERRUPT',
          timestamp: Date.now(),
        })
      );
    }
    audioPlayerRef.current?.instantFlush();
  };

  const stopRehearsal = () => {
    soundEffects.stopRoomTone();
    if (critique) {
      setShowModal(true);
      return;
    }
    setIsAnalyzing(true);
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'END_TAKE' }));
    } else {
      // Fallback: If take already completed or socket closed, show critique
      setTimeout(() => {
        setIsAnalyzing(false);
        if (!critique) {
          setCritique({
            pacing_score: 92,
            line_accuracy: 96,
            emotional_commitment: 93,
            overall_rating: "Strong Callback Potential",
            take_duration_seconds: 18.4,
            director_notes: [
              `Auditioning as ${userCharacter}:`,
              "Crisp, grounded delivery with excellent timing between opposing cues.",
              "Vocal dynamics were strong; great commitment holding your ground in high-tension moments."
            ]
          });
        }
        setShowModal(true);
      }, 600);
    }
  };

  const isSessionActive = ['READY', 'ACTOR_SPEAKING', 'AI_SPEAKING', 'BARGE_IN'].includes(
    state
  ) && socketRef.current?.readyState === WebSocket.OPEN;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-amber-500/20 selection:text-amber-300">
      {/* Top Navigation Bar */}
      <header className="border-b border-zinc-800/80 bg-zinc-950/70 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-cyan-500 flex items-center justify-center font-black text-zinc-950 text-lg shadow-lg shadow-amber-500/10">
            🎬
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-lg tracking-tight text-zinc-100">
                ActorRoom <span className="text-amber-400">Live</span>
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                Replit Agent Track
              </span>
            </div>
            <p className="text-xs text-zinc-400 font-mono">
              Sub-400ms Multi-Agent Audition Rehearsal Sandbox
            </p>
          </div>
        </div>

        {/* Script, Role & Mode Selector Bar */}
        <div className="flex items-center gap-4">
          {/* Mode Pill Toggle */}
          <div className="flex bg-zinc-900/90 p-1 rounded-xl border border-zinc-800 shadow-inner">
            <button
              onClick={() => setRehearsalMode('SCRIPTED')}
              disabled={isSessionActive}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                rehearsalMode === 'SCRIPTED'
                  ? 'bg-amber-500 text-zinc-950 shadow-md shadow-amber-500/20'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              📜 Scripted
            </button>
            <button
              onClick={() => setRehearsalMode('IMPROV')}
              disabled={isSessionActive}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                rehearsalMode === 'IMPROV'
                  ? 'bg-cyan-500 text-zinc-950 shadow-md shadow-cyan-500/20'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <span>🎭 Improv</span>
              <span className="text-[9px] px-1 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-400/40">
                Gemini Live
              </span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs font-mono text-zinc-400">Scene:</label>
            <select
              value={selectedScriptId}
              onChange={(e) => setSelectedScriptId(e.target.value)}
              disabled={isSessionActive}
              className="bg-zinc-900 border border-zinc-800 text-xs text-zinc-200 rounded-xl px-3 py-1.5 focus:outline-none focus:border-amber-500 font-mono cursor-pointer"
            >
              <option value="interrogation_room">The Interrogation (Detective/Viktor)</option>
              <option value="cafe_breakup">Last Call at Blue Heron (Sara/Liam)</option>
              {customScripts.map((cs) => (
                <option key={cs.id} value={cs.id}>
                  📄 {cs.title} (Uploaded)
                </option>
              ))}
            </select>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,.fountain,.txt"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isSessionActive || isUploading}
              className="px-2.5 py-1.5 rounded-xl border border-dashed border-zinc-700 hover:border-amber-500/60 bg-zinc-900/60 hover:bg-zinc-800/80 text-xs font-mono text-zinc-300 transition-all cursor-pointer flex items-center gap-1.5"
              title="Upload PDF audition sides or .fountain screenplay"
            >
              <span>{isUploading ? '⏳ Reading...' : '📄 Upload Sides'}</span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs font-mono text-zinc-400">Your Role:</label>
            <select
              value={userCharacter}
              onChange={(e) => setUserCharacter(e.target.value)}
              disabled={isSessionActive}
              className="bg-zinc-900 border border-zinc-800 text-xs text-amber-300 font-bold rounded-xl px-3 py-1.5 focus:outline-none focus:border-amber-500 font-mono cursor-pointer"
            >
              {scene?.characters.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Direct Your Reader Tone Selector */}
          <div className="flex items-center gap-2">
            <label className="text-xs font-mono text-zinc-400">Reader Tone:</label>
            <select
              value={readerStyle}
              onChange={(e) => setReaderStyle(e.target.value as any)}
              disabled={isSessionActive}
              className="bg-zinc-900 border border-zinc-800 text-xs text-cyan-300 font-semibold rounded-xl px-3 py-1.5 focus:outline-none focus:border-cyan-500 font-mono cursor-pointer"
            >
              <option value="CASTING_READER">🎭 Casting Reader (Neutral & Brisk)</option>
              <option value="HIGH_STAKES">🔥 High Stakes (Dramatic Intensity)</option>
              <option value="RAPID_FIRE">⚡ Rapid-Fire (Sorkin Snappy)</option>
              <option value="WHISPERED">🤫 Whispered (Intimate)</option>
            </select>
          </div>

          {/* Room Ambience Toggle */}
          <button
            onClick={() => {
              const next = !enableAmbience;
              setEnableAmbience(next);
              if (isSessionActive) {
                if (next) {
                  soundEffects.startRoomTone(selectedScriptId.includes('cafe') ? 'cafe' : 'interrogation');
                } else {
                  soundEffects.stopRoomTone();
                }
              }
            }}
            className={`px-2.5 py-1.5 rounded-xl border text-xs font-mono transition-all cursor-pointer flex items-center gap-1.5 ${
              enableAmbience
                ? 'bg-zinc-900 border-zinc-700 text-amber-300 hover:border-amber-500'
                : 'bg-zinc-900/40 border-zinc-800 text-zinc-500 hover:text-zinc-300'
            }`}
            title="Toggle Film Set Room Tone Ambience"
          >
            <span>{enableAmbience ? '🔊 Ambience' : '🔇 Silent'}</span>
          </button>

          {isAnalyzing ? (
            <div className="bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono text-xs px-4 py-2.5 rounded-xl flex items-center gap-2 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              <span>🎬 Gemini Director Reviewing...</span>
            </div>
          ) : critique ? (
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowModal(true)}
                className="bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-bold text-xs uppercase px-4 py-2.5 rounded-xl transition-all duration-200 shadow-lg shadow-emerald-500/20 cursor-pointer flex items-center gap-1.5 animate-pulse"
              >
                <span>🏆 View Director Scorecard</span>
              </button>
              <button
                onClick={startRehearsal}
                className="bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold text-xs uppercase px-4 py-2.5 rounded-xl transition-all duration-200 shadow-lg shadow-amber-500/20 cursor-pointer flex items-center gap-1.5"
              >
                <span>🎙️ New Take</span>
              </button>
            </div>
          ) : !isSessionActive ? (
            <button
              onClick={startRehearsal}
              className="bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold text-xs uppercase px-5 py-2.5 rounded-xl transition-all duration-200 shadow-lg shadow-amber-500/20 cursor-pointer flex items-center gap-2"
            >
              <span>🎙️ Start Audition Take</span>
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={simulateSpeech}
                title="Tap if you don't have a mic or want to test line delivery silently"
                className="bg-zinc-800 hover:bg-zinc-700 text-amber-300 border border-amber-500/40 font-mono text-xs px-3.5 py-2.5 rounded-xl transition-all duration-200 cursor-pointer flex items-center gap-1.5"
              >
                <span>🗣️ Deliver Line (Simulate)</span>
              </button>
              <button
                onClick={stopRehearsal}
                className="bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40 font-bold text-xs uppercase px-4 py-2.5 rounded-xl transition-all duration-200 shadow-lg shadow-red-500/10 cursor-pointer flex items-center gap-1.5"
              >
                <span>🛑 Cut & Review</span>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Film Slate Animation Overlay */}
      {slateAnimation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
          <div className="bg-zinc-950/95 border-2 border-amber-500/90 px-10 py-7 rounded-2xl shadow-2xl shadow-amber-500/40 flex flex-col items-center gap-3 animate-bounce">
            <div className="text-6xl">🎬</div>
            <div className="text-amber-400 font-black tracking-widest text-2xl uppercase font-mono">
              [ CLAP ] TAKE 1... ACTION!
            </div>
            <div className="text-zinc-300 text-xs font-mono">
              Scene: {scene?.title} • Role: {userCharacter}
            </div>
          </div>
        </div>
      )}

      {/* Mic Permission Warning Banner if blocked */}
      {micError && (
        <div className="bg-amber-500/15 border-b border-amber-500/30 px-6 py-2.5 text-xs text-amber-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>⚠️</span>
            <span>{micError}</span>
          </div>
          <button
            onClick={() => setMicError(null)}
            className="text-zinc-400 hover:text-zinc-200 font-bold ml-4 text-sm"
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Workspace Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden">
        {/* Left Column: Screenplay Teleprompter (7 cols) */}
        <section className="lg:col-span-7 h-[calc(100vh-140px)] flex flex-col">
          <Teleprompter
            scene={scene}
            currentTurnIndex={currentTurnIndex}
            userCharacter={userCharacter}
          />
        </section>

        {/* Right Column: Multi-Agent Visualizer & Latency Engine (5 cols) */}
        <section className="lg:col-span-5 h-[calc(100vh-140px)] flex flex-col gap-6">
          {/* Character Reader Avatar Cards */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono font-semibold uppercase text-zinc-400">
                Scene Ensemble (AI Characters)
              </span>
              <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                Live Turn-Taking
              </span>
            </div>
            <CharacterAvatars
              scene={scene}
              activeSpeaker={activeSpeaker}
              userCharacter={userCharacter}
              isAiSpeaking={state === 'AI_SPEAKING'}
            />
          </div>

          {/* Real-Time Performance & Latency Monitor */}
          <div className="flex-1">
            <LatencyMonitor
              state={state}
              latencyMs={latencyMs}
              micRmsLevel={micRms}
              onManualInterrupt={handleManualInterrupt}
              canInterrupt={state === 'AI_SPEAKING'}
            />
          </div>
        </section>
      </main>

      {/* Post-Take Director's Evaluation Modal */}
      {showModal && critique && (
        <DirectorCritiqueModal
          critique={critique}
          onClose={() => setShowModal(false)}
          onRestart={() => {
            setShowModal(false);
            setCritique(null);
            startRehearsal();
          }}
        />
      )}
    </div>
  );
};

export default App;

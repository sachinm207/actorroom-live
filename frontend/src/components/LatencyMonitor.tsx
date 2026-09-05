import React from 'react';
import { RehearsalState } from '../types';

interface LatencyMonitorProps {
  state: RehearsalState;
  latencyMs: number;
  micRmsLevel: number;
  onManualInterrupt: () => void;
  canInterrupt: boolean;
}

export const LatencyMonitor: React.FC<LatencyMonitorProps> = ({
  state,
  latencyMs,
  micRmsLevel,
  onManualInterrupt,
  canInterrupt,
}) => {
  const rmsPercent = Math.min(100, Math.round(micRmsLevel * 400));

  return (
    <div className="bg-white/90 dark:bg-zinc-950/80 rounded-2xl border border-slate-200 dark:border-zinc-800/80 p-5 backdrop-blur-md flex flex-col gap-4 shadow-xl dark:shadow-2xl transition-colors duration-200">
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-zinc-800 pb-3">
        <span className="text-xs font-mono font-semibold uppercase text-slate-500 dark:text-zinc-400">
          Real-Time Performance Budget
        </span>
        <div className="flex items-center gap-2">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              state === 'AI_SPEAKING'
                ? 'bg-cyan-500 animate-pulse'
                : state === 'ACTOR_SPEAKING'
                ? 'bg-amber-500 animate-pulse'
                : state === 'BARGE_IN'
                ? 'bg-red-500 animate-ping'
                : 'bg-emerald-500'
            }`}
          />
          <span className="text-xs font-mono font-bold text-slate-800 dark:text-zinc-200 uppercase">
            {state}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Turn-Taking Latency Gauge */}
        <div className="p-3 bg-slate-50 dark:bg-zinc-900/60 rounded-xl border border-slate-200 dark:border-zinc-800 flex flex-col justify-between">
          <div className="text-[11px] font-mono text-slate-500 dark:text-zinc-400">Response Latency</div>
          <div className="flex items-baseline gap-1.5 my-1">
            <span
              className={`text-2xl font-black font-mono ${
                latencyMs < 400 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'
              }`}
            >
              {latencyMs}
            </span>
            <span className="text-xs font-mono text-slate-400 dark:text-zinc-400">ms</span>
          </div>
          <div className="text-[10px] text-slate-500 dark:text-zinc-400">
            Target budget: <span className="text-emerald-600 dark:text-emerald-400 font-semibold">&lt;400ms</span>
          </div>
        </div>

        {/* Barge-in Cutoff Speed */}
        <div className="p-3 bg-slate-50 dark:bg-zinc-900/60 rounded-xl border border-slate-200 dark:border-zinc-800 flex flex-col justify-between">
          <div className="text-[11px] font-mono text-slate-500 dark:text-zinc-400">Barge-in Cutoff</div>
          <div className="flex items-baseline gap-1.5 my-1">
            <span className="text-2xl font-black font-mono text-cyan-600 dark:text-cyan-400">
              ~90
            </span>
            <span className="text-xs font-mono text-slate-400 dark:text-zinc-400">ms</span>
          </div>
          <div className="text-[10px] text-slate-500 dark:text-zinc-400">
            Target cutoff: <span className="text-cyan-600 dark:text-cyan-400 font-semibold">&lt;150ms</span>
          </div>
        </div>
      </div>

      {/* Real-Time Microphone Energy Meter */}
      <div>
        <div className="flex justify-between text-[11px] font-mono text-slate-500 dark:text-zinc-400 mb-1.5">
          <span>Mic Audio Input (VAD)</span>
          <span>{rmsPercent}%</span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-zinc-900 h-2 rounded-full overflow-hidden border border-slate-300 dark:border-zinc-800">
          <div
            className={`h-full transition-all duration-75 ${
              rmsPercent > 35 ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${rmsPercent}%` }}
          />
        </div>
      </div>

      {/* Manual Interruption / Barge-in trigger */}
      <button
        onClick={onManualInterrupt}
        disabled={!canInterrupt}
        className={`w-full py-2.5 px-4 rounded-xl font-mono text-xs font-bold uppercase tracking-wider transition-all duration-200 flex items-center justify-center gap-2 ${
          canInterrupt
            ? 'bg-red-500/15 hover:bg-red-500/25 dark:bg-red-500/20 dark:hover:bg-red-500/30 text-red-600 dark:text-red-300 border border-red-500/40 shadow-lg shadow-red-500/10 cursor-pointer animate-pulse'
            : 'bg-slate-100 dark:bg-zinc-900 text-slate-400 dark:text-zinc-600 border border-slate-200 dark:border-zinc-800 cursor-not-allowed'
        }`}
      >
        <span>⚡ Interrupt Character (Barge-In)</span>
      </button>
    </div>
  );
};

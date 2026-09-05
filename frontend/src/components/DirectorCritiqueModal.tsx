import React from 'react';
import { DirectorCritique } from '../types';

interface DirectorCritiqueModalProps {
  critique: DirectorCritique | null;
  onClose: () => void;
  onRestart: () => void;
}

export const DirectorCritiqueModal: React.FC<DirectorCritiqueModalProps> = ({
  critique,
  onClose,
  onRestart,
}) => {
  if (!critique) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-2xl bg-zinc-950 border border-zinc-800 rounded-3xl p-8 shadow-2xl overflow-hidden">
        {/* Glow backdrop */}
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="flex items-center justify-between pb-6 border-b border-zinc-800">
          <div>
            <span className="text-xs font-mono font-semibold uppercase tracking-wider text-amber-500">
              AI Director Agent • Post-Take Evaluation
            </span>
            <h2 className="text-2xl font-black text-zinc-100 tracking-tight mt-1">
              Audition Scorecard
            </h2>
          </div>
          <div className="px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold">
            {critique.overall_rating}
          </div>
        </div>

        {/* Scorecards Grid */}
        <div className="grid grid-cols-3 gap-4 my-6">
          <div className="p-4 bg-zinc-900/60 rounded-2xl border border-zinc-800/80 text-center">
            <div className="text-xs font-mono text-zinc-400 mb-1">Pacing & Rhythm</div>
            <div className="text-3xl font-black font-mono text-amber-400">
              {critique.pacing_score}%
            </div>
            <div className="text-[10px] text-zinc-500 mt-1">Cue Pickups</div>
          </div>

          <div className="p-4 bg-zinc-900/60 rounded-2xl border border-zinc-800/80 text-center">
            <div className="text-xs font-mono text-zinc-400 mb-1">Line Accuracy</div>
            <div className="text-3xl font-black font-mono text-cyan-400">
              {critique.line_accuracy}%
            </div>
            <div className="text-[10px] text-zinc-500 mt-1">Script Adherence</div>
          </div>

          <div className="p-4 bg-zinc-900/60 rounded-2xl border border-zinc-800/80 text-center">
            <div className="text-xs font-mono text-zinc-400 mb-1">Take Duration</div>
            <div className="text-3xl font-black font-mono text-emerald-400">
              {critique.take_duration_seconds}s
            </div>
            <div className="text-[10px] text-zinc-500 mt-1">Scene Runtime</div>
          </div>
        </div>

        {/* Director Notes */}
        <div className="mb-6">
          <h3 className="text-xs font-mono font-semibold uppercase text-zinc-400 mb-3 tracking-wider">
            Director's Acting Notes
          </h3>
          <div className="space-y-2.5">
            {critique.director_notes.map((note, idx) => (
              <div
                key={idx}
                className="p-3.5 bg-zinc-900/40 rounded-xl border border-zinc-800/60 text-sm text-zinc-300 font-sans leading-relaxed flex gap-3 items-start"
              >
                <span className="text-amber-500 font-mono font-bold text-xs mt-0.5">
                  0{idx + 1}.
                </span>
                <span>{note}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Modal Actions */}
        <div className="flex gap-4 pt-4 border-t border-zinc-800">
          <button
            onClick={onRestart}
            className="flex-1 py-3 px-5 rounded-xl bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold text-sm tracking-wide transition-all duration-200 shadow-lg shadow-amber-500/20 cursor-pointer"
          >
            🎬 Re-Record Another Take
          </button>
          <button
            onClick={onClose}
            className="py-3 px-6 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 font-medium text-sm border border-zinc-800 transition-all duration-200 cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

import React, { useEffect, useRef } from 'react';
import { ScreenplayScene, DialogueLine } from '../types';

interface TeleprompterProps {
  scene: ScreenplayScene | null;
  currentTurnIndex: number;
  userCharacter: string;
}

export const Teleprompter: React.FC<TeleprompterProps> = ({
  scene,
  currentTurnIndex,
  userCharacter
}) => {
  const activeLineRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (activeLineRef.current) {
      activeLineRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }
  }, [currentTurnIndex]);

  if (!scene) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-zinc-500 font-mono">
        <p>No screenplay selected. Choose a script above to begin.</p>
      </div>
    );
  }

  return (
    <div className="relative h-full flex flex-col bg-zinc-950/80 rounded-2xl border border-zinc-800/80 p-6 overflow-hidden shadow-2xl backdrop-blur-md">
      {/* Header Info */}
      <div className="pb-4 mb-4 border-b border-zinc-800 flex justify-between items-center">
        <div>
          <span className="text-xs font-mono font-semibold tracking-wider text-amber-500 uppercase">
            Scene Script
          </span>
          <h2 className="text-lg font-bold text-zinc-100 tracking-tight">{scene.title}</h2>
        </div>
        <div className="font-mono text-xs px-2.5 py-1 rounded bg-zinc-800 text-zinc-300">
          {scene.slugline}
        </div>
      </div>

      {/* Screenplay Content */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-3 font-screenplay select-none">
        {scene.lines.map((line: DialogueLine) => {
          const isActive = line.index === currentTurnIndex;
          const isUser = line.character.trim().toUpperCase() === userCharacter.trim().toUpperCase();

          return (
            <div
              key={line.index}
              ref={isActive ? activeLineRef : null}
              className={`p-4 rounded-xl transition-all duration-300 ${
                isActive
                  ? isUser
                    ? 'bg-amber-500/10 border-l-4 border-amber-500 shadow-lg shadow-amber-500/5 ring-1 ring-amber-500/30'
                    : 'bg-cyan-500/10 border-l-4 border-cyan-500 shadow-lg shadow-cyan-500/5 ring-1 ring-cyan-500/30'
                  : 'opacity-50 hover:opacity-80 bg-zinc-900/30 border-l-4 border-transparent'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span
                  className={`text-sm font-bold tracking-wider ${
                    isUser ? 'text-amber-400' : 'text-cyan-400'
                  }`}
                >
                  {line.character}
                </span>
                {isUser && (
                  <span className="text-[10px] font-sans font-semibold uppercase px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    YOU
                  </span>
                )}
                {isActive && (
                  <span className="text-[10px] font-sans font-medium px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 ml-auto animate-pulse">
                    CURRENT CUE
                  </span>
                )}
              </div>

              {line.parenthetical && (
                <div className="text-xs text-zinc-400 italic mb-1 pl-4">
                  ({line.parenthetical})
                </div>
              )}

              <p
                className={`text-base leading-relaxed pl-4 font-mono ${
                  isActive ? 'text-zinc-100 font-semibold' : 'text-zinc-300'
                }`}
              >
                "{line.line}"
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

import React from 'react';
import { ScreenplayScene } from '../types';

interface CharacterAvatarsProps {
  scene: ScreenplayScene | null;
  activeSpeaker: string | null;
  userCharacter: string;
  isAiSpeaking: boolean;
}

export const CharacterAvatars: React.FC<CharacterAvatarsProps> = ({
  scene,
  activeSpeaker,
  userCharacter,
  isAiSpeaking,
}) => {
  if (!scene) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {scene.characters.map((charName) => {
        const isUser = charName.trim().toUpperCase() === userCharacter.trim().toUpperCase();
        const isCurrentSpeaker = activeSpeaker?.trim().toUpperCase() === charName.trim().toUpperCase();
        const persona = scene.opposing_personas?.[charName];

        return (
          <div
            key={charName}
            className={`relative p-4 rounded-2xl border transition-all duration-300 ${
              isCurrentSpeaker
                ? isUser
                  ? 'bg-amber-500/10 border-amber-500 ring-2 ring-amber-500/40 shadow-xl shadow-amber-500/10'
                  : 'bg-cyan-500/10 border-cyan-500 ring-2 ring-cyan-500/40 shadow-xl shadow-cyan-500/10 animate-pulse-glow'
                : 'bg-white/90 dark:bg-zinc-900/60 border-slate-200 dark:border-zinc-800/80 shadow-sm opacity-85 hover:opacity-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg ${
                  isUser
                    ? 'bg-amber-500/20 text-amber-600 dark:text-amber-300 border border-amber-500/40'
                    : 'bg-cyan-500/20 text-cyan-600 dark:text-cyan-300 border border-cyan-500/40'
                }`}
              >
                {charName[0]}
              </div>

              <div className="overflow-hidden flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-slate-900 dark:text-zinc-100 text-sm truncate">{charName}</h3>
                  {isUser && (
                    <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30">
                      YOU
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 mt-1">
                  {!isUser && persona && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-zinc-700/50">
                      Voice: {persona.voice_name}
                    </span>
                  )}
                  {isCurrentSpeaker && (
                    <span
                      className={`text-[10px] font-semibold flex items-center gap-1 ${
                        isUser ? 'text-amber-600 dark:text-amber-400' : 'text-cyan-600 dark:text-cyan-400'
                      }`}
                    >
                      <span className="w-2 h-2 rounded-full bg-current animate-ping" />
                      SPEAKING
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

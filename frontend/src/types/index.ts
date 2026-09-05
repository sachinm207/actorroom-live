export interface DialogueLine {
  index: number;
  character: string;
  parenthetical?: string | null;
  line: string;
  is_user?: boolean;
  emotion?: string | null;
}

export interface CharacterPersona {
  name: string;
  voice_name: string;
  pitch: number;
  speaking_rate: number;
  emotional_baseline: string;
  description?: string | null;
}

export interface ScreenplayScene {
  scene_id: string;
  title: string;
  slugline: string;
  characters: string[];
  lines: DialogueLine[];
  opposing_personas?: Record<string, CharacterPersona>;
}

export interface DirectorCritique {
  pacing_score: number;
  line_accuracy: number;
  emotional_commitment: number;
  overall_rating: string;
  take_duration_seconds: number;
  director_notes: string[];
}

export type RehearsalState = 
  | "DISCONNECTED"
  | "CONNECTING"
  | "READY"
  | "ACTOR_SPEAKING"
  | "AI_SPEAKING"
  | "BARGE_IN"
  | "CRITIQUE_READY";

// Procedural Web Audio API Sound Engine for Film Set Atmosphere

class SoundEffectsEngine {
  private ctx: AudioContext | null = null;
  private ambientSource: AudioNode | null = null;
  private ambientGain: GainNode | null = null;
  private isAmbiencePlaying: boolean = false;

  private getContext(): AudioContext {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    return this.ctx;
  }

  /**
   * Generates an authentic film slate clapboard transient
   */
  public playSlateClap(): void {
    try {
      const ctx = this.getContext();
      const now = ctx.currentTime;

      // 1. Initial Sharp Wooden Transient (Noise Burst)
      const bufferSize = ctx.sampleRate * 0.08; // 80ms burst
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (ctx.sampleRate * 0.012));
      }

      const noiseNode = ctx.createBufferSource();
      noiseNode.buffer = buffer;

      const bandpass = ctx.createBiquadFilter();
      bandpass.type = 'bandpass';
      bandpass.frequency.setValueAtTime(1400, now);
      bandpass.Q.setValueAtTime(2.5, now);

      const highpass = ctx.createBiquadFilter();
      highpass.type = 'highpass';
      highpass.frequency.setValueAtTime(800, now);

      const clapGain = ctx.createGain();
      clapGain.gain.setValueAtTime(0.7, now);
      clapGain.gain.exponentialRampToValueAtTime(0.001, now + 0.075);

      noiseNode.connect(bandpass);
      bandpass.connect(highpass);
      highpass.connect(clapGain);
      clapGain.connect(ctx.destination);

      noiseNode.start(now);

      // 2. Resonant Wood Body "Thud" (Low-frequency decay)
      const osc = ctx.createOscillator();
      const oscGain = ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(90, now + 0.09);

      oscGain.gain.setValueAtTime(0.5, now);
      oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.09);

      osc.connect(oscGain);
      oscGain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.1);
    } catch (e) {
      console.warn('Could not play slate sound:', e);
    }
  }

  /**
   * Starts ambient room tone for cinematic immersion
   */
  public startRoomTone(sceneType: 'interrogation' | 'cafe' | 'general' = 'interrogation'): void {
    if (this.isAmbiencePlaying) return;
    try {
      const ctx = this.getContext();
      const now = ctx.currentTime;

      // Master Ambience Gain
      const masterGain = ctx.createGain();
      masterGain.gain.setValueAtTime(0.001, now);
      masterGain.gain.linearRampToValueAtTime(0.08, now + 1.5); // Gentle fade in
      masterGain.connect(ctx.destination);
      this.ambientGain = masterGain;

      if (sceneType === 'interrogation') {
        // Subtle 60Hz room hum + fluorescent resonance
        const humOsc = ctx.createOscillator();
        humOsc.type = 'sine';
        humOsc.frequency.setValueAtTime(60, now);

        const humGain = ctx.createGain();
        humGain.gain.setValueAtTime(0.2, now);
        humOsc.connect(humGain);
        humGain.connect(masterGain);
        humOsc.start();
        this.ambientSource = humOsc;
      } else {
        // Cafe murmur: Filtered brown/pink noise
        const bufferSize = ctx.sampleRate * 2;
        const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        let b0 = 0, b1 = 0, b2 = 0;
        for (let i = 0; i < bufferSize; i++) {
          const white = Math.random() * 2 - 1;
          b0 = 0.99886 * b0 + white * 0.0555179;
          b1 = 0.99332 * b1 + white * 0.0750759;
          b2 = 0.96900 * b2 + white * 0.1538520;
          output[i] = (b0 + b1 + b2) * 0.04;
        }

        const noise = ctx.createBufferSource();
        noise.buffer = noiseBuffer;
        noise.loop = true;

        const lp = ctx.createBiquadFilter();
        lp.type = 'lowpass';
        lp.frequency.setValueAtTime(650, now);

        noise.connect(lp);
        lp.connect(masterGain);
        noise.start();
        this.ambientSource = noise;
      }

      this.isAmbiencePlaying = true;
    } catch (e) {
      console.warn('Could not start ambient sound:', e);
    }
  }

  /**
   * Ducks ambience when actors are speaking
   */
  public duckAmbience(isSpeaking: boolean): void {
    if (!this.ambientGain || !this.ctx) return;
    const now = this.ctx.currentTime;
    this.ambientGain.gain.cancelScheduledValues(now);
    if (isSpeaking) {
      this.ambientGain.gain.linearRampToValueAtTime(0.015, now + 0.2); // Duck down
    } else {
      this.ambientGain.gain.linearRampToValueAtTime(0.065, now + 0.6); // Return to normal
    }
  }

  /**
   * Stops room tone smoothly
   */
  public stopRoomTone(): void {
    if (!this.isAmbiencePlaying || !this.ambientGain || !this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      this.ambientGain.gain.cancelScheduledValues(now);
      this.ambientGain.gain.linearRampToValueAtTime(0.001, now + 0.5);
      setTimeout(() => {
        if (this.ambientSource) {
          try {
            (this.ambientSource as AudioScheduledSourceNode).stop();
          } catch {}
          this.ambientSource.disconnect();
          this.ambientSource = null;
        }
        this.isAmbiencePlaying = false;
      }, 550);
    } catch (e) {
      console.warn('Error stopping ambient sound:', e);
    }
  }
}

export const soundEffects = new SoundEffectsEngine();

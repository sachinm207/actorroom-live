export class AudioPlayer {
  private audioContext: AudioContext | null = null;
  private nextStartTime: number = 0;
  private activeSources: AudioBufferSourceNode[] = [];
  private sampleRate: number = 16000;

  constructor(sampleRate: number = 16000) {
    this.sampleRate = sampleRate;
  }

  private initContext(): AudioContext {
    if (!this.audioContext || this.audioContext.state === 'closed') {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: this.sampleRate
      });
      this.nextStartTime = 0;
    }
    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }
    return this.audioContext;
  }

  enqueuePcmChunk(pcm16Buffer: ArrayBuffer): void {
    const ctx = this.initContext();
    const int16Array = new Int16Array(pcm16Buffer);
    if (int16Array.length === 0) return;

    // Convert Int16 to Float32
    const audioBuffer = ctx.createBuffer(1, int16Array.length, this.sampleRate);
    const channelData = audioBuffer.getChannelData(0);
    for (let i = 0; i < int16Array.length; i++) {
      channelData[i] = int16Array[i] / 32768.0;
    }

    const source = ctx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(ctx.destination);

    const currentTime = ctx.currentTime;
    if (this.nextStartTime < currentTime) {
      this.nextStartTime = currentTime + 0.02; // Small 20ms lead jitter buffer
    }

    source.start(this.nextStartTime);
    this.activeSources.push(source);

    source.onended = () => {
      const idx = this.activeSources.indexOf(source);
      if (idx !== -1) {
        this.activeSources.splice(idx, 1);
      }
    };

    this.nextStartTime += audioBuffer.duration;
  }

  instantFlush(): void {
    // Stop all currently playing audio sources immediately (barge-in cutoff)
    for (const source of this.activeSources) {
      try {
        source.stop();
        source.disconnect();
      } catch (e) {
        // Source might have already finished
      }
    }
    this.activeSources = [];
    if (this.audioContext) {
      this.nextStartTime = this.audioContext.currentTime;
    }
  }

  close(): void {
    this.instantFlush();
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }
  }
}

export class AudioRecorder {
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private processor: ScriptProcessorNode | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private isRecording = false;
  private onAudioChunk: (pcmBytes: ArrayBuffer) => void;
  private onRmsLevel: (rms: number) => void;

  constructor(
    onAudioChunk: (pcmBytes: ArrayBuffer) => void,
    onRmsLevel: (rms: number) => void
  ) {
    this.onAudioChunk = onAudioChunk;
    this.onRmsLevel = onRmsLevel;
  }

  async start(): Promise<void> {
    if (this.isRecording) return;

    this.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      }
    });

    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
      sampleRate: 16000
    });

    this.source = this.audioContext.createMediaStreamSource(this.mediaStream);
    // Buffer size 1024 or 512 for low latency
    this.processor = this.audioContext.createScriptProcessor(1024, 1, 1);

    this.processor.onaudioprocess = (e) => {
      if (!this.isRecording) return;
      const inputData = e.inputBuffer.getChannelData(0);

      // Compute RMS for live meter
      let sum = 0;
      for (let i = 0; i < inputData.length; i++) {
        sum += inputData[i] * inputData[i];
      }
      const rms = Math.sqrt(sum / inputData.length);
      this.onRmsLevel(rms);

      // Convert Float32Array (-1.0 to 1.0) to Int16Array (-32768 to 32767)
      const pcm16 = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        const s = Math.max(-1, Math.min(1, inputData[i]));
        pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }

      this.onAudioChunk(pcm16.buffer);
    };

    this.source.connect(this.processor);
    this.processor.connect(this.audioContext.destination);
    this.isRecording = true;
  }

  stop(): void {
    this.isRecording = false;
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(t => t.stop());
      this.mediaStream = null;
    }
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.onRmsLevel(0);
  }
}

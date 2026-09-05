import asyncio
import json
import sys
import websockets
from app.services.audio_pipeline import AudioPipeline

async def run_improv_test(uri: str = "ws://127.0.0.1:8000/ws/rehearse"):
    print("=" * 65)
    print("🎭 ACTORROOM LIVE: GEMINI LIVE IMPROV MODE VERIFICATION")
    print("=" * 65)

    try:
        async with websockets.connect(uri) as ws:
            print(f"[OK] Connected to WebSocket at {uri}")

            # 1. Start session in IMPROV mode
            start_payload = {
                "type": "START_SESSION",
                "script_id": "interrogation_room",
                "user_character": "DETECTIVE MILLER",
                "mode": "IMPROV"
            }
            await ws.send(json.dumps(start_payload))
            print("[SEND] Sent START_SESSION (Mode: IMPROV, User: DETECTIVE MILLER)")

            # 2. Wait for SESSION_READY
            msg = await ws.recv()
            data = json.loads(msg)
            assert data["type"] == "SESSION_READY", f"Expected SESSION_READY, got {data}"
            print(f"[RECV] SESSION_READY: Scene '{data['scene_title']}'")

            # 3. Wait for Opening Turn LINE_SYNC
            msg = await ws.recv()
            data = json.loads(msg)
            assert data["type"] == "LINE_SYNC"
            print(f"[RECV] Opening CUE: [{data['speaker']}] {data['line_text']}")

            # 4. Simulate Actor speaking an improvised question
            print("\n🎙️ [ACTOR SPEAKING] Simulating actor asking an unscripted question...")
            speech_chunk = AudioPipeline.generate_pcm_sine_wave(frequency_hz=340, duration_seconds=0.04, volume=0.5)
            for _ in range(25):  # 1.0s speech
                await ws.send(speech_chunk)
                await asyncio.sleep(0.04)

            # 5. Actor finishes speaking (silence frames to trigger Gemini turn)
            print("🤫 [ACTOR PAUSE] Silence detected... Handing turn to Gemini Improv...")
            silence_chunk = b"\x00" * len(speech_chunk)
            for _ in range(15):  # 600ms silence
                await ws.send(silence_chunk)
                await asyncio.sleep(0.04)

            # 6. Expect LINE_SYNC for Viktor's newly improvised response!
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    continue
                data = json.loads(msg)
                if data["type"] == "LINE_SYNC" and data.get("speaker") == "VIKTOR":
                    line = data.get("line_text", "")
                    if line.startswith("["):
                        print(f"  (Status: {line})")
                        continue
                    print(f"\n✨ [GEMINI LIVE IMPROV RECEIVED] Viktor: \"{line}\"")
                    break

            # 7. Expect AUDIO_START and receive audio chunks
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    print(f"[AUDIO] Received neural voice chunk ({len(msg)} bytes)")
                    break
                data = json.loads(msg)
                if data["type"] == "AUDIO_START":
                    print(f"[AUDIO] Voice streaming started for [{data['speaker']}]")

            # 8. Conclude take
            print("\n🎬 Concluding Improv Take...")
            await ws.send(json.dumps({"type": "END_TAKE"}))

            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    continue
                data = json.loads(msg)
                if data["type"] == "DIRECTOR_REPORT":
                    critique = data["critique"]
                    print("\n🏆 [GEMINI DIRECTOR IMPROV CRITIQUE]")
                    print(f"  • Rating: {critique['overall_rating']}")
                    print(f"  • Pacing Score: {critique['pacing_score']}%")
                    print("  • Notes:")
                    for n in critique['director_notes']:
                        print(f"    - {n}")
                    break

            print("\n" + "=" * 65)
            print("✅ GEMINI LIVE IMPROV MODE VERIFIED SUCCESSFULLY!")
            print("=" * 65)
            return True

    except Exception as e:
        print(f"\n❌ Improv test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_improv_test())
    sys.exit(0 if success else 1)

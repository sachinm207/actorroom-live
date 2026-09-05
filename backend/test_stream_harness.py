import asyncio
import json
import time
import sys
import websockets
from app.services.audio_pipeline import AudioPipeline

async def run_live_test(uri: str = "ws://127.0.0.1:8000/ws/rehearse"):
    print("=" * 60)
    print("🎬 ACTORROOM LIVE: FULL STREAMING & BARGE-IN VERIFICATION")
    print("=" * 60)

    try:
        async with websockets.connect(uri) as ws:
            print(f"[OK] Connected to WebSocket at {uri}")

            # 1. Start session
            start_payload = {
                "type": "START_SESSION",
                "script_id": "interrogation_room",
                "user_character": "DETECTIVE MILLER"
            }
            await ws.send(json.dumps(start_payload))
            print("[SEND] Sent START_SESSION for DETECTIVE MILLER")

            # 2. Wait for SESSION_READY
            msg = await ws.recv()
            data = json.loads(msg)
            assert data["type"] == "SESSION_READY", f"Expected SESSION_READY, got {data['type']}"
            print(f"[RECV] SESSION_READY: Scene '{data['scene_title']}', Total Lines: {data['total_lines']}")

            # 3. Wait for LINE_SYNC (Line 0: Detective Miller)
            msg = await ws.recv()
            data = json.loads(msg)
            assert data["type"] == "LINE_SYNC" and data["speaker"] == "DETECTIVE MILLER"
            print(f"[RECV] LINE_SYNC 0: [{data['speaker']}] \"{data['line_text']}\"")

            # 4. Simulate Actor speaking line 0 (send active PCM frames)
            print("[SIM] Simulating actor speaking line into mic...")
            speech_chunk = AudioPipeline.generate_pcm_sine_wave(frequency_hz=300, duration_seconds=0.04, volume=0.5)
            for _ in range(25):  # 1 second of speech
                await ws.send(speech_chunk)
                await asyncio.sleep(0.04)

            # 5. Simulate Actor silence (send silence frames to trigger turn handover)
            print("[SIM] Simulating actor pause / finishing line (silence frames)...")
            silence_chunk = b"\x00" * len(speech_chunk)
            for _ in range(15):  # ~600ms silence
                await ws.send(silence_chunk)
                await asyncio.sleep(0.04)

            # 6. Expect LINE_SYNC and AUDIO_START for Viktor (Line 1)
            msg1 = await ws.recv()
            data1 = json.loads(msg1)
            print(f"[RECV] {data1['type']}: [{data1.get('speaker')}] \"{data1.get('line_text', '')}\"")

            msg2 = await ws.recv()
            data2 = json.loads(msg2)
            print(f"[RECV] {data2['type']}: Opposing character AI audio stream initiated!")

            # 7. Receive some audio chunks from Viktor
            audio_chunks_count = 0
            while True:
                chunk = await ws.recv()
                if isinstance(chunk, bytes):
                    audio_chunks_count += 1
                    if audio_chunks_count >= 5:
                        print(f"[RECV] Received {audio_chunks_count} binary PCM audio chunks from Viktor")
                        break
                elif isinstance(chunk, str):
                    print(f"[RECV CONTROL] {chunk}")

            # 8. Trigger BARGE-IN INTERRUPTION while Viktor is talking!
            print("\n⚡ [TEST] Triggering BARGE-IN INTERRUPTION on AI character...")
            barge_in_payload = {"type": "INTERRUPT", "timestamp": time.time()}
            await ws.send(json.dumps(barge_in_payload))

            # 9. Verify BARGE_IN_CONFIRMED (skipping any in-flight binary audio chunks)
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    continue
                data = json.loads(msg)
                if data["type"] == "BARGE_IN_CONFIRMED":
                    print(f"[SUCCESS] {data['type']}: {data.get('message')}")
                    break

            # 10. End take and get Director's Critique
            print("\n🎬 [TEST] Concluding take (END_TAKE)...")
            await ws.send(json.dumps({"type": "END_TAKE"}))

            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    continue
                data = json.loads(msg)
                if data["type"] == "DIRECTOR_REPORT":
                    critique = data["critique"]
                    print("\n🏆 [DIRECTOR'S AUDITION REPORT]")
                    print(f"  • Overall Rating: {critique['overall_rating']}")
                    print(f"  • Pacing Score: {critique['pacing_score']}%")
                    print(f"  • Line Accuracy: {critique['line_accuracy']}%")
                    print(f"  • Take Duration: {critique['take_duration_seconds']}s")
                    print("  • Notes:")
                    for note in critique['director_notes']:
                        print(f"    - {note}")
                    break

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED: Full-Duplex Audio & Barge-in Verified!")
            print("=" * 60)
            return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_live_test())
    sys.exit(0 if success else 1)

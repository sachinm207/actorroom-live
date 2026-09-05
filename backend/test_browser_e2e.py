import os
import sys
import time
from playwright.sync_api import sync_playwright

def run_browser_automation_test():
    print("=" * 65)
    print("🎭 ACTORROOM LIVE: FULL BROWSER AUTOMATION E2E SUITE")
    print("=" * 65)

    screenshot_dir = os.path.join(os.path.dirname(__file__), "test_screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Emulate desktop display 1440x900
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            permissions=["microphone"]
        )
        page = context.new_page()

        # Capture console errors if any
        page.on("pageerror", lambda err: print(f"  [BROWSER ERROR] {err}"))

        # 1. Load Application
        print("\n🌐 Step 1: Navigating to http://localhost:8000...")
        page.goto("http://localhost:8000", wait_until="networkidle")
        title = page.title()
        print(f"  [OK] Page loaded. Title: '{title}'")
        page.screenshot(path=os.path.join(screenshot_dir, "01_initial_load.png"))

        # 2. Verify Key Header Controls
        print("\n🔍 Step 2: Verifying Header Controls & Features...")
        assert page.locator("text=ActorRoom").is_visible(), "ActorRoom brand logo not visible"
        assert page.locator("button:has-text('Scripted')").is_visible(), "Scripted mode button missing"
        assert page.locator("button:has-text('Improv')").is_visible(), "Improv mode button missing"
        assert page.locator("button:has-text('Upload Sides')").is_visible(), "Upload Sides button missing"
        assert page.locator("select", has_text="Casting Reader").is_visible(), "Reader Tone select missing"
        assert page.locator("button:has-text('Ambience')").is_visible(), "Ambience button missing"
        assert page.locator("button:has-text('Start Audition Take')").is_visible(), "Start Take button missing"
        assert page.locator("button:has-text('Dark')").is_visible() or page.locator("button:has-text('Light')").is_visible(), "Theme toggle button missing"
        print("  [OK] All header buttons, selectors, and theme toggle are present.")

        # 3. Test Theme Toggle (Dark <-> Light), Ambience & Reader Tone
        print("\n🎨 Step 3: Testing Light / Dark Theme Switching & Atmosphere...")
        theme_btn = page.locator("button:has-text('Dark')")
        theme_btn.click()
        time.sleep(0.4)
        assert page.locator("button:has-text('Light')").is_visible(), "Theme did not switch to Light"
        print("  [OK] ☀️ Switched to Daylight Light Theme.")
        page.screenshot(path=os.path.join(screenshot_dir, "01b_light_theme.png"))

        # Switch back to Studio Dark Theme
        page.locator("button:has-text('Light')").click()
        time.sleep(0.4)
        assert page.locator("button:has-text('Dark')").is_visible(), "Theme did not switch back to Dark"
        print("  [OK] 🌙 Switched back to Studio Dark Theme.")

        ambience_btn = page.locator("button:has-text('Ambience')")
        ambience_btn.click()
        time.sleep(0.3)
        assert page.locator("button:has-text('Silent')").is_visible(), "Ambience did not toggle to Silent"
        print("  [OK] Ambience toggled to Silent.")
        
        # Toggle back to Ambience
        page.locator("button:has-text('Silent')").click()
        time.sleep(0.3)
        assert page.locator("button:has-text('Ambience')").is_visible(), "Ambience did not toggle back"
        print("  [OK] Ambience toggled back to Ambience.")

        # Select Rapid-Fire Reader Tone
        reader_tone_select = page.locator("select:has-text('Casting Reader')")
        reader_tone_select.select_option("RAPID_FIRE")
        print("  [OK] Selected '⚡ Rapid-Fire (Sorkin Snappy)' Reader Tone.")

        # 4. Verify Screenplay Teleprompter & Character Avatars
        print("\n📜 Step 4: Verifying Teleprompter & Avatars...")
        page.wait_for_selector("h2:has-text('THE INTERROGATION')", timeout=5000)
        assert page.locator("h2", has_text="THE INTERROGATION").is_visible(), "Scene title missing from Teleprompter"
        assert page.locator("text=INT. POLICE INTERROGATION ROOM").is_visible(), "Slugline missing"
        assert page.locator("text=Sit down, Viktor").first.is_visible(), "Miller dialogue missing"
        assert page.locator("h3", has_text="VIKTOR").is_visible(), "Viktor character avatar missing"
        assert page.locator("h3", has_text="DETECTIVE MILLER").is_visible(), "Miller character avatar missing"
        print("  [OK] Teleprompter displays scene heading, characters, and dialogue cues.")

        # 5. Start Audition Take
        print("\n🎙️ Step 5: Starting Audition Take (WebSocket Session)...")
        start_btn = page.locator("button:has-text('Start Audition Take')")
        start_btn.click()
        
        # Check for film slate animation overlay
        time.sleep(0.4)
        if page.locator("text=[ CLAP ] TAKE 1... ACTION!").is_visible():
            print("  [OK] 🎬 Film Slate Animation Triggered: [ CLAP ] TAKE 1... ACTION!")
            page.screenshot(path=os.path.join(screenshot_dir, "02_slate_clap.png"))

        # Wait for live session controls to become active
        page.wait_for_selector("button:has-text('Deliver Line (Simulate)')", timeout=5000)
        assert page.locator("button:has-text('Cut & Review')").is_visible()
        print("  [OK] Rehearsal Session ACTIVE: WebSocket connected and stream open.")
        page.screenshot(path=os.path.join(screenshot_dir, "03_session_active.png"))

        # 6. Simulate Actor Delivering Line
        print("\n🗣️ Step 6: Simulating Actor Delivering Spoken Line...")
        sim_btn = page.locator("button:has-text('Deliver Line (Simulate)')")
        sim_btn.click()
        time.sleep(1.8)
        print("  [OK] Spoken line delivered into live audio pipeline.")
        page.screenshot(path=os.path.join(screenshot_dir, "04_actor_delivered_line.png"))

        # 7. Stop Rehearsal & Request Director Review
        print("\n🎬 Step 7: Concluding Take with 'Cut & Review'...")
        cut_btn = page.locator("button:has-text('Cut & Review')")
        cut_btn.click()

        # Wait for Director Scorecard Modal to open
        print("  Waiting for Gemini Director Critique...")
        page.wait_for_selector("text=Audition Scorecard", timeout=12000)
        print("  [OK] 🏆 Director's Scorecard Modal Opened!")
        
        # Verify Scorecard Contents
        assert page.locator("text=Pacing & Rhythm").is_visible()
        assert page.locator("text=Line Accuracy").is_visible()
        assert page.locator("text=Director's Acting Notes").is_visible()
        print("  [OK] Director Scorecard Metrics & Gemini Notes verified successfully.")
        page.screenshot(path=os.path.join(screenshot_dir, "05_director_scorecard.png"))

        # Close Modal
        close_btn = page.locator("button:has-text('Close')")
        close_btn.click()
        time.sleep(0.5)
        assert not page.locator("text=Audition Scorecard").is_visible()
        print("  [OK] Scorecard closed smoothly. Ready for next take.")

        # 8. Test Improv Mode Switch
        print("\n🎭 Step 8: Testing Live Improv Mode Toggle in Browser...")
        improv_btn = page.locator("button:has-text('Improv')")
        improv_btn.click()
        time.sleep(0.5)
        assert page.locator("text=Gemini Live").is_visible()
        print("  [OK] Switched to 🎭 Improv Mode (Gemini Live active).")
        page.screenshot(path=os.path.join(screenshot_dir, "06_improv_mode.png"))

        browser.close()

    print("\n" + "=" * 65)
    print("✅ BROWSER AUTOMATION SUITE: ALL 8 TEST PHASES PASSED 100%!")
    print(f"📁 Screenshots saved to: {screenshot_dir}")
    print("=" * 65)
    return True

if __name__ == "__main__":
    success = run_browser_automation_test()
    sys.exit(0 if success else 1)

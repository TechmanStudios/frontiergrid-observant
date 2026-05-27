from __future__ import annotations

import sys
import time
from pathlib import Path
import re
from playwright.sync_api import sync_playwright, Page

# Data Store loaded from our workspace drafts
DATA = {
    "abstract": "",
    "benefits": "",
    "uei": "MTXPXGQWBWW5",
    "cage": "8X4K7",
    "legal_name": "Techman Studios",
    "phone": "256-689-6804",
    "ceo_email": "techman@techmanstudios.com",
    "pi_email": "techmandesign@gmail.com",
    "taba_amount": "0",
    "place_perf": "Alexandria, AL 36250",
    "state": "AL",
}


def load_drafts() -> None:
    project_root = Path(__file__).resolve().parent.parent
    submission_dir = project_root / "docs" / "submission"

    # Load abstract
    abstract_path = submission_dir / "technical_abstract.md"
    if abstract_path.exists():
        text = abstract_path.read_text(encoding="utf-8")
        # Remove markdown header if present
        text = re.sub(r"^#.*?\n", "", text, flags=re.MULTILINE).strip()
        DATA["abstract"] = text
        print(f"Loaded Technical Abstract ({len(text)} chars)")
    else:
        print("Warning: technical_abstract.md not found. Using default placeholder.")

    # Load benefits
    benefits_path = submission_dir / "anticipated_benefits.md"
    if benefits_path.exists():
        text = benefits_path.read_text(encoding="utf-8")
        text = re.sub(r"^#.*?\n", "", text, flags=re.MULTILINE).strip()
        DATA["benefits"] = text
        print(f"Loaded Anticipated Benefits ({len(text)} chars)")
    else:
        print("Warning: anticipated_benefits.md not found. Using default placeholder.")


def check_and_autofill(page: Page, filled_selectors: set[str]) -> None:
    """Scan the current page and all iframes for input fields and autofill them."""
    try:
        # Save a screenshot to the recordings folder so the agent/user can inspect the visual state
        recording_dir = Path("C:/Users/techm/.gemini/antigravity/browser_recordings")
        recording_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = recording_dir / "dsip_screen.png"
        page.screenshot(path=str(screenshot_path))
        
        # Traverse all frames on the page (main frame + any iframes)
        for frame in page.frames:
            try:
                elements = frame.query_selector_all("input, textarea, select")
                if elements:
                    print(f"[Debug] Frame '{frame.name or 'main'}' found {len(elements)} inputs.")
            except Exception:
                continue

            for el in elements:
                try:
                    if not el.is_visible():
                        continue
                except Exception:
                    continue

                el_id = el.get_attribute("id") or el.get_attribute("name") or el.get_attribute("class")
                if not el_id:
                    continue

                # Print element detail to help debug
                tag = el.evaluate("el => el.tagName.toLowerCase()")
                print(f"  - Found field: <{tag}> id={el_id}")

                # Create a unique key combining frame name and element ID
                el_key = f"{frame.name or 'main'}:{el_id}"

                # Skip if we already filled this element in this page view
                if el_key in filled_selectors:
                    continue


                try:
                    # Read element tag
                    tag = el.evaluate("el => el.tagName.toLowerCase()")
                    
                    # Check if field is already populated
                    current_value = el.input_value() if tag in ("input", "textarea", "select") else ""
                    if current_value and len(current_value.strip()) > 3:
                        # Field is already filled, don't overwrite
                        continue
                except Exception:
                    continue

                # Matching Rules
                el_id_lower = el_id.lower()

                # 1. Technical Abstract
                if tag == "textarea" and "abstract" in el_id_lower:
                    print(f"[Autofill] Typing Technical Abstract into: {el_id}")
                    el.fill(DATA["abstract"])
                    filled_selectors.add(el_key)

                # 2. Anticipated Benefits
                elif tag == "textarea" and ("benefit" in el_id_lower or "commercial" in el_id_lower):
                    print(f"[Autofill] Typing Anticipated Benefits into: {el_id}")
                    el.fill(DATA["benefits"])
                    filled_selectors.add(el_key)

                # 3. UEI
                elif tag == "input" and "uei" in el_id_lower:
                    print(f"[Autofill] Typing UEI into: {el_id}")
                    el.fill(DATA["uei"])
                    filled_selectors.add(el_key)

                # 4. CAGE Code
                elif tag == "input" and "cage" in el_id_lower:
                    print(f"[Autofill] Typing CAGE Code into: {el_id}")
                    el.fill(DATA["cage"])
                    filled_selectors.add(el_key)

                # 5. TABA Amount
                elif tag == "input" and ("taba" in el_id_lower and ("amount" in el_id_lower or "value" in el_id_lower)):
                    print(f"[Autofill] Typing TABA Amount into: {el_id}")
                    el.fill(DATA["taba_amount"])
                    filled_selectors.add(el_key)

                # 6. Place of Performance
                elif tag == "input" and ("performance" in el_id_lower or "perf" in el_id_lower or "place" in el_id_lower):
                    print(f"[Autofill] Typing Place of Performance into: {el_id}")
                    el.fill(DATA["place_perf"])
                    filled_selectors.add(el_key)

                # 7. Phone
                elif tag == "input" and "phone" in el_id_lower and "company" in el_id_lower:
                    print(f"[Autofill] Typing Company Phone into: {el_id}")
                    el.fill(DATA["phone"])
                    filled_selectors.add(el_key)

                # 8. CEO / CO Email
                elif tag == "input" and "email" in el_id_lower and ("ceo" in el_id_lower or "signatory" in el_id_lower or "official" in el_id_lower):
                    print(f"[Autofill] Typing CEO Email into: {el_id}")
                    el.fill(DATA["ceo_email"])
                    filled_selectors.add(el_key)

                # 9. PI Email
                elif tag == "input" and "email" in el_id_lower and ("pi" in el_id_lower or "tpoc" in el_id_lower or "engineer" in el_id_lower):
                    print(f"[Autofill] Typing PI Email into: {el_id}")
                    el.fill(DATA["pi_email"])
                    filled_selectors.add(el_key)

    except Exception as e:
        # Catch and print general errors for debugging
        print(f"[Debug Error] check_and_autofill encountered: {e}")



def main() -> None:
    print("====================================================")
    print("         DSIP PORTAL AUTOFILL ASSISTANT              ")
    print("====================================================")
    
    load_drafts()
    
    target_url = "https://www.dodsbirsttr.mil/submissions/proposal/94dc715ce5cb49b4a379d0040140cae2_140774/proposal-summary"
    
    print("\nLaunching headful browser...")
    with sync_playwright() as p:
        # Launch Chromium or Edge if present. chromium is default
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Capture console messages from the page
        page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
        
        print(f"Navigating to: {target_url}")
        page.goto(target_url)
        
        print("\n*** ASSISTANT ACTIVE ***")
        print("Please log in to the portal in the browser window.")
        print("I will monitor the pages and automatically type in draft values as you reach the forms.")
        print("Press Ctrl+C in this terminal window to stop the assistant.\n")
        
        last_url = ""
        filled_selectors: set[str] = set()
        
        try:
            while True:
                if page.is_closed():
                    print("Browser window closed. Exiting.")
                    break
                
                # Check for URL navigation changes
                current_url = page.url
                if current_url != last_url:
                    print(f"[Navigate] Current URL: {current_url}")
                    # Clear filled markers so we attempt to fill on the new page
                    filled_selectors.clear()
                    last_url = current_url
                
                # Run the autofill checker
                check_and_autofill(page, filled_selectors)

                # Control Channel: check if external command was sent
                cmd_file = Path("C:/Users/techm/.gemini/antigravity/scratch/cmd.txt")
                if cmd_file.exists():
                    try:
                        content = cmd_file.read_text(encoding="utf-8").strip()
                        cmd_file.unlink() # consume the command
                        print(f"[Control] Processing: {content}")
                        if content == "screenshot":
                            page.screenshot(path="C:/Users/techm/.gemini/antigravity/browser_recordings/dsip_screen.png")
                            print("[Control] Forced screenshot captured.")
                        elif content.startswith("click "):
                            target = content[6:]
                            clicked = False
                            # Search in all frames
                            for frame in page.frames:
                                try:
                                    if frame.locator(target).count() > 0:
                                        frame.locator(target).first.click()
                                        print(f"[Control] Clicked selector in frame '{frame.name or 'main'}': {target}")
                                        clicked = True
                                        break
                                    elif frame.get_by_text(target).count() > 0:
                                        frame.get_by_text(target).first.click()
                                        print(f"[Control] Clicked text in frame '{frame.name or 'main'}': {target}")
                                        clicked = True
                                        break
                                except Exception:
                                    pass
                            if not clicked:
                                # Try clicking link or button containing text
                                for frame in page.frames:
                                    try:
                                        elements = frame.query_selector_all("a, button, div, span")
                                        for el in elements:
                                            if target.lower() in (el.inner_text() or "").lower():
                                                el.click()
                                                print(f"[Control] Clicked matched text element in frame '{frame.name or 'main'}': {el.inner_text()}")
                                                clicked = True
                                                break
                                        if clicked:
                                            break
                                    except Exception:
                                        pass
                            if not clicked:
                                print(f"[Control] Click target not found: '{target}'")
                        elif content.startswith("scroll "):
                            pixels = int(content[7:])
                            page.evaluate(f"window.scrollBy(0, {pixels})")
                            print(f"[Control] Scrolled by {pixels} pixels.")
                        elif content.startswith("fill "):
                            parts = content[5:].split(" ", 1)
                            if len(parts) == 2:
                                sel, val = parts
                                # Resolve local draft key if matching
                                if val in DATA:
                                    val = DATA[val]
                                page.fill(sel, val)
                                print(f"[Control] Filled {sel}")
                            else:
                                print("[Control] Invalid fill format. Use: fill selector value")
                        elif content.startswith("eval "):
                            code = content[5:]
                            res = page.evaluate(code)
                            print(f"[Control] Eval result: {res}")
                        elif content.startswith("goto "):
                            url = content[5:]
                            page.goto(url)
                            print(f"[Control] Navigated to: {url}")
                    except Exception as ce:
                        print(f"[Control Error] Failed to execute control command: {ce}")
                
                time.sleep(1.5)
        except KeyboardInterrupt:
            print("\nAutofill Assistant stopped by user. Closing browser...")
        finally:
            browser.close()


if __name__ == "__main__":
    main()


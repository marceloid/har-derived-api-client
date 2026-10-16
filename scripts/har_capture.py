#!/usr/bin/env python3
"""
har_capture.py - Launch browser with Playwright, execute actions, and save network traffic to a HAR file.
"""

import sys
import argparse
import time
from playwright.sync_api import sync_playwright

def run_capture(url, har_path, actions=None, wait_time=3, headed=False):
    actions = actions or []
    print(f"Launching browser to capture {url} -> {har_path}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        context = browser.new_context(
            record_har_path=har_path,
            record_har_content="embed"
        )
        page = context.new_page()

        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle", timeout=60000)

        for act in actions:
            parts = act.split(":", 2)
            cmd = parts[0].lower()

            if cmd == "fill" and len(parts) == 3:
                selector, text = parts[1], parts[2]
                print(f"Action: fill {selector} with '{text}'")
                page.fill(selector, text)
            elif cmd == "click" and len(parts) >= 2:
                selector = parts[1]
                print(f"Action: click {selector}")
                page.click(selector)
            elif cmd == "press" and len(parts) == 3:
                selector, key = parts[1], parts[2]
                print(f"Action: press {key} on {selector}")
                page.press(selector, key)
            elif cmd == "sleep" and len(parts) >= 2:
                secs = float(parts[1])
                print(f"Action: sleep {secs}s")
                time.sleep(secs)
            elif cmd == "goto" and len(parts) >= 2:
                target_url = parts[1]
                print(f"Action: goto {target_url}")
                page.goto(target_url, wait_until="networkidle")

        if wait_time > 0:
            print(f"Waiting {wait_time}s for late requests to flush...")
            time.sleep(wait_time)

        context.close()
        browser.close()

    print(f"HAR successfully saved to {har_path}")

def main():
    parser = argparse.ArgumentParser(description="Capture HAR with Playwright")
    parser.add_argument("url", help="Initial URL")
    parser.add_argument("har_file", help="Output HAR path")
    parser.add_argument("--action", action="append", help="Action in format 'fill:sel:text', 'click:sel', 'press:sel:key', 'sleep:sec'")
    parser.add_argument("--wait", type=float, default=3.0, help="Wait time in seconds after actions")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode")

    args = parser.parse_args()
    run_capture(args.url, args.har_file, args.action, args.wait, args.headed)

if __name__ == "__main__":
    main()

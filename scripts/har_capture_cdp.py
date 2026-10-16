#!/usr/bin/env python3
"""
har_capture_cdp.py - Attach to an existing CDP browser endpoint and record network traffic to HAR.
"""

import sys
import json
import time
import argparse
from playwright.sync_api import sync_playwright

def run_cdp_capture(cdp_url, har_path, goto_url=None, actions=None, wait_time=3):
    actions = actions or []
    print(f"Connecting to CDP endpoint: {cdp_url}...")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()

        requests_log = []

        def on_request(req):
            entry = {
                'url': req.url,
                'method': req.method,
                'headers': req.headers,
                'postData': req.post_data
            }
            requests_log.append(entry)

        page.on("request", on_request)

        if goto_url:
            print(f"Navigating to {goto_url}...")
            page.goto(goto_url, wait_until="networkidle")

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

        if wait_time > 0:
            print(f"Waiting {wait_time}s...")
            time.sleep(wait_time)

        # Save requests summary
        with open(har_path, 'w', encoding='utf-8') as f:
            json.dump({'requests': requests_log}, f, indent=2)

        print(f"Captured {len(requests_log)} requests to {har_path}")

def main():
    parser = argparse.ArgumentParser(description="Capture network via CDP")
    parser.add_argument("cdp_url", help="CDP WebSocket URL")
    parser.add_argument("output_json", help="Output JSON path")
    parser.add_argument("--goto", help="Optional URL to navigate to")
    parser.add_argument("--action", action="append", help="Action spec")
    parser.add_argument("--wait", type=float, default=3.0)

    args = parser.parse_args()
    run_cdp_capture(args.cdp_url, args.output_json, args.goto, args.action, args.wait)

if __name__ == "__main__":
    main()

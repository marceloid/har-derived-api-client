#!/usr/bin/env python3
"""
har_to_client.py - Filter HAR files to XHR/fetch/JSON and generate API client templates.
"""

import json
import sys
import argparse
from urllib.parse import urlparse, parse_qs

def parse_har(har_path, host_filter=None, max_body=500):
    with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)

    entries = data.get('log', {}).get('entries', [])
    print(f"Total entries in HAR: {len(entries)}")

    api_entries = []

    for entry in entries:
        req = entry.get('request', {})
        res = entry.get('response', {})
        url = req.get('url', '')
        parsed_url = urlparse(url)

        if host_filter and host_filter.lower() not in parsed_url.netloc.lower():
            continue

        # Filter out static assets
        path_lower = parsed_url.path.lower()
        if any(path_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.woff', '.woff2', '.ttf', '.js', '.map']):
            continue

        res_mime = res.get('content', {}).get('mimeType', '').lower()
        res_text = res.get('content', {}).get('text', '')

        # Keep XHR / fetch / JSON / APIs
        is_json = 'json' in res_mime or (res_text and res_text.strip().startswith(('{', '[')))
        is_api = '/api/' in url or '/rest/' in url or '/service' in url or is_json

        if is_api or is_json or req.get('method') in ['POST', 'PUT', 'DELETE', 'PATCH']:
            api_entries.append({
                'method': req.get('method'),
                'url': url,
                'path': parsed_url.path,
                'query': parse_qs(parsed_url.query),
                'headers': {h['name']: h['value'] for h in req.get('headers', [])},
                'cookies': req.get('cookies', []),
                'post_data': req.get('postData', {}),
                'status': res.get('status'),
                'res_mime': res_mime,
                'res_body': res_text[:max_body] if res_text else ''
            })

    print(f"\nFiltered API/XHR entries found: {len(api_entries)}\n")

    for i, e in enumerate(api_entries, 1):
        print(f"================================================================================")
        print(f"[{i}] {e['method']} {e['url']} (Status: {e['status']})")
        print(f"--------------------------------------------------------------------------------")

        if e['query']:
            print("Query Parameters:")
            for k, v in e['query'].items():
                print(f"  {k}: {v}")

        # Highlight important headers (Auth, Content-Type, etc.)
        important_headers = {}
        for k, v in e['headers'].items():
            k_lower = k.lower()
            if any(h in k_lower for h in ['auth', 'token', 'cookie', 'content-type', 'accept', 'x-', 'referer', 'origin']):
                # Mask long tokens for safety in logs
                val_display = v
                if 'bearer' in v.lower() and len(v) > 40:
                    val_display = v[:20] + '...' + v[-10:]
                important_headers[k] = val_display

        if important_headers:
            print("Relevant Request Headers:")
            for k, v in important_headers.items():
                print(f"  {k}: {v}")

        if e['post_data']:
            print("Request Body:")
            print(f"  MimeType: {e['post_data'].get('mimeType')}")
            print(f"  Text: {e['post_data'].get('text')}")

        if e['res_body']:
            print("Response Body Sample:")
            print(f"  {e['res_body']}")

        print("\n")

def main():
    parser = argparse.ArgumentParser(description="Extract API endpoints from HAR")
    parser.add_argument("har_file", help="Path to HAR file")
    parser.add_argument("--host", help="Filter by host substring")
    parser.add_argument("--max-body", type=int, default=500, help="Max characters of body to show")

    args = parser.parse_args()
    parse_har(args.har_file, args.host, args.max_body)

if __name__ == "__main__":
    main()

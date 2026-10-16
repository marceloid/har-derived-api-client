---
name: har-derived-api-client
description: "Record a website's network traffic (HAR/XHR) and distill it into a browserless, pure HTTP/JSON API client. Use when replacing UI browser automation with clean API calls, reverse-engineering internal APIs, or converting web scraping into fast REST requests."
---

# HAR-Derived API Client

Drive a website once with a real browser while recording its network traffic to a HAR file (or via Chrome CDP), then distill that HAR into the site's private JSON API so you can call it directly with plain HTTP — far faster, deterministic, and cheaper than controlling a browser on every request.

## When to Use

- "Build a CLI/client for <website>" — derive its API instead of scripting clicks.
- "This site has no public API but the page clearly fetches JSON in the background."
- Reverse-engineering autocomplete, search, or internal municipal/enterprise APIs (e.g. SISCONP, SIATU).
- Eliminating headless browser dependencies from backend services.

## Architecture & Workflow

1. **Capture**: Run the browser once to record network requests (`.har` or CDP Network).
2. **Derive**: Analyze endpoints, query params, headers, authentication tokens, and request/response payloads using `scripts/har_to_client.py`.
3. **Synthesize**: Write a pure TypeScript/Node.js or Python client with `fetch()` / `httpx`.
4. **Test**: Validate directly with HTTP requests without opening any browser.

## Scripts

- `scripts/har_capture.py`: Launches a browser with Playwright, performs actions, and records a full HAR file with embedded responses.
  ```bash
  python3 <skill-path>/scripts/har_capture.py "https://example.com" out.har --action "fill:input[name=cpf]:12345678900" --action "click:button[type=submit]" --wait 3
  ```
- `scripts/har_capture_cdp.py`: Attaches to an existing Chrome browser over CDP to record traffic.
- `scripts/har_to_client.py`: Parses the HAR file, filters out static assets, and displays all API endpoints with headers, request bodies, and JSON responses.
  ```bash
  python3 <skill-path>/scripts/har_to_client.py out.har --host pbh.gov.br --max-body 500
  ```

# geminiScrapper

## What This Is

An API scraper built with Python, FastAPI, and Playwright that allows sending prompts to Gemini via a headless/automated browser session and returning the responses through a standard REST POST endpoint. It acts as an unofficial API wrapper for personal use.

## Core Value

Reliably mimic a real API experience by successfully passing prompts to the Gemini web interface and capturing the complete response text.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] FastAPI server with a POST endpoint receiving a prompt in the request body.
- [ ] Playwright integration to control a Chromium browser instance.
- [ ] Connection to an existing user browser profile to bypass login/authentication walls.
- [ ] Logic to locate the Gemini chat input, paste the prompt, and submit.
- [ ] Logic to wait for the response generation to finish and extract the resulting text.
- [ ] Return the extracted text as a JSON response to the API caller.

### Out of Scope

- Handling re-authentication or login flows — relying entirely on the pre-existing user profile.
- Scaling to handle multiple concurrent requests simultaneously — this is for personal use, so a single synchronous queue or basic handling is sufficient initially.

## Context

- **Tech Stack:** Python, FastAPI, Playwright.
- **Target Platform:** Google Gemini web interface.
- **Authentication:** Relies on an existing browser profile (already logged in).
- **Usage:** Personal use only, bridging the gap where official APIs might be costly or have different constraints.

## Constraints

- **Authentication:** Must launch Playwright using an existing user data directory.
- **Browser Automation:** Must handle dynamic DOM changes in the Gemini interface, which are prone to updates.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use FastAPI | Lightweight, fast, and easy to build async APIs in Python | — Pending |
| Use Playwright with existing profile | Avoids dealing with complex login/captcha flows and provides a persistent session | — Pending |

---
*Last updated: 2026-05-22 after initialization*

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

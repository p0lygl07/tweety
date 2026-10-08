# Changelog

## v0.1.0 — 2026-10-08 (working prototype)
First end-to-end working build on hardware.

- Firmware (`firmware/main.py`): single-file MicroPython that boots into a captive setup
  portal (hosts `Tweety-Setup` AP + browser config page) or arms as a network canary.
- Canary: listens on a decoy port, POSTs a JSON alert to a user webhook on any connection,
  sends a fake SSH banner, LED heartbeat/trip states.
- Verified on a Pico W: portal served, Wi-Fi join, trip detected, webhook alert delivered.
- Case: `hardware/case/` — Pico W two-shell adapted from the Kraken/Pico case, canary emblem
  (flush two-colour, eye knockout) + LED light-window. Generator + 3MF + STLs.
- Emblem: `emblem/` — canary art (SVG + PNG) extracted from the source insignia.

### Open items (next)
- Blank-webhook guard in the setup portal (accepts empty webhook today).
- Captive-portal DNS auto-pop.
- Decide per-unit vs. shared AP password.
- Price + Shopify listing.
- v2: physical-tripwire mode (reed/tilt/vibration sensor + screw terminal).
- Push to github.com/p0lygl07/tweety.

# Tweety  (in the lab)

**Network canary / tripwire** — a Raspberry Pi **Pico W** that sits silent on an unused
port and screams the instant anything touches it. The **blue-team** member of the line:
every other P01yg107 tool attacks, Tweety watches your back.

- **Board:** Raspberry Pi **Pico W** (RP2040 + CYW43439 2.4 GHz Wi-Fi) — micro-USB
- **How it works:** listens on a decoy port (default **2323**). Nothing legitimate ever
  connects there, so any connection is an intruder — it fires a webhook alert with the
  source IP. No false positives by design.
- **Setup:** first boot hosts its own **"Tweety-Setup"** Wi-Fi AP + a browser config page.
  The customer picks their Wi-Fi and pastes **their own webhook** (Discord / Slack /
  webhook.site / anything that takes a POST). No app, no cable, no cloud account.
- **Theme:** original red **canary** mark, flush two-colour (PETG-CF body + Hyper-PLA emblem)
- **Firmware:** own firmware (MicroPython) — MIT, in `firmware/`
- **Price:** TBD (preorder)   **Repo:** github.com/p0lygl07/tweety (to push)
- **Status:** working prototype — portal + Wi-Fi + canary + webhook alert verified
  end-to-end on hardware (2026-10-08). Case + emblem done (`hardware/case/tweety-case.3mf`).
- **Case:** two-shell, adapted from the Kraken/Pico case (shared footprint); canary emblem
  swapped in, plus an LED light-window so the heartbeat/trip blink shows.

## Quick start
1. Flash MicroPython (Pico W build) → copy `firmware/main.py` to the board as `main.py`.
2. `mpremote mip install urequests`
3. Power it → join Wi-Fi **Tweety-Setup** (pass `tweetsetup`) → open `http://192.168.4.1`.
4. Pick Wi-Fi, paste your webhook, Save & Arm.
5. Trip it: `ssh <device-ip> -p 2323` → your webhook gets a JSON alert.

Full walk-throughs in `docs/QUICKSTART.md` (customer) and `docs/SETUP.md` (provisioning).

## LED states
| LED | Meaning |
|-----|---------|
| slow pulse | setup mode (waiting for config) |
| solid | armed and watching |
| rapid flash | trip — alert fired |
| fast panic blink | Wi-Fi failed → fell back to setup so it can be fixed |

## Layout
```
firmware/   main.py (setup-portal + canary), config.example.json
tools/      wifi_test.py (bring-up test)
hardware/   case/ — generator, 3MF, STLs, top-view render
emblem/     canary silhouette / 2-colour / lid art (SVG + PNG) + contour JSON
docs/       QUICKSTART.md, SETUP.md
```

> Authorized use only. Tweety is a defensive tripwire for networks you own or are cleared
> to monitor.

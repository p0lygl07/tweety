# Tweety — Bill of Materials (per unit)

## Core
| Part | Spec | Qty | ~Cost (small qty) |
|------|------|-----|------|
| Dev board | Raspberry Pi **Pico W** (RP2040 + CYW43439 Wi-Fi) | 1 | $6 |
| Enclosure | PETG-CF two-shell case + Hyper-PLA two-colour canary emblem | 1 | ~$0.70 |
| Misc | none required (no sensors in v1 network-canary mode) | — | — |

**Prototype core ≈ $6–7/unit.** Lowest-BOM product in the line — board + a printed case,
no antenna, no extra chips. Tools: USB (micro-USB) cable for flashing, calipers.

## Notes
- **Must be the Pico W** (not a plain Pico) — the whole product depends on the onboard
  Wi-Fi. A non-W Pico has no radio and cannot run as a network canary.
- Firmware is our own (MIT), flashed on top of MicroPython — not a BOM cost.
- v2 (physical-tripwire mode) would add a reed switch / tilt / vibration sensor + a 2-pin
  screw terminal (~$0.30) — parked for now.

## Scale path
Pico W in trays + bulk PETG-CF/Hyper-PLA keeps per-unit cost the lowest of any tool we ship,
which leaves the most margin room at a defensive-tool price point.

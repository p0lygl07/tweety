# Tweety — Enclosure (DONE)

Built from the **Kraken HID / Pico case** — the Pico W shares the Pico footprint, so the
proven shell is reused unchanged. Original `kraken-case.3mf` left untouched; the Tweety
variant is **`tweety-case.3mf`** (in `hardware/case/` and `03_Manufacturing/Print-Files-3MF/`).

## What changed from the Kraken case
**Only the emblem.** The kraken part was swapped for the canary — nothing else was touched:
the lid shell, base, GPIO pin labels, USB cutout, window and plate layout are byte-identical,
and so are the print profile and filament assignments.

1. **Emblem:** the kraken-shaped pocket in the lid's emblem face was filled, a **canary**
   pocket cut in its place, and the `kraken` part replaced with the canary solid.
   Parts are now `lid` (extruder 1) + **`canary` (extruder 2)** inside `lid_with_canary`.
2. **Eye knockout:** the canary's eye is a hole in the emblem, so the black case shows
   through it — same flush two-colour trick as the Oikake ghost. No third colour.

Reproducible: `hardware/case/swap_emblem.py` performs the swap on the original Kraken 3MF.

## Geometry (verified)
| Part | Size (mm) | Notes |
|------|-----------|-------|
| Lid (`lid_with_canary`) | 27.4 × 57.4 × 7.8 | unchanged from the Kraken lid |
| Canary emblem | 15.86 × 14.19 × 0.6 | same 0.6 mm thickness and bbox area as the kraken |
| Base (`case_base`) | 24.7 × 54.7 × 3.0 | untouched |

**The emblem face prints face-down** (the emblem occupies the first 0.6 mm off the plate) —
that's what makes it perfectly flush. The art is mirrored in the model so it reads the right
way round on the finished part, exactly like the engraved pin labels already do.
See `tweety-orientation-check.png` and `tweety-emblem-face.png`.

## Printing
Open **`tweety-case.3mf`** in Creality Print. Two objects land — `case_base` and
`lid_with_canary` — already arranged, and the filament assignments come with the file:

- **Filament 1 — PETG-CF `#3A3A3D`** (250 °C): base, lid shell
- **Filament 2 — Hyper PLA red `#C12E1F`** (220 °C): the canary

No "multi-part object" prompt and no collision warning — the lid and canary are already
one object with two parts, which is how the Kraken case was always built.

### PETG-CF print notes (K2, from the line)
- Hardened steel nozzle (carbon fibre is abrasive).
- Dry filament ~65 °C / 4–6 h first.
- ~250 °C nozzle, 0.2 mm layers. Hyper-PLA emblem ~220 °C.

## Confirm before a batch
- Slicer check: the canary shows on **extruder 2** (red), the eye stays case-black, and
  nothing squid-shaped remains anywhere on the lid.
- First layer is the emblem face — watch that the colour change is clean on layer 1–3.
- Everything else is the shipping Kraken case, so fit is already proven.

## Emblem files
`emblem/tweety-lid.svg` (flush/knockout — the art used on the case), `tweety-2color.svg`,
`tweety-canary-silhouette.svg` (+ matching PNGs) and `canary_contours.json` (the geometry
`swap_emblem.py` reads). Mirrored into `04_Brand-Assets/Tweety/`.

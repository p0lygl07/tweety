# Tweety — Provisioning / Flashing (builder notes)

How to flash a blank Pico W into a Tweety. Run everything from **Windows PowerShell**
(WSL2 can't see USB serial without usbipd — don't fight it).

## 1. MicroPython
Download the **Pico W** build (`RPI_PICO_W`) from https://micropython.org/download/RPI_PICO_W/
(must be the W build — it carries the Wi-Fi driver).

Hold **BOOTSEL**, plug in USB, release → drive `RPI-RP2` appears → drag the `.uf2` on. It
reboots and the drive disappears = flashed.

## 2. Tools
```powershell
pip install mpremote
mpremote connect list          # note the COM port, e.g. COM16
```

## 3. Dependencies + firmware
```powershell
mpremote connect COM16 mip install urequests
mpremote connect COM16 fs cp firmware/main.py :main.py
mpremote connect COM16 reset
```
`main.py` auto-runs on power-up. With no saved config it boots into **setup mode** and hosts
the `Tweety-Setup` AP.

## 4. Verify (optional)
```powershell
mpremote connect COM16 repl       # Ctrl-D to soft-reboot, watch it print SETUP MODE
mpremote connect COM16 fs cat config.json   # after a customer configures it
```
A quick Wi-Fi bring-up test (before loading the full firmware) lives in `tools/wifi_test.py`:
```powershell
mpremote connect COM16 run tools/wifi_test.py
```

## 5. Factory reset a unit
```powershell
mpremote connect COM16 fs rm config.json
mpremote connect COM16 reset
```
Back to a clean `Tweety-Setup` state for the next customer.

## How the firmware is structured (`firmware/main.py`)
- **boot** → `load_config()`; no valid `config.json` → `run_setup()`, else `run_canary()`.
- **run_setup()** — hosts `Tweety-Setup` AP, scans nearby Wi-Fi, serves the config page on
  `192.168.4.1`, writes `config.json` on POST, reboots.
- **run_canary()** — joins Wi-Fi, binds the watch port, and POSTs the JSON alert on any
  connection. Bad Wi-Fi falls back to `run_setup()` so a unit never bricks.

## Known open items
- **Blank-webhook guard** — the portal currently accepts an empty webhook field (saves with
  no alert target). Add a required-field check so Save is rejected until a webhook is entered.
  (This is the one thing that bit us in testing.)
- **Captive-portal auto-pop** — add a DNS catch-all so the setup page opens automatically on
  join, instead of typing `192.168.4.1`.
- **Per-unit AP password** — currently a shared default; decide per-unit vs. standard.

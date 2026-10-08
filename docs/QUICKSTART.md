# Tweety — Quick Start (customer)

Tweety is a **network canary**. Plug it in, point it at your alert channel, and it tells you
the moment anything touches it. No app, no account.

## 1. Power it on
Plug Tweety into any USB power (wall brick, PC, battery). The LED does a **slow pulse** —
that means it's in setup mode, waiting for you.

## 2. Join its Wi-Fi
On your phone or laptop, open Wi-Fi settings and connect to:

- **Network:** `Tweety-Setup`
- **Password:** `tweetsetup`

Your device may say "no internet" — that's normal, stay connected. (If your phone won't load
the next step, turn **mobile data off** so it uses this Wi-Fi.)

## 3. Open the setup page
In a browser go to **http://192.168.4.1**

Fill in:
- **Your Wi-Fi network** — pick it from the list (2.4 GHz only — Tweety can't see 5 GHz).
- **Wi-Fi password**
- **Alert webhook URL** — where alerts go. Any URL that accepts a POST:
  - **Discord:** channel → Edit → Integrations → Webhooks → New → copy URL
  - **Slack:** an Incoming Webhook URL
  - **Test it first:** open https://webhook.site, copy your unique URL, paste it here
- **Device name** — e.g. "Front-office Tweety"
- **Watch port** — leave `2323` unless you have a reason to change it

Tap **Save & Arm**. Tweety reboots and joins your network.

## 4. It's armed
The LED goes **solid** = watching. Done. Leave it plugged in wherever you want a tripwire:
a spare USB port on a server, a network closet, a reception desk.

## 5. Test it
From another device on the same network:
```
ssh <tweety-ip> -p 2323
```
(or just open `http://<tweety-ip>:2323` in a browser). Tweety's LED does a **rapid flash**
and your webhook gets an alert like:
```json
{"event":"trip","device":"Tweety","source_ip":"192.168.1.44","port":2323,"canary_ip":"192.168.1.50"}
```

## Reconfigure later
Changed your Wi-Fi or webhook? Hold tight — if Tweety can't reach your Wi-Fi it automatically
drops back into **Tweety-Setup** mode (slow pulse) so you can set it up again. To force it,
clear the saved config (delete `config.json` over USB) and reboot.

## LED cheat-sheet
| LED | Meaning |
|-----|---------|
| slow pulse | setup mode — join `Tweety-Setup` |
| solid | armed and watching |
| rapid flash | something tripped it — alert sent |
| fast panic blink | couldn't join Wi-Fi — dropping back to setup |

---
*Authorized use only. Tweety is a defensive tripwire for networks you own or are cleared to monitor.*

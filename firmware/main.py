# main.py - Tweety canary (Pico W)
# Boots into SETUP mode (hosts its own AP + web config page) when there is no
# valid saved config, otherwise boots into CANARY mode and arms.
# P01yg107 Labs

import network, socket, time, json, machine

CONFIG_FILE = "config.json"
SETUP_AP    = "Tweety-Setup"      # AP customers connect to for first-time setup
SETUP_PASS  = "tweetsetup"        # 8+ chars; shown on the quick-start card
AP_IP       = "192.168.4.1"

led = machine.Pin("LED", machine.Pin.OUT)

def blink(n=1, on=0.08, off=0.08):
    for _ in range(n):
        led.on(); time.sleep(on); led.off(); time.sleep(off)

# ---------- config ----------
def load_config():
    try:
        with open(CONFIG_FILE) as f:
            c = json.load(f)
        if c.get("ssid"):
            return c
    except Exception:
        pass
    return None

def save_config(c):
    with open(CONFIG_FILE, "w") as f:
        json.dump(c, f)

# ---------- tiny url helpers ----------
def url_decode(s):
    s = s.replace("+", " ")
    out = ""
    i = 0
    while i < len(s):
        if s[i] == "%" and i + 2 < len(s):
            try:
                out += chr(int(s[i+1:i+3], 16)); i += 3; continue
            except Exception:
                pass
        out += s[i]; i += 1
    return out

def parse_form(body):
    d = {}
    for pair in body.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            d[url_decode(k)] = url_decode(v)
    return d

# ---------- setup mode ----------
def scan_networks():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    seen = []
    try:
        for n in sta.scan():
            name = n[0].decode("utf-8", "ignore")
            if name and name not in seen:
                seen.append(name)
    except Exception:
        pass
    return seen[:20]

def setup_page(nets, saved=False):
    opts = "".join("<option value='%s'>%s</option>" % (n, n) for n in nets)
    done = ""
    if saved:
        done = ("<div class='ok'>Saved. Tweety is rebooting and joining your "
                "network. You can close this page.</div>")
    return """<!DOCTYPE html><html><head><meta name='viewport'
content='width=device-width,initial-scale=1'><title>Tweety Setup</title>
<style>
body{font-family:system-ui,sans-serif;background:#1a1a1f;color:#f3f3f3;margin:0;padding:24px}
.card{max-width:420px;margin:0 auto;background:#24242b;border:1px solid #3a3a44;
border-radius:14px;padding:22px}
h1{color:#ffd23f;font-size:22px;margin:0 0 4px}
.sub{color:#9a9aa5;font-size:13px;margin:0 0 18px}
label{display:block;font-size:13px;margin:14px 0 5px;color:#cfcfd6}
input,select{width:100%;box-sizing:border-box;padding:11px;border-radius:8px;
border:1px solid #44444f;background:#1a1a1f;color:#fff;font-size:15px}
button{width:100%;margin-top:20px;padding:13px;border:0;border-radius:9px;
background:#ffd23f;color:#1a1a1f;font-size:16px;font-weight:700}
.ok{background:#1f3a24;border:1px solid #2f7d3e;color:#8ef0a0;padding:12px;
border-radius:8px;margin-bottom:16px;font-size:14px}
.hint{color:#7a7a85;font-size:11px;margin-top:4px}
</style></head><body><div class='card'>
<h1>&#128038; Tweety Setup</h1>
<p class='sub'>P01yg107 Labs - network canary</p>
""" + done + """
<form method='POST' action='/save'>
<label>Your WiFi network</label>
<select name='ssid'>""" + opts + """</select>
<label>WiFi password</label>
<input name='password' type='password' placeholder='network password'>
<label>Alert webhook URL</label>
<input name='webhook' type='url' placeholder='https://...'>
<div class='hint'>Discord, Slack, webhook.site, or any URL that accepts a POST.</div>
<label>Device name</label>
<input name='device_name' value='Tweety' placeholder='Tweety'>
<label>Watch port</label>
<input name='port' value='2323' placeholder='2323'>
<div class='hint'>An unused port. Any connection to it fires an alert.</div>
<button type='submit'>Save &amp; Arm</button>
</form></div></body></html>"""

def http_send(conn, body, status="200 OK"):
    if isinstance(body, str):
        body = body.encode("utf-8")
    header = ("HTTP/1.1 %s\r\nContent-Type: text/html\r\n"
              "Content-Length: %d\r\nConnection: close\r\n\r\n"
              % (status, len(body))).encode("utf-8")
    data = header + body
    # send in small chunks; MicroPython can short-write a big single send
    mv = memoryview(data)
    sent = 0
    while sent < len(data):
        try:
            n = conn.send(mv[sent:sent + 512])
        except OSError:
            break
        if not n:
            break
        sent += n

def run_setup():
    # steady slow pulse = waiting for setup
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SETUP_AP, password=SETUP_PASS)
    while not ap.active():
        time.sleep(0.2)
    print("SETUP MODE - join WiFi '%s' (pass '%s') then open http://%s"
          % (SETUP_AP, SETUP_PASS, AP_IP))

    nets = scan_networks()
    led.on()   # solid LED while serving setup (no blink to race the accept loop)
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 80))
    s.listen(3)

    while True:
        conn, addr = s.accept()
        try:
            conn.settimeout(3.0)
            req = conn.recv(2048)
            if not req:
                conn.close(); continue
            req = req.decode("utf-8", "ignore")
            line1 = req.split("\r\n", 1)[0]
            method = line1.split(" ")[0]
            path = line1.split(" ")[1] if len(line1.split(" ")) > 1 else "/"

            if method == "POST" and path == "/save":
                body = req.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in req else ""
                # a short POST body can arrive split; grab a little more if needed
                if "webhook=" not in body:
                    try:
                        body += conn.recv(2048).decode("utf-8", "ignore")
                    except Exception:
                        pass
                f = parse_form(body)
                cfg = {
                    "ssid": f.get("ssid", ""),
                    "password": f.get("password", ""),
                    "webhook_url": f.get("webhook", ""),
                    "device_name": f.get("device_name", "Tweety") or "Tweety",
                    "port": int(f.get("port", "2323") or "2323"),
                    "fake_banner": "SSH-2.0-OpenSSH_8.2",
                }
                save_config(cfg)
                http_send(conn, setup_page(nets, saved=True))
                conn.close()
                time.sleep(2)
                machine.reset()
            else:
                http_send(conn, setup_page(nets))
        except Exception as e:
            print("setup req error:", e)
        finally:
            try: conn.close()
            except Exception: pass

# ---------- canary mode ----------
def run_canary(cfg):
    try:
        import urequests as requests
    except ImportError:
        import requests

    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(cfg["ssid"], cfg["password"])
    for _ in range(30):
        if sta.isconnected():
            break
        blink(1, 0.05, 0.25)

    if not sta.isconnected():
        print("WiFi failed (status %s) - falling back to SETUP so customer can fix it"
              % sta.status())
        sta.active(False)
        run_setup()
        return

    ip = sta.ifconfig()[0]
    print("%s armed at %s on port %d" % (cfg["device_name"], ip, cfg["port"]))

    def alert(src_ip):
        payload = {"event": "trip", "device": cfg["device_name"],
                   "source_ip": src_ip, "port": cfg["port"], "canary_ip": ip}
        print("TRIP from", src_ip)
        try:
            r = requests.post(cfg["webhook_url"], json=payload,
                              headers={"Content-Type": "application/json"})
            r.close()
        except Exception as e:
            print("alert failed:", e)

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", cfg["port"]))
    s.listen(1)
    while True:
        led.on()                      # solid = armed
        conn, addr = s.accept()
        alert(addr[0])
        blink(6, 0.04, 0.04)          # rapid flash = trip
        try:
            conn.send((cfg.get("fake_banner", "") + "\r\n").encode())
        except Exception:
            pass
        conn.close()

# ---------- boot ----------
cfg = load_config()
if cfg is None:
    run_setup()
else:
    run_canary(cfg)

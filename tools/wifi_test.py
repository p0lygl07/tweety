# wifi_test.py — Pico W WiFi bring-up test
# Edit SSID and PASS, then:  mpremote connect COM5 run wifi_test.py

import network, time

SSID = "YOUR_WIFI_NAME"
PASS = "YOUR_WIFI_PASSWORD"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASS)

# wait up to ~10s for a connection
for _ in range(20):
    if wlan.isconnected():
        break
    print("...connecting")
    time.sleep(0.5)

print("connected:", wlan.isconnected())
if wlan.isconnected():
    print("ip:", wlan.ifconfig()[0])
else:
    print("FAILED - check SSID/PASS and that it's a 2.4GHz network")
    print("status code:", wlan.status())

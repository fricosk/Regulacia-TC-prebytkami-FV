from flask import Flask, render_template_string
import time
import requests
from pymodbus.client import ModbusTcpClient

app = Flask(__name__)


# -------------------------
# CONFIG
# -------------------------
API_TOKEN = "j2m1svhomy55p5jw90epj8pj701js41b"
GROWATT_URL = "https://openapi.growatt.com/v1/plant/list"

HP_IP = "192.168.2.186"
HP_PORT = 5000
HP_UNIT_ID = 1

ON_THRESHOLD = 3500
OFF_THRESHOLD = 2000


# -------------------------
# HEAT PUMP
# -------------------------
class HeatPump:
    REG_MODE = 0x2004
    REG_OUTDOOR = 0x4007
    REG_RETURN = 0x4008
    REG_TANK = 0x400A
    REG_OUTLET = 0x400C

    def __init__(self):
        self.client = ModbusTcpClient(HP_IP, port=HP_PORT, timeout=3)
        self.client.connect()

    def write_mode(self, value):
        try:
            self.client.write_register(address=self.REG_MODE, value=value, device_id=HP_UNIT_ID)
        except TypeError:
            self.client.write_register(address=self.REG_MODE, value=value, unit=HP_UNIT_ID)

    def read(self, addr):
        try:
            r = self.client.read_holding_registers(address=addr, count=1, device_id=HP_UNIT_ID)
        except TypeError:
            r = self.client.read_holding_registers(address=addr, count=1, unit=HP_UNIT_ID)

        if r.isError():
            return None
        return r.registers[0]

    def turn_on(self):
        self.write_mode(0x80)

    def turn_off(self):
        self.write_mode(0x00)

    def is_on(self):
        v = self.read(self.REG_MODE)
        return bool(v & 0x80) if v is not None else False

    def temps(self):
        def v(x): return x if x is not None else 0

        return {
            "outdoor": v(self.read(self.REG_OUTDOOR)),
            "return": v(self.read(self.REG_RETURN)),
            "tank": v(self.read(self.REG_TANK)),
            "outlet": v(self.read(self.REG_OUTLET)),
        }


hp = HeatPump()


# -------------------------
# CACHE (60s)
# -------------------------
_last_power = 0
_last_time = 0


def get_power():
    global _last_power, _last_time

    now = time.time()

    if now - _last_time < 60:
        return _last_power

    headers = {"token": API_TOKEN}
    r = requests.get(GROWATT_URL, headers=headers, timeout=10)
    data = r.json()

    if data.get("error_code") != 0:
        return _last_power

    plants = data.get("data", {}).get("plants", [])
    power = float(plants[0].get("current_power", 0)) if plants else 0

    _last_power = power
    _last_time = now

    return power


# -------------------------
# SMART CONTROL
# -------------------------
last_switch = 0
state = False


def control(power):
    global last_switch, state

    now = time.time()

    if now - last_switch < 60:
        return

    if not state and power > ON_THRESHOLD:
        hp.turn_on()
        state = True
        last_switch = now

    elif state and power < OFF_THRESHOLD:
        hp.turn_off()
        state = False
        last_switch = now


# -------------------------
# WEB PAGE
# -------------------------
HTML = """
<!doctype html>
<html>
<head>
    <meta http-equiv="refresh" content="5">
    <title>Energy Manager</title>
    <style>
        body { font-family: Arial; background:#111; color:#0f0; text-align:center; }
        .box { margin:20px; padding:20px; border:1px solid #0f0; display:inline-block; }
    </style>
</head>
<body>

<h1>⚡ Energy Manager</h1>

<div class="box">
    <h2>FV výkon</h2>
    <h1>{{ power }} W</h1>
</div>

<div class="box">
    <h2>Čerpadlo</h2>
    <h1>{{ state }}</h1>
</div>

<div class="box">
    <h2>Teploty</h2>
    🌡 Outdoor: {{ temps.outdoor }} °C<br>
    🌡 Return: {{ temps.return }} °C<br>
    🌡 Tank: {{ temps.tank }} °C<br>
    🌡 Outlet: {{ temps.outlet }} °C
</div>

</body>
</html>
"""


# -------------------------
# ROUTE
# -------------------------
@app.route("/")
def index():
    power = get_power()
    control(power)
    temps = hp.temps()
    state_txt = "ON 🔥" if hp.is_on() else "OFF ❄️"

    return render_template_string(
        HTML,
        power=power,
        state=state_txt,
        temps=temps
    )


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
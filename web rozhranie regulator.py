import time
import threading
import requests
from flask import Flask, render_template
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
OFF_THRESHOLD = 2500

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
        if not self.client.connect():
            raise ConnectionError("Heat pump connect failed")

    def write_mode(self, value):
        try:
            self.client.write_register(
                address=self.REG_MODE,
                value=value,
                slave=HP_UNIT_ID
            )
        except TypeError:
            self.client.write_register(
                address=self.REG_MODE,
                value=value
            )

    def read(self, addr):
        try:
            r = self.client.read_holding_registers(
                address=addr,
                count=1,
                slave=HP_UNIT_ID  # ← namiesto unit/device_id
            )
        except TypeError:
            r = self.client.read_holding_registers(
                address=addr,
                count=1
            )

        if r.isError():
            return None
        return r.registers[0]

    def turn_on(self):
        self.write_mode(0x80)

    def turn_off(self):
        self.write_mode(0x00)

    def is_on(self):
        val = self.read(self.REG_MODE)
        return bool(val & 0x80) if val else False

    def get_temps(self):
        def v(x): return x if x else 0
        return {
            "outdoor": v(self.read(self.REG_OUTDOOR)),
            "return": v(self.read(self.REG_RETURN)),
            "tank": v(self.read(self.REG_TANK)),
            "outlet": v(self.read(self.REG_OUTLET)),
        }

# -------------------------
# GROWATT
# -------------------------
_last_power = 0
_last_power_time = 0

def get_power():
    global _last_power, _last_power_time

    if time.time() - _last_power_time < 60:
        return _last_power

    try:
        r = requests.get(GROWATT_URL, headers={"token": API_TOKEN}, timeout=10)
        data = r.json()

        plants = data.get("data", {}).get("plants", [])
        power = float(plants[0].get("current_power", 0)) if plants else 0

        _last_power = power
        _last_power_time = time.time()
        return power

    except:
        return _last_power

# -------------------------
# GLOBAL STATE
# -------------------------
hp = HeatPump()
state = {
    "power": 0,
    "temps": {},
    "pump": False
}

last_switch = 0

# -------------------------
# BACKGROUND LOOP
# -------------------------
def control_loop():
    global last_switch

    while True:
        try:
            power = get_power()
            temps = hp.get_temps()
            pump = hp.is_on()

            # logika
            if time.time() - last_switch > 60:

                if not pump and power > ON_THRESHOLD:
                    hp.turn_on()
                    last_switch = time.time()

                elif pump and power < OFF_THRESHOLD:
                    hp.turn_off()
                    last_switch = time.time()

            state["power"] = power
            state["temps"] = temps
            state["pump"] = pump

        except Exception as e:
            print("ERROR:", e)

        time.sleep(5)

# -------------------------
# WEB ROUTE
# -------------------------
@app.route("/")
def index():
    return render_template("index.html", data=state)

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    threading.Thread(target=control_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

    @app.route("/debug")
    def debug():
        return state
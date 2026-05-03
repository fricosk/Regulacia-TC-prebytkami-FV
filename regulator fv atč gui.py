import time
import requests
import tkinter as tk
from pymodbus.client import ModbusTcpClient


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
                device_id=HP_UNIT_ID
            )
        except TypeError:
            self.client.write_register(
                address=self.REG_MODE,
                value=value,
                unit=HP_UNIT_ID
            )

    def read(self, addr):
        try:
            r = self.client.read_holding_registers(
                address=addr,
                count=1,
                device_id=HP_UNIT_ID
            )
        except TypeError:
            r = self.client.read_holding_registers(
                address=addr,
                count=1,
                unit=HP_UNIT_ID
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
        return bool(val & 0x80) if val is not None else False

    def get_temps(self):
        def v(x): return x if x is not None else 0

        return {
            "outdoor": v(self.read(self.REG_OUTDOOR)),
            "return": v(self.read(self.REG_RETURN)),
            "tank": v(self.read(self.REG_TANK)),
            "outlet": v(self.read(self.REG_OUTLET)),
        }

    def close(self):
        self.client.close()


# -------------------------
# GROWATT (GLOBAL CACHE)
# -------------------------
_last_power = 0
_last_power_time = 0


def get_power():
    global _last_power, _last_power_time

    now = time.time()

    # cache 60s
    if now - _last_power_time < 60:
        return _last_power

    headers = {"token": API_TOKEN}

    r = requests.get(GROWATT_URL, headers=headers, timeout=10)
    data = r.json()

    if data.get("error_code") != 0:
        return _last_power

    plants = data.get("data", {}).get("plants", [])
    power = float(plants[0].get("current_power", 0)) if plants else 0

    _last_power = power
    _last_power_time = now

    return power


# -------------------------
# GUI APP
# -------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Energy Manager")
        self.root.geometry("340x260")

        self.hp = HeatPump()
        self.is_on = False

        self.last_switch_time = 0

        # Labels
        self.power_label = tk.Label(root, text="FV: --- W", font=("Arial", 14))
        self.power_label.pack()

        self.state_label = tk.Label(root, text="Pump: ---", font=("Arial", 14))
        self.state_label.pack()

        self.temp_label = tk.Label(root, text="", justify="left")
        self.temp_label.pack()

        self.update()

    # -------------------------
    # SAFETY: 60s cooldown
    # -------------------------
    def can_switch(self):
        return (time.time() - self.last_switch_time) > 60

    # -------------------------
    # MAIN LOOP
    # -------------------------
    def update(self):
        try:
            power = get_power()
            temps = self.hp.get_temps()
            state = self.hp.is_on()

            # -------------------------
            # CONTROL LOGIC
            # -------------------------
            if self.can_switch():

                if not self.is_on and power > ON_THRESHOLD:
                    self.hp.turn_on()
                    self.is_on = True
                    self.last_switch_time = time.time()

                elif self.is_on and power < OFF_THRESHOLD:
                    self.hp.turn_off()
                    self.is_on = False
                    self.last_switch_time = time.time()

            # -------------------------
            # UI UPDATE
            # -------------------------
            self.power_label.config(text=f"⚡ FV: {power:.0f} W")
            self.state_label.config(text=f"🔥 Pump: {'ON' if state else 'OFF'}")

            self.temp_label.config(text=
                f"🌡 Outdoor: {temps['outdoor']} °C\n"
                f"🌡 Return:  {temps['return']} °C\n"
                f"🌡 Tank:    {temps['tank']} °C\n"
                f"🌡 Outlet:  {temps['outlet']} °C"
            )

        except Exception as e:
            self.state_label.config(text=f"Error: {e}")

        # refresh GUI každých 5 sekúnd
        self.root.after(5000, self.update)


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
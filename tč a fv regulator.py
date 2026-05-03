import time
import requests
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
    REG_OUTLET = 0x400C   # 🔥 výstupná teplota

    def __init__(self):
        self.client = ModbusTcpClient(HP_IP, port=HP_PORT, timeout=3)
        if not self.client.connect():
            raise ConnectionError("Heat pump connect failed")

    # -------- WRITE --------
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

    # -------- READ --------
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

    # -------- CONTROL --------
    def turn_on(self):
        self.write_mode(0x80)

    def turn_off(self):
        self.write_mode(0x00)

    # -------- STATUS --------
    def is_on(self):
        val = self.read(self.REG_MODE)
        return bool(val & 0x80) if val is not None else False

    def get_temps(self):
        def v(x):
            return x if x is not None else 0

        return {
            "outdoor": v(self.read(self.REG_OUTDOOR)),
            "return": v(self.read(self.REG_RETURN)),
            "tank": v(self.read(self.REG_TANK)),
            "outlet": v(self.read(self.REG_OUTLET)),  # 🔥 NOVÉ
        }

    def close(self):
        self.client.close()


# -------------------------
# GROWATT
# -------------------------
def get_power():
    headers = {"token": API_TOKEN}

    r = requests.get(GROWATT_URL, headers=headers, timeout=10)
    r.raise_for_status()

    data = r.json()

    if data.get("error_code") != 0:
        raise RuntimeError(data.get("error_msg"))

    plants = data.get("data", {}).get("plants", [])
    return float(plants[0].get("current_power", 0)) if plants else 0


# -------------------------
# MAIN LOOP
# -------------------------
def main():
    hp = HeatPump()
    is_on = False

    try:
        while True:
            power = get_power()
            temps = hp.get_temps()
            state = hp.is_on()

            # -------------------------
            # CONTROL LOGIC
            # -------------------------
            if not is_on and power > ON_THRESHOLD:
                hp.turn_on()
                is_on = True

            elif is_on and power < OFF_THRESHOLD:
                hp.turn_off()
                is_on = False

            # -------------------------
            # OUTPUT
            # -------------------------
            print("\n==============================")
            print(f"⚡ FV výkon: {power:.0f} W")
            print(f"🔥 Čerpadlo: {'ON' if state else 'OFF'}")
            print(f"🌡 Vonkajšia: {temps['outdoor']} °C")
            print(f"🌡 Výstup:    {temps['outlet']} °C")  # 🔥 NOVÉ
            print(f"🌡 Návrat:    {temps['return']} °C")
            print(f"🌡 Zásobník:  {temps['tank']} °C")
            print("==============================")

            time.sleep(120)

    finally:
        hp.close()


if __name__ == "__main__":
    main()
from pymodbus.client import ModbusTcpClient


class ModbusReadError(Exception):
    pass


class HeatPumpController:
    # -------------------------
    # REGISTER MAP
    # -------------------------
    REG_ERROR_CODE = 0x4006
    REG_OUTDOOR_TEMP = 0x4007
    REG_RETURN_TEMP = 0x4008
    REG_TANK_TEMP = 0x400A
    REG_OUTLET_TEMP = 0x400C
    REG_COMPRESSOR_TEMP = 0x4011
    REG_FLOW_RATE = 0x4002

    def __init__(self, ip="192.168.2.186", port=5000, unit_id=1, scale_temp=1.0):
        self.client = ModbusTcpClient(ip, port=port)
        self.unit_id = unit_id
        self.scale_temp = scale_temp  # napr. 0.1 ak zariadenie používa ×10

        if not self.client.connect():
            raise ConnectionError(f"Cannot connect to Modbus device at {ip}:{port}")

    # -------------------------
    # CONTEXT MANAGER
    # -------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # -------------------------
    # LOW LEVEL READ (WITH RETRY)
    # -------------------------
    def read(self, address, count=1, retries=3):
        last_error = None

        for _ in range(retries):
            try:
                result = self.client.read_holding_registers(
                    address=address,
                    count=count,
                    device_id=self.unit_id  # kompatibilné s väčšinou verzií pymodbus
                )

                if not result.isError():
                    return result.registers

                last_error = result

            except Exception as e:
                last_error = e

        raise ModbusReadError(f"Read failed @ {hex(address)}: {last_error}")

    # -------------------------
    # DECODING
    # -------------------------
    @staticmethod
    def to_signed(val):
        return val - 65536 if val > 32767 else val

    def _temp(self, raw):
        return self.to_signed(raw) * self.scale_temp

    # -------------------------
    # BATCH READ (OPTIMIZED)
    # -------------------------
    def read_all_temps(self):
        """
        Číta blok registrov naraz kvôli výkonu
        rozsah pokrýva: 0x4007 → 0x4011
        """
        start = self.REG_OUTDOOR_TEMP
        count = (self.REG_COMPRESSOR_TEMP - start) + 1

        regs = self.read(start, count)

        def r(addr):
            return regs[addr - start]

        return {
            "outdoor": self._temp(r(self.REG_OUTDOOR_TEMP)),
            "return": self._temp(r(self.REG_RETURN_TEMP)),
            "tank": self._temp(r(self.REG_TANK_TEMP)),
            "outlet": self._temp(r(self.REG_OUTLET_TEMP)),
            "compressor": self._temp(r(self.REG_COMPRESSOR_TEMP)),
        }

    # -------------------------
    # INDIVIDUAL READS
    # -------------------------
    def outdoor_temp(self):
        return self._temp(self.read(self.REG_OUTDOOR_TEMP)[0])

    def return_water_temp(self):
        return self._temp(self.read(self.REG_RETURN_TEMP)[0])

    def tank_temp(self):
        return self._temp(self.read(self.REG_TANK_TEMP)[0])

    def outlet_temp(self):
        return self._temp(self.read(self.REG_OUTLET_TEMP)[0])

    def compressor_return_air(self):
        return self._temp(self.read(self.REG_COMPRESSOR_TEMP)[0])

    # -------------------------
    # STATUS
    # -------------------------
    def error_code(self):
        return self.read(self.REG_ERROR_CODE)[0]

    def flow_rate(self):
        return self.read(self.REG_FLOW_RATE)[0]

    # -------------------------
    # RAW ACCESS
    # -------------------------
    def dump(self, start=0x4000, count=50):
        return self.read(start, count)

    # -------------------------
    # CLEAN CLOSE
    # -------------------------
    def close(self):
        if self.client:
            self.client.close()


# -------------------------
# USAGE
# -------------------------
if __name__ == "__main__":
    # ak zariadenie používa ×10 → nastav scale_temp=0.1
    with HeatPumpController(scale_temp=1.0) as hp:
        temps = hp.read_all_temps()

        print("Outdoor:", temps["outdoor"], "°C")
        print("Return:", temps["return"], "°C")
        print("Tank:", temps["tank"], "°C")
        print("Outlet:", temps["outlet"], "°C")
        print("Compressor:", temps["compressor"], "°C")

        print("Flow rate:", hp.flow_rate())
        print("Error code:", hp.error_code())
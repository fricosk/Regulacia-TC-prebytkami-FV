from pymodbus.client import ModbusTcpClient


class HeatPumpController:
    def __init__(self, ip="192.168.2.186", port=5000, unit_id=1):
        self.client = ModbusTcpClient(ip, port=port)
        self.unit_id = unit_id
        self.client.connect()

    # -------------------------
    # LOW LEVEL READ
    # -------------------------
    def read(self, address, count=1):
        result = self.client.read_holding_registers(
            address=address,
            count=count,
            device_id=self.unit_id
        )

        if result.isError():
            raise Exception(f"Modbus error: {result}")

        return result.registers

    # -------------------------
    # DECODING
    # -------------------------
    @staticmethod
    def to_signed(val):
        return val - 65536 if val > 32767 else val

    # -------------------------
    # TEMPERATURES (SUMAIR MAP)
    # -------------------------

    def outdoor_temp(self):
        # 4007h
        val = self.read(0x4007)[0]
        return self.to_signed(val)

    def return_water_temp(self):
        # 4008h
        val = self.read(0x4008)[0]
        return self.to_signed(val)

    def tank_temp(self):
        # 400Ah
        val = self.read(0x400A)[0]
        return self.to_signed(val)

    def outlet_temp(self):
        # 400Ch
        val = self.read(0x400C)[0]
        return self.to_signed(val)

    def compressor_return_air(self):
        # 4011h (1st compressor discharge temp is example)
        val = self.read(0x4011)[0]
        return self.to_signed(val)

    # -------------------------
    # STATUS
    # -------------------------
    def error_code(self):
        # 4006h
        return self.read(0x4006)[0]

    def flow_rate(self):
        # 4002h
        return self.read(0x4002)[0]

    # -------------------------
    # RAW ACCESS
    # -------------------------
    def dump(self, start=0x4000, count=50):
        return self.read(start, count)

    # -------------------------
    # CLEAN CLOSE
    # -------------------------
    def close(self):
        self.client.close()
hp = HeatPumpController()

print("Outdoor:", hp.outdoor_temp(), "°C")
print("Return:", hp.return_water_temp(), "°C")
print("Tank:", hp.tank_temp(), "°C")
print("Outlet:", hp.outlet_temp(), "°C")


hp.close()
import json
import time
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

class Modbus:
    def __init__(self, modbusConfig):
        self.client = ModbusSerialClient(
            method=modbusConfig.get("method", "rtu"),
            port=modbusConfig.get("port", "/dev/ttyS0"),
            baudrate=modbusConfig.get("baud", 9600),
            stopbits=modbusConfig.get("stopbits", 1),
            bytesize=modbusConfig.get("bytesize", 8),
            parity=modbusConfig.get("parity", "N"),
            timeout=modbusConfig.get("timeout", 1)
        )

    def connect(self):
        if not self.client.connect():
            print("Modbus: Connection failed.")
            return
        else:
            print("Modbus: Connected.")

    def disconnect(self):
        self.client.close()
        print("Modbus: Disconnected.")

    def read_register(self, address, dtype, device, attempts):
        count = 1 if dtype in ["uint16", "int16"] else 2

        for attempt in range(attempts):
            resp = self.client.read_holding_registers(address=address, count=count, slave=device)
            if not resp.isError():
                decoder = BinaryPayloadDecoder.fromRegisters(resp.registers, byteorder=Endian.Big)
                match dtype:
                    case "uint16": return decoder.decode_16bit_uint()
                    case "int16": return decoder.decode_16bit_int()
                    case "uint32": return decoder.decode_32bit_uint()
                    case "int32": return decoder.decode_32bit_int()
                    case _: return None
            else:
                print(f"Modbus: Failed to read {address}, attempt {attempt + 1}")
                time.sleep(1)
        return None

import json
import time
import threading

from mqtt import Mqtt
from modbus import Modbus
from app import App

def main():
    
    # Load and check config.json
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        modbusConfig = config["modbus"]
        registers = config["registers"]
        mqttConfig = config["mqtt"]
    except:
        print("Invalid config")
        exit()
    print("Config loaded")

    # Start MQTT
    mqttClient = Mqtt(mqttConfig)
    mqttClient.connect()

    # Start MODBUS
    modbusClient = Modbus(modbusConfig)
    modbusClient.connect()

    # Read Registers
    globalInterval = modbusConfig.get("interval", 10)
    device = modbusConfig.get("device", 85)
    prefix = mqttConfig.get("prefix", "modbus2mqtt")
    attempts = mqttConfig.get("attempts", 3)
    last_poll_times = {reg["name"]: 0 for reg in registers}

    def convertInteger(reg):
        try:
            if reg.startswith("0x"):
                reg_value = int(reg, 16)
            else:
                reg_value = int(reg)
        except AttributeError:
            reg_value = reg
        return reg_value

    try:
        while True:
            now = time.time()

            for reg in registers:
                reg_interval = reg.get("interval", globalInterval)
                last_polled = last_poll_times[reg["name"]]

                if now - last_polled >= reg_interval:
                    raw = modbusClient.read_register(convertInteger(reg["address"]), reg["type"], convertInteger(device), attempts)
                    if raw is None:
                        print(f"{reg['name']}: Failed")

                    else:
                        value = raw * reg.get("scale", 1.0)
                        print(f"{reg['name']}: {value:.2f}")
                        mqttClient.send(prefix+"/"+reg['name'], f"{value:.2f}")

                    last_poll_times[reg["name"]] = now

            time.sleep(1)

    except KeyboardInterrupt:
        print("Exited")
    finally:
        modbusClient.disconnect()
        mqttClient.disconnect()

if __name__ == "__main__":
    app_instance = App()
    thread = threading.Thread(target=app_instance.run)
    thread.start()
    main()

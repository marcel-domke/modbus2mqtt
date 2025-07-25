import paho.mqtt.client as mqtt
import json

class Mqtt:
    def __init__(self, mqttConfig, debug = False):
        self.debug = debug
        self.broker = mqttConfig.get("address", "127.0.0.1")
        self.port = mqttConfig.get("port", 1883)
        self.username = mqttConfig.get("username", None)
        self.password = mqttConfig.get("password", None)
        self.client = mqtt.Client()

        if (self.username != None and self.password != None):
            self.client.username_pw_set(self.username, self.password)
        
    def connect(self):
        """Connecting to the MQTT-Broker."""
        print(f"MQTT: Connecting to {self.broker}:{self.port}...")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
        print("MQTT: Connected.")

    def send(self, topic, nachricht):
        """Send a Message to a MQTT-Topic."""
        if self.debug == True:
            print(f"MQTT: Sending Message to Topic: '{topic}'...")
        self.client.publish(topic, nachricht)

    def disconnect(self):
        """Disconnecting from the MQTT-Broker."""
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT: Disconnected.")

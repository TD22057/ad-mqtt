import logging


class Data (dict):
    pass


class Config:
    def __init__(self):
        # ser2sock server information
        self.alarm = Data()
        self.alarm.host = '127.0.0.1'
        self.alarm.port = 1000

        # MQTT broker (names must match insteon-mqtt settings variables)
        self.mqtt = Data()
        self.mqtt.broker = '127.0.0.1'
        self.mqtt.port = 1883
        self.mqtt.availability_topic = "alarm/available"
        # Optional user/pass for the broker
        self.mqtt.username = None
        self.mqtt.password = None
        self.mqtt.encryption = Data()
        # Optional encryption settings for the broker.
        self.mqtt.encryption.ca_cert = None
        self.mqtt.encryption.certfile = None
        self.mqtt.encryption.keyfile = None

        # Logging configuration
        self.log = Data()
        self.log.level = logging.INFO
        self.log.screen = True
        self.log.file = None
        self.log.size_kb = 5000
        self.log.backup_count = 3
        self.log.modules = ["ad_mqtt", "insteon_mqtt"]

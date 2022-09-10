#!./venv/bin/python

import sys
import os
sys.path.insert( 0, "." )
import ad_mqtt as AD

cfg = AD.Config()

# Alarm Decoder ser2sock server location.
cfg.alarm.host = os.getenv("ADMQTT_SOCKET_HOST","127.0.0.1")
cfg.alarm.port = int(os.getenv("ADMQTT_SOCKET_PORT",10000))
# To reset all zones to closed (not faulted) on startup, set this to True
cfg.alarm.restore_on_startup = bool(os.getenv("ADMQTT_RESTORE_ON_STARTUP",False))

# MQTT Broker connection
cfg.mqtt.broker = os.getenv("ADMQTT_MQTT_HOST","127.0.0.1")
cfg.mqtt.port = int(os.getenv("ADMQTT_MQTT_PORT",1883))
# Optional user/pass for the broker
cfg.mqtt.username = os.getenv("ADMQTT_MQTT_USERNAME",None)
cfg.mqtt.password = os.getenv("ADMQTT_MQTT_PASSWORD",None)
# Optional encryption settings for the broker.
cfg.mqtt.encryption.ca_cert = os.getenv("ADMQTT_MQTT_CA_CERT",None)
cfg.mqtt.encryption.certfile = os.getenv("ADMQTT_MQTT_CERTFILE",None)
cfg.mqtt.encryption.keyfile = os.getenv("ADMQTT_MQTT_KEYFILE",None)

# Debugging information
cfg.log.level = os.getenv("ADMQTT_LOG_LEVEL","INFO")
cfg.log.screen = bool(os.getenv("ADMQTT_LOG_SCREEN",False))
file_config = os.getenv("ADMQTT_LOG_FILE","log.txt")
# Allowing env var to disable default file logging
if len(file_config) == 0:
    file_config = None
cfg.log.file = file_config
cfg.log.size_kb = 5000
cfg.log.backup_count = 3
cfg.log.modules = ["ad_mqtt", "insteon_mqtt"]

# For possible device class values, see:
# https://www.home-assistant.io/integrations/binary_sensor/#device-class
alarm_code = os.getenv("ADMQTT_ALARM_CODE","1234")

# Getting devices configuration
exec(open("devices.py").read())
devices = get_devices()

AD.run.run(cfg, alarm_code, devices)

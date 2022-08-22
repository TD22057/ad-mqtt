#!./venv/bin/python

import logging
import sys
sys.path.insert( 0, "." )
import ad_mqtt as AD

cfg = AD.Config()

# Alarm Decoder ser2sock server location.
cfg.alarm.host = '127.0.0.1'
cfg.alarm.port = 10000
# To reset all zones to closed (not faulted) on startup, set this to True
cfg.alarm.restore_on_startup = False

# MQTT Broker connection
cfg.mqtt.broker = '127.0.0.1'
cfg.mqtt.port = 1883
# Optional user/pass for the broker
cfg.mqtt.username = None
cfg.mqtt.password = None
# Optional encryption settings for the broker.
cfg.mqtt.encryption.ca_cert = None
cfg.mqtt.encryption.certfile = None
cfg.mqtt.encryption.keyfile = None

# Debugging information
cfg.log.level = logging.INFO
cfg.log.screen = False
cfg.log.file = "log.txt"
cfg.log.size_kb = 5000
cfg.log.backup_count = 3
cfg.log.modules = ["ad_mqtt", "insteon_mqtt"]

# For possible device class values, see:
# https://www.home-assistant.io/integrations/binary_sensor/#device-class
alarm_code = "1234"
devices = [
    # Zone( zone_number, HAS_entity_name, description, device_class )
    AD.Zone(1, "fire", "Fire Alarm", "smoke"),
    AD.Zone(2, "basement_door", "Basement Door"),
    # RF zone ( serial_number, zone_number, HAS_entity_name, description )
    AD.RfZone( 12345, 25, "front_door", "Front Door"),
    AD.RfZone( 12345, 27, "dining_room_door", "Dining Room Door"),
    AD.RfZone( 12345, 29, "kitchen_window_right", "Kitchen Right Window"),
    AD.RfZone( 12345, 30, "guest_bedroom_window", "Guest Bedroom Window"),
    AD.Rf( 12345, loops=[
        AD.Zone(31, "side_window", "Side Window"),
        None, None,  # loops 2, 3 unused
        AD.Zone(32, "side_window_tampler", "Side Window Tampler", "tampler"),
        ]),
    ]

AD.run.run(cfg, alarm_code, devices)

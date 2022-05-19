#!./venv/bin/python

import logging
import sys
sys.path.insert( 0, "." )
import ad_mqtt.run as AD2MQTT
from decouple import config

ad_host = config('AD_HOST', default="127.0.0.1")
ad_port = config('AD_PORT',default=10000, cast=int)
mqtt_broker = config('MQTT_BROKER', default="127.0.0.1")
mqtt_port = config('MQTT_PORT',default=1883, cast=int)
mqtt_user = config('MQTT_USER',default="")
mqtt_pass = config('MQTT_PASS',default="")
mqtt_id = config('MQTT_ID',default="ad-mqtt")
log_level = config('LOG_LEVEL',default=logging.ERROR)
log_screen = config('LOG_SCREEN',default=False, cast=bool)
log_file = config('LOG_FILE',default="log.txt")

alarm_code = config('ALARM_CODE', default="1234")

zone_data = {
    1 : { "entity" : "fire",
          "label" : "Fire Alarm" },
    2 : { "entity" : "basement_door",
          "label" : "Basement Door" },
    25 : { "entity" : "front_door",
           "label" : "Front Door",
           "rf_id" : "012345" },
    27 : { "entity" : "dining_room_door",
           "label" : "Dining Room Door",
           "rf_id" : "012345" },
    29 : { "entity" : "kitchen_window_right",
           "label" : "Kitchen Right Window",
           "rf_id" : "012345" },
    30 : { "entity" : "guest_bedroom_window",
           "label" : "Guest Bedroom Window",
           "rf_id" : "012345" },
    31 : { "entity" : "guest_bathroom_window",
           "label" : "Guest Bathroom Window",
           "rf_id" : "012345" },
    33 : { "entity" : "downstairs_bathroom_window",
           "label" : "Downstairs Bathroom Window",
           "rf_id" : "012345" },
    34 : { "entity" : "den_door",
           "label" : "Den Door",
           "rf_id" : "012345" },
    35 : { "entity" : "den_window",
           "label" : "Den Window",
           "rf_id" : "012345" },
    36 : { "entity" : "media_door_left",
           "label" : "Media Left Door",
           "rf_id" : "012345" },
    37 : { "entity" : "media_door_right",
           "label" : "Media Right Door",
           "rf_id" : "012345" },
    }
ad_mqtt.run.run(ad_host, ad_port, mqtt_broker,mqtt_port,mqtt_user,mqtt_pass,mqtt_id,alarm_code, zone_data,
                log_level=log_level, log_screen=log_screen, log_file=log_file)
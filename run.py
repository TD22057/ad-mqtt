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

AD2MQTT.run(ad_host, ad_port, mqtt_broker,mqtt_port,mqtt_user,mqtt_pass,mqtt_id,alarm_code, zone_data,
                log_level=log_level, log_screen=log_screen, log_file=log_file)
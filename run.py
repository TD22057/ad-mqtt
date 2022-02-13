#!./venv/bin/python

import logging
import sys
sys.path.insert( 0, "." )
import ad_mqtt

host = ''
port = 22053
log_level = logging.DEBUG
log_screen = False
log_file = "log.txt"

alarm_code = "1234"
zone_data = {
    1 : { "entity" : "fire",
          "label" : "Fire Alarm" },
    2 : { "entity" : "basement_door",
          "label" : "Basement Door" },
    # Wireless sensors need rf_id
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

ad_mqtt.run.run(host, port, alarm_code, zone_data,
                log_level=log_level, log_screen=log_screen, log_file=log_file)

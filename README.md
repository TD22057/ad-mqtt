

Version: 0.0.1

```
git clone https://github.com/TD22057/ad-mqtt.git
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

[edit run.py to add ser2sock, zone info]

./run.py
```

Designed to work with Home Assistant.  Uses MQTT discovery to create sensors
for all zones and the alarm panel automatically.  Times are passed in the
MQTT messages and retained so they can be used to create real "last changed"
time sensors if desired in HASS.

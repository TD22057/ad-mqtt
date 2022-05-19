Version: 0.1.0

```
git clone https://github.com/TD22057/ad-mqtt.git
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

[edit run.py to add zone info and add .env with ser2sock, mqtt broker config]

./run.py
```

Designed to work with Home Assistant. Uses MQTT discovery to create sensors
for all zones and the alarm panel automatically. Times are passed in the
MQTT messages and retained so they can be used to create real "last changed"
time sensors if desired in HASS.

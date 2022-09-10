
[![Docker Image CI](https://github.com/rgriffogoes/ad-mqtt/actions/workflows/docker-image.yml/badge.svg)](https://github.com/rgriffogoes/ad-mqtt/actions/workflows/docker-image.yml)

#### AlarmDecoder to MQTT Bridge (ad-mqtt)

Simple Python application to interface [AlarmDecoder](https://github.com/nutechsoftware/alarmdecoder) with a [MQTT Broker](https://en.wikipedia.org/wiki/MQTT).

Designed to work with [Home Assistant](https://www.home-assistant.io/).  
Uses MQTT discovery to create sensors for all zones and the alarm panel
automatically.  Times are passed in the MQTT messages and retained so they
can be used to create real "last changed" time sensors if desired in HASS.

##### Direct python execution
```
git clone https://github.com/TD22057/ad-mqtt.git
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

[edit run.py to add ser2sock+mqtt broker host:port settings, 
edit devices.py to add zone info]

./run.py
```

##### Docker Execution
Example docker execution with some parameters passed as environment vars. 
Please notice the mandatory devices.py mapping.

```
sudo docker run -e ADMQTT_SOCKET_HOST=192.168.1.71  
  -e ADMQTT_MQTT_HOST=192.168.1.6 
  -e ADMQTT_LOG_LEVEL=DEBUG 
  -v /home/user/devices.py:/home/devices.py -d ad-mqtt:latest
```
Use devices.py file in this repo as example file for configuring your zones.
Check run.py for available environment variables.

##### Changelog

###### Version: 0.3.0
 - Environment variables for major configurations
 - External zone config file
 - Dockerfile for containerized execution
 - Github workflow to build and push docker image

###### Version: 0.2.3
 - Initial changelog recording
import logging
import alarmdecoder as ad
import insteon_mqtt as mqtt
from .Bridge import Bridge
from .Client import Client
from .Discovery import Discovery
from .log import log_setup


def run(ad_host, ad_port, mqtt_broker, mqtt_port, mqtt_user, mqtt_pass, mqtt_id, alarm_code, zone_data,
        log_level, log_screen=True, log_file=None):
    log_setup(log_level, log_screen, log_file)
    # Alarm decoder network device.
    ad_client = Client(ad_host, ad_port)
    decoder = ad.AlarmDecoder(ad_client)
    decoder._wire_events()

    # MQTT Config
    mqtt_client = mqtt.network.Mqtt()
    mqtt_client.load_config(config={
        'broker': mqtt_broker,
        'port': mqtt_port,
        'username': mqtt_user,
        'password': mqtt_pass,
        'id': mqtt_id,
        'availability_topic': "alarm/available"
    })

    bridge = Bridge(mqtt_client, decoder, zone_data, alarm_code)
    Discovery(mqtt_client, bridge, zone_data)

    loop = mqtt.network.poll.Manager()
    loop.add(ad_client, connected=False)
    loop.add(mqtt_client, connected=False)

    while loop.active():
        loop.select()

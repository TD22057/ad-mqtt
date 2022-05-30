import logging
import alarmdecoder as AD
import insteon_mqtt as IM
from .Bridge import Bridge
from .Client import Client
from .Discovery import Discovery


def run(ad_host, ad_port, mqtt_broker_ip, mqtt_broker_port, mqtt_user, mqtt_pass, alarm_code, zone_data,
        log_level=logging.INFO, log_screen=True, log_file=None):
    fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)
    if log_screen:
        screen_handler = logging.StreamHandler()
        screen_handler.setFormatter(formatter)
    if log_file:
        file_handler = logging.handlers.WatchedFileHandler(log_file)
        file_handler.setFormatter(formatter)

    log_names = [
        "ad_mqtt",
        # "insteon_mqtt",
    ]
    for name in log_names:
        log = logging.getLogger(name)
        log.setLevel(log_level)
        if log_screen:
            log.addHandler(screen_handler)
        if log_file:
            log.addHandler(file_handler)

    # Alarm decoder network device.
    ad_client = Client(ad_host, ad_port)
    decoder = AD.AlarmDecoder(ad_client)
    decoder._wire_events()

    mqtt_client = IM.network.Mqtt()
    mqtt_client.load_config(config={
        'broker': mqtt_broker_ip,
        'port': mqtt_broker_port,
        'username': mqtt_user,
        'password': mqtt_pass,
        'id': "ad_mqtt",
        'availability_topic': "alarm/available"
    })

    bridge = Bridge(mqtt_client, decoder, zone_data, alarm_code)
    discovery = Discovery(mqtt_client, bridge, zone_data)

    loop = IM.network.poll.Manager()
    loop.add(ad_client, connected=False)
    loop.add(mqtt_client, connected=False)

    while loop.active():
        loop.select()

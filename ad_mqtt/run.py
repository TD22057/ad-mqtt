import logging
import alarmdecoder as AD
import insteon_mqtt as IM
from .Bridge import Bridge
from .Client import Client
from .Discovery import Discovery


def run(host, port, alarm_code, zone_data,
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
        #"insteon_mqtt",
        ]
    for name in log_names:
        log = logging.getLogger(name)
        log.setLevel(log_level)
        if log_screen:
            log.addHandler(screen_handler)
        if log_file:
            log.addHandler(file_handler)

    # Alarm decoder network device.
    adClient = Client(host, port)
    decoder = AD.AlarmDecoder(adClient)
    decoder._wire_events()

    mqttClient = IM.network.Mqtt()
    mqttClient.availability_topic = "alarm/available"

    bridge = Bridge(mqttClient, decoder, zone_data, alarm_code)
    discovery = Discovery(mqttClient, bridge, zone_data)

    loop = IM.network.poll.Manager()
    loop.add(adClient, connected=False)
    loop.add(mqttClient, connected=False)

    while loop.active():
        loop.select()

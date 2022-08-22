import logging
import alarmdecoder as AD
import insteon_mqtt as IM
from .Bridge import Bridge
from .Client import Client
from . import Devices
from .Discovery import Discovery


def setup_logging(log_cfg):
    fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)

    if log_cfg.screen:
        screen_handler = logging.StreamHandler()
        screen_handler.setFormatter(formatter)

    if log_cfg.file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_cfg.file, maxBytes=log_cfg.size_kb * 1000,
            backupCount=log_cfg.backup_count)
        file_handler.setFormatter(formatter)

    for name in log_cfg.modules:
        log = logging.getLogger(name)
        log.setLevel(log_cfg.level)
        if log_cfg.screen:
            log.addHandler(screen_handler)
        if log_cfg.file:
            log.addHandler(file_handler)


def run(cfg, alarm_code, devices):
    setup_logging(cfg.log)

    log = logging.getLogger(__name__)

    try:
        zones, rf_devices = Devices.init_devices(devices)

        # Alarm decoder network device.
        ad_client = Client(cfg.alarm.host, cfg.alarm.port)
        decoder = AD.AlarmDecoder(ad_client)
        decoder._wire_events()

        mqtt_client = IM.network.Mqtt(id="ad-mqtt")
        # IM uses dict: cfg['a'] not cfg.a
        mqtt_client.load_config(cfg.mqtt.__dict__)

        bridge = Bridge(mqtt_client, decoder, alarm_code, zones, rf_devices)
        discovery = Discovery(mqtt_client, bridge, zones)

        loop = IM.network.poll.Manager()
        loop.add(ad_client, connected=False)
        loop.add(mqtt_client, connected=False)

        while loop.active():
            loop.select()
    except:
        log.exception("Unexpected exception")
        raise

import datetime as DT
import json
import logging

LOG = logging.getLogger(__name__)


class Bridge:
    def __init__(self, mqtt, decoder, code, zones, rf_devices):
        self.mqtt = mqtt
        self.ad = decoder
        self._connect()
        self.qos = 1
        self.retain = True
        self.panel_attr = {}
        self.panel_status = None
        self.is_bypass = False
        self.last_alarm_zone = ""

        self.code = code
        self.zones = zones
        self.rf_devices = rf_devices
        self.req_chime_on = None

        self.panel_state_topic = "alarm/panel/state"
        self.panel_set_topic = "alarm/panel/set"
        self.panel_msg_topic = "alarm/panel/message"
        self.panel_faulted_topic = "alarm/panel/faulted"
        self.panel_battery_topic = "alarm/panel/battery"
        self.panel_bypass_topic = "alarm/panel/bypass"

        self.chime_state_topic = "alarm/panel/chime/state"
        self.chime_set_topic = "alarm/panel/chime/set"

        self.bypass_state_topic = "alarm/panel/bypass/state"
        self.bypass_set_topic = "alarm/panel/bypass/set"

        self.sensor_state_topic = "alarm/sensor/{entity}/state"
        self.sensor_battery_topic = "alarm/sensor/{entity}/battery"

        mqtt.signal_connected.connect(self.mqtt_connected)

    def mqtt_connected(self, device, connected):
        if not connected:
            return

        qos = 1
        self.mqtt.subscribe(self.panel_set_topic, qos, self.cb_panel_set)
        self.mqtt.subscribe(self.chime_set_topic, qos, self.cb_chime_set)
        self.mqtt.subscribe(self.bypass_set_topic, qos, self.cb_bypass_set)

    def cb_panel_set(self, client, user_data, message):
        msg = message.payload.decode("utf-8")
        LOG.info("Read panel set '%s'", msg)
        try:
            data = json.loads(msg)
        except:
            LOG.exception("Error decoding panel set message")
            return

        input_code = data.get("code", None)
        if input_code != self.code:
            LOG.error("Invalid alarm code '%s' entered", input_code)
            return

        action = data.get("action", None)

        # TODO: how to report error message?
        keys = ""
        if self.is_bypass:
            keys = f"{self.code}6#"

        if action == "arm_away":
            keys += f"{self.code}2"
        elif action == "arm_stay":
            keys += f"{self.code}3"
        elif action == "arm_night":
            keys += f"{self.code}7"
        elif action == "disarm":
            keys += f"{self.code}1"
        else:
            LOG.error("Invalid alarm action '%s'", action)
            return

        LOG.info("Arm code: '%s'", keys)
        self.ad.send(keys)

    def cb_chime_set(self, client, user_data, message):
        msg = message.payload.decode("utf-8").strip()
        LOG.info("Read chime set '%s'", msg)

        chime_on = msg.lower() == "on"
        self.set_chime(chime_on)

    def set_chime(self, chime_on):
        # If we know the chime state, then we can test whether the request is
        # a change or not.  Need this because the chime state MQTT message
        # will have retain=T and every time we start up we'll get it but we
        # only want to change the chime state if it's actually different
        # because the chime command is a toggle - not a set and we could
        # toggle it the wrong way.
        if "chime_on" in self.panel_attr:
            if chime_on != self.panel_attr.get("chime_on", False):
                LOG.info("Toggling chime status")
                self.ad.send(self.code + "9")

            self.req_chime_on = None

        # Pend the request until we know the chime state.
        else:
            self.req_chime_on = chime_on

    def cb_bypass_set(self, client, user_data, message):
        msg = message.payload.decode("utf-8").strip()
        LOG.info("Read bypass set '%s'", msg)
        self.is_bypass = (msg.lower() == "on")

        payload = {"status" : "ON" if self.is_bypass else "OFF"}
        self.publish(self.bypass_state_topic, {}, payload)

    def publish(self, topic, topic_args, payload_args, zone_num=None,
                zone=None):
        time = DT.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        payload_args["time"] = time

        if zone is not None or zone_num is not None:
            if not zone:
                zone = self.zones.get(zone_num)
                if not zone:
                    LOG.error("Skipping unknown zone %s", zone_num)

            if zone:
                topic_args["entity"] = zone.entity
                payload_args["zone_num"] = zone.zone

        topic_str = topic.format(**topic_args)
        payload = json.dumps(payload_args)
        LOG.info("Publish '%s' = %s", topic_str, payload)
        self.mqtt.publish(topic_str, payload, qos=self.qos, retain=self.retain)

    def on_arm(self, dev, stay):
        LOG.info("on_arm %s", stay)
        self._update_panel_status("armed_home" if stay else "armed_away")

    def on_disarm(self, dev):
        LOG.info("on_disarm")
        self._update_panel_status("disarmed")

    def on_power_changed(self, dev, status):
        # message.ac_power
        pass

    def on_ready_changed(self, dev, status):
        pass

    def on_alarm(self, dev, zone):
        LOG.info("on_alarm zone: %s", zone)

        # Update the faulted zone first.
        info = self.zones.get(zone)
        if not info:
            LOG.error("Skipping unknown zone %s", zone)
        else:
            self.last_alarm_zone = info.entity

        self._update_panel_status("triggered", zone=zone)

    def on_alarm_restored(self, dev, zone, user=None):
        LOG.info("on_alarm_restored zone: %s", zone)
        self._update_panel_status("disarmed", zone=zone)
        self.last_alarm_zone = "None"

    def on_fire(self, dev, status):
        # message.fire_alarm
        pass

    def on_bypass(self, dev, status, zone=None):
        # status == bool
        LOG.info("on_bypass %s zone=%s", status, zone)

        payload = {"status" : "ON" if status else "OFF"}
        self.publish(self.panel_bypass_topic, {}, payload, zone_num=zone)

    def on_boot(self, dev):
        pass

    def on_zone_fault(self, dev, zone):
        LOG.info("on_zone_fault %s", zone)

        info = self.zones.get(zone)
        if info:
            info.faulted = True

        payload = {"status" : "ON"}
        self.publish(self.sensor_state_topic, {}, payload, zone_num=zone,
                     zone=info)

    def on_zone_restore(self, dev, zone):
        LOG.info("on_zone_restored %s", zone)
        info = self.zones.get(zone)
        if info:
            info.faulted = False

        payload = {"status" : "OFF"}
        self.publish(self.sensor_state_topic, {}, payload, zone_num=zone,
                     zone=info)

    def on_low_battery(self, dev, status):
        # status = bool
        payload = {"status" : 10 if status else 100}
        self.publish(self.panel_battery_topic, {}, payload)

    def on_panic(self, dev, status):
        # status == bool
        pass

    def on_relay_changed(self, dev, message):
        pass

    def on_chime_changed(self, dev, status):
        # status = bool
        payload = {"status" : "ON" if status else "OFF"}
        self.publish(self.chime_state_topic, {}, payload)

    def on_message(self, dev, message):
        LOG.debug("on_message %s", repr(message))

        msg = message
        # first call: update sensor states
        if not self.panel_attr:
            self.on_chime_changed(dev, msg.chime_on)
            self.on_bypass(dev, msg.zone_bypassed)
            self.on_low_battery(dev, msg.battery_low)

        panel_attr = {
            "ac_power_on": msg.ac_power,
            "alarm_event_occurred": msg.alarm_event_occurred,
            "backlight_on": msg.backlight_on,
            "battery_low": msg.battery_low,
            "check_zone": msg.check_zone,
            "chime_on": msg.chime_on,
            "entry_delay_off": msg.entry_delay_off,
            "programming_mode": msg.programming_mode,
            "ready": msg.ready,
            "zone_bypassed": msg.zone_bypassed,
            }

        payload = {"status" : msg.text.strip()}
        self.publish(self.panel_msg_topic, {}, payload)

        # If there is a pending chime state request, process it now that we
        # know the current chime state.
        if self.req_chime_on is not None:
            self.set_chime(self.req_chime_on)

        # Update the panel state if this is the first call we've seen or if
        # the attributes have changed.
        if self.panel_status is None or self.panel_attr != panel_attr:
            status = self.panel_status
            if self.panel_status is None:
                status = "disarmed"
                if msg.alarm_sounding:
                    status = "triggered"
                elif msg.armed_away:
                    status = "armed_away"
                elif msg.armed_home:
                    status = "armed_home"

            self.panel_attr = panel_attr
            self._update_panel_status(status)

    def on_expander_message(self, dev, message):
        LOG.info("on_expander_message %s", repr(message))

    def on_lrr_message(self, dev, message):
        LOG.info("on_lrr_message %s", repr(message))

    def on_rfx_message(self, dev, message):
        msg = message
        serial = int(msg.serial_number)
        info = self.rf_devices.get(serial)
        if info is None:
            LOG.debug("Ignoring unknown RF serial number %s", msg.serial_number)
            return

        LOG.info("on_rfx_message serial=%s value=%s battery=%s supervision=%s "
                 "loop=%s", msg.serial_number, msg.value, msg.battery,
                 msg.supervision, msg.loop)

        battery_payload = None
        if msg.value is not None:
            is_low_battery = bool(msg.value & 0x02)
            battery_payload = {"status" : 10 if is_low_battery else 100}


        for i, loop in enumerate( info.loops ):
            if not loop:
                continue

            if battery_payload:
                self.publish(self.sensor_battery_topic, {}, battery_payload,
                             zone_num=loop.zone)

            # True = faulted, False = cleared
            if msg.loop[i] == loop.faulted:
                continue

            if msg.loop[i]:
                self.on_zone_fault(dev, loop.zone)
            else:
                self.on_zone_restore(dev, loop.zone)

            loop.faulted = msg.loop[i]

        # TODO: check loop and update sensor state.
        # Need to map loop value to zone number and sensor info
        # then check message.loop[loop_num] == True:fault, False:clear

    def on_open(self, dev):
        LOG.info("on_open")

    def on_close(self, dev):
        LOG.info("on_close")

    def _connect(self):
        self.ad.on_arm += self.on_arm
        self.ad.on_disarm += self.on_disarm
        self.ad.on_power_changed += self.on_power_changed
        self.ad.on_ready_changed += self.on_ready_changed
        self.ad.on_alarm += self.on_alarm
        self.ad.on_alarm_restored += self.on_alarm_restored
        self.ad.on_fire += self.on_fire
        self.ad.on_bypass += self.on_bypass
        self.ad.on_boot += self.on_boot
        self.ad.on_zone_fault += self.on_zone_fault
        self.ad.on_zone_restore += self.on_zone_restore
        self.ad.on_low_battery += self.on_low_battery
        self.ad.on_panic += self.on_panic
        self.ad.on_relay_changed += self.on_relay_changed
        self.ad.on_chime_changed += self.on_chime_changed
        self.ad.on_message += self.on_message
        self.ad.on_expander_message += self.on_expander_message
        self.ad.on_lrr_message += self.on_lrr_message
        self.ad.on_rfx_message += self.on_rfx_message
        self.ad.on_open += self.on_open
        self.ad.on_close += self.on_close

    def _update_panel_status(self, status, zone=None):
        self.panel_status = status

        payload = {"status" : self.panel_status, "attr" : self.panel_attr,
                   "last_alarm_zone" : self.last_alarm_zone}
        self.publish(self.panel_state_topic, {}, payload, zone_num=zone)

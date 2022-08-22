import json
import logging

LOG = logging.getLogger(__name__)

class Discovery:
    def __init__(self, mqtt, bridge, zones):
        self.mqtt = mqtt
        mqtt.signal_connected.connect(self.mqtt_connected)
        self.messages = []

        topic = 'homeassistant/alarm_control_panel/admqtt_alarm_panel/config'
        # Combine the time vield from the json message w/ all the attributes
        # into a single json dict for the entity attributes.
        attr_templ = ('{ "time" : "{{value_json.time}}", '
                      '"last_alarm_zone" : "{{value_json.last_alarm_zone}}", '
                      '{% for k,v in value_json.attr.items() %}'
                      '{{ k | tojson }} : {{ v | tojson }}'
                      '{{ ", " if not loop.last else "" }}'
                      '{% endfor %} }')
        payload = {
            'object_id' : 'alarm_panel_mqtt',
            'unique_id' : 'admqtt_alarm_panel',
            'state_topic' : bridge.panel_state_topic,
            'value_template' : '{{value_json.status}}',
            'availability_topic' : 'alarm/available',
            'code' : 'REMOTE_CODE',
            'command_topic' : bridge.panel_set_topic,
            'command_template' : ('{ "action": "{{action}}",'
                                  '  "code": "{{code}}"}'),
            'payload_arm_away' : 'arm_away',
            'payload_arm_home' : 'arm_stay',
            'payload_arm_night' : 'arm_night',
            'payload_disarm' : 'disarm',
            'json_attributes_topic' : bridge.panel_state_topic,
            'json_attributes_template' : attr_templ,
            'qos' : 1,
            }
        self.messages.append((topic, payload))

        # main panel battery sensor
        topic = 'homeassistant/sensor/admqtt_alarm_panel_battery/config'
        payload = {
            'name' : "Alarm Panel Battery",
            'object_id' : "alarm_panel_battery",
            'unique_id' : "admqtt_alarm_panel_battery",
            'state_topic' : bridge.panel_battery_topic,
            'value_template' : '{{value_json.status}}',
            'unit_of_measurement': '%',
            'device_class' : 'battery',
            }
        self.messages.append((topic, payload))

        # bypass state sensor
        topic = 'homeassistant/binary_sensor/admqtt_alarm_panel_bypass/config'
        payload = {
            'name' : "Alarm Panel Bypass",
            'object_id' : "alarm_panel_bypass",
            'unique_id' : "admqtt_alarm_panel_bypass",
            'state_topic' : bridge.panel_bypass_topic,
            'value_template' : '{{value_json.status}}',
            }
        self.messages.append((topic, payload))

        # Ideally this would be an attribute of the alarm panel but that's
        # pulling attributes from the message.  Should probably process the
        # attributes when they arrive in the on_message and if they change,
        # trigger an alarm panel state update and add the faulted zone
        # automatically there.
        topic = 'homeassistant/sensor/admqtt_alarm_panel_faulted/config'
        payload = {
            'name' : 'Alarm Faulted Zone',
            'object_id' : 'alarm_panel_faulted',
            'unique_id' : 'admqtt_alarm_panel_faulted',
            'icon' : 'mdi:alarm-check',
            'state_topic' : bridge.panel_faulted_topic,
            'value_template' : '{{value_json.status}}',
            'json_attributes_topic' : bridge.panel_faulted_topic,
            'json_attributes_template' :
               ('{ "zone_num" : {{value_json.zone_num}},'
                 '"entity" : "{{value_json.entity}}" }'),
            }
        self.messages.append((topic, payload))

        topic = 'homeassistant/sensor/admqtt_alarm_panel_message/config'
        payload = {
            'name' : 'Alarm Panel Message',
            'object_id' : 'alarm_panel_message',
            'unique_id' : 'admqtt_alarm_panel_message',
            'icon' : 'mdi:alarm-check',
            'state_topic' : bridge.panel_msg_topic,
            'value_template' : '{{value_json.status}}',
            'json_attributes_topic' : bridge.panel_msg_topic,
            'json_attributes_template' : '{ "time" : "{{value_json.time}}" }',
            }
        self.messages.append((topic, payload))

        topic = 'homeassistant/switch/admqtt_alarm_panel_chime/config'
        payload = {
            'name' : 'Alarm Chime',
            'object_id' : 'alarm_panel_chime',
            'unique_id' : 'admqtt_alarm_panel_chime',
            'icon' : 'mdi:bell-ring',
            'state_topic' : bridge.chime_state_topic,
            'value_template' : '{{value_json.status}}',
            'command_topic' : bridge.chime_set_topic,
            'qos' : 1,
            }
        self.messages.append((topic, payload))

        topic = 'homeassistant/switch/admqtt_alarm_panel_bypass/config'
        payload = {
            'name' : 'Alarm Bypass',
            'object_id' : 'alarm_panel_bypass',
            'unique_id' : 'admqtt_alarm_panel_bypass',
            'icon' : 'mdi:bell-ring',
            'state_topic' : bridge.bypass_state_topic,
            'value_template' : '{{value_json.status}}',
            'command_topic' : bridge.bypass_set_topic,
            'qos' : 1,
            'retain' : True,
            }
        self.messages.append((topic, payload))

        for z in zones.values():
            z.unique_id = 'admqtt_' + z.entity
            attr_templ = ('{ "time" : "{{value_json.time}}", '
                          '"zone_num" : {{value_json.zone_num}} }')

            topic = f'homeassistant/binary_sensor/{z.unique_id}/config'
            state_topic = bridge.sensor_state_topic.format(
                unique_id=z.unique_id, entity=z.entity)
            payload = {
                'name' : z.label,
                'object_id' : z.entity,
                'unique_id' : z.unique_id,
                'state_topic' : state_topic,
                'value_template' : '{{value_json.status}}',
                'json_attributes_topic' : state_topic,
                'json_attributes_template' : attr_templ,
                }
            if z.device_class is not None:
                payload['device_class'] = z.device_class
            self.messages.append((topic, payload))

            if z.has_battery:
                bat_entity = z.entity + '_battery'
                bat_unique_id = z.unique_id + '_battery'
                topic = f'homeassistant/sensor/{bat_unique_id}/config'
                state_topic = bridge.sensor_battery_topic.format(
                    unique_id=bat_unique_id, entity=bat_entity)
                payload = {
                    'name' : z.label + ' Battery',
                    'object_id' : bat_entity,
                    'unique_id' : bat_unique_id,
                    'state_topic' : state_topic,
                    'value_template' : '{{value_json.status}}',
                    'unit_of_measurement': '%',
                    'device_class' : 'battery',
                    'json_attributes_topic' : state_topic,
                    'json_attributes_template' : attr_templ,
                    }
                self.messages.append((topic, payload))

    def mqtt_connected(self, device, connected):
        if not self.messages:
            return

        LOG.info( "Discovery publish for %d messages", len( self.messages ) )

        # Ideally we'd publish one, wait for an ack, then publish the next.
        # But this doesn't work because paho will throw an error if you
        # publish in the on_publish callback (which IMO makes no sense).
        for topic, payload in self.messages:
            self.mqtt.publish(topic, json.dumps(payload), qos=1, retain=True)

        self.messages = []

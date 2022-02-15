import json

class Discovery:
    def __init__(self, mqtt, bridge, zone_data):
        self.mqtt = mqtt
        mqtt.signal_connected.connect(self.mqtt_connected)
        self.messages = []

        topic = 'homeassistant/alarm_control_panel/admqtt_alarm_panel/config'
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
            'json_attributes_topic' : bridge.panel_msg_topic,
            'json_attributes_template' : '{{value_json.attr | tojson}}',
            'qos' : 1,
            }
        self.messages.append( (topic, payload) )

        # TODO: create last updated time sensors for everything since HA
        # doesn't save that information.

        # TODO: create main panel battery sensor
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
        self.messages.append( (topic, payload) )

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
               ( '{ "zone_num" : {{value_json.zone_num}},'
                 '"entity" : "{{value_json.entity}}" }'),
            }
        self.messages.append( (topic, payload) )

        topic = 'homeassistant/sensor/admqtt_alarm_panel_message/config'
        payload = {
            'name' : 'Alarm Panel Message',
            'object_id' : 'alarm_panel_message',
            'unique_id' : 'admqtt_alarm_panel_message',
            'icon' : 'mdi:alarm-check',
            'state_topic' : bridge.panel_msg_topic,
            'value_template' : '{{value_json.status}}',
            }
        self.messages.append( (topic, payload) )

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
        self.messages.append( (topic, payload) )

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
        self.messages.append( (topic, payload) )

        for info in zone_data.values():
            entity = info['entity']
            has_battery = info.get('rf_id', None)
            info['unique_id'] = unique_id = 'admqtt_' + entity

            topic = f'homeassistant/binary_sensor/{unique_id}/config'
            payload = {
                'name' : info['label'],
                'object_id' : entity,
                'unique_id' : unique_id,
                'state_topic' : bridge.sensor_state_topic.format(
                    unique_id=unique_id, entity=entity),
                'value_template' : '{{value_json.status}}',
                }
            if 'window' in entity.lower():
                payload['device_class'] = 'window'
            elif 'door' in entity.lower():
                payload['device_class'] = 'door'
            self.messages.append( (topic, payload) )

            if has_battery:
                bat_entity = entity + '_battery'
                bat_unique_id = unique_id + '_battery'
                topic = f'homeassistant/sensor/{bat_unique_id}/config'
                payload = {
                    'name' : info['label'] + ' Battery',
                    'object_id' : bat_entity,
                    'unique_id' : bat_unique_id,
                    'state_topic' : bridge.sensor_battery_topic.format(
                        unique_id=bat_unique_id, entity=bat_entity),
                    'value_template' : '{{value_json.status}}',
                    'unit_of_measurement': '%',
                    'device_class' : 'battery',
                    }
                self.messages.append( (topic, payload) )

    def mqtt_connected(self, device, connected):
        if not self.messages:
            return

        # queue w/ response doesn't work because paho doesn't allow it
        # - it's throws an error if you publish in the on_publish
        # callback. (which IMO makes no sense).
        for topic, payload in self.messages:
            self.mqtt.publish(topic, json.dumps(payload), qos=1, retain=True)

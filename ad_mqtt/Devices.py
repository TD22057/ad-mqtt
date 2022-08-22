
def init_devices(devices):
    zones, rf_devices = {}, {}

    for d in devices:
        if not isinstance(d, RfZone):
            zones[d.zone] = d
        else:
            rf_devices[d.id] = d
            for l in d.loops:
                if l is not None:
                    zones[l.zone] = l

    return zones, rf_devices


class Zone:
    def __init__(self, zone, entity, label, device_class=None):
        self.zone = zone   # int zone number
        self.entity = entity
        self.label = label
        self.faulted = None  # None=Unknown, True=faulted, False=clear
        self.has_battery = False
        self.unique_id = None
        self.device_class = device_class if device_class else \
                            guess_class((entity, label))


class Rf:
    def __init__(self, id, loops):
        self.id = int(id)
        self.loops = [None]*4
        for i, l in enumerate(loops):
            self.loops[i] = l
            l.has_battery = True


class RfZone (Rf):
    def __init__(self, id, zone, entity, label):
        super().__init__(id, [Zone(zone, entity, label)])


class_keywords = {
    # Map of keyword to HASS device class
    "fire" : "smoke",
    "door" : "door",
    "window" : "window",
    }

def guess_class(labels):
    for l in labels:
        s = l.lower()
        for k, v in class_keywords.items():
            if k in s:
                return v

    return None

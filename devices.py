def get_devices():
    return [
    # Zone( zone_number, HAS_entity_name, description, device_class )
    AD.Zone(1, "fire", "Fire Alarm", "smoke"),
    AD.Zone(2, "basement_door", "Basement Door"),
    # RF zone ( serial_number, zone_number, HAS_entity_name, description )
    AD.RfZone( 12345, 25, "front_door", "Front Door"),
    AD.RfZone( 12345, 27, "dining_room_door", "Dining Room Door"),
    AD.RfZone( 12345, 29, "kitchen_window_right", "Kitchen Right Window"),
    AD.RfZone( 12345, 30, "guest_bedroom_window", "Guest Bedroom Window"),
    AD.Rf( 12345, loops=[
        AD.Zone(31, "side_window", "Side Window"),
        None, None,  # loops 2, 3 unused
        AD.Zone(32, "side_window_tampler", "Side Window Tampler", "tampler"),
        ]) 
    ]
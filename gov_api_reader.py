# Full list of event types
# Taken from https://api.weather.gov/alerts/types
"""
[
    "911 Telephone Outage Emergency",
    "Administrative Message",
    "Air Quality Alert",
    "Air Stagnation Advisory",
    "Arroyo And Small Stream Flood Advisory",
    "Ashfall Advisory",
    "Ashfall Warning",
    "Avalanche Advisory",
    "Avalanche Warning",
    "Avalanche Watch",
    "Beach Hazards Statement",
    "Blizzard Warning",
    "Blizzard Watch",
    "Blowing Dust Advisory",
    "Blowing Dust Warning",
    "Brisk Wind Advisory",
    "Child Abduction Emergency",
    "Civil Danger Warning",
    "Civil Emergency Message",
    "Coastal Flood Advisory",
    "Coastal Flood Statement",
    "Coastal Flood Warning",
    "Coastal Flood Watch",
    "Dense Fog Advisory",
    "Dense Smoke Advisory",
    "Dust Advisory",
    "Dust Storm Warning",
    "Earthquake Warning",
    "Evacuation - Immediate",
    "Excessive Heat Warning",
    "Excessive Heat Watch",
    "Extreme Cold Warning",
    "Extreme Cold Watch",
    "Extreme Fire Danger",
    "Extreme Wind Warning",
    "Fire Warning",
    "Fire Weather Watch",
    "Flash Flood Statement",
    "Flash Flood Warning",
    "Flash Flood Watch",
    "Flood Advisory",
    "Flood Statement",
    "Flood Warning",
    "Flood Watch",
    "Freeze Warning",
    "Freeze Watch",
    "Freezing Fog Advisory",
    "Freezing Rain Advisory",
    "Freezing Spray Advisory",
    "Frost Advisory",
    "Gale Warning",
    "Gale Watch",
    "Hard Freeze Warning",
    "Hard Freeze Watch",
    "Hazardous Materials Warning",
    "Hazardous Seas Warning",
    "Hazardous Seas Watch",
    "Hazardous Weather Outlook",
    "Heat Advisory",
    "Heavy Freezing Spray Warning",
    "Heavy Freezing Spray Watch",
    "High Surf Advisory",
    "High Surf Warning",
    "High Wind Warning",
    "High Wind Watch",
    "Hurricane Force Wind Warning",
    "Hurricane Force Wind Watch",
    "Hurricane Local Statement",
    "Hurricane Warning",
    "Hurricane Watch",
    "Hydrologic Advisory",
    "Hydrologic Outlook",
    "Ice Storm Warning",
    "Lake Effect Snow Advisory",
    "Lake Effect Snow Warning",
    "Lake Effect Snow Watch",
    "Lake Wind Advisory",
    "Lakeshore Flood Advisory",
    "Lakeshore Flood Statement",
    "Lakeshore Flood Warning",
    "Lakeshore Flood Watch",
    "Law Enforcement Warning",
    "Local Area Emergency",
    "Low Water Advisory",
    "Marine Weather Statement",
    "Nuclear Power Plant Warning",
    "Radiological Hazard Warning",
    "Red Flag Warning",
    "Rip Current Statement",
    "Severe Thunderstorm Warning",
    "Severe Thunderstorm Watch",
    "Severe Weather Statement",
    "Shelter In Place Warning",
    "Short Term Forecast",
    "Small Craft Advisory",
    "Small Craft Advisory For Hazardous Seas",
    "Small Craft Advisory For Rough Bar",
    "Small Craft Advisory For Winds",
    "Small Stream Flood Advisory",
    "Snow Squall Warning",
    "Special Marine Warning",
    "Special Weather Statement",
    "Storm Surge Warning",
    "Storm Surge Watch",
    "Storm Warning",
    "Storm Watch",
    "Test",
    "Tornado Warning",
    "Tornado Watch",
    "Tropical Depression Local Statement",
    "Tropical Storm Local Statement",
    "Tropical Storm Warning",
    "Tropical Storm Watch",
    "Tsunami Advisory",
    "Tsunami Warning",
    "Tsunami Watch",
    "Typhoon Local Statement",
    "Typhoon Warning",
    "Typhoon Watch",
    "Urban And Small Stream Flood Advisory",
    "Volcano Warning",
    "Wind Advisory",
    "Wind Chill Advisory",
    "Wind Chill Warning",
    "Wind Chill Watch",
    "Winter Storm Warning",
    "Winter Storm Watch",
    "Winter Weather Advisory"
]
"""

import urequests as request
from machine import Pin
from time import sleep

VERSION = 1

state_groups = {
    "w-pacific": ["WA", "OR", "CA"],
    "w-mountain": ["MT", "ID", "WY", "NV", "UT", "CO", "AZ", "NM"],
    "mw-west": ["ND", "SD", "MN", "NE", "IA", "KS", "MO"],
    "mw-east": ["WI", "MI", "IL", "IA", "OH"],
    "s-west": ["OK", "AR", "TX", "LA"],
    "s-east": ["MS", "AL", "TN", "KY"],
    # Note, DC is not a state but is included in the API for reasons unbeknownst to me
    "s-atlantic": ["FL", "GA", "SC", "NC", "VA", "WV", "DC", "MD", "DE"],
    "ne-atlantic": ["PA", "NJ", "NY"],
    "ne-england": ["VT", "NH", "ME", "MA", "RI", "CT"]
}

alert_types = {
    "tornado": [
        "Tornado Warning", "Tornado Watch"
    ],
    "storms": [
        "Hurricane Warning", "Hurricane Watch",
        "Storm Warning", "Storm Watch",
        "Tropical Storm Warning", "Tropical Storm Watch",
        "Typhoon Warning", "Typhoon Watch"
    ],
    "evacuation": [
        "Evacuation - Immediate"
    ]
}

alert_states = {
    "w-pacific": [False, False, False],
    "w-mountain": [False, False, False],
    "mw-west": [False, False, False],
    "mw-east": [False, False, False],
    "s-west": [False, False, False],
    "s-east": [False, False, False],
    "s-atlantic": [False, False, False],
    "ne-atlantic": [False, False, False],
    "ne-england": [False, False, False]
}


UPDATE_PIN = 2

alert_pins = {
    "w-pacific": [32, 23, ],
    "w-mountain": [33, 22, ],
    "mw-west": [25, 21, ],
    "mw-east": [26, 19, ],
    "s-west": [27, 18, ],
    "s-east": [14, 5, ],
    "s-atlantic": [12, 17, ],
    "ne-atlantic": [13, 16, ],
    "ne-england": [15, 4, ]
}


# Get updated version based on raw GitHub file
def get_current_version():
    try:
        response = request.get(
            url="https://raw.githubusercontent.com/BenSnellgrove/US-Regional-Storm-Display/master/version.txt"
        )
        return int(response.text)

    # File unavailable, assume no connection or dev mode.
    except Exception:
        return VERSION + 1


def get_active_events(state: str):
    # Gov API wants headers, for abuse tracking reasons
    headers = {
        "User-Agent": "Weather scanner v0.1",
        "From": "esp32, 9 min cooldown on each state"
    }

    # HTTP Get request
    response = request.get(url="https://api.weather.gov/alerts/active?area=" + state, headers=headers)

    # Buffer is half size of long buffer to ensure no data is missed
    buf = bytearray(512)
    bufPrev = bytearray(512)
    bufLong = bytearray(1024)

    foundEvents = {
        "tornado": False,
        "storms": False,
        "evacuation": False
    }

    # Event scan
    while True:
        # Data has to be read into a buffer because .text loads the whole page into memory and the chip doesn't have
        #  enough memory for that
        bufPrev = buf
        numbytes = response.raw.readinto(buf)
        bufLong = bufPrev + buf

        index = bufLong.find(b'"event": "')
        if index != -1:
            if buf.find(b'",', index) != -1:
                cur_event = bufLong[
                            buf.index(b'": "', index) + 4:buf.index(b'",', index)
                            ]

                for a_type in alert_types:
                    if cur_event in alert_types[a_type]:
                        foundEvents[a_type] = True

        # EOF
        if numbytes < len(buf):
            break

    # Close input buffer
    response.raw.close()
    return foundEvents


# Version checking
if VERSION < get_current_version():
    # Turn on update Pin
    print("Update required!")
    print("Please visit https://github.com/BenSnellgrove/US-Regional-Storm-Display for the latest version")

    led = Pin(UPDATE_PIN, Pin.OUT)
    led.value(True)
    for n in range(10):
        sleep(0.7)
        led.value(not led.value())
    led.value(False)

    # Allow continued use, don't want to force updates


while True:

    try:

        # Each group 1min apart
        for state_group in state_groups:
            # Reset alert states
            alert_states[state_group] = [False, False, False]
            for us_state in state_groups[state_group]:
                alert_states[state_group] = [a and b for a, b in
                                             zip(alert_states[state_group], get_active_events(us_state))]
                #alert_states[state_group] = [True, True, False]

            # Pins
            print(f"state_group {state_group}")
            print(alert_states[state_group])


            # Work this way round, so can remove pins and maintain functionality
            pin_group = alert_pins[state_group]
            for pin_n in range(len(pin_group)):
                led = Pin(pin_group[pin_n], Pin.OUT)
                led.value(alert_states[state_group][pin_n])

            sleep(60)

    # On absolutely any error
    except Exception:
        led = Pin(UPDATE_PIN, Pin.OUT)
        led.value(True)


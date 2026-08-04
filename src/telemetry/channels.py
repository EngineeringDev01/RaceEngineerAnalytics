STANDARD_CHANNELS = {

    "time": "Time",

    "distance": "Distance",

    "speed": [
        "Speed",
        "Wheel Speed FL"
    ],

    "engine": [
        "Engine RPM",
        "Eng Torq"
    ],

    "driver_inputs": [
        "Throttle Pos",
        "Brk_Press_Fnt",
        "Brk_Press_Rear",
        "Steered Angle"
    ],

    "vehicle_dynamic": [
        "G Force Lat",
        "G Force Long",
        "Yaw rate",
        "Pitch angle",
        "Roll angle"
    ],

    "tyres": [
        "Tyre Temp FL",
        "Tyre Temp FR",
        "Tyre Temp RL",
        "Tyre Temp RR"
    ]
}


def find_available_channels(dataframe):

    available = {}

    columns = dataframe.columns

    for group, channels in STANDARD_CHANNELS.items():

        if isinstance(channels, list):

            available[group] = [
                c for c in channels
                if c in columns
            ]

        else:

            available[group] = (
                channels
                if channels in columns
                else None
            )

    return available
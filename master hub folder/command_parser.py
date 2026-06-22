# command_parser.py

DOMAIN_SELECTION_MAP = {
    "NEUTRAL_IOT": "IOT",
    "NEUTRAL_EMBEDDED": "EMBEDDED",
    "NEUTRAL_DESKTOP": "DESKTOP",
    "NEUTRAL_MOBILE": "MOBILE"
}

ACTION_PREFIX_MAP = {
    "LEFT": "IOT",
    "POP": "EMBEDDED",
    "PUSH": "DESKTOP",
    "RIGHT": "MOBILE"
}


def parse_command(command):
    command = command.strip().upper()

    if command == "DROP":
        return "GLOBAL", "STOP"

    if command in DOMAIN_SELECTION_MAP:
        return "SELECT", DOMAIN_SELECTION_MAP[command]

    parts = command.split("_", 1)

    if len(parts) != 2:
        return None, None

    prefix = parts[0]
    action = parts[1]

    domain = ACTION_PREFIX_MAP.get(prefix)

    return domain, action
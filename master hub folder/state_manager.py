# state_manager.py

current_state = "DEVICE_SELECTION"
current_domain = None


def get_state():
    return current_state


def set_state(state):
    global current_state
    current_state = state


def get_domain():
    return current_domain


def set_domain(domain):
    global current_domain
    current_domain = domain


def reset():
    global current_state, current_domain
    current_state = "DEVICE_SELECTION"
    current_domain = None
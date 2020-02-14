from signals.signal import TickerSignal, CounterSignal, Signal

def deserialize(data):
    if isinstance(data, list):
        return [deserialize(item) for item in data]

    if "type" not in data:
        raise ValueError("[type] is missing from data")
    if "name" not in data:
        raise ValueError("[name] is missing from data")
    
    type = data["type"]
    name = data["name"]

    visible = True
    if "visible" in data:
        visible = data["visible"]
    dependencies = None
    if "dependencies" in data:
        dependencies = data["dependencies"]

    s = None
    if type == "ticker":
        s = _create_ticker(data, name)
    elif type == "counter":
        s = _create_counter(data, name)
    else:
        raise ValueError(f"type [{type}] not implemented.")

    s.visible = visible
    s.dependencies = dependencies
    return s

def _create_ticker(data, name):
    if "period" not in data:
        raise ValueError(f"[period] not present in Ticker {name}")
    period = data["period"]
    return TickerSignal(name, period=period)

def _create_counter(data, name):
    old_state_trigger = Signal.LOW
    if "old_state_trigger" in data:
        old_state_trigger = data["old_state_trigger"]

    new_state_trigger = Signal.HIGH
    if "new_state_trigger" in data:
        new_state_trigger = data["new_state_trigger"]

    return CounterSignal(name,
                         old_state_trigger=old_state_trigger,
                         new_state_trigger=new_state_trigger)

from signals.signal import TickerSignal, CounterSignal, Signal, ParameterSignal

def deserialize(data):
    if isinstance(data, list):
        return [deserialize(item) for item in data]

    if "type" not in data:
        raise ValueError("[type] is missing from data")
    if "name" not in data:
        raise ValueError("[name] is missing from data")
    
    type = data["type"]
    name = data["name"]

    initial_state = None
    if "initial_state" in data:
        initial_state = data["initial_state"]

    s = None
    if type == "ticker":
        s = _create_ticker(data, name, initial_state)
    elif type == "counter":
        s = _create_counter(data, name, initial_state)
    elif type == "parameter":
        s = _create_parameter(data, name, initial_state)
    else:
        raise ValueError(f"type [{type}] not implemented.")

    visible = True
    if "visible" in data:
        visible = data["visible"]
    dependencies = None
    if "dependencies" in data:
        dependencies = data["dependencies"]

    if s.visible is None:
        s.visible = visible
    if s.dependencies is None:
        s.dependencies = dependencies
    elif dependencies is not None:
        s.dependencies += dependencies
    return s

def _create_ticker(data, name, initial_state):
    if "period" not in data:
        raise ValueError(f"[period] not present in Ticker {name}")
    period = data["period"]
    return TickerSignal(name, initial_state=initial_state, period=period)

def _create_counter(data, name, initial_state):
    old_state_trigger = Signal.LOW
    if "old_state_trigger" in data:
        old_state_trigger = data["old_state_trigger"]

    new_state_trigger = Signal.HIGH
    if "new_state_trigger" in data:
        new_state_trigger = data["new_state_trigger"]

    return CounterSignal(name, initial_state=initial_state,
                         old_state_trigger=old_state_trigger,
                         new_state_trigger=new_state_trigger)

def _create_parameter(data, name, initial_state):
    if "true_state" not in data:
        raise ValueError(f"[true_state] not present in Parameter {name}")
    true_state = data["true_state"]

    return ParameterSignal(name, true_state, initial_state=initial_state)

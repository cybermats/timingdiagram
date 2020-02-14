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
        
    if s.visible is None:
        s.visible = visible
        
    dependencies = None
    if "dependencies" in data:
        dependencies = data["dependencies"]

    if s.dependencies is None or dependencies is not None:
        s.dependencies = dependencies

    states = None
    if "states" in data:
        states = data["states"]

    if s.states is None or states is not None:
        s.states = states

    delay = None
    if "delay" in data:
        delay = data["delay"]

    if s.delay is None or delay is not None:
        s.delay = delay
        
    return s

def _create_ticker(data, name, initial_state):
    if "period" not in data and "frequency" not in data:
        raise ValueError(f"Neither [period] nor [frequency] are present in Ticker {name}")
    if "period" in data and "frequency" in data:
        raise ValueError(f"Both [period] and [frequency] are present in Ticker {name}")
    period = 1
    if "frequency" in data:
        period = 1 / data["frequency"]
    else:
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

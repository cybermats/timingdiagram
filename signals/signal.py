
class Signal():
  UNDEFINED="UNDEFINED"
  HIGH="HIGH"
  LOW="LOW"
  IMPEDANCE="IMPEDANCE"
  DATA="DATA"

  def __init__(self, name,
               initial_state=UNDEFINED):
    self.name = name
    self.state = initial_state
    self.dependencies = []
    self.visible = True
    
    self.history = [(None, initial_state)]

  def tick(self, current_time):
    pass

  def context(self, s_name, old_state, new_state, next_time):
    pass

  def first_tick(self):
    pass

  def _save(self, current_time, state):
    self.history.append((current_time, state))

  def get_history(self):
    return self.history

class FlipSignal(Signal):
  def __init__(self, name,
               initial_state,
               states):
    if not initial_state:
      initial_state = Signal.LOW

    super().__init__(name,
                     initial_state=initial_state)
      
    if not states:
      states = [Signal.LOW, Signal.HIGH]

    self.delay = 0
    self.states = states

  def _flip(self):
    old_state = self.state
    old_location = self.states.index(old_state)
    new_location = (old_location + 1) % len(self.states)
    new_state = self.states[new_location]
    self.state = new_state
    return old_state, new_state

class TickerSignal(FlipSignal):
  def __init__(self, name,
               initial_state=None,
               states=None,
               period=None,
               frequency=None):
    if not period and not frequency:
      raise ValueError("One of Period or Frequency has to be specified")
    if period and frequency:
      raise ValueError("Only one of Period or Frequency can be specified")
    if frequency:
      period = 1 / frequency
    self.period = period
    super().__init__(name, initial_state, states)

  def tick(self, current_time):
    super().tick(current_time)
    old_state, new_state = super()._flip()
    next_time = current_time + (self.period / 2)
    self._save(current_time, new_state)
    return old_state, new_state, next_time

  def first_tick(self):
    return self.period/2

class CounterSignal(FlipSignal):
  def __init__(self, name,
               old_state_trigger=Signal.LOW,
               new_state_trigger=Signal.HIGH,
               initial_state=None,
               states=None):
    self.old_state_trigger = old_state_trigger
    self.new_state_trigger = new_state_trigger
    super().__init__(name, initial_state, states)

  def tick(self, current_time):
    super().tick(current_time)
    old_state, new_state = super()._flip()

    self._save(current_time, new_state)
    return old_state, new_state, None

  def context(self, s_name, old_state, new_state, current_time, next_time):
    if (old_state == self.old_state_trigger and
        new_state == self.new_state_trigger):
      return current_time + self.delay
    return None


class Signal():
  UNDEFINED="UNDEFINED"
  HIGH="HIGH"
  LOW="LOW"
  IMPEDANCE="IMPEDANCE"
  DATA="DATA"

  def __init__(self, name, initial_state):
    self.name = name
    self.state = initial_state
    self.dependencies = None
    
    self.visible = None
    
    self.history = [(None, initial_state)]
    self.causes = []
    self.show_cause = True

  def tick(self, current_time):
    pass

  def context(self, s_name, old_state, new_state, next_time):
    pass

  def first_tick(self):
    pass

  def set_dependency_state(self, name, value):
    pass

  def _save(self, current_time, state):
    self.history.append((current_time, state))

class FlipSignal(Signal):
  def __init__(self,
               name,
               initial_state):
    if initial_state is None:
      initial_state = Signal.LOW
    super().__init__(name, initial_state)
      
    self.states = [ Signal.LOW, Signal.HIGH ]
    self.delay = 0

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
    super().__init__(name, initial_state)
      
    if states is not None:
      self.states = states

    
    if not period and not frequency:
      raise ValueError("One of Period or Frequency has to be specified")
    if period and frequency:
      raise ValueError("Only one of Period or Frequency can be specified")
    if frequency:
      period = 1 / frequency
    self.period = period

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
               initial_state=None,
               old_state_trigger=Signal.LOW,
               new_state_trigger=Signal.HIGH,
               states=None):
    super().__init__(name, initial_state=initial_state)
      
    if states is not None:
      self.states = states
    self.old_state_trigger = old_state_trigger
    self.new_state_trigger = new_state_trigger

  def tick(self, current_time):
    super().tick(current_time)
    old_state, new_state = super()._flip()

    self._save(current_time, new_state)
    return old_state, new_state, None

  def context(self, s_name, old_state, new_state, current_time, next_time):
    if (old_state == self.old_state_trigger and
        new_state == self.new_state_trigger):
      trigger_time = current_time
      if self.delay is not None:
        if isinstance(self.delay, dict):
          trigger_time += self.delay[self.state]
        else:
          trigger_time += self.delay
          
      self.causes.append(_Cause(orig_name=s_name, orig_time=current_time,
                                event_name=self.name, event_time=trigger_time))
      return trigger_time
    return None

class ParameterSignal(FlipSignal):
  def __init__(self, name,
               true_state,
               initial_state=None,
               states=None):
    super().__init__(name, initial_state=initial_state)
    if states is not None:
      self.states = states

    self.dependencies = list(true_state.keys())
    self.dependency_states = dict()
    self.true_state = true_state
    self.current_state = False
    self.cause = _Cause()
    

  def tick(self, current_time):
    super().tick(current_time)
    old_state, new_state = super()._flip()

    self._save(current_time, new_state)
    return old_state, new_state, None

  def context(self, s_name, old_state, new_state, current_time, next_time):
    self.dependency_states[s_name] = new_state
    self.cause.add_cause(s_name, current_time)
    true_state = self._check_state()
    if true_state != self.current_state:
      trigger_time = current_time
      if self.delay is not None:
        if isinstance(self.delay, dict):
          trigger_time += self.delay[self.state]
        else:
          trigger_time += self.delay
          
      self.cause.add_event(self.name, trigger_time)
      self.causes.append(self.cause)
      self.cause = _Cause()
      self.current_state = true_state
      return trigger_time
     
    
  def set_dependency_state(self, name, value):
    self.dependency_states[name] = value
    self.current_state = self._check_state()
    
  def _check_state(self):
    for name, state in self.true_state.items():
      if name not in self.dependency_states:
        return False
      if self.dependency_states[name] != self.true_state[name]:
        return False

    return True

class _Cause():
  def __init__(self,
               orig_name=None,
               orig_time=None,
               event_name=None,
               event_time=None):
    self.dependencies = {}
    if orig_name is not None and orig_time is not None:
      self.dependencies[orig_name] = orig_time
    if event_name is not None and event_time is not None:
      self.event = (event_name, event_time)

  def add_cause(self, name, time):
    self.dependencies[name] = time

  def add_event(self, name, time):
    self.event = (name, time)



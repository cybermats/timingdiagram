from heapq import heappush, heappop
import itertools

class Signal():
  UNDEFINED="UNDEFINED"
  HIGH="HIGH"
  LOW="LOW"
  IMPEDANCE="IMPEDANCE"
  DATA="DATA"

  def __init__(self, name,
               initial_state=UNDEFINED,
               dependencies=None):
    self.name = name
    self.state = initial_state
    self.dependencies = dependencies
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
               states,
               dependencies=None):
    if not initial_state:
      initial_state = Signal.LOW
    if not states:
      states = [Signal.LOW, Signal.HIGH]

    self.states = states
    super().__init__(name,
                     initial_state=initial_state,
                     dependencies=dependencies)

  def _flip(self):
    old_state = self.state
    old_location = self.states.index(old_state)
    new_location = (old_location + 1) % len(self.states)
    new_state = self.states[new_location]
    self.state = new_state
    return old_state, new_state

class TickerSignal(FlipSignal):
  def __init__(self, name, initial_state=None, states=None,
               period=None, frequency=None,
               dependencies=None):
    if not period and not frequency:
      raise ValueError("One of Period or Frequency has to be specified")
    if period and frequency:
      raise ValueError("Only one of Period or Frequency can be specified")
    if frequency:
      period = 1 / frequency
    self.period = period
    super().__init__(name, initial_state, states,
                     dependencies=dependencies)

  def tick(self, current_time):
    super().tick(current_time)
    old_state, new_state = super()._flip()
    next_time = current_time + (self.period / 2)
    self._save(current_time, new_state)
    return old_state, new_state, next_time

  def first_tick(self):
    return self.period/2

class CounterSignal(FlipSignal):
  def __init__(self, name, initial_state=None, states=None, dependencies=None):
    super().__init__(name, initial_state, states,
                     dependencies=dependencies)

  def tick(self, current_time):
    super().tick(current_time)
    old_state, new_state = super()._flip()

    self._save(current_time, new_state)
    return old_state, new_state, None

  def context(self, s_name, old_state, new_state, current_time, next_time):
    if old_state == Signal.LOW and new_state == Signal.HIGH:
      return current_time
    return None

class SignalCollection():
  def __init__(self):
    self.all = {}
    self.dependent = {}
    self.heap = SignalHeap()

  def add(self, signal):
    if signal.name in self.all:
      raise RuntimeError("Signal with the same name already exists.")
    self.all[signal.name] = signal
    if signal.name in self.dependent:
      raise KeyError(
        "signal with the same name already exists in dependencies.")
    self.dependent[signal.name] = []
    if signal.dependencies is None:
      self.heap.add_signal(signal, time=signal.first_tick())
    else:
      for dependency in signal.dependencies:
        if not dependency in self.dependent:
          raise KeyError("All dependencies has not been registred.")
        self.dependent[dependency].append(signal)

  def tick(self):
    current_time, s = self.heap.pop_signal()
    old_state, new_state, next_time = s.tick(current_time)
    if next_time:
      self.heap.add_signal(s, next_time)
    for dependency in self.dependent[s.name]:
      next_dependency_time = dependency.context(
          s.name, old_state, new_state, current_time, next_time)
      if next_dependency_time:
        self.heap.add_signal(dependency, next_dependency_time)


class SignalHeap():
  def __init__(self):
    self.pq = []
    self.entry_finder = {}
    self.REMOVED = '<removed-task>'
    self.counter = itertools.count()

  def add_signal(self, signal, time=0):
    if signal in self.entry_finder:
      self.remove_signal(signal)
    count = next(self.counter)
    entry = [time, count, signal]
    self.entry_finder[signal] = entry
    heappush(self.pq, entry)

  def remove_signal(self, signal):
    entry = self.entry_finder.pop(signal)
    entry[-1] = self.REMOVED

  def pop_signal(self):
    while self.pq:
      time, count, signal = heappop(self.pq)
      if signal is not self.REMOVED:
        del self.entry_finder[signal]
        return time, signal
    raise KeyError('pop from an empty priority queue')

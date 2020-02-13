from heapq import heappush, heappop

class SignalHeap():
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

  def pop_signal():
    while self.pq:
      time, count, signal = heappop(self.pq)
      if signal is not self.REMOVED:
        del self.entry_finder[signal]
        return time, signal
    raise KeyError('pop from an empty priority queue')

class Signal():
  UNDEFINED="UNDEFINED"

  def __init__(self, name, initial_state=Signal.UNKNOWN, dependencies=None):
    self.state = initial_state
    self.name = name
    self.dependencies = dependencies

  def tick(self, current_time):
    pass

  def context(self, s_name, old_state, new_state, next_time):
    pass

class TickerSignal(Signal):
  def __init__(self, initial_state, states, period=None, frequency=None,
               dependencies=None):
    if not period or not frequency:
      raise ValueError("One of Period or Frequency has to be specified")
    if period and frequency:
      raise ValueError("Only one of Period or Frequency can be specified")
    if frequency:
      period = 1 / frequency
    self.period = period
    self.states = states
    super.__init__(self, initial_state=initial_state,
                   dependencies=dependencies)

  def tick(self, current_time):
    super().tick(self, current_time)
    old_state = self.state
    old_location = self.states.index(old_state)
    new_location = (old_location + 1) % len(self.states)
    new_state = self.states[new_location]
    self.state = new_state
    next_time = current_time + (self.period / 2)
    return old_state, new_state, next_time


class SignalCollection():
  def __init__(self):
    self.all = {}
    self.dependent = {}
    self.heap = SignalHeap()

  def add(self, signal, dependencies = None):
    if signal.name() in self.all:
      raise RuntimeError("Signal with the same name already exists.")
    self.all[name] = signal
    if dependencies is None:
      self.heap.add_signal(signal)
    else:
      for dependency in dependencies:
        if not dependency in self.dependent:
          self.dependent[dependency] = []
        self.dependent[dependency].append(signal)

  def tick():
    current_time, s = self.heap.pop_signal()
    s_name = s.name()
    old_state, new_state, next_time = s.tick(current_time)
    self.heap.add_signal(s, next_time)
    for dependency in self.dependent[s_name]:
      next_dependency_time = dependency.context(
          s_name, old_state, new_state, next_time)
      if next_dependency_time:
        self.heap.add_signal(dependency, next_dependency_time)

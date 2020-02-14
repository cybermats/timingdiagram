from heapq import heappush, heappop
import itertools

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

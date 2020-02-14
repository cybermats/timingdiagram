from PIL import Image, ImageDraw, ImageFont
from signal import Signal


class Canvas:
    def __init__(self, width, height):
        self.height = 40
        self.h_spacing = 60
        self.v_spacing = 40
        self.start = 40
        self.time_multiplier = 2
        self.slope_time = 2
        self.background = (255, 255, 255)
        self.foreground = (0, 0, 0)
        self.image = None
        self.draw = None

        self.font = ImageFont.truetype("arial.ttf", 15)

        self.signals = []
        self.oldest = None

    def add_signal(self, signal):
        name = signal.name
        history = signal.get_history()
        self.signals.append((name, history))

        age, _ = history[-1]
        if not self.oldest or self.oldest < age:
            self.oldest = age

    def render(self):
        width = int(self.h_spacing +
                    self.time_multiplier * self.oldest +
                    self.h_spacing)
        height = int(self.start + len(self.signals) *
                     (self.height + self.v_spacing))

        self.image = Image.new("RGB", (width, height), color=self.background)
        self.draw = ImageDraw.Draw(self.image)
        start = self.start
        for name, history in self.signals:
            size = self.draw.textsize(name, font=self.font)
            x = self.h_spacing - size[0]
            y = start + self.height/2 - (size[1]/2)
            self.draw.text((x, y), name, fill=self.foreground, font=self.font)

            xy = []
            prev_time = None
            prev_state = None
            prev_x = None
            prev_y = None
            prev_time = None
            for (curr_time, curr_state) in history:
              if curr_time:
                xy += self._get_shape(prev_time, prev_state,
                                     curr_time, curr_state)
              else:
                curr_time = 0

              prev_time = curr_time
              prev_state = curr_state

            if prev_time and prev_time < self.oldest:
              xy += self._get_shape(prev_time, prev_state,
                                   self.oldest, prev_state)

            if xy:
              xy = [(x + self.h_spacing, y + start) for
                    (x, y) in xy]
              self.draw.line(xy, fill=self.foreground)

            start = start + self.height + self.v_spacing

    def _get_shape(self, prev_time, prev_state, curr_time, curr_state):
      xy = []
      if prev_state is Signal.LOW and curr_state is Signal.HIGH:
        prev_x = prev_time * self.time_multiplier
        prev_y = self.height

        curr_x = curr_time * self.time_multiplier
        curr_y = 0

        xy = [(prev_x + self.slope_time, prev_y),
              (curr_x - self.slope_time, prev_y)]
        xy += [(curr_x - self.slope_time, prev_y),
               (curr_x + self.slope_time, curr_y)]
      elif prev_state is Signal.HIGH and curr_state is Signal.LOW:
        prev_x = prev_time * self.time_multiplier
        prev_y = 0

        curr_x = curr_time * self.time_multiplier
        curr_y = self.height

        xy = [(prev_x + self.slope_time, prev_y),
              (curr_x - self.slope_time, prev_y)]
        xy += [(curr_x - self.slope_time, prev_y),
               (curr_x + self.slope_time, curr_y)]
      elif prev_state == curr_state:
        if prev_state == Signal.LOW:
          prev_x = prev_time * self.time_multiplier
          prev_y = self.height
          curr_x = curr_time * self.time_multiplier
          curr_y = self.height

          xy = [(prev_x + self.slope_time, prev_y),
                (curr_x + self.slope_time, curr_y)]
        elif prev_state == Signal.HIGH:
          prev_x = prev_time * self.time_multiplier
          prev_y = 0
          curr_x = curr_time * self.time_multiplier
          curr_y = 0

          xy = [(prev_x + self.slope_time, prev_y),
                (curr_x + self.slope_time, curr_y)]

      return xy

    def show(self):
        self.image.show()

from PIL import Image, ImageDraw, ImageFont
from signals.signal import Signal


class Canvas:
    def __init__(self, data=None):
        self.height = 40
        self.h_spacing = 60
        self.v_spacing = 40
        self.start = 40
        self.time_multiplier = 2
        self.slope_time = 5
        self.background = (255, 255, 255)
        self.foreground = (0, 0, 0)
        self.linecolor = (64, 64, 255)
        self.font_file = "fonts/Roboto-Regular.ttf"
        self.font_size = 15

        if data:
            if "height" in data:
                self.height = data["height"]
            if "h_spacing" in data:
                self.h_spacing = data["h_spacing"]
            if "v_spacing" in data:
                self.v_spacing = data["v_spacing"]
            if "start" in data:
                self.start = data["start"]
            if "time_multiplier" in data:
                self.time_multiplier = data["time_multiplier"]
            if "slope_time" in data:
                self.slope_time = data["slope_time"]
            if "background" in data:
                bg = data["background"]
                self.background = (bg[0], bg[1], bg[2])
            if "foreground" in data:
                fg = data["foreground"]
                self.foreground = (fg[0], fg[1], fg[2])
            if "linecolor" in data:
                c = data["linecolor"]
                self.linecolor = (c[0], c[1], c[2])
            if "font_file" in data:
                self.font_file = data["font_file"]
            if "font_size" in data:
                self.font_size = data["font_size"]

        self.font = ImageFont.truetype(self.font_file, self.font_size)

        self.image = None
        self.draw = None
        self.signals = []
        self.causes = []
        self.oldest = None

    def add_signal(self, signal):
        if not signal.visible:
            return
        name = signal.name
        history = signal.history
        self.signals.append((name, history))
        if signal.show_cause:
            for cause in signal.causes:
                self.causes.append(cause)

        age, _ = history[-1]
        if age is not None:
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
        starts = {}
        for name, history in self.signals:
            starts[name] = start
            size = self.draw.textsize(name, font=self.font)
            x = self.h_spacing - size[0]
            y = start + self.height/2 - (size[1]/2)
            self.draw.text((x, y), name, fill=self.foreground, font=self.font)

            lines = []
            prev_time = None
            prev_state = None
            for (curr_time, curr_state) in history:
                if curr_time:
                    lines += self._get_shape(prev_time, prev_state,
                                     curr_time, curr_state)
                else:
                    curr_time = 0

                prev_time = curr_time
                prev_state = curr_state

            if prev_time and prev_time < self.oldest:
                lines += self._get_shape(prev_time, prev_state,
                                         self.oldest, prev_state,
                                         last=True)

            for line in lines:
              line = [(x + self.h_spacing, y + start) for
                      (x, y) in line]
              self.draw.line(line, fill=self.foreground)

            start = start + self.height + self.v_spacing

        cause_lines = []
        for cause in self.causes:
            name, time = cause.event
            if name not in starts:
                continue
            if time >= self.oldest:
                continue
            end_x = time * self.time_multiplier + self.h_spacing
            end_y = starts[name] + self.height/2

            for d_name, d_time in cause.dependencies.items():
                if d_name not in starts:
                    continue
                start_x = d_time * self.time_multiplier + self.h_spacing
                start_y = starts[d_name] + self.height/2
                cause_lines.append([(start_x, start_y), (end_x, end_y)])
        for line in cause_lines:
            self.draw.line(line, fill=self.linecolor)

    def _get_shape(self, prev_time, prev_state, curr_time, curr_state, last=False):
      lines = []
      #
      # Transition from LOW to HIGH
      #
      if prev_state == Signal.LOW and curr_state == Signal.HIGH:
        prev_x = prev_time * self.time_multiplier
        prev_y = self.height

        curr_x = curr_time * self.time_multiplier
        curr_y = 0

        lines.append([(prev_x + self.slope_time, prev_y),
              (curr_x - self.slope_time, prev_y)])
        lines.append([(curr_x - self.slope_time, prev_y),
               (curr_x + self.slope_time, curr_y)])
      #
      # Transition from HIGH to LOW
      #
      elif prev_state == Signal.HIGH and curr_state == Signal.LOW:
        prev_x = prev_time * self.time_multiplier
        prev_y = 0

        curr_x = curr_time * self.time_multiplier
        curr_y = self.height

        lines.append([(prev_x + self.slope_time, prev_y),
              (curr_x - self.slope_time, prev_y)])
        lines.append([(curr_x - self.slope_time, prev_y),
               (curr_x + self.slope_time, curr_y)])
      #
      # Transition from UNDEFINED to DATA
      #
      elif prev_state == Signal.UNDEFINED and curr_state == Signal.DATA:
        prev_x = prev_time * self.time_multiplier
        curr_x = curr_time * self.time_multiplier

        # Box
        lines.append([(prev_x + self.slope_time, 0),
              (curr_x - self.slope_time, 0)])
        lines.append([(prev_x + self.slope_time, self.height),
              (curr_x - self.slope_time, self.height)])
        # Shadow
        for x in range(int(prev_x + self.slope_time),
                       int(curr_x - self.slope_time*2),
                       int(self.slope_time*2)):
          lines.append([(x, 0), (x + self.slope_time*2, self.height)])
          lines.append([(x, self.height), (x + self.slope_time*2, 0)])
        # Slope
        lines.append([(curr_x - self.slope_time, 0),
              (curr_x + self.slope_time, self.height)])
        lines.append([(curr_x - self.slope_time, self.height),
              (curr_x + self.slope_time, 0)])

      #
      # Transition from DATA to UNDEFINED
      #
      elif prev_state == Signal.DATA and curr_state == Signal.UNDEFINED:
        prev_x = prev_time * self.time_multiplier
        curr_x = curr_time * self.time_multiplier

        # Box
        lines.append([(prev_x + self.slope_time, 0),
              (curr_x - self.slope_time, 0)])
        lines.append([(prev_x + self.slope_time, self.height),
              (curr_x - self.slope_time, self.height)])
        # Slope
        lines.append([(curr_x - self.slope_time, 0),
              (curr_x + self.slope_time, self.height)])
        lines.append([(curr_x - self.slope_time, self.height),
              (curr_x + self.slope_time, 0)])


      #
      # Change of DATA on the bus
      #
      elif prev_state == Signal.DATA and curr_state == Signal.DATA and not last:
        prev_x = prev_time * self.time_multiplier
        curr_x = curr_time * self.time_multiplier

        # Box
        lines.append([(prev_x + self.slope_time, 0),
              (curr_x - self.slope_time, 0)])
        lines.append([(prev_x + self.slope_time, self.height),
              (curr_x - self.slope_time, self.height)])
        # Slope
        lines.append([(curr_x - self.slope_time, 0),
              (curr_x + self.slope_time, self.height)])
        lines.append([(curr_x - self.slope_time, self.height),
              (curr_x + self.slope_time, 0)])


      #
      # Transition from the same states
      #
      elif prev_state == curr_state:
        if prev_state == Signal.LOW:
          prev_x = prev_time * self.time_multiplier
          prev_y = self.height
          curr_x = curr_time * self.time_multiplier
          curr_y = self.height

          lines.append([(prev_x + self.slope_time, prev_y),
                (curr_x + self.slope_time, curr_y)])
        elif prev_state == Signal.HIGH:
          prev_x = prev_time * self.time_multiplier
          prev_y = 0
          curr_x = curr_time * self.time_multiplier
          curr_y = 0

          lines.append([(prev_x + self.slope_time, prev_y),
                (curr_x + self.slope_time, curr_y)])

        elif prev_state == Signal.DATA:
          prev_x = prev_time * self.time_multiplier
          curr_x = curr_time * self.time_multiplier

          # Box
          lines.append([(prev_x + self.slope_time, 0),
                        (curr_x - self.slope_time, 0)])
          lines.append([(prev_x + self.slope_time, self.height),
                        (curr_x - self.slope_time, self.height)])

        elif prev_state == Signal.UNDEFINED:
          prev_x = prev_time * self.time_multiplier
          curr_x = curr_time * self.time_multiplier

          # Box
          lines.append([(prev_x + self.slope_time, 0),
                        (curr_x - self.slope_time, 0)])
          lines.append([(prev_x + self.slope_time, self.height),
                        (curr_x - self.slope_time, self.height)])
          # Shadow
          for x in range(int(prev_x + self.slope_time),
                         int(curr_x - self.slope_time*2),
                         int(self.slope_time*2)):
            lines.append([(x, 0), (x + self.slope_time*2, self.height)])
            lines.append([(x, self.height), (x + self.slope_time*2, 0)])

      return lines

    def show(self):
        self.image.show()

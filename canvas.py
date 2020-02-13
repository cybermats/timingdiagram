from PIL import Image, ImageDraw
from signal import Signal


class Canvas:
    def __init__(self, width, height):
        self.height = 40
        self.h_spacing = 40
        self.v_spacing = 40
        self.start = 40
        self.time_multiplier = 2
        self.slope_time = 2
        self.background = (255, 255, 255)
        self.foreground = (0, 0, 0)
        self.image = None
        self.draw = None

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
        width = int(self.h_spacing + self.v_spacing +
                    self.time_multiplier * self.oldest + self.v_spacing)
        height = int(self.start + len(self.signals) *
                     (self.height + self.v_spacing))
        
        self.image = Image.new("RGB", (width, height), color=self.background)
        self.draw = ImageDraw.Draw(self.image)
        start = self.start
        for name, history in self.signals:
            size = self.draw.textsize(name)
            x = self.h_spacing - size[0]
            y = start + self.height/2 - (size[1]/2)
            self.draw.text((x, y), name, fill=self.foreground)

            xy = []
            prev_x = None
            prev_y = None
            prev_time = None
            for (time, state) in history:
                x = self.h_spacing
                y = start
                if state is Signal.LOW:
                    y += self.height
            
                if time:
                    x += self.time_multiplier * time
                    xy += [prev_x + self.slope_time,prev_y,
                           x - self.slope_time, prev_y]
                    xy += [x - self.slope_time, prev_y,
                           x + self.slope_time, y]
                    prev_time = time

                prev_x = x
                prev_y = y

            if prev_time and prev_time < self.oldest:
                x = self.h_spacing + self.time_multiplier * self.oldest
                xy += [prev_x + self.slope_time, prev_y,
                       x, prev_y]

            if xy:
                self.draw.line(xy, fill=self.foreground)
        
            start = start + self.height + self.v_spacing

        

    def show(self):
        self.image.show()

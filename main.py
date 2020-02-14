from signals.signal import TickerSignal, CounterSignal, Signal
from signals.utils import SignalCollection
from signals.json import deserialize
from canvas import Canvas
import json

def main(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    if "signals" not in data:
        raise ValueError("Input file malformed. Missing 'signals'.")
    if "canvas" not in data:
        raise ValueError("Input file malformed. Missing 'canvas'.")

    signals = deserialize(data["signals"])

    sc = SignalCollection()
    for signal in signals:
        sc.add(signal)

    until_time=600
    if "time" in data:
        until_time = data["time"]
    
    while sc.tick(until_time):
        continue

    cvs = Canvas(data["canvas"])
    for signal in signals:
        cvs.add_signal(signal)
        
    cvs.render()
    cvs.show()

if __name__ == "__main__":
    main("tickers.json")



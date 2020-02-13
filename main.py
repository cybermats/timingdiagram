from signal import TickerSignal, SignalCollection, CounterSignal
from canvas import Canvas

def main():
    ts = TickerSignal("CLK", period=40)
    cs = CounterSignal("CNTR", dependencies=["CLK"])
    cs2 = CounterSignal("CNTR2", dependencies=["CNTR"])
    sc = SignalCollection()
    sc.add(ts)
    sc.add(cs)
    sc.add(cs2)
    next_time = 0
    for _ in range(20):
        sc.tick()

    cvs = Canvas(256, 256)
    cvs.add_signal(ts)
    cvs.add_signal(cs)
    cvs.add_signal(cs2)
    cvs.render()
    cvs.show()
    print(ts.name)
    print(ts.get_history())
    print(cs.name)
    print(cs.get_history())
    print(cs2.name)
    print(cs2.get_history())


if __name__ == "__main__":
    main()



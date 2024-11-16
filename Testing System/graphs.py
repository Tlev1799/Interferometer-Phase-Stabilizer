import matplotlib.pyplot as plt

DEFAULT_PAUSE_TIME = 0.02

class Graphs:
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.graph = None

    def prepare(self, x, y):
        self.graph, = self.ax.plot(x, y)

    def update(self, new_x, new_y, pause_time=DEFAULT_PAUSE_TIME):
        self.graph.set_xdata(new_x)
        self.graph.set_ydata(new_y)
        plt.draw()
        plt.pause(pause_time)

    def end_update(self):
        plt.ioff()
        plt.show()

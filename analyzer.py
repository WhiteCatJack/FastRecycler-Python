import matplotlib.pyplot as plt


class Data:
    def __init__(self, garbage_record_manager):
        self.data_manager = garbage_record_manager
        self.time_series = self.data_manager.garbage_record_time_series

    def show_graph(self):
        self.time_series.plot()
        plt.show()

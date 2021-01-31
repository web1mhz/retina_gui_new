
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

# class MplCanvas(FigureCanvasQTAgg):

#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#         super(MplCanvas, self).__init__(fig)


class matplotlibWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())
        toolbar = NavigationToolbar(self.canvas, self)
        vertical_layout=QVBoxLayout()
        vertical_layout.addWidget(toolbar) 
        vertical_layout.addWidget(self.canvas)
        vertical_layout.setContentsMargins(1,1,1,1)
        self.canvas.axes=self.canvas.figure.add_subplot(1,1,1)
        self.canvas.axes.grid()


        # self.canvas.axes=self.canvas.figure.add_subplot(1,2,2)
        # self.canvas.axes.grid()
        widget = self.setLayout(vertical_layout)
        
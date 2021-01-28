
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class matplotlibWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())
        vertical_layout=QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        vertical_layout.setContentsMargins(1,1,1,1)
        self.canvas.axes=self.canvas.figure.add_subplot(1,1,1)
        self.canvas.axes.grid()


        # self.canvas.axes=self.canvas.figure.add_subplot(1,2,2)
        # self.canvas.axes.grid()

        self.setLayout(vertical_layout)
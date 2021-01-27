import sys
import pandas as pd
from PyQt5.QtWidgets import *

from ui_py.graph_viewer_ui import Ui_Dialog

class graphDisplay(QDialog, Ui_Dialog):
    def __init__(self, csv_file):
        super().__init__() 

        self.setupUi(self)

        self.csv_file = csv_file

        # self.readCSV()       

        self.graphButton.clicked.connect(self.show_graph)
        self.imgprintButton.clicked.connect(self.save)

    def readCSV(self):
        df =pd.read_csv(self.csv_file)
        print(df)


    def show_graph(self):
        QMessageBox.about(self, '굿', '굿')

        df =pd.read_csv(self.csv_file)        

        label_cnt = df['label'].value_counts()
        
        x_list = label_cnt.index
        y_list = label_cnt        

        # bar, plot
        # x_list =['a']
        # y_list =[10]

        # errorbar
        # x_list = [1,2,3,4,5,6,]
        # y_list =[10,20,30,40,50,60]
        # y_err = [-1, 10, -30,-1,5,-5]
        # data_name ='ktg'


        self.graphViewer.canvas.axes.bar(x_list, y_list)
        self.graphViewer.canvas.axes.plot(x_list, y_list)  
        # self.graphViewer.canvas.axes.errorbar(x_list, y_list, yerr=y_err, label=data_name)              
        self.graphViewer.canvas.axes.legend()
        self.graphViewer.canvas.axes.set_xlabel('class name')
        self.graphViewer.canvas.axes.set_ylabel('count')
        self.graphViewer.canvas.draw()

    def save(self):
        pix = self.graphViewer.grab()
        filename=QFileDialog.getSaveFileName(self)[0]
        pix.save(filename + '.png')


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 전체화면   
    w = graphDisplay() # 전체화면에 차지하는 영역
    w.show() # 전체화면에 차지하는 영역을 보여주고
    app.exec_() # 전체 화면 종료        
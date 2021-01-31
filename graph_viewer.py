import sys
import pandas as pd
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from ui_py.graph_viewer_ui import Ui_Dialog

class graphDisplay(QDialog, Ui_Dialog):
    def __init__(self, csv_file):
        super().__init__() 

        self.setupUi(self)

        self.csv_file = csv_file

        self.imgprintButton.setEnabled(False)

        # self.readCSV()       

        self.graphButton.clicked.connect(self.show_graph)
        self.imgprintButton.clicked.connect(self.save)
        self.exitgraphButton.clicked.connect(self.exitCall)        
        # self.exitgraphButton.clicked.connect(QtCore.QCoreApplication.instance().quit) # 프로그램 전체종료

    def readCSV(self):
        df =pd.read_csv(self.csv_file)
        print(df)


    def show_graph(self):
        # QMessageBox.about(self, '굿', '굿')

        df =pd.read_csv(self.csv_file)        

        label_cnt = df['label'].value_counts()
        label_cnt.sort_index(inplace = True)               
        
        cnt_x = label_cnt.index
        cnt_y = label_cnt

        grouped = df['accuracy'].groupby(df['label'])
        label_acc = grouped.mean()*100
        label_acc.sort_index(inplace=True) 

        acc_x = label_acc.index
        acc_y = label_acc       

        # bar, plot
        # x_list =['a']
        # y_list =[10]

        # errorbar
        # x_list = [1,2,3,4,5,6,]
        # y_list =[10,20,30,40,50,60]
        # y_err = [-1, 10, -30,-1,5,-5]

        data_name =['Detection Count', 'Accuracy'] 
        
        self.bar = self.graphViewer.canvas.axes.bar(cnt_x, cnt_y , label= data_name[0])
        self.rects = self.graphViewer.canvas.axes.plot(acc_x, acc_y, 'r--', label= data_name[1])  
        # self.graphViewer.canvas.axes.errorbar(x_list, y_list, yerr=y_err, label=data_name)              
        self.graphViewer.canvas.axes.legend()
        self.graphViewer.canvas.axes.set_xlabel('class name')
        self.graphViewer.canvas.axes.set_ylabel('count')
        self.graphViewer.canvas.draw()   
        
        self.imgprintButton.setEnabled(True)

    def save(self):
        pix = self.graphViewer.grab()       
        filename=QFileDialog.getSaveFileName(self,'Save Image Graph', '.', "Image Files (*.png *.jpeg)")[0]
        pix.save(filename)

    @pyqtSlot()
    def exitCall(self):  
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 전체화면

    # 자체파일 실행
    # csv_file = 'results\wildboar04_result_1611756037.csv'   
    # w = graphDisplay(csv_file) # 전체화면에 차지하는 영역
    # 자체파일 실행 끝

    w = graphDisplay() # 전체화면에 차지하는 영역
    w.show() # 전체화면에 차지하는 영역을 보여주고
    app.exec_() # 전체 화면 종료        
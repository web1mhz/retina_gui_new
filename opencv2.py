import cv2
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QDialog, QMessageBox, QFileDialog
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

from ui_py.result_view_v1_dialog import Ui_Dialog

class Worker(QThread): # 원본 동영상 디스플레이
    changePixmap = pyqtSignal(QImage)    
    def __init__(self, myvar):
        super().__init__()
        self.myvar = myvar
        self.scaled_size = QSize(461, 311)

    def run(self):        
        # cap = cv2.VideoCapture(0) # 웹캠 연결
        cap = cv2.VideoCapture(self.myvar) # 비디오 파일 연결      
        while True:
            ret, frame = cap.read()           
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(self.scaled_size, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

    def stop(self):
        self.working = False
        self.quit()
        self.wait(10) #5000ms = 5s              
            
class VideoDisplay(QDialog, Ui_Dialog):
    def __init__(self, origin_file, file_name):
        super().__init__() 

        self.setupUi(self)
        self.ofname =origin_file
        self.fname =file_name
        self.is_alive = False
        self.is_alive1 = False
        self.playButton.setEnabled=False

        self.initUI()

        self.playButton.clicked.connect(self.displayall)
        self.exitButton.clicked.connect(self.exitCall)

    @pyqtSlot()
    def displayall(self): 

        if not self.is_alive and not self.is_alive1:
            self.worker.stop()
            self.worker1.stop()
            self.initUI()
        else :
            return None            

        print('다시재생', self.is_alive, self.is_alive1)  

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.origin_label.setPixmap(QPixmap.fromImage(image))

    # 탐지 결과 동영상 연결
    @pyqtSlot(QImage)
    def setImage1(self, image):
        self.result_label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):   

        #self.fname, _ = QFileDialog.getOpenFileName(self, "Open Movie",'.', "Video Files (*.mp4 *.avi *.mov)")

        if self.ofname:
            self.worker = Worker(myvar=self.ofname) # 외부 쓰레드 선언
            self.is_alive = True
            self.display()             
        else:
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.")
            #sys.exit()

        # 탐지 결과 동영상 파일 이름    
        if self.fname:
            self.worker1 = Worker(myvar=self.fname) # 외부 쓰레드 선언
            self.is_alive1 = True            
            self.display1()             
        else:
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.")
            #sys.exit()            
              

    def display(self):        
        self.worker.changePixmap.connect(self.setImage) # 외부 쓰레드와 연결
        self.worker.start() # 외부 쓰레드 작동       
        self.worker.stop()
        self.is_alive = False
        self.playButton.setEnabled=True                

    # 탐지 결과 동영상 연결
    def display1(self):               
        self.worker1.changePixmap.connect(self.setImage1) # 외부 쓰레드와 연결
        self.worker1.start() # 외부 쓰레드 작동        
        self.worker1.stop()
        self.is_alive1 = False
        self.playButton.setEnabled=True    

    @pyqtSlot()
    def exitCall(self):
        self.close()

    # 디스플레이 쓰레드 종료
    def closeEvent(self, event):
        self.worker.stop()        
        self.worker.terminate()  # 외부 쓰레드 파괴하고

        self.worker1.stop()   
        self.worker1.terminate() # 외부 쓰레드 파괴하고
        print('쓰레드 파괴됨')       

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 전체화면   
    w = VideoDisplay() # 전체화면에 차지하는 영역
    w.show() # 전체화면에 차지하는 영역을 보여주고
    app.exec_() # 전체 화면 종료
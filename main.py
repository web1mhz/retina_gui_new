### 설치 패키지
# 설치확인 : pip show pytube
# 1. pip install pytube
# 2. pip install pyqt5
# 3. qt designer tool 사용
# 4. pip install PyQtWebEngine 
# QT 디자이너 경로 "G:\Anaconda3\Library\bin\designer.exe"
# They proposed a possibility: the backend of QMediaPlayer only supports avi format, not mp4 format.
# 코덱 설치가 필요
# K-Lite_Codec_Pack_1595_Basic.exe 실행

import os
import sys
import time
import cv2
import numpy as np
import pandas as pd
import datetime


from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDir, Qt, QUrl, QThread
from PyQt5.QtGui import QIcon


from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound
from PyQt5.QtMultimediaWidgets import QVideoWidget

# UI 호출
from ui_py.Main_ui import Ui_MainWindow # 1. ui를 py로 변환된 파일을 임포트해서

# 외부 라이브러리 호출
from lib.AuthDialog import AuthDialog
from lib.IntroWorker import IntroWorker
from ExeDialog import ExeDialog

class BaseWindow(QMainWindow, Ui_MainWindow): # 2. 여기에 임포트된 파일의 클래스를 불러오고
    def __init__(self):
        super().__init__()

        self.setupUi(self) # 3. setupUi(self) 함수를 호출하면 됨

         # 비디오 파일경로 초기화
        self.fileName=''
        self.fileName_result=''
        self.inputFile=''       


        # 프로그램 화면 설정
        self.setWindowTitle("KNPS DNN-Wildlife Detection Program")

        # 비디오 파일 실행 - playButton과 연결
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface) 
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.mediaPlayer.setVideoOutput(self.videowidget)        
                  

        # 비디오 파일 실행 - resultButton과 연결
        self.mediaPlayer_result = QMediaPlayer(None, QMediaPlayer.VideoSurface) 
        # self.mediaPlayer_result = QMediaPlayer(None, QMediaPlayer.StreamPlayback)      
        self.mediaPlayer_result.setVideoOutput(self.videowidget_result)

        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.resultButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # 비디오 플레이 슬라이더 바 초기값 설정
        self.horizontalSlider.setRange(0, 0)
        self.horizontalSlider_2.setRange(0, 0) 

        self.initLock()
        self.initIntroThread()  

        # 시그널 초기화 : 시그널은 버튼 등 유저인터페이스와 함수를 연결하는 것
        self.initSignal()            

    def initIntroThread(self):
        # worker 선언
        self.introObj = IntroWorker()
        # Thread 선언
        self.introThread = QThread()
        # worker를 Thread로 전환
        self.introObj.moveToThread(self.introThread)
        # 시그널 연결
        self.introObj.startMsg.connect(self.showIntroInfo)
        # Thread 시작 메소트 연결
        self.introThread.started.connect(self.introObj.playBgm)
        # Thread 시작
        self.introThread.start()


    def showIntroInfo(self, name, fileName):        
        self.showStatusMsg('노래출처:' + fileName)

    def initLock(self):        
        self.playButton.setEnabled(False)
        self.resultButton.setEnabled(False)
        self.predictButton.setEnabled(False)

    def initAuthActive(self):        
        # self.playButton.setEnabled(True)
        # self.resultButton.setEnabled(True)
        self.predictButton.setEnabled(True)
        self.exitButton.clicked.connect(QtCore.QCoreApplication.instance().quit) # 종료  


    def initSignal(self):
        self.loginButton.clicked.connect(self.authCheck) # 사용자 인증
        self.actionopen.triggered.connect(self.openFile) # 메뉴바 열기
        self.actionExit.triggered.connect(QtCore.QCoreApplication.instance().quit) # 종료
        self.playButton.clicked.connect(self.play) # 재생 버튼
        self.resultButton.clicked.connect(self.play_result) # 결과재생
        self.exitButton.clicked.connect(QtCore.QCoreApplication.instance().quit) # 종료

        # 학습예측 버튼 기능 연결 시작--------------------------------------------------------
        self.predictButton.clicked.connect(self.retinaExeDlg)
        # 예측 버튼 기능 연결 끝--------------------------------------------------------------

        # 비디오 관련 기능 버튼 시작 --------------------------------------------------------
        self.horizontalSlider.sliderMoved.connect(self.setPosition)
        self.horizontalSlider_2.sliderMoved.connect(self.setPosition)

        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)


        self.mediaPlayer_result.stateChanged.connect(self.mediaStateChanged_r)
        self.mediaPlayer_result.positionChanged.connect(self.positionChanged_r)
        self.mediaPlayer_result.durationChanged.connect(self.durationChanged_r)
        self.mediaPlayer_result.error.connect(self.handleError_r)
        # 비디오 관련 기능 버튼 끝 --------------------------------------------------------
   
 
    def exitCall(self):
        sys.exit(app.exec_())

    # 상황표시바 메시지 출력
    def showStatusMsg(self, msg):
        self.statusbar.showMessage(msg) 


    @pyqtSlot() # 명시적으로 slot임을 알려줌
    def authCheck(self):

        dlg = AuthDialog() # 외부 라이브러리 연결
        dlg.exec_() # 외부 라이브러리 실행(AuthDialog.py)

        # 메인과 호출되는 다이얼로그 변수연결해서 값을 전달.
        self.user_id = dlg.user_id
        self.user_pw = dlg.user_pw

        if self.user_id == 'knps' and self.user_pw == 'knps1234': # 아이디와 비밀번호 일치여부 확인
            
            self.initAuthActive()
            self.loginButton.setText('인증완료')
            self.loginButton.setEnabled(False) # 인증버튼 비활성화            

            self.showStatusMsg('로그인 성공')

        else:
            QMessageBox.about(self, '인증오류', ' 아이디 또는 비밀번호 인증오류')  


    @pyqtSlot()
    def retinaExeDlg1(self):
        self.tgDialog = ExeDialog()       
        self.tgDialog.exec_()
    
    @pyqtSlot()
    def retinaExeDlg(self):  
       
        exeDialog = ExeDialog()       
        exeDialog.exec_()                 

        self.fname = exeDialog.fname
        self.result_mp4 = exeDialog.result_mp4         

        if self.fname != '' and self.result_mp4 !='':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.fname)))
            self.playButton.setEnabled(True)
            self.mediaPlayer.play()
                  

        if self.fname != '' and self.result_mp4 !='':            
            self.mediaPlayer_result.setMedia(QMediaContent(QUrl.fromLocalFile(self.result_mp4)))
            self.resultButton.setEnabled(True)
            self.mediaPlayer_result.play()
               

    @pyqtSlot()
    def openFile(self):
        substring = ['image', 'output']        
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                '.', "Video Files (*.mp4 *.flv *.ts *.mts *.avi *.wmv *.mov)")       

        if self.fileName != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.fileName)))            
            self.mediaPlayer.play()                       
            self.playButton.setEnabled(True)        
           

        if self.fileName != '' and 'output' in self.fileName:
            self.fileName_result = os.path.splitext(self.fileName)[0].replace('output', 'result') + '.mp4'
            self.mediaPlayer_result.setMedia(QMediaContent(QUrl.fromLocalFile(self.fileName_result)))
            # self.mediaPlayer_result.play()           
            self.resultButton.setEnabled(True)
            

        print(os.path.splitext(self.fileName)[0].replace('image', 'result') + '.mp4')
        print(os.path.basename(self.fileName).replace('image', 'result'))   
        

    @pyqtSlot()   
    def play(self):    

        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:            
            self.mediaPlayer.pause()
            
        else:
            self.mediaPlayer.play()
                          

    @pyqtSlot()   
    def play_result(self):        

        if self.mediaPlayer_result.state() == QMediaPlayer.PlayingState:            
            self.mediaPlayer_result.pause()
            
        else:
            self.mediaPlayer_result.play()
            

    # 동영상 관련 파일은 스트림 형태이기때문에 @pyqtSlot()를 
    # 활성화 하면 state, position 등 관련 오류가 발생하는 것 같음
    #@pyqtSlot() 
    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.playButton.setText('')
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playButton.setText('')

    def mediaStateChanged_r(self, state):
        if self.mediaPlayer_result.state() == QMediaPlayer.PlayingState:
            self.resultButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.resultButton.setText('')
        else:
            self.resultButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.resultButton.setText('')
    
    #@pyqtSlot()
    def positionChanged(self, position):
        if self.mediaPlayer:
            self.horizontalSlider.setValue(position)

    def positionChanged_r(self, position):
        if self.mediaPlayer_result:
            self.horizontalSlider_2.setValue(position)

    #@pyqtSlot()
    def durationChanged(self, duration):
        if self.mediaPlayer:
            self.horizontalSlider.setRange(0, duration)

    def durationChanged_r(self, duration):
        if self.mediaPlayer_result:
            self.horizontalSlider_2.setRange(0, duration)

    #@pyqtSlot()
    def setPosition(self, position):
        if self.mediaPlayer:
            self.mediaPlayer.setPosition(position)

    def setPosition_r(self, position):
        if self.mediaPlayer_result:
            self.mediaPlayer_result.setPosition(position)
    
    #@pyqtSlot()
    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def handleError_r(self, position):
        self.resultButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer_result.errorString())


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    main = BaseWindow()
    main.show()
    app.exec_()

   



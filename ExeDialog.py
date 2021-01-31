import sys
import os
from pathlib import Path # 로그홈디렉토리 지정패키지
import time
import datetime
import cv2
import numpy as np
import pandas as pd
import math

import tensorflow as tf
import keras
from keras_retinanet import models
from keras_retinanet.models import backbone
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QByteArray, QDir, QThread, QTimer, QUrl, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QMovie

from opencv2 import VideoDisplay
from graph_viewer import graphDisplay


from ui_py.ExeDialog_ui_v1 import Ui_Dialog # 1. ui를 py로 변환된 파일을 임포트해서


class WorkerThread(QThread):   
    
    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)

    def run(self):
        time.sleep(5)

class LoadingScreen(QWidget):

    def __init__(self):       
        super().__init__()
        self.setFixedSize(64,64)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.label_animation = QLabel(self)
        
        self.movie = QMovie('resource/loading.gif')
             
      
    def startAnimation(self):        
        self.label_animation.setMovie(self.movie)
        self.movie.start()
        self.show()
             

    def stopAnimation(self):
        self.movie.stop()
        self.close()  

class ExeDialog(QDialog, Ui_Dialog): # 2. 여기에 임포트된 파일의 클래스를 불러오고
    def __init__(self, in_file):
        super().__init__()

        # 1. 화면구성
        self.setupUi(self) # 3. setupUi(self) 함수를 호출하면 됨

        # 2. 변수 선언

        self.fname=in_file
        self.result_mp4=''
        self.label_to_names_txt ='model/labels_to_names_seq.txt'
        self.eng_to_kor_txt = 'model/eng_to_kor.txt'

        # ====================================
        self.workerThread = WorkerThread()
        # ====================================  
              
        # self.loading_screen = LoadingScreen()
         
        # ---- 날짜 초기화 -------------------------------------------------------------------
        self.now = datetime.datetime.now()
        self.nowDatetime = self.now.strftime('%Y-%m-%d %H:%M:%S')

                
        # --------------------------야생동물 탐지 클래스명 변경----------------------------------
        # self.labels_to_names_seq = {0: 'marten',1:'raccoon',2:'waterdeer', 3:'wildboar', 4:'wildcat'} # 포유류 5종 wildlife5_xxxx
        # labels_to_names_seq = {0: 'marten',1:'waterdeer', 2:'wildboar', 3:'wildcat'} # 포유류 4종 wildlife4_xxxx
        # labels_to_names_seq = {0: 'marten',1:'waterdeer', 2:'wildboar'} # 포유류 3종 wildlife3_xxxx
        # labels_to_names_seq = {0: 'raccoon',1:'wildcat'} # 포유류 2종 wildlife2_xxxx
        # self.labels_to_names_seq = {0: 'wildboar'}
        # --------------------------클래스명 변경---------------------------------------------- 

        # 기준경로 설정 * 필수 : 경로오류가 안나오게 하려면------------------------------------------------------------------------
        self.bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname('main.py')))
        print(self.bundle_dir)
        # ------------------------------------------------------------------------------------

        # ---- 레티나넷 관련 초기화 ------------------------------------------------------------
        self.sess = self.get_session()      

        self.retinanet_init()

        # ---- 위젯 초기화 -------------------------------------------------------------------
        self.toolInputButton.setEnabled(False)
        self.inputlineEdit.setEnabled(False)
        self.savetolineEdit.setEnabled(False)
        self.runExeButton.setEnabled(False)
        self.logOutputButton.setEnabled(False)
        self.exitButtonDlg.setEnabled(False)
        self.radioButton_2.setEnabled(False)
        self.radioButton_3.setEnabled(False)

        # 3. 버튼과 기능 연결 -----------------------------------------------------------------
        
        if self.fname != '':
            self.exit_file()
        else :
            self.toolInputButton.clicked.connect(self.input_file)
        self.toolSaveButton.clicked.connect(self.save_file)
        self.runExeButton.clicked.connect(self.retina_predict)
        self.exitButtonDlg.clicked.connect(self.exitCall)
        self.logOutputButton.clicked.connect(self.saveResults)        

        
    # 텐셔플로우 섹션 초기화 -----------------------------------------------------------------
    def get_session(self):        
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True 
        sess = tf.Session(config=config)
        keras.backend.tensorflow_backend.set_session(sess)
        return sess

    def retinanet_init(self):

        # self.loading_screen.startAnimation()

        # 클래스 이름 불러오기         
        self.labels_to_names_seq = self.labels_to_names(self.label_to_names_txt)     

        model = 'model/retina7_model.h5'
        # self.bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname('main.py')))
        self.data_path = os.path.abspath(os.path.join(self.bundle_dir, model))
        self.model_path = self.data_path
        self.retina_model = models.load_model(self.model_path, backbone_name='resnet50')

        # self.loading_screen.stopAnimation()

    
    def labels_to_names(self, path):    
        d = {}
        with open(path, encoding='utf-8') as f:
            for line in f:
                (key, val) = line.split(',')
                d[int(key)] = val.strip()        
        return d 


    def processData(self):
        self.workerThread.start()
        QMessageBox.information(self, '성공', '성공')


    # 버튼과 연결된 기능 @pyqtSlot() 관련 함수 시작

    def exit_file(self):

        if self.fname:           
            self.inputlineEdit.setText(self.fname)
            self.log_infile()
            self.toolSaveButton.setEnabled(True)
            self.runExeButton.setEnabled(True)

        else:
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.") 
            
    @pyqtSlot()
    def input_file(self):
        
        if self.fname =='':
            self.fname, _ = QFileDialog.getOpenFileName(self, "Open Movie",'.', "Video Files (*.mp4 *.avi *.mov)")

        if self.fname:           
            self.inputlineEdit.setText(self.fname)
            self.log_infile()
            self.toolSaveButton.setEnabled(True)
            self.runExeButton.setEnabled(True)
        else:
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.")

    @pyqtSlot()
    def save_file(self): #--------------------------------------------------내일 시작지점------------------------
        if self.fname !='':
            self.FILE_PREFIX = os.path.basename(self.fname).split('.')[0]
            self.created = str(math.ceil(time.time()))            
        else:
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.")
            return None

        self.results = QFileDialog.getExistingDirectory(self, 'Select Directory')
       
        if os.path.isdir(self.results):
            self.result_mp4 = os.path.join(self.results, self.FILE_PREFIX + '_result_' + self.created + '.mp4')           
            self.savetolineEdit.setText(self.result_mp4)
            self.log_savefile()
        else:
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.")

        
    
    @pyqtSlot()    
    def retina_predict(self):          
        self.runExeButton.setEnabled(False)
        self.append_log_msg('야생동물 탐지가 시작되었습니다.') 

        if self.radioButton:
            dict_name= self.labels_to_names(self.eng_to_kor_txt)
            classtype = dict_name.values()
            
            QMessageBox.about(self, "Info", "중대형포유류 탐지모델이 선택됨.\n" + str(list(classtype)))


        if self.fname and self.result_mp4:

            self.predict_results = self.detect_video_retina(self.retina_model, self.fname, self.result_mp4)

            self.logOutputButton.setEnabled(True)
        else:
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.")

    @pyqtSlot()
    def saveResults(self):

        self.start = time.time()  
        created_time = str(math.ceil(self.start))      

        if self.results and self.result is not None:
            # csv_path = os.path.join(self.results, created_time + '_result.csv')
            self.csv_path = os.path.join(self.results, self.FILE_PREFIX + '_result_' + self.created + '.csv')                           
            self.predict_results.to_csv(self.csv_path, index=False)
            self.append_log_msg(self.csv_path + ' 에 모델평가 결과 저장완료')
            self.exitButtonDlg.setEnabled(True)

            self.displayGraph()
        

    def displayGraph(self):

        graph = graphDisplay(self.csv_path) # 외부 라이브러리 연결
        graph.exec_() # 외부 라이브러리 실행(graphDisplay.py)

    
    @pyqtSlot()
    def exitCall(self):        
        self.sess.close()        
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '종료하시겠습니까?', '정말로?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            self.sess.close() 
        else:
            event.ignore() 

    def result_display(self, avg):
        QMessageBox.about(self,'예측완료: ', avg)

        # if self.result_mp4 !='':
        #     Vd = VideoDisplay(self.fname,self.result_mp4)
        #     Vd.exec_()
        # else:
        #     QMessageBox.about(self,'예측실패','다시 시도하세요')

    def file_info(self, filename):
        # 만든시간을 타임 스탬프로 출력
        ctime = os.path.getctime(filename)
        # 수정시간을 타임 스탬프로 출력
        mtime = os.path.getmtime(filename)
        # 마지막 엑세스시간을 타임 스탬프로 출력
        atime = os.path.getatime(filename)
        # 파일크기
        size = os.path.getsize(filename)

        real_ctime = datetime.datetime.fromtimestamp(ctime)
        real_mtime = datetime.datetime.fromtimestamp(mtime)
        reat_atime = datetime.datetime.fromtimestamp(atime)
        file_size = size/(1024*1024)

        #타임스탬프를 실제 시간으로 변경하기
        # print ('만든시간:', real_ctime)
        # print ('수정시간:',)
        # print ('마지막엑세스시간:', datetime.datetime.fromtimestamp(atime))
        # print ('파일크기', file_size)

        return real_ctime

    # 레티나넷 모델 예측 수행 시작지점 ==============================================================
    def detect_video_retina(self, model, input_path, output_path=""):

        start = time.time()

        # 1. 츨력정보 - 파일정보 ==============================================       
        real_ctime =self.file_info(input_path)        
        # 1. 츨력정보 - 파일정보 끝 ==========================================

        cap = cv2.VideoCapture(input_path)        
        codec = cv2.VideoWriter_fourcc(*'XVID')
        vid_fps = cap.get(cv2.CAP_PROP_FPS)
        vid_size= (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        vid_writer = cv2.VideoWriter(output_path, codec, vid_fps, vid_size)
        
        frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print('총 Frame 갯수:', frame_cnt) # 출력 1

        # 2. 출력정보 동영상 플레임 수 =====================================
        create_date = f'동영상 생성날짜: {real_ctime}'
        video_size = f'동영상 크기: {vid_size}'      
        frame_info = f'동영상 총 플레임 수: {frame_cnt}'         
        # 2. 출력정보 끝 ==================================================

        self.append_log_msg(create_date +'\n'+ video_size + '\n'+ frame_info)
         
        total_frame=frame_cnt       

        
        box_cnt_1=[]
        # name_1=[]
        # accuracy_1=[]
        # boxbnd_1=[]
        alls=[]        
        
        predict_results=pd.DataFrame()      

        
        while True: #frame_cnt > (total_frame - 3):

            hasFrame, image_frame = cap.read()
            if not hasFrame:
                print('프레임이 없거나 종료 되었습니다.')
                break

            detected_image, cnt, c_name, c_accuracy, c_boxbnd, all_ = self.get_detected_image_retina(model, image_frame, total_frame, frame_cnt, use_copied_array=False, is_print=True)
           
            print(cnt, "개 유형이 탐지됨")
            box_cnt_1.append(cnt)           
            # name_1.append(c_name)
            # accuracy_1.append(c_accuracy)
            # boxbnd_1.append(c_boxbnd)            
                      
            predict_results= predict_results.append(all_)

            frame_cnt-=1

            print(f"{frame_cnt}프레임, {frame_cnt/total_frame * 100 : .2f} % 남음")

            # 프로그레스바 처리 시작 ===============
            remain = frame_cnt/total_frame * 100
            progress = int(100-remain)
            self.exeProgressBar.setValue(progress)
            # 프로그레스바 처리 끝 =================            

            vid_writer.write(detected_image)

        
        names = ['label','accuracy','box_cnt','xmin','ymin', 'xmax', 'ymax']
        #names = ['label','accuracy','box_cnt','boxbnd']
        predict_results.columns = names        
        avg = np.array(predict_results['accuracy']).astype(np.float32)
        print(np.mean(avg))        
        cnt = predict_results.shape[0]

        cnt_by_label=predict_results['label'].value_counts(normalize=True)
        print(cnt_by_label.to_string())           


        vid_writer.release()
        cap.release()
        lapse_time = round(time.time()-start, 5)
        print('### Video Detect 총 수행시간:', lapse_time)
        min = int(lapse_time / 60)
        second = ((lapse_time / 60) - min) * 60 
        print(f"총 수행시간은 {min}분 {second :.0f}초 걸렸습니다.")

        # acc_avg = np.mean(np_accuracy_1)
        # sum_cnt = np.sum(np_cnt_1)
        result_str = f'탐지개체수 합: {cnt}: 탐지정확도:{np.mean(avg)*100 :.2f}' 
        
        # 모델예측결과 출력
        self.result_display(result_str)
        self.append_log_msg('=== 야생동물 유형별 탐지 정확도=====')
        self.append_log_msg(cnt_by_label.to_string())
                  

        return predict_results    

    def get_detected_image_retina(self, model, img_array, total_frame, frame_cnt, use_copied_array, is_print=True):       
    
        # copy to draw on
        draw_img = None
        if use_copied_array:
            draw_img = img_array.copy()
        else:
            draw_img = img_array
        
        img_array = preprocess_image(img_array)
        img_array, scale = resize_image(img_array)
        
        # process image
        start = time.time()
        # 모델 예측
        boxes, scores, labels = model.predict_on_batch(np.expand_dims(img_array, axis=0))        
        
        # correct for image scale
        boxes /= scale
        box_cnt_all=[]    
        box_cnt = 0
        boxbnd=[]
        accuracy=[]
        score_p=[]
        target_label=[]
        name=[]
        all_list=[]
        
        # visualize detections
        # box는 np.array 데이터 형식
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            # scores are sorted so we can break
            if score < 0.5:
                break

            color = label_color(label)            

            b = box.astype(int)

            # 물체탐지 박스 개수
            box_cnt+=1
            # box 경계 두께 지정
            linewidth = 5
            
            draw_box(draw_img, b, color=color,thickness=linewidth)
            
            score_percent = score * 100

            caption = "{} {:.1f}%".format(self.labels_to_names_seq[label], score_percent)
            
            acc = "{:.2f}%".format(score_percent)             
            
            # draw_caption(draw_img, b, caption)
            self.modified_draw_caption(draw_img, b, caption, color) 


            accuracy.append(acc) #### [99 99]
            score_p.append(score_percent)
            target_label.append(label) ### [wild wild]
            name.append(self.labels_to_names_seq[label]) ### [wild wild]
            boxbnd.append(b.tolist()) #### [1 1 1 1 2 2 2 2]
            box_cnt_all.append(box_cnt)

            if box is None:
                print('box_cnt', box_cnt)

            all_item = f'{self.labels_to_names_seq[label]},{score},{box_cnt}, {b[0]},{b[1]},{b[2]},{b[3]}' 
            # 탐지동물, 정확도, 탐지수, 박스영역좌표(xmin, ymin, xmax, ymax) 
            all_list.append(all_item.split(','))
        
        if is_print:
            # print("이미지 1장 processing 시간: ", round(time.time() - start,5))
            # print(f" 탐지된 유형은 {name}로 {box_cnt}개 입니다.")            
            # print(f" {name} 유형별 탐지정확도는 \n {accuracy}입니다.")
            pass 

        result_msg = f"{name} 탐지유형 수: {box_cnt}, 탐지정확도: {accuracy}, 처리시간:{round(time.time() - start,5)}"  

        self.append_log_msg(result_msg)

        # print(name) 
        # print(score_p)        
        # print(box_cnt_all)
        # print(boxbnd)
        # print(len(boxbnd))  

        # all_col = {'name': name, 'score:': score_p, 'box_cnt': box_cnt_all, 'xmin':boxbnd}
        # df = pd.DataFrame(all_col)
        # print(df)         
      
        return draw_img, box_cnt, name, score_p, boxbnd, all_list


    def modified_draw_caption(self, image, box, caption, color):
        """ Draws a caption above the box in an image."""
        b = np.array(box).astype(int)

        # getTextSize(글자, 글꼴, 크기, 두께)
        text_size = cv2.getTextSize(caption, cv2.FONT_HERSHEY_DUPLEX, 1, 1)
        text_length = text_size[0][0]
        text_height = text_size[0][1]

        # print(text_size)

        cv2.rectangle(image, (b[0], b[1] - text_height), (b[0] + text_length, b[1]), color, -1)
        cv2.putText(image, caption, (b[0], b[1]), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1)
    
    def append_log_msg(self, act):  

        app_msg = act + '- (' + self.nowDatetime + ')'        
        self.logPlainTextEdit.appendPlainText(app_msg) 

        # 활동 로그 저장(또는 DB를 사용 추천)
        home = Path.home()
        # log_path = os.path.join(os.getcwd(), 'log') # 현재 폴더 경로
        log_path = os.path.join(home, 'wd_log')
        log_dir = os.path.isdir(log_path)

        if not log_dir:
            os.mkdir(log_path)
        log_txt = os.path.join(log_path, 'log.txt')

        with open(log_txt, 'a') as f:
            f.write(app_msg+'\n')

    def log_infile(self):        
        self.mp4_size = os.path.getsize(self.fname)
        self.log_content = f'입력동영상 {self.fname} 파일이 선택했습니다.' + '\n'
        self.log_content = self.log_content + "파일크기(mb): " + str(self.mp4_size / (1024*1024))                
        self.append_log_msg(self.log_content)

    
    def log_savefile(self):
        self.runExeButton.setEnabled(True)        
        self.log_content = f'{self.result_mp4} 파일로 저장됩니다.'
        self.append_log_msg(self.log_content)

   
if __name__ == "__main__":    
    app = QApplication(sys.argv)

    # 자체파일 실행
    # in_file ='results\wildboar04_result_1611756679.mp4'
    # main = ExeDialog(in_file)
    # 자체파일 실행 끝

    main = ExeDialog()
    main.show()
    app.exec_()   



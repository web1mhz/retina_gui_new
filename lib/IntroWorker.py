import sys, os
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtMultimedia import QSound

# Thred는 반드시 QObject를 상속받아야 한다.

class IntroWorker(QObject):

    startMsg =pyqtSignal(str, str) # 메인쓰레드와 연결

    @pyqtSlot()
    def playBgm(self):
        # 바로 재생은 QSound.play()
        bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname('videoMain.py')))
        print(bundle_dir)
        data_path = os.path.abspath(os.path.join(bundle_dir, 'resource/intro.wav'))

        self.intro = QSound('resource/intro.wav')
        self.intro.play()
        self.startMsg.emit('Anoymouns', self.intro.fileName())

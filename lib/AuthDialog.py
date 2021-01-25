import sys
from PyQt5.QtWidgets import *

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()

        self.user_id = None
        self.user_pw = None

    def setupUi(self):
        # self.setGeometry(800, 500, 300, 100)
        self.setWindowTitle('로그인')
        self.setFixedSize(300, 100)

        label1 = QLabel('ID:')
        label2 = QLabel('Password:')

        self.lineEdit1 = QLineEdit() # 아이디
        self.lineEdit2 = QLineEdit() # 비밀번호
        self.lineEdit2.setEchoMode(QLineEdit().Password)



        self.pushButton = QPushButton('로그인') ## 버튼 함수 : 시그널
        self.pushButton.clicked.connect(self.submitLogin)


        layout = QGridLayout()
        layout.addWidget(label1, 0,0)
        layout.addWidget(self.lineEdit1, 0,1)
        layout.addWidget(self.pushButton, 0,2)
        layout.addWidget(label2, 1,0)
        layout.addWidget(self.lineEdit2, 1,1)

        self.setLayout(layout)

    def submitLogin(self):

        self.user_id = self.lineEdit1.text()
        self.user_pw = self.lineEdit2.text()

        # print(self.user_id, self.user_pw)

        if self.user_id is None or self.user_id == '' or not self.user_id:
            QMessageBox.about(self,'인증오류', 'ID를 입력하세요')
            self.lineEdit1.setFocus(True)
            return None

        if self.user_pw is None or self.user_pw == '' or not self.user_pw:
            QMessageBox.about(self,'인증오류', '비밀번호를 입력하세요')
            self.lineEdit2.setFocus(True)
            return None


        # 이 부분에서 필요한 경우 실제 로컬DB 또는 서버로 연동 후 
        # 유저 정보 및 사용 유효기간을 체크하는 코드를 입력하는 곳
        # code ...........
        # 또는 메인함수에서 해도 됨

        self.close()
        

if __name__ == "__main__":    
    app = QApplication(sys.argv)
    loginDialog = AuthDialog()
    loginDialog.show()

    app.exec_()
   



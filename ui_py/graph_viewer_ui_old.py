# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/graph_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from ui_py.matplotlibwidget import matplotlibWidget
# pyrcc5 bg.qrc -o bg_rc.py 를 실행해서 grc를 py로 변환해서 사용
import resource.bg_rc


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 500)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(600, 500))
        Dialog.setMaximumSize(QtCore.QSize(600, 500))
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(0, 0, 601, 61))
        font = QtGui.QFont()
        font.setFamily("KoPub돋움체 Bold")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAutoFillBackground(False)
        self.label.setStyleSheet("background-image: url(:/bg_top/desert.jpg);")
        self.label.setPixmap(QtGui.QPixmap("ui\\../resource/desert.jpg"))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.graphButton = QtWidgets.QPushButton(Dialog)
        self.graphButton.setGeometry(QtCore.QRect(140, 450, 161, 41))
        self.graphButton.setObjectName("graphButton")
        self.imgprintButton = QtWidgets.QPushButton(Dialog)
        self.imgprintButton.setGeometry(QtCore.QRect(310, 450, 121, 41))
        self.imgprintButton.setObjectName("imgprintButton")
        self.exitgraphButton = QtWidgets.QPushButton(Dialog)
        self.exitgraphButton.setGeometry(QtCore.QRect(510, 450, 81, 41))
        self.exitgraphButton.setObjectName("exitgraphButton")
        self.graphViewer = matplotlibWidget(Dialog)
        self.graphViewer.setGeometry(QtCore.QRect(0, 60, 601, 381))
        self.graphViewer.setObjectName("graphViewer")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "야생동물 AI 탐지 결과"))
        self.graphButton.setText(_translate("Dialog", "그래프 작성"))
        self.imgprintButton.setText(_translate("Dialog", "이미지 출력"))
        self.exitgraphButton.setText(_translate("Dialog", "종료"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
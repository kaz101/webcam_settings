#! /usr/bin/env python3

# Import the reqired modules
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QApplication
import subprocess
import PyQt5
import os
import cam_settings
import sys

class Webcam_settings(QtWidgets.QMainWindow, cam_settings.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Webcam_settings, self).__init__(parent)
        self.setupUi(self)
        self.webcams = get_webcams()
        self.ctrls_names = []
        self.object_list = []
        self.ctrls = {}
        self.nothing, self.webcams_keys = get_controls(self.webcams,0)
        for i in self.webcams_keys:
            self.device_box.addItem(i)
        self.device_box.setCurrentIndex(0)
        self.device_box.currentIndexChanged.connect(lambda: self.populate_settings())
        self.populate_settings()

    def clear_layout(self):
        try:
            print(self.object_list[0])
            self.verticalLayout_2.removeWidget(self.object_list[0])
        except IndexError:
            pass

    def populate_settings(self):
        for i in self.object_list:
            i.delete()

        #self.ctrls.clear()
        self.ctrls, self.webcams_keys = get_controls(self.webcams,self.device_box.currentIndex())
        #self.ctrls_names.clear()
        self.ctrls_names = list(self.ctrls)
        for i in self.ctrls_names:
            self.Sliders = Sliders(i, self.ctrls,self.webcams_keys[self.device_box.currentIndex()])
            self.object_list.append(self.Sliders)
            self.verticalLayout_2.addLayout(self.Sliders.layout)
        self.current_webcam_label.setText(self.webcams[self.webcams_keys[self.device_box.currentIndex()]])

class Sliders(QtWidgets.QWidget):
    def __init__(self,name, ctrls,current_cam, parent=None):
        self.layout = QtWidgets.QHBoxLayout()

        self.spacer = QtWidgets.QSpacerItem(100,1,QtWidgets.QSizePolicy.Preferred)
        self.spacer1 = QtWidgets.QSpacerItem(44,10,QtWidgets.QSizePolicy.Expanding)

        self.default = QtWidgets.QPushButton()
        self.default.setText('Reset')
        self.default.clicked.connect(lambda: set_ctrl(current_cam,name,int(ctrls[name]['default'])))

        self.label = QtWidgets.QLabel()
        self.label.setText(name.capitalize().replace('_',' '))
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding , QtWidgets.QSizePolicy.Expanding)
        self.label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.label.setFont(QtGui.QFont('Times',13))

        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.slider.setValue((int(ctrls[name]['value'])))
        try:
            self.slider.setMinimum(int(ctrls[name]['min']))
            self.slider.setMaximum(int(ctrls[name]['max']))
        except KeyError:
            pass
        self.slider.valueChanged.connect(lambda: set_ctrl(current_cam,name,self.slider.value()))
        self.layout.addWidget(self.label)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.slider)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.default)

    def delete(self):
        print('deleting')
    #    self.layout.removeWidget(self.label)
    #    self.layout.removeItem(self.spacer)
    #    self.layout.removeWidget(self.slider)
    #    self.layout.removeItem(self.spacer)
    #    self.layout.removeWidget(self.default)
        del self.layout



def get_webcams():
    devices = subprocess.run(['v4l2-ctl','--list-devices'],capture_output=True)
    devices_list = devices.stdout.decode()
    devices_list = devices_list.split('\n')
    webcams = {}
    for i in devices_list:
        if not '/dev' in i and i:
            webcams[devices_list[devices_list.index(i)+1].strip()] = i.strip()
    return webcams

def get_controls(webcams,index):

    webcams_keys = list(webcams.keys())
    ctrls_list = subprocess.run(['v4l2-ctl','-d',webcams_keys[index],'--list-ctrls'],capture_output=True)
    ctrls_list = ctrls_list.stdout.decode().split('\n')
    ctrls = {}
    for i in ctrls_list:
        i = i.split()
        try:
            ctrls[i[0].strip()] = i[4:]
        except IndexError:
            continue
    for key, value in ctrls.items():
            settings = {}
            for i in value:
                i = i.split('=')
                settings[i[0]] = i[1]
                ctrls[key] = settings
    return ctrls, webcams_keys

def set_ctrl(webcam,control,value):
    print(webcam)
    print(value)
    print(control)
    os.popen(f'v4l2-ctl -d {webcam} --set-ctrl={control}={value}')


def main():
    app = QApplication(sys.argv)
    form = Webcam_settings()
    form.show()
    app.exec_()
if __name__ == '__main__':
    main()

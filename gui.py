import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QHBoxLayout,QVBoxLayout, QGridLayout, QLabel
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore
 
class App(QWidget):
 
    def __init__(self, width, height):
        super().__init__()
        self.title = 'User Alignment Anontator'
        self.left = 0
        self.top = 0
        self.width = width
        self.height = height

        self.anotatons = {}
        self.data = [{'left_clients': range(19), 'right_clients': range(7)}, {'left_clients': range(4), 'right_clients': range(8)}, {'left_clients': range(4), 'right_clients': range(4)}]
        self.curr_anot_idx = 0

        self.left_buttons_dic = {}
        self.right_buttons_dic = {}
        self.last_clicked_button = None
        self.initUI()
     
    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.start_btn = QPushButton('Start Anotation', self) 
        self.start_btn.clicked.connect(self.start_on_click)
        self.grid = QGridLayout()
        self.grid.addWidget(self.start_btn, 0, 0) 
        self.start_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setLayout(self.grid)    
        
        self.show()

    def start_on_click(self):

        left_label = QLabel() 
        pixmap = QPixmap('imgs/predictions.png')
        pixmap = pixmap.scaled(5*self.height//6, 5*self.width//6, QtCore.Qt.KeepAspectRatio)
        left_label.setPixmap(pixmap)  
        self.grid.addWidget(left_label, 0, 0, 1, 5)

        right_label = QLabel() 
        pixmap = QPixmap('imgs/predictions.png')
        pixmap = pixmap.scaled(5*self.height//6, 5*self.width//6, QtCore.Qt.KeepAspectRatio)
        right_label.setPixmap(pixmap)
        self.grid.addWidget(right_label, 0, 5, 1, 5) 


        self.left_img_clients = self.data[self.curr_anot_idx]['left_clients']
        self.right_img_clients = self.data[self.curr_anot_idx]['right_clients']

        self.lscroll_area = QtWidgets.QScrollArea()
        self.lscroll_widget = QtWidgets.QWidget()
        self.lscroll_widget_layout = QtWidgets.QGridLayout()
        self.lscroll_widget.setLayout(self.lscroll_widget_layout)
        self.lscroll_area.setWidget(self.lscroll_widget)
        self.lscroll_area.setWidgetResizable(True)
        self.lscroll_area.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)

        self.rscroll_area = QtWidgets.QScrollArea()
        self.rscroll_widget = QtWidgets.QWidget()
        self.rscroll_widget_layout = QtWidgets.QGridLayout()
        self.rscroll_widget.setLayout(self.rscroll_widget_layout)
        self.rscroll_area.setWidget(self.rscroll_widget)
        self.rscroll_area.setWidgetResizable(True)
        self.rscroll_area.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)


        self.add_client_btns()

        self.next_btn = QPushButton('next', self)
        self.next_btn.clicked.connect(self.next_btn_on_click)
        self.grid.addWidget(self.next_btn, 1, 5)

        self.back_btn = QPushButton('back', self)
        self.back_btn.clicked.connect(self.back_btn_on_click)
        self.grid.addWidget(self.back_btn, 1, 4)

        self.grid.addWidget(self.lscroll_area, 2, 1)
        self.grid.addWidget(self.rscroll_area, 2, 7)

        self.sender().deleteLater()

    def add_client_btns(self):
        for i, item in enumerate(self.left_img_clients):
            button = QPushButton(str(item), self)
            button.setCheckable(True)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

            button.clicked.connect(self.on_click)
            button.ud_attr = {'type':'left'}
            self.left_buttons_dic[str(item)] = button
            self.lscroll_widget_layout.addWidget(button, int(item)//5, int(item)%5)
            #self.grid.addWidget(button, i+2, 2)

        self.lspaceItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.lscroll_widget_layout.addItem(self.lspaceItem, int(item)//5+1, int(item)%5+1)

        for i, item in enumerate(self.right_img_clients):
            button = QPushButton(str(item), self)
            button.setCheckable(True)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            button.clicked.connect(self.on_click)
            button.ud_attr = {'type':'right'}
            self.right_buttons_dic[str(item)] = button
            self.rscroll_widget_layout.addWidget(button, int(item)//5, int(item)%5)
            #self.grid.addWidget(button, i+2, 7)
        self.rspaceItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.rscroll_widget_layout.addItem(self.rspaceItem, int(item)//5+1, int(item)%5+1)

    def delete_client_btns(self):
        self.lscroll_widget_layout.removeItem(self.lspaceItem)
        self.rscroll_widget_layout.removeItem(self.rspaceItem)
        for btn_key, btn in  self.left_buttons_dic.items():
            btn.deleteLater()
        self.left_buttons_dic = {}

        for btn_key, btn in  self.right_buttons_dic.items():
            btn.deleteLater()
        self.right_buttons_dic = {}


    def next_btn_on_click(self):
        self.anotatons[self.curr_anot_idx] = self.get_align_indices()
        self.curr_anot_idx = (self.curr_anot_idx +1)%len(self.data)
        self.delete_client_btns()
        self.left_img_clients = self.data[self.curr_anot_idx]['left_clients']
        self.right_img_clients = self.data[self.curr_anot_idx]['right_clients']
        self.add_client_btns()
        self.load_anots()
        self.last_clicked_button = None
        print(self.anotatons)

    def back_btn_on_click(self):
        self.anotatons[self.curr_anot_idx] = self.get_align_indices()
        self.curr_anot_idx = (self.curr_anot_idx - 1)%len(self.data)
        self.delete_client_btns()
        self.left_img_clients = self.data[self.curr_anot_idx]['left_clients']
        self.right_img_clients = self.data[self.curr_anot_idx]['right_clients']
        self.add_client_btns()
        self.load_anots()
        self.last_clicked_button = None
        print(self.anotatons)

    def load_anots(self):
        if self.curr_anot_idx in self.anotatons:
            align_indices = self.anotatons[self.curr_anot_idx]
            for left_key, right_key in align_indices:
                lbtn = self.left_buttons_dic[left_key]
                lbtn.setText(left_key+'-'+right_key)
                lbtn.setChecked(True)
                lbtn.setStyleSheet("background-color: green")
                rbtn = self.right_buttons_dic[right_key]
                rbtn.setText(right_key+'-'+left_key)
                rbtn.setChecked(True)
                rbtn.setStyleSheet("background-color: green")

    def get_align_indices(self):
        align_indices = []
        for btn_key, btn in self.left_buttons_dic.items():
            btn_caption = btn.text()
            if '-' in btn_caption:
                align_indices.append(btn_caption.split('-'))
        #print(align_indices)
        return align_indices

     
    #@pyqtSlot()
    def on_click(self):
        sender_caption = self.sender().text()
        if self.sender().isChecked() and (self.last_clicked_button != None):
            if self.sender().ud_attr['type'] !=  self.last_clicked_button.ud_attr['type']:
                self.sender().setText(sender_caption.split('-')[0] + '-' +self.last_clicked_button.text().split('-')[0])
                self.sender().setStyleSheet("background-color: green")
                self.last_clicked_button.setStyleSheet("background-color: green")
                self.last_clicked_button.setText(self.last_clicked_button.text().split('-')[0] + '-' + sender_caption.split('-')[0])
                self.last_clicked_button = None
            else:
                self.sender().setChecked(False)
                self.last_clicked_button.setChecked(False)
                self.last_clicked_button.setStyleSheet("background-color: none")
                self.last_clicked_button = None

        elif self.sender().isChecked() and (self.last_clicked_button == None):
            self.last_clicked_button = self.sender()
            self.last_clicked_button.setStyleSheet("background-color: yellow")
        
        elif not self.sender().isChecked():
            if '-' in sender_caption:
                if self.sender().ud_attr['type'] == 'left':
                    left_btn_key, right_btn_key = sender_caption.split('-')
                else:
                    right_btn_key, left_btn_key = sender_caption.split('-')
                self.left_buttons_dic[left_btn_key].setText(left_btn_key) 
                self.left_buttons_dic[left_btn_key].setChecked(False)
                self.left_buttons_dic[left_btn_key].setStyleSheet("background-color: none")
                self.right_buttons_dic[right_btn_key].setText(right_btn_key)
                self.right_buttons_dic[right_btn_key].setChecked(False)
                self.right_buttons_dic[right_btn_key].setStyleSheet("background-color: none")
            else:
                self.sender().setStyleSheet("background-color: none")
                self.last_clicked_button = None

     
if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    ex = App(width=width, height=height)
    sys.exit(app.exec_())
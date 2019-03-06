import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QHBoxLayout,QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtCore import pyqtSlot
 
class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'User Alignment Anontator'
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 500

        self.anotatons = []
        self.data = [(range(9), range(7))]
        self.curr_anot_idx = 0

        self.left_img_clients = range(9)
        self.right_img_clients = range(7)
        self.left_buttons_dic = {}
        self.right_buttons_dic = {}
        self.last_clicked_button = None
        self.initUI()
     
    def initUI(self):

        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.start_btn = QPushButton('Start Anotation', self) 
        self.start_btn.clicked.connect(self.start_on_click)
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        self.grid.addWidget(self.start_btn, 0, 0)
        self.setLayout(self.grid)    
        
        self.show()

    def start_on_click(self):
        self.add_client_btns()
        
        self.sender().deleteLater()

    
    def add_client_btns(self):
        self.next_btn = QPushButton('next', self)
        self.next_btn.move(10, 10)
        self.next_btn.clicked.connect(self.save)
        self.grid.addWidget(self.next_btn, 0, 1)
        
        shift_y = 200
        for i, item in enumerate(self.left_img_clients):
            button = QPushButton(str(item), self)
            button.setCheckable(True)
            #button.move(10,shift_y)
            shift_y = shift_y + 30
            button.clicked.connect(self.on_click)
            button.ud_attr = {'type':'left'}
            self.left_buttons_dic[str(item)] = button
            self.grid.addWidget(button, i+1, 0)

        shift_y = 200
        for i, item in enumerate(self.right_img_clients):
            button = QPushButton(str(item), self)
            button.setCheckable(True)
            #button.move(620,shift_y)
            #shift_y = shift_y + 30
            button.clicked.connect(self.on_click)
            button.ud_attr = {'type':'right'}
            self.right_buttons_dic[str(item)] = button
            self.grid.addWidget(button, i+1, 1)

    def save(self):
        align_indices = []
        for btn_key, btn in self.left_buttons_dic.items():
            btn_caption = btn.text()
            if '-' in btn_caption:
                align_indices.append(btn_caption.split('-'))
        print(align_indices)

     
    #@pyqtSlot()
    def on_click(self):
        sender_caption = self.sender().text()
        if self.sender().isChecked() and (self.last_clicked_button != None):
            if self.sender().ud_attr['type'] !=  self.last_clicked_button.ud_attr['type']:
                self.sender().setText(sender_caption.split('-')[0] + '-' +self.last_clicked_button.text().split('-')[0])
                self.last_clicked_button.setText(self.last_clicked_button.text().split('-')[0] + '-' + sender_caption.split('-')[0])
                self.last_clicked_button = None
            else:
                self.sender().setChecked(False)
                self.last_clicked_button.setChecked(False)
                self.last_clicked_button = None

        elif self.sender().isChecked() and (self.last_clicked_button == None):
            self.last_clicked_button = self.sender()
        
        elif not self.sender().isChecked():
            self.last_clicked_button = None
            if '-' in sender_caption:
                if self.sender().ud_attr['type'] == 'left':
                    left_btn_key, right_btn_key = sender_caption.split('-')
                else:
                    right_btn_key, left_btn_key = sender_caption.split('-')
                self.left_buttons_dic[left_btn_key].setText(left_btn_key) 
                self.left_buttons_dic[left_btn_key].setChecked(False)
                self.right_buttons_dic[right_btn_key].setText(right_btn_key)
                self.right_buttons_dic[right_btn_key].setChecked(False)

            #self.sender().setStyleSheet("background-color: none")

     
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QHBoxLayout,QVBoxLayout, QGridLayout, QLabel, QFileDialog
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, qRgb
import cv2
import numpy as np
import os
import sys
import json

from user_alignment_anotator import UserAlignmentAnotator

class NotImplementedException:
    pass

gray_color_table = [qRgb(i, i, i) for i in range(256)]

def toQImage(im, copy=False):
    if im is None:
        return QImage()

    if im.dtype == np.uint8:
        if len(im.shape) == 2:
            qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim.copy() if copy else qim

        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                return qim.copy() if copy else qim
            elif im.shape[2] == 4:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                return qim.copy() if copy else qim

    raise NotImplementedException


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._photo.setPixmap(pixmap)
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.1
                self._zoom += 1
            else:
                factor = 0.9
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(QtCore.QPoint(event.pos()))
        super(PhotoViewer, self).mousePressEvent(event)
 
class App(QWidget):
 
    def __init__(self, width, height):
        super().__init__()
        self.title = 'User Alignment Annotator'
        self.left = 0
        self.top = 0
        self.width = width
        self.height = height

        self.annotatons = {}
        self.data_dic = {'annotatons': self.annotatons}
        self.anot_save_path = None
        self.data_path = None
        #self.uaa.curr_index = 0

        self.left_buttons_dic = {}
        self.right_buttons_dic = {}
        self.last_clicked_button = None
        self.initUI()

    def load_saved_anots_on_click(self):
        self.anot_save_path = QFileDialog.getOpenFileName(self,
                                      "Open File", 'annotatons' +".json",
                                      "JSON (*.json)" )[0]
        if os.path.isfile(self.anot_save_path):
            self.data_dic = json.load(open(self.anot_save_path, 'r'))
            self.annotatons = self.data_dic['annotatons']
            self.data_path = self.data_dic['data_path']
            curr_index = max(-1, self.data_dic['curr_index']-1)
            history = self.data_dic['history']
            self.uaa = UserAlignmentAnotator(1, 1, 
                            images_path=self.data_path, 
                            curr_index=curr_index,
                            history=history)

            self.start_on_click()
            self.load_anots()
   
     
    def initUI(self):
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.start_btn = QPushButton('Start New Annotation', self) 
        self.start_btn.clicked.connect(self.start_on_click)
        self.start_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.start_btn.setEnabled(self.data_path != None)
        self.start_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.grid = QGridLayout()
        self.grid.addWidget(self.start_btn, 2, 0)

        self.load_btn = QPushButton('Load Saved Annotation', self) 
        self.load_btn.clicked.connect(self.load_saved_anots_on_click)
        self.load_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.grid.addWidget(self.load_btn, 3, 0)

        self.browse_btn = QPushButton('Select Data Folder', self) 
        self.browse_btn.clicked.connect(self.browse_on_click)
        self.browse_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.grid.addWidget(self.browse_btn, 0, 0)

        self.path_label = QLabel('Data Path: ')
        self.path_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.grid.addWidget(self.path_label, 1, 0)

        self.spaceItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.grid.addItem(self.spaceItem, 4, 0)        
        self.setLayout(self.grid)    
        self.show()

    def browse_on_click(self):
        self.data_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.data_dic['data_path'] = self.data_path
        self.start_btn.setEnabled(self.data_path != None)
        self.path_label.setText('Data Path: ' + self.data_path)
        self.uaa = UserAlignmentAnotator(1, 1, images_path=self.data_path)


    def view_left_image(self, img1):
        img1 = toQImage(img1)
        pixmap = QPixmap.fromImage(img1)
        self.left_viewer.viewport().resize(img1.height(), img1.width())
        self.left_viewer.setPhoto(pixmap)  
        self.grid.addWidget(self.left_viewer, 0, 0, 1, 5)

    def view_right_image(self, img2):
        img2 = toQImage(img2)
        self.right_viewer.viewport().resize(img2.height(), img2.width())
        pixmap = QPixmap.fromImage(img2)
        self.right_viewer.setPhoto(pixmap)
        self.grid.addWidget(self.right_viewer, 0, 5, 1, 5) 

    def start_on_click(self):
        img1,k1,img2,k2 = self.uaa.next_pair()
        #im = cv2.imread(os.path.join(self.data_path, 'predictions.png'))
        #im = im.scaled(5*self.height//6, 5*self.width//6, QtCore.Qt.KeepAspectRatio)
        self.left_viewer = PhotoViewer(self)
        self.view_left_image(img1)

        #im = cv2.imread(os.path.join(self.data_path, 'predictions.png'))
        #im = im.scaled(5*self.height//6, 5*self.width//6, QtCore.Qt.KeepAspectRatio)
        self.right_viewer = PhotoViewer(self)
        self.view_right_image(img2)

        self.left_img_clients = k1#self.data[self.uaa.curr_index]['left_clients']
        self.right_img_clients = k2#self.data[self.uaa.curr_index]['right_clients']

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

        self.save_btn = QPushButton('save', self)
        self.save_btn.clicked.connect(self.save_btn_on_click)
        self.grid.addWidget(self.save_btn, 1, 5)

        self.next_btn = QPushButton('next', self)
        self.next_btn.clicked.connect(self.next_btn_on_click)
        self.grid.addWidget(self.next_btn, 1, 4)

        self.back_btn = QPushButton('back', self)
        self.back_btn.clicked.connect(self.back_btn_on_click)
        self.grid.addWidget(self.back_btn, 1, 3)

        self.progress_label = QLabel('%d/%d'%(self.uaa.curr_index+1, self.uaa.N-1))
        self.progress_label.setAlignment(QtCore.Qt.AlignTop)
        self.grid.addWidget(self.progress_label, 2, 4)
        self.grid.addWidget(self.lscroll_area, 2, 1)
        self.grid.addWidget(self.rscroll_area, 2, 7)

        self.start_btn.deleteLater()
        self.browse_btn.deleteLater()
        self.path_label.deleteLater()
        self.load_btn.deleteLater()
        self.grid.removeItem(self.spaceItem)


    def save_annotations(self):
        self.data_dic['curr_index'] = self.uaa.curr_index
        self.data_dic['history'] = self.uaa.history
        with open(self.anot_save_path, 'w') as f:
            json.dump(self.data_dic, f)

    def save_btn_on_click(self):
        if  (self.anot_save_path == None) or (not os.path.isfile(self.anot_save_path)):
            self.anot_save_path = QFileDialog.getSaveFileName(self,
                                      "Select Json to Save", 'annotatons' +".json",
                                     "JSON (*.json)" )[0]
            
        if (self.anot_save_path != None) and self.anot_save_path != '':
            self.save_annotations()


    def add_client_btns(self):
        for i, item in enumerate(self.left_img_clients):
            button = QPushButton(str(item), self)
            button.setCheckable(True)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

            button.clicked.connect(self.on_click)
            button.ud_attr = {'type':'left'}
            self.left_buttons_dic[str(item)] = button
            self.lscroll_widget_layout.addWidget(button, int(item)//5, int(item)%5)

        self.lspaceItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.lscroll_area.setFixedHeight(button.height()*4.7)
        self.lscroll_widget_layout.addItem(self.lspaceItem, i//5+1, 5)

        for i, item in enumerate(self.right_img_clients):
            button = QPushButton(str(item), self)
            button.setCheckable(True)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            button.clicked.connect(self.on_click)
            button.ud_attr = {'type':'right'}
            self.right_buttons_dic[str(item)] = button
            self.rscroll_widget_layout.addWidget(button, int(item)//5, int(item)%5)
        self.rspaceItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.rscroll_area.setFixedHeight(button.height()*4.7)
        self.rscroll_widget_layout.addItem(self.rspaceItem, i//5+1, 5)

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
        img1,k1,img2,k2 = self.uaa.next_pair()
        self.view_left_image(img1)
        self.view_right_image(img2)
        #self.uaa.curr_index = (self.uaa.curr_index +1)%len(self.data)
        self.delete_client_btns()
        self.left_img_clients = k1#self.data[self.uaa.curr_index]['left_clients']
        self.right_img_clients = k2#self.data[self.uaa.curr_index]['right_clients']
        self.add_client_btns()
        self.load_anots()
        self.last_clicked_button = None
        if (self.anot_save_path != None) and os.path.isfile(self.anot_save_path):
            self.save_annotations()
        self.progress_label.setText('%d/%d'%(self.uaa.curr_index+1, self.uaa.N-1))

    def back_btn_on_click(self):
        img1,k1,img2,k2 = self.uaa.back_pair()
        self.view_left_image(img1)
        self.view_right_image(img2)
        # self.uaa.curr_index = (self.uaa.curr_index - 1)%len(self.data)
        self.delete_client_btns()
        self.left_img_clients = k1#self.data[self.uaa.curr_index]['left_clients']
        self.right_img_clients = k2#self.data[self.uaa.curr_index]['right_clients']
        self.add_client_btns()
        self.load_anots()
        self.last_clicked_button = None
        if (self.anot_save_path != None) and os.path.isfile(self.anot_save_path):
            self.save_annotations()
        self.progress_label.setText('%d/%d'%(self.uaa.curr_index+1, self.uaa.N-1))

    def load_anots(self):
        if str(self.uaa.curr_index) in self.annotatons:
            align_indices = self.annotatons[str(self.uaa.curr_index)]
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
        return align_indices

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.back_btn_on_click()
        if event.key() == QtCore.Qt.Key_Right:
            self.next_btn_on_click()

     
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
                self.annotatons[str(self.uaa.curr_index)] = self.get_align_indices()
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
                self.annotatons[str(self.uaa.curr_index)] = self.get_align_indices()
            else:
                self.sender().setStyleSheet("background-color: none")
                self.last_clicked_button = None

     
if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    ex = App(width=width, height=height)
    sys.exit(app.exec_())

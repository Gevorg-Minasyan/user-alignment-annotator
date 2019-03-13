import cv2
import numpy as np
import os
from pathlib import Path
import glob
from utils import PascalVocReader

class UserAlignmentAnotator(object):
	def __init__(self,
				 stride, 
				 lag, 
				 images_path='imgs/',
				 lay_folder_path='layouts/',
				 curr_index=-1,
				 history=[]):
		
		self.images_path = images_path
		self.images_info_list = sorted(glob.glob(os.path.join(images_path, '*.xml')))
		self.images_info_list = [name.replace('\\', '/')  for name in self.images_info_list]
		self.N = len(self.images_info_list)

		self.history = history
		self.curr_index = curr_index
		self.stride = stride
		self.lag = lag
		self.lay_folder_path = lay_folder_path

		self.write_layout_info()

	def write_layout_info(self):
		
		for xml_path in self.images_info_list:
			ano_reader = PascalVocReader(xml_path)
			boxes = [[shape[1][0][0],shape[1][0][1], abs(shape[1][0][0]-shape[1][1][0]),abs(shape[1][0][1]-shape[1][1][1])] for shape in ano_reader.getShapes()]
			hash_boxes = dict(enumerate(boxes))
			file_path = self.lay_folder_path + xml_path.split('/')[-1][:-4] + '.lay'  
			with open(file_path,'w') as layout_file:
				layout_file.write(xml_path+'\n')
				for k,v in hash_boxes.items():
					info = str(k)+':'+' '.join([str(m) for m in v])+'\n'
					layout_file.write(info)  
				layout_file.close()

	def next(self):

		if self.curr_index == -1:
			left, right = 0, 0+self.lag
			if len(self.history) == 0:
				self.history.append((left,right))
			self.curr_index += 1
			return self.history[self.curr_index]
		
		if self.curr_index+1 <len(self.history):
			self.curr_index += 1
			return self.history[self.curr_index]
		else:
			left,right = self.history[-1] 
			next_left  = left+self.stride
			next_right = next_left + self.lag
			
			if next_right >= self.N:
				return self.history[self.curr_index]
				
			self.history.append((next_left,next_right))
			self.curr_index +=1
			return self.history[self.curr_index]

	def back(self):
		if self.curr_index == -1:
			return None
		if self.curr_index == 0:
			return self.history[self.curr_index]
		self.curr_index -=1
		return self.history[self.curr_index]

	def parse_layout_file(self, lay_file_path):
		info = {}
		with open(lay_file_path, 'r') as f:
			data = f.read().split('\n')
		if data[-1] == '\n' or data[-1] == '':
			data = data[:-1]
			
		info[data[0]] = {}
		for box in data[1:]:
			sp = box.split(':')
			info[data[0]][sp[0]] = [int(m) for m in sp[1].split(' ')]
		return info

	def plotify(self,left,right, alignments=None):
		left_xml_path  = self.images_info_list[left]
		right_xml_path = self.images_info_list[right]
		
		left_jpg_path  = left_xml_path[:-4] + '.jpg'
		right_jpg_path = right_xml_path[:-4] + '.jpg'

		left_info  = self.parse_layout_file(self.lay_folder_path + left_xml_path.split('/')[-1][:-4] + '.lay')
		right_info = self.parse_layout_file(self.lay_folder_path + right_xml_path.split('/')[-1][:-4] + '.lay')
		left_boxes_info  = left_info[left_xml_path]
		right_boxes_info = right_info[right_xml_path]

		left_img  = cv2.imread(left_jpg_path,cv2.IMREAD_UNCHANGED)
		right_img = cv2.imread(right_jpg_path,cv2.IMREAD_UNCHANGED)

		#For alignments with colors
		# left_colors = None
		# right_colors = None
		# if alignments:
		#     pass
		get_size = lambda area,max_area: 0.7 if area >= max_area//2 else 0.6 if area>= max_area//3 else 0.45 #1.1*area/(max_area**0.99)

		left_hashes = []
		left_areas = {}
		mx = 0
		for id, box in left_boxes_info.items():
			left_hashes.append(id)
			x1,y1,w,h = box
			x2 = x1 + w 
			y2 = y1 + h 
			area = w*h
			if area>mx:
				mx = area
			left_areas[id] = [area,(x1,y1)]
			left_img = cv2.rectangle(left_img, (x1,y1), (x2,y2), (20,200,120), 2)
		

		for id, box in left_boxes_info.items():
			text_sz = get_size(left_areas[id][0],mx)
			x1,y1 = left_areas[id][1]
			left_img = cv2.putText(left_img, str(id), (x1+int(w*0.3), y1+int(h*0.7)), cv2.FONT_HERSHEY_DUPLEX, text_sz, (255, 255, 255),1, lineType=cv2.LINE_AA)
		
		right_hashes = []
		right_areas = {}
		mx=0
		for id, box in right_boxes_info.items():
			right_hashes.append(id)
			x1,y1,w,h = box
			x2 = x1 + w 
			y2 = y1 + h 
			area =w *h
			if area>mx:
				mx = area
			right_areas[id] = [area,(x1,y1)]
			right_img = cv2.rectangle(right_img, (x1,y1), (x2,y2), (20,200,120), 2)
		
		for id, box in right_boxes_info.items():
			text_sz = get_size(right_areas[id][0],mx)
			x1,y1 = right_areas[id][1]
			right_img = cv2.putText(right_img, str(id), (x1+int(w*0.3), y1+int(h*0.7)), cv2.FONT_HERSHEY_DUPLEX, text_sz, (255, 255, 255),1, lineType=cv2.LINE_AA)

		return left_img,left_hashes,right_img,right_hashes

	def next_pair(self):
		left,right = self.next()
		name1 = self.lay_folder_path+str(left)+'.jpg'
		name2 = self.lay_folder_path+str(right)+'.jpg'
		try:
			img1  = cv2.imread(name1,cv2.IMREAD_UNCHANGED)
			if img1 is None:
				raise FileNotFoundError	
			img2  = cv2.imread(name2,cv2.IMREAD_UNCHANGED)
			if img2	 is None:
				raise FileNotFoundError

			left_xml_path  = self.images_info_list[left]
			right_xml_path = self.images_info_list[right]
			left_info  = self.parse_layout_file(self.lay_folder_path + left_xml_path.split('/')[-1][:-4] + '.lay')
			right_info = self.parse_layout_file(self.lay_folder_path + right_xml_path.split('/')[-1][:-4] + '.lay')
			left_boxes_info  = left_info[left_xml_path]
			right_boxes_info = right_info[right_xml_path]
			k1 = list(left_boxes_info.keys())
			k2 = list(right_boxes_info.keys())
		except FileNotFoundError:
			img1,k1,img2,k2  = self.plotify(left,right)
			cv2.imwrite(name1,img1)
			cv2.imwrite(name2,img2)
		return img1,k1,img2,k2 #or path1,k1,path2,k2



	def back_pair(self):
		left,right = self.back()
		name1 = self.lay_folder_path+str(left)+'.jpg'
		name2 = self.lay_folder_path+str(right)+'.jpg'
		try:
			img1  = cv2.imread(name1,cv2.IMREAD_UNCHANGED)
			if img1 is None:
				raise FileNotFoundError
			img2  = cv2.imread(name2,cv2.IMREAD_UNCHANGED)
			if img2	 is None:
				raise FileNotFoundError
			left_xml_path  = self.images_info_list[left]
			right_xml_path = self.images_info_list[right]
			left_info  = self.parse_layout_file(self.lay_folder_path + left_xml_path.split('/')[-1][:-4] + '.lay')
			right_info = self.parse_layout_file(self.lay_folder_path + right_xml_path.split('/')[-1][:-4] + '.lay')
			left_boxes_info  = left_info[left_xml_path]
			right_boxes_info = right_info[right_xml_path]
			k1 = list(left_boxes_info.keys())
			k2 = list(right_boxes_info.keys())

		except FileNotFoundError:
			img1,k1,img2,k2  = self.plotify(left,right)
			cv2.imwrite(name1,img1)
			cv2.imwrite(name2,img2)
		return img1,k1,img2,k2

if __name__ == "__main__":
	uaa = UserAlignmentAnotator(1,1)
	uaa.write_layout_info()
	img1,k1,img2,k2 = uaa.next_pair()
	uaa.next_pair()


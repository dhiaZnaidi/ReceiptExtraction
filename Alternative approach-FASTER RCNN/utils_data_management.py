# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 17:04:12 2022

@author: 21692
"""
import os 
import json 
from PIL import Image as Im 

def crop_to_roi(images_name,info_data_name,save_path):
  for img,info in zip(images_name,info_data_name):
            img_name = img.split('/')[-1]
            im = Im.open(img)
            f = info
            f_open = open(f)
            data = json.load(f_open)
            roi = data['roi']
            left, top , right, bottom = roi.values()
            image = im.crop((left, top, right, bottom))
            image.save(save_path+img_name)
            

def update_dict(liste): 
    x_min,y_min,x_max,y_max= liste
    coord_dict = dict()
    coord_dict["xmin"] = x_min
    coord_dict["ymin"] = y_min
    coord_dict["xmax"] = x_max
    coord_dict["ymax"] = y_max
    return coord_dict

def resize_to_roi(zone,roi):
  roi_x,roi_y,_,_ = roi.values()
  xmin = zone['xmin'] -roi_x
  ymin = zone['ymin'] - roi_y
  xmax = zone['xmax'] -roi_x
  ymax = zone['ymax'] - roi_y
  return xmin,ymin,xmax,ymax

def get_RawData(json_file_path,img_path):
  coord = {}

  coord['img_path'] = img_path
  coord['info_data_path']=json_file_path
  coord['img_name']=os.path.splitext(img_path)[0].split('/')[-1]

        #Taille image 
  img = Im.open(coord['img_path'])
  coord['img_size']=img.size
  coord['img_size_str']=str(img.size)
  
  coord["date"] = list()

  with open(coord['info_data_path'], 'r') as file:

            data = json.load(file)
            total_zone = data['total'][-1]
            date_zone = data['date']
            roi_size = data['roi_size']

            roi = data['roi']
            coord["total"] = list(resize_to_roi(total_zone,roi))
            coord["date"] = list(resize_to_roi(date_zone,roi))
  return coord





def valid_champs(infos,imgs):
  valid_infos=[]
  valid_imgs = []
  for file_info,img in zip(infos,imgs) :
    f = file_info
    f_open = open(f)
    data = json.load(f_open)

    if len(data["total"]) != 0 :
      valid_infos.append(file_info)
      valid_imgs.append(img)
  
  return valid_imgs, valid_infos









# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 17:14:44 2022

@author: 21692
"""

from utils_data_management import * 
from glob import glob
import pandas as pd
def train_val_split(main_dir,trainRatio):
    """construction des datasets sous forme de dataframe"""

    img_path,json_path = valid_champs(sorted(glob(main_dir+'/info_data/*')),sorted(glob(main_dir+'/cropped_images/*')))
    number_samples = len(img_path)
    train_samples = int(number_samples * trainRatio)
    train_set = [img_path[:train_samples] , json_path[:train_samples] ]

    val_set = [img_path[train_samples:] , json_path[train_samples:] ]

    glob_dataframe = []
    for sets in [train_set,val_set]:
      coord_list=[]
      for img,info in zip(sets[0],sets[1]) :
          coord = get_RawData(info,img)
          coord_list.append(coord) 
      #transformation de la liste en dataframe
      dataframe=pd.DataFrame(coord_list)  
      glob_dataframe.append(dataframe)
    
    df_train = glob_dataframe[0]
    df_train['set']='train'
    df_val = glob_dataframe[1]
    df_val['set']='val'

    df = pd.concat([df_train,df_val])

      
    return df


def get_train_val(df):
    df_train = df[df["set"] =="train"]
    df_val = df[df["set"] == "val"]
    return df_train,df_val
    
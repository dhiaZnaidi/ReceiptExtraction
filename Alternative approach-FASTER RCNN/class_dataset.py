# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 17:11:10 2022

@author: 21692
"""
from PIL import Image as Im

import torch
from torch.utils.data import Dataset

class ReceiptDataset(Dataset):
    """ On hérite ici de la classe dataset pour sa modification """

    def __init__(self, dataframe, resize_img=None, resize_box = None):
    
        self.dataframe=dataframe
        #initialisation des images-ids,on utilise le nom des fichiers comme id_unique
        self.image_ids=dataframe.img_name.unique()
        #initialisation des fonctions de redimentionnement
        self.resize_img = resize_img
        self.resize_box = resize_box

    def __len__(self) -> int:
        return self.image_ids.shape[0]

    def __getitem__(self, index):
        
         #lecture des images (on recupère la ligne associée à chaque index(coordonnées reçu et total)
        image_id = self.image_ids[index]
        row = self.dataframe[self.dataframe['img_name'] == image_id]
        total_box=row.total.values[0]
        date_box=row.date.values[0]
        image = Im.open(row.img_path.values[0])
        #concaténation des coodonnées du reçu et du total
        
        if self.resize_box:
            total_box = self.resize_box(total_box, (image.size[1], image.size[0]))
            date_box = self.resize_box(date_box, (image.size[1], image.size[0]))

        if self.resize_img:
            image = self.resize_img(image)

   
        boxes=[date_box,total_box]

        # création de dictionnaire cible et formats appropriés de données pour tensorflow
        target = {}
        target['boxes']= torch.as_tensor(boxes,dtype=torch.float32)
        #on a ici 2 classes
        target['labels'] =torch.as_tensor([1,2],dtype=torch.int64)
        target['image_id'] = torch.tensor([index])
        target['area'] = torch.tensor([(date_box[3] - date_box[1]) * (date_box[2] - date_box[0]), (total_box[3] - total_box[1]) * (total_box[2] - total_box[0])])
        target['iscrowd'] = torch.zeros((2,), dtype=torch.int64)


        return image, target


class RescaleBox(object):
    """Class de redimensionnement des images """
    
    def __init__(self, new_shape):
        assert isinstance(new_shape, tuple)
        self.new_shape = new_shape

    def __call__(self, sample, original_shape):
        w_ratio = self.new_shape[0] / original_shape[0]
        h_ratio = self.new_shape[1] / original_shape[1]
      
        #     xmin,                ymin,              xmax,              ymax
        return [sample[0]*h_ratio, sample[1]*w_ratio, sample[2]*h_ratio, sample[3]*w_ratio]
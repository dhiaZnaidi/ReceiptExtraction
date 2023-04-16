# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 17:20:17 2022

@author: 21692
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.patches import Patch
from PIL import Image as Im 
import numpy as np


import torchvision
from torchvision import transforms


def visualize_img(rows,columns,dataset):
    """  visualisation des reçus"""
    fig, axs = plt.subplots(rows, columns, figsize=(30, 20))

    for idx in range (rows*columns):
        row=dataset.sample()
        img=Im.open(row.img_path.values[0])


        coord_t=row.total.values[0]
        xmin_tot=coord_t[0]
        ymin_tot=coord_t[1]
        xmax_tot=coord_t[2]
        ymax_tot = coord_t[3]


        coord_date=row.date.values[0]
        xmin_date=coord_date[0]
        ymin_date=coord_date[1]
        xmax_date=coord_date[2]
        ymax_date = coord_date[3]
       
        axs[idx // columns, idx % columns].imshow(img)
        rect_t = Rectangle(xy=(xmin_tot, ymin_tot), width=xmax_tot - xmin_tot,height=ymax_tot - ymin_tot,  linewidth=1, edgecolor='b', facecolor='none')

        rect_r = Rectangle(xy=(xmin_date, ymin_date), width=xmax_date - xmin_date,height=ymax_date - ymin_date,  linewidth=1, edgecolor='r', facecolor='none')
        
        axs[idx // columns, idx % columns].add_patch(rect_r)
        axs[idx // columns, idx % columns].add_patch(rect_t)
    plt.suptitle('Dataset visualization')
    plt.show()      


<<<<<<< HEAD
def visualize_prediction(model, dataset, n_rows, n_columns, brut_data= None):
=======
def visualize_prediction(model,device, dataset, n_rows, n_columns, brut_data= None):
>>>>>>> 60cb07b0d3a51414e2e88e1dde44f209f91ba512
    """ Visualisation des prédictions """
    model.eval() # on définit le model en mode évaluation

    np.random.seed(40)

    # rondom d'indexes à tracer
    indexes = np.random.randint(0, len(dataset), n_rows * n_columns)
    
    fig, axs = plt.subplots(n_rows, n_columns, figsize=(17, 20))

    for idx, sample_idx in enumerate(indexes):
        img, true_roi = dataset[sample_idx] # selection random d'une image
        true_date = true_roi["boxes"][0]
        true_total = true_roi["boxes"][1]

        # 
        #Obtention des resultats de prédition pour une image et copie du résultat du GPU vers le CPU
        
         
        prediction = model([img.to(device)])[0]#.detach().cpu().numpy()
        #On recupère toutes les prédictions sous forme de tuple(box,classe,score) par ordre de précision
        data_zip=list(zip(*[v for k,v in prediction.items()]))
        #0n recupère les tuples appartenant à la classe 1(zone délimitant la date)
        all_date_pred = [value for value in data_zip if value[1]==1]
        #0n recupère les tuples appartenant à la classe 2(zone délimitant le total)
        all_total_pred = [value for value in data_zip if value[1]==2]


        # transform the PyTorch Tensor to PIL format 
        #transformation du tensor pythorh au format PIL pour matplotlib
        img = transforms.ToPILImage()(img)

        axs[idx // n_columns, idx % n_columns].imshow(img)

        # create  de rectangle en rouge pour les vraies coordonnées délimitant le réçu et son total
     
        true_date = Rectangle(xy=(true_date[0], true_date[1]), width=true_date[2] - true_date[0],
                                  height=true_date[3] - true_date[1], 
                                  linewidth=1, edgecolor='green', facecolor='none', alpha=0.7)
          
        true_total = Rectangle(xy=(true_total[0], true_total[1]), width=true_total[2] - true_total[0],
                                  height=true_total[3] - true_total[1], 
                                  linewidth=1, edgecolor='green', facecolor='none', alpha=0.7)

        if not brut_data:

            axs[idx // n_columns, idx % n_columns].add_patch(true_date)
            axs[idx // n_columns, idx % n_columns].add_patch(true_total)


        #Si prédiction de zone de la date alors on affiche le premiers élement avec le meilleur score
        if all_date_pred :
         
          all_date_pred = all_date_pred[0][0].detach().cpu().numpy()
         
          date_pred= Rectangle(xy=(all_date_pred[0], all_date_pred[1]), width=all_date_pred[2] - all_date_pred[0],
                                height=all_date_pred[3] - all_date_pred[1], 
                                linewidth=1, edgecolor='yellow', facecolor='none', alpha=0.7)
          
          
        #Si prédiction de zone de total alors on affiche le premiers élement avec le meilleur score
        if all_total_pred :
          all_total_pred = all_total_pred[0][0].detach().cpu().numpy()
          total_pred = Rectangle(xy=(all_total_pred[0], all_total_pred[1]), width=all_total_pred[2] - all_total_pred[0],
                                        height=all_total_pred[3] - all_total_pred[1], 
                                        linewidth=1, edgecolor='yellow', facecolor='none', alpha=0.7)
          
        axs[idx // n_columns, idx % n_columns].add_patch(date_pred)
        axs[idx // n_columns, idx % n_columns].add_patch(total_pred)


        legend_elements = [Patch(facecolor='none', edgecolor='green', 
                                label='ground truth '),
                          Patch(facecolor='none', edgecolor='yellow',
                                label='predicted'),]

        axs[idx // n_columns, idx % n_columns].legend(handles=legend_elements, loc='upper left')
        axs[idx // n_columns, idx % n_columns].axis('off')

    plt.subplots_adjust(wspace=0.25, hspace=0.2)
    plt.suptitle('Visualization of model predictions')
    plt.show()      








# -*- coding: utf-8 -*-
"""Commande_Entreprise_SROIE2019_Data_Cleaning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yZyvC6zOCsZ23uJBvTRZC_r_DtlOXxue

# Importing librairies
"""

from shutil import copyfile
import zipfile
import requests

import shutil

import os
cwd = os.getcwd()

"""# Extracting zipfile from Kaggle"""

! pip install kaggle

!mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d urbikn/sroie-datasetv2

zip_ref = zipfile.ZipFile(cwd+"/sroie-datasetv2.zip", 'r')
zip_ref.extractall(cwd)
zip_ref.close()

"""# Renaming files"""

dir_path = os.getcwd()+'/SROIE2019'

top_folders = ["train","test"]
folders = os.listdir(dir_path+'/train')

def rename_organize_files(dir_path,top_folders,folders):
  for top in top_folders :
    count = 0
    # count increase by 1 in each iteration
    # iterate all files from a directory

    parent_dir = dir_path+"/"+top
    for path in os.listdir(parent_dir+'/img'):
        # check if current path is a file
        if os.path.isfile(os.path.join(parent_dir+"/img", path)):
            count += 1
    print('File count in '+top+':', count)

    n = len(str(count))


    for folder in folders:
        i = 0
        subdir_path = parent_dir+"/"+folder
        for file_name in sorted(os.listdir(subdir_path)):
            # Construct old file name
            source = file_name
            
            index = str(i)
            while len(index) < n :
                index = "0"+index
            
            #To get the extension of the file
            split_tup = os.path.splitext(file_name)

            
            # Adding the count to the new file name and extension
            destination = top + index + split_tup[1]

            # Renaming the file
            os.rename(os.path.join(subdir_path,source), os.path.join(subdir_path,destination))
            i+= 1
        print('All Files in dir '+top+' in folder '+folder +' Renamed')
    
    print('All Files in dir '+top+' Renamed')




rename_organize_files(dir_path,top_folders,folders)

"""# Checking data

### Checking invalidities in the data
"""

def check_incoherence(dir_path,top_folders):

  from string import ascii_letters, digits, punctuation

  acceptable_characters = ascii_letters + digits + punctuation +" \t\n"

  invalid_files = list()

  txt_files = list()
  for folder in top_folders:
    txt_files.append(sorted(os.listdir(dir_path+'/'+folder+'/box'))) #Ici on extrait tous les box dans le train et le test
  i = 0

  for folder in top_folders:
    current_dir_txt = dir_path+'/'+folder+'/box/'


    current_txt_files = txt_files[i]

    for file in current_txt_files:
      try : 
        with open(current_dir_txt+file, "r", encoding = "utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                entries = line.split(",", maxsplit=8)
                for c in entries[-1]:
                    if not c in acceptable_characters:
                        print(f"Invalid char {repr(c)} in {current_dir_txt+file} on line {line_no}")
                        invalid_files.append(current_dir_txt+file)
      except : 
        print(f"Can't decode file using utf-8 decoder for {current_dir_txt+file}")
        invalid_files.append(current_dir_txt+file)
    i+=1
  
  return invalid_files

def remove_invalid_files(paths):
  files_to_be_removed = list()

  for path in paths :
    root_ext = os.path.splitext(path)
    file_name = root_ext[0].split('/')[-1]
    modified = '/'.join(root_ext[0].split('/')[:-2])
    for folder in ['box','entities','img'] :
      if folder == 'img': 
        file_path = '/'.join([modified,folder,file_name+'.jpg'])
        files_to_be_removed.append(file_path)
      else :
        file_path = '/'.join([modified,folder,file_name+'.txt'])
        files_to_be_removed.append(file_path)

  files_to_be_removed.extend([cwd+"/SROIE2019/train/box/train068.txt",
                              cwd+"/SROIE2019/train/img/train068.jpg",
                              cwd+"/SROIE2019/train/entities/train068.txt"])
  files_to_be_removed.extend(
      [cwd+'/SROIE2019/train/img/train192.jpg',
cwd+'/SROIE2019/train/box/train192.txt',
cwd+'/SROIE2019/train/entities/train192.txt',
cwd+'/SROIE2019/train/img/train601.jpg',
cwd+'/SROIE2019/train/box/train601.txt',
cwd+'/SROIE2019/train/entities/train601.txt',
cwd+'/SROIE2019/test/img/test043.jpg',
cwd+'/SROIE2019/test/box/test043.txt',
cwd+'/SROIE2019/test/entities/test043.txt']
  )
  
  for file in files_to_be_removed :
    os.remove(file)
    print (f"Does the file {file} exists ? => {os.path.exists(file)}")
    if not(os.path.exists(file)):
      print(f"the file {file} was successfuly removed")
      
invalid_files = check_incoherence(dir_path,top_folders)
remove_invalid_files(invalid_files)

rename_organize_files(dir_path,top_folders,folders)

"""### Transforming entities files to json files"""

os.mkdir(dir_path+"/train/json_entities")
os.mkdir(dir_path+"/test/json_entities")

import json


def transform_entities(dir_path,top_folders,subfolder,json_subfolder):
  for folder in top_folders:
    cwd = dir_path + '/' + folder
    entities = cwd+ '/' + subfolder
    for file in sorted(os.listdir(entities)):

      with open(entities+'/'+file,"r") as f:
        s = f.read()
        res = json.loads(s)
        f.close()
      json_wd = cwd+'/'+json_subfolder
      with open(json_wd+'/'+file.split('.')[0]+".json", "w") as outfile:
        outfile.write(s)
        outfile.close()


transform_entities(dir_path,top_folders,"entities",'json_entities')

"""## Extracting coordinates and text in the bounding boxes properly"""

def box_to_xyhw(coordinates):
  x1,y1,x2,y2,x3,y3,x4,y4 = coordinates
  x = x1
  y = y1
  w = abs(x2-x1)
  h = abs(y4-y1)
  return [x,y,h,w]

def box_to_minmax(coordinates):
  x1,y1,x2,y2,x3,y3,x4,y4 = coordinates
  x_min = x1
  y_min = y1
  x_max = x3
  y_max = y3
  return [x_min,y_min,x_max,y_max]

def box_to_cxcyhw(coordinates):
  x1,y1,x2,y2,x3,y3,x4,y4 = coordinates
  w = abs(x2-x1)
  h = abs(y4-y1)
  cx = w/2
  cy = h/2
  return [cx,cy,h,w]

""" 
In the txt files , the first 8 coordinates indicate the positions (x1,y1),(x2,y2),(x3,y3),(x4,y4) such as the bounding box is :

(x1,y1)-------------------------------------------------------------------------(x2,y2)
   |                                                                               |
   |                                                                               |
   |                                                                               |
   |                                                                               |
(x4,y4)-------------------------------------------------------------------------(x3,y3)

Then what follows is the text within that bouding box extracted by the OCR
"""


def extract_information_from_txt(file_name):
  """
  The aim of this function is to reorganize our txt file
  """
  L = list()
  new_list_of_contents = list()
  with open(file_name,'r') as f:

    string_of_contents = f.read() #Here we get a whole string representing the file
    list_of_contents = string_of_contents.split("\n") #Here we get a list of strings where each string represents a line within the our file
    list_of_contents = list(filter(None,list_of_contents)) # This i suseful to remove empty strings (generally present at the end of the file) from our list
    for s in list_of_contents:
      k = s.split(',',maxsplit = 8)
      coordinates = list(map(lambda s : int(s),k[:-1])) # Here we extract the coordinates in a list of int
      text = k[-1] #Here we extract the text
      new_list_of_contents.append([coordinates,text]) 
    
    for liste in new_list_of_contents:
      L.append(list_to_dict(liste))
    return new_list_of_contents

def list_to_dict(liste_ligne) : 
    coordinate_dict=dict()
    coordinates_list = liste_ligne[0]
    content = liste_ligne[1]
    diction = dict()
    i=1
    
    n = len(liste_ligne[0])
    for k in range(0,n-1,2):
      coordinate_dict["x"+str(i)] = coordinates_list[k]
      coordinate_dict["y"+str(i)] = coordinates_list[k+1]
      i+=1

    diction["Coordinates"] = coordinate_dict
    diction["Text"] = content
    return diction

def improve_list(liste): 
    x_min,y_min,x_max,y_max= box_to_minmax(liste)
    coord_dict = dict()
    coord_dict["xmin"] = x_min
    coord_dict["ymin"] = y_min
    coord_dict["xmax"] = x_max
    coord_dict["ymax"] = y_max
    return coord_dict

def improve_dict(original_dict) : 
    new_dict = dict()

    old_coordinate_dict = original_dict["Coordinates"]
    content = original_dict["Text"]
    coordinates = [el for el in old_coordinate_dict.values()]

    x_min,y_min,x_max,y_max= box_to_minmax(coordinates)

    coord_dict = dict()

    coord_dict["xmin"] = x_min
    coord_dict["ymin"] = y_min
    coord_dict["xmax"] = x_max
    coord_dict["ymax"] = y_max

    new_dict["Coordinates"] = coord_dict
    new_dict["Text"] = content
    return new_dict

#Caution : using only os.listdir(directory) will list all the elements of a file but in disorder which is not what we want given that names 
#and order of the files in our 3 given directories is crucial

#To overcome this problem, we will use sorted(os.listdir(directory)) instead

def grab_date_total_from_json(file):
  import json
  # Opening JSON file
  elements = list()
  f = open(file)
    
  # returns JSON object as a dictionary
  data = json.load(f)
  elements.append(data['date'])
  elements.append(data['total'])
  return elements

def find_total_in_text(list_lines):
  interest = list()
  ref = 'tot'
  for line in list_lines : 
    if (ref in line[1].lower()):
      interest.append(line)
  return interest

def find_date_in_text(list_lines,date):
  keyword = 'date'
  interest = list()
  for line in list_lines : 
    if (date.lower() in line[1].lower()) or (keyword in line[1].lower() ):
      interest.append(line)
  if len(interest) == 1 : 
    return [interest[0]]
  elif len(interest) >= 2 : 
    if (keyword in interest[0][1].lower() ) and not(date.lower() in interest[0][1].lower() ):
      return interest[:2]
    elif( (date.lower() and keyword) in interest[0][1].lower()) : 
      return [interest[0]]
    else : 
      return [interest[0]]

def check_similarities_strings(s1,s2):

  from difflib import SequenceMatcher
  if len(s1) <= len(s2):
    return SequenceMatcher(None, s1, s2).ratio()
  else :
    return 0

def find_amount_in_text(liste_content,total_amnt,th_similarities):
  interest = list()
  for line in liste_content: 
    if check_similarities_strings(total_amnt,line[1]) > th_similarities :
      interest.append(line)
  return interest

def get_total_price_together(tot_list,price_list,th_dist,total_amnt,th_similarities):
  global_list = list()
  interest = list()

  for l in tot_list:
    for prix in price_list : 
      if on_the_same_line(l,prix,th_dist) and check_similarities_strings(total_amnt,prix[1]) > th_similarities:
        #print (l[0],prix[0])
        #print(l[1] + " and " + prix[1] + " are next to each other")
        global_box_horiz =  merge_boxes(l,prix,th_dist) 
        global_box_horiz_tr = box_to_xyhw(global_box_horiz)
        global_list.append([global_box_horiz, global_box_horiz_tr])
        interest.append([l,prix])

      elif on_the_same_column(l,prix,th_dist) and check_similarities_strings(total_amnt,prix[1]) > th_similarities :
        #print (l[0],prix[0])
        #print(l[1] + " and " + prix[1] + " are above each other")
        global_box_vert =  merge_boxes(l,prix,th_dist) 
        global_box_vert_tr = box_to_xyhw(global_box_vert)
    
        global_list.append([global_box_vert, global_box_vert_tr])
        interest.append([l,prix])
  

  return global_list,interest

def on_the_same_line(l1,l2,th_pix_dis):
    d1 = list_to_dict(l1)
    d2 = list_to_dict(l2)
  
    y1_1 = d1["Coordinates"]['y1']
    y1_2 = d2["Coordinates"]['y1']
    if abs(y1_1 - y1_2) <th_pix_dis:
      return True
    else:
      return False

def on_the_same_column(l1,l2,th_pix_dis):
    d1 = list_to_dict(l1) 
    d2 = list_to_dict(l2)

    x1_1 = d1["Coordinates"]['x1']
    x1_2 = d2["Coordinates"]['x1']
    x2_1 = d1["Coordinates"]['x2']
    x2_2 = d2["Coordinates"]['x2']
    y1_1 = d1["Coordinates"]['y1']
    y1_2 = d2["Coordinates"]['y1']
    if   (abs(x1_1 - x1_2) <th_pix_dis  or  abs(x2_1 - x2_2) <th_pix_dis) and abs(y1_1 - y1_2) < 70 :
      return True
    else:
      return False

def merge_boxes(l1,l2,th_dist):
  if on_the_same_line(l1,l2,th_dist):
    x1 = min(l1[0][0],l2[0][0])
    y1 = min(l1[0][1],l2[0][1])
    x2 = max(l1[0][2],l2[0][2])
    y2 = min(l1[0][3],l2[0][3])
    x3 = max(l1[0][4],l2[0][4])
    y3 = max(l1[0][5],l2[0][5])
    x4 = min(l1[0][6],l2[0][6])
    y4 = max(l1[0][7],l2[0][7])
    return [x1,y1,x2,y2,x3,y3,x4,y4]

  elif on_the_same_column(l1,l2,th_dist):
    x1 = min(l1[0][0],l2[0][0])
    y1 = min(l1[0][1],l2[0][1])
    x2 = max(l1[0][2],l2[0][2])
    y2 = min(l1[0][3],l2[0][3])
    x3 = max(l1[0][4],l2[0][4])
    y3 = max(l1[0][5],l2[0][5])
    x4 = min(l1[0][6],l2[0][6])
    y4 = max(l1[0][7],l2[0][7])
    return [x1,y1,x2,y2,x3,y3,x4,y4]
  else : 
    return l2[0]

def extractROIcoordinates(list_content):
    
    x1 = [L[0][0] for L in list_content]
    y1 = [L[0][1] for L in list_content]
    x3 = [L[0][4] for L in list_content]
    y3 = [L[0][5] for L in list_content]  
    
    return min(x1)-10,min(y1)-20,max(x3)+10,max(y3)+20

"""## Now let's attack the most important part : Rearranging our data"""

import shutil

shutil.copytree( cwd+"/SROIE2019/train/img", cwd+"/Dataset/train/images")
shutil.copytree( cwd+"/SROIE2019/train/json_entities", cwd+"/Dataset/train/gdt")
shutil.copytree( cwd+"/SROIE2019/train/box", cwd+"/Dataset/train/box")
shutil.copytree( cwd+"/SROIE2019/test/img", cwd+"/Dataset/test/images")
shutil.copytree( cwd+"/SROIE2019/test/json_entities", cwd+"/Dataset/test/gdt")
shutil.copytree( cwd+"/SROIE2019/test/box", cwd+"/Dataset/test/box")

os.mkdir(cwd+"/Dataset/train/info_data")
os.mkdir(cwd+"/Dataset/test/info_data")

from glob import glob

test_img = sorted(glob(cwd+"/Dataset/test/images/*"))
test_json = sorted(glob(cwd+"/Dataset/test/gdt/*"))
test_box = sorted(glob(cwd+"/Dataset/test/box/*"))

# fetch all files
for source in test_json:
    file_name = source.split('/')[-1]
    # construct full file path
    destination = cwd+'/Dataset/train/gdt/' + file_name
    # copy only files
    if os.path.isfile(source):
        shutil.copy(source, destination)

# fetch all files
for source in test_img:
    file_name = source.split('/')[-1]
    # construct full file path
    destination = cwd+'/Dataset/train/images/' + file_name
    # copy only files
    if os.path.isfile(source):
        shutil.copy(source, destination)

# fetch all files
for source in test_box:
    file_name = source.split('/')[-1]
    # construct full file path
    destination = cwd+'/Dataset/train/box/' + file_name
    # copy only files
    if os.path.isfile(source):
        shutil.copy(source, destination)

shutil.rmtree(cwd+"/Dataset/test")

def rename_organize_files_new_dataset(dir_path,folders):
  count = 0
    # count increase by 1 in each iteration
    # iterate all files from a directory
  for path in os.listdir(dir_path+'/images'):
        # check if current path is a file
      if os.path.isfile(os.path.join(dir_path+"/images", path)):
          count += 1
  print('File count in /images folder :', count)

  n = len(str(count))


  for folder in folders:
    i = 0
    parent_dir = dir_path+"/"+folder
    for file_name in sorted(os.listdir(parent_dir)):
      # Construct old file name
      source = file_name
      index = str(i)
      while len(index) < n :
        index = "0"+index
            
            #To get the extension of the file
      split_tup = os.path.splitext(file_name)

            
            # Adding the count to the new file name and extension
      destination = index + split_tup[1]

            # Renaming the file
      os.rename(os.path.join(parent_dir,source), os.path.join(parent_dir,destination))
      i+= 1
    print('All Files in dir '+folder+' Renamed')




rename_organize_files_new_dataset(cwd+'/Dataset/train',["images","gdt","box"])

bbox_files = sorted(glob(cwd+"/Dataset/train/box/*"))
images = sorted(glob(cwd+"/Dataset/train/images/*"))
json_files = sorted(glob(cwd+"/Dataset/train/gdt/*"))

images

def create_information_file(bbox_files,images,json_files) :
  from PIL import Image as Im

  for box_file_name,json_file_name,image in zip(bbox_files,json_files,images):

    root = os.path.splitext(json_file_name)
    name = root[0].split('/')[-1]

    root_info_data = cwd+"/Dataset/train/info_data/"

    content_info_dict = dict()

    liste_content = extract_information_from_txt(box_file_name)

    date,total_amnt = grab_date_total_from_json(json_file_name)

    tot_list = find_total_in_text(liste_content)

    price_list = find_amount_in_text(liste_content,total_amnt,0.6)

    global_bboxes ,prepare_dict = get_total_price_together(tot_list,price_list,15,total_amnt,0.7)

    date_list = find_date_in_text(liste_content,date)
    x1,y1,x3,y3 = extractROIcoordinates(liste_content)

    # Now let's prepare our json file structure

    important_words = list()
    date_dict = dict()
    
    date_dict["words"] = [improve_dict(list_to_dict(liste)) for liste in date_list]
    date_dict["label"] = "date"
    important_words.append(date_dict)

    for combined_liste in prepare_dict:
      dicti = dict()
      dicti["words"] = [improve_dict(list_to_dict(liste)) for liste in combined_liste]
      dicti["label"] = "total"
      important_words.append(dicti)

    
    content_info_dict["image_path"] = image
    content_info_dict["image_size"] = Im.open(image).size
    content_info_dict["info_json_path"] = json_file_name
    content_info_dict["important_words"] = important_words
    content_info_dict["total"] = [improve_list(liste[0]) for liste in global_bboxes]
    
    if len(date_list) == 1 : 
      content_info_dict["date"] = improve_list(date_list[0][0])
    else : 
      try : 
        content_info_dict["date"] = improve_list(merge_boxes(date_list[0],date_list[1],15))
      except :
        print(box_file_name)
    
    content_info_dict["roi"] = {'xmin': x1,'ymin': y1,'xmax': x3,'ymax': y3}
    content_info_dict["roi_size"] = (x3-x1 , y3-y1)

    ## Now let's dump this dictionary to a json file

        # Serializing json
    json_object = json.dumps(content_info_dict, indent=4)
    
    # Writing to sample.json
    with open(root_info_data+name+".json", "w") as outfile:
        outfile.write(json_object)
        outfile.close()

create_information_file(bbox_files,images,json_files)

shutil.copytree(cwd+"/Dataset/train",cwd+"/fullDataset")

shutil.rmtree(cwd+"/fullDataset/box")


"""# Downloading the new data into our local spacework

"""

shutil.rmtree(cwd+'/Dataset')

dir_path = cwd+"/fullDataset"
zip_dest = cwd+"/Dataset.zip"

!zip -r "/content/Dataset.zip" "/content/fullDataset"


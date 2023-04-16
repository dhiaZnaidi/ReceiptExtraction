# -*- coding: utf-8 -*-
"""dataset_calling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bMeQHaZHHuObDdNrk0xQQtyOifhOJ3AT
"""

import os
import json


import numpy as np
import tensorflow as tf

# -*- coding: utf-8 -*-

"""
Receipt dataset manager
"""



class ReceiptDetection:
    def __init__(self, path="", trainRatio=0.7, batch_size=32, floatType=32):
        super(ReceiptDetection, self).__init__()
        if floatType == 32:
            self.floatType = tf.float32
        elif floatType == 16:
            self.floatType = tf.float16
        else:
            raise Exception('floatType should be either 32 or 16')

        self.path = path
        self.img_resolution = (300,300)
        self.classes = {
            'background': 0,
            'total': 1,
            'date': 2
        }
        self.images_path = path + "/images/"
        self.annotations_path = path + "/info_data/"
        self.images_name = []
        if path != "":
            self.images_name = [
                im.replace(".jpg", "")
                for im in os.listdir(self.images_path)
                if os.path.isfile(os.path.join(self.images_path, im))
            ]
        self.number_samples = len(self.images_name)
        self.train_samples = int(self.number_samples * trainRatio)
        self.train_set = self.images_name[: self.train_samples - self.train_samples % batch_size]
        self.val_set = self.images_name[self.train_samples :]
        self.batches = [
            self.train_set[i : i + batch_size] for i in range(0, len(self.train_set), batch_size)
        ]

    def getRawData(self, images_name: list):
        from PIL import Image as Im
        """
        Method to get images and annotations from a list of images name
        Args:
            - (list) images name without extension
        Return:
            - (tf.Tensor) Images of shape:
                [number of images, self.img_resolution]
            - (list of tf.Tensor) Boxes of shape:
                [number of images, number of objects, 4]
            - (list tf.Tensor) Classes of shape:
                [number of images, number of objects]
        """
        images = []
        boxes = []
        classes = []
        for img in images_name:
            im = Im.open(self.images_path + img + ".jpg")
            f = self.annotations_path + img + ".json"
            f_open = open(f)
            data = json.load(f_open)
            roi = data['roi']
            left, top , right, bottom = roi.values()
            image = im.crop((left, top, right, bottom))


            #image = tf.keras.preprocessing.image.load_img(self.images_path + img + ".jpg")
            w, h = image.size[0], image.size[1]
            image = tf.image.resize(np.array(image), self.img_resolution)
            images_array = tf.keras.preprocessing.image.img_to_array(image) / 255.0
            images.append(images_array)

            # annotation
            boxes_img_i, classes_img_i = self.getAnnotations(img, (w, h))
            boxes.append(boxes_img_i)
            classes.append(classes_img_i)
        return tf.convert_to_tensor(images, dtype=self.floatType), boxes, classes

    def getAnnotations(self, image_name: str, resolution: tuple):
        """
        Method to get annotation: boxes and classes
        Args:
            - (str) image name without extension
            - (tuple) image resolution (W, H, C) or (W, H)
        Return:
            - (tf.Tensor) Boxes of shape: [number of objects, 4]
            - (tf.Tensor) Classes of shape: [number of objects]
        """
        boxes = []
        classes = []
        info_data = self.annotations_path + image_name + ".json"

        f_open = open(info_data)
        data = json.load(f_open)

        objects = data['total']
        classes = [self.classes["total"] for i in range(len(objects))]
        objects.append(data['date'])
        classes.append(self.classes["date"])
        ROI_x , ROI_y ,_ , _ = data['roi'].values()

        for obj in objects:
            xmin = float(obj['xmin']-ROI_x) / resolution[0]
            ymin = float(obj['ymin']-ROI_y) / resolution[1]
            xmax = float(obj['xmax']-ROI_x) / resolution[0]
            ymax = float(obj['ymax']-ROI_y) / resolution[1]

            # calculate cx, cy, width, height
            width = xmax - xmin
            height = ymax - ymin
            if xmin + width > 1.0 or ymin + height > 1.0 or xmin < 0.0 or ymin < 0.0:
                print(
                    "Boxe outside picture: (xmin, ymin, xmax, ymax):\
                      ({} {}, {}, {})".format(
                        xmin, ymin, xmax, ymax
                    )
                )

            boxes.append([xmin + width / 2.0, ymin + height / 2.0, width, height])


        return tf.convert_to_tensor(boxes, dtype=self.floatType), tf.convert_to_tensor(
            classes, dtype=tf.int16
        )

    

    def computeRectangleArea(self, xmin, ymin, xmax, ymax):
        return (xmax - xmin) * (ymax - ymin)

    



    def computeJaccardIdxSpeedUp(
        self, gt_box: tf.Tensor, default_boxes: tf.Tensor, iou_threshold: float
    ):
        """
        Method to get the boolean tensor where iou is superior to
        the specified threshold between the gt box and the default one
        D: number of default boxes
        Args:
            - (tf.Tensor) box with 4 parameters: cx, cy, w, h [4]
            - (tf.Tensor) box with 4 parameters: cx, cy, w, h [D, 4]
            - (float) iou threshold to use
        Return:
            - (tf.Tensor) 0 if iou > threshold, 1 otherwise [D]
        """
        # convert to xmin, ymin, xmax, ymax
        default_boxes = tf.concat(
            [
                default_boxes[:, :2] - default_boxes[:, 2:] / 2,
                default_boxes[:, :2] + default_boxes[:, 2:] / 2,
            ],
            axis=-1,
        )
        gt_box = tf.concat([gt_box[:2] - gt_box[2:] / 2, gt_box[:2] + gt_box[2:] / 2], axis=-1)
        gt_box = tf.expand_dims(gt_box, 0)
        gt_box = tf.repeat(gt_box, repeats=[default_boxes.shape[0]], axis=0)

        # compute intersection
        inter_xymin = tf.math.maximum(default_boxes[:, :2], gt_box[:, :2])
        inter_xymax = tf.math.minimum(default_boxes[:, 2:], gt_box[:, 2:])
        inter_width_height = tf.clip_by_value(inter_xymax - inter_xymin, 0.0, 300.0)
        inter_area = inter_width_height[:, 0] * inter_width_height[:, 1]

        # compute area of the boxes
        gt_box_width_height = tf.clip_by_value(gt_box[:, 2:] - gt_box[:, :2], 0.0, 300.0)
        gt_box_width_height_area = gt_box_width_height[:, 0] * gt_box_width_height[:, 1]

        default_boxes_width_height = tf.clip_by_value(
            default_boxes[:, 2:] - default_boxes[:, :2], 0.0, 300.0
        )
        default_boxes_width_height_area = (
            default_boxes_width_height[:, 0] * default_boxes_width_height[:, 1]
        )

        # compute iou
        iou = inter_area / (gt_box_width_height_area + default_boxes_width_height_area - inter_area)
        return tf.dtypes.cast(iou >= iou_threshold, tf.int16)

    def getLocOffsetsSpeedUp(self, gt_box: tf.Tensor, iou_bin: tf.Tensor, default_boxes: tf.Tensor):
        """
        Method to get the offset from default boxes to box_gt on cx, cy, w, h
        where iou_idx is 1
        D: number of default boxes
        Args:
            - (tf.Tensor) box with 4 parameters: cx, cy, w, h [4]
            - (tf.Tensor) 1 if iou > threshold, 0 otherwise [D]
            - (tf.Tensor) default boxes with 4 parameters: cx, cy, w, h [D, 4]
        Return:
            - (tf.Tensor) offsets if iou_bin == 1, otherwise 0 [D, 4]
        """
        gt_box = tf.expand_dims(gt_box, 0)
        gt_box = tf.repeat(gt_box, repeats=[default_boxes.shape[0]], axis=0)
        offsets = gt_box - default_boxes

        iou_bin = tf.expand_dims(iou_bin, 1)
        iou_bin = tf.repeat(iou_bin, repeats=[4], axis=1)
        offsets = offsets * tf.dtypes.cast(iou_bin, self.floatType)
        return offsets

    def getImagesAndGtSpeedUp(self, images_name: list, default_boxes: list):
        """
        Method to get the groud truth for confidence and localization
        S: number of stage
        D: number of default boxes
        B: batch size (number of images)
        Args:
            - (list) images name without extension
            - (tf.Tensor) default boxes per stage: [D, 4]
                4 parameters: cx, cy, w, h
        Return:
            - (tf.Tensor) Images of shape:
                [number of images, self.img_resolution]
            - (tf.Tensor) confs ground truth: [B, D]
            - (tf.Tensor) locs ground truth: [B, D, 4]
        """
        images, boxes, classes = self.getRawData(images_name)
        gt_confs = []
        gt_locs = []
        for i, gt_boxes_img in enumerate(boxes):
            gt_confs_per_image = tf.zeros([len(default_boxes)], tf.int16)
            gt_locs_per_image = tf.zeros([len(default_boxes), 4], self.floatType)
            iou_bin_masks = []
            for g, gt_box in enumerate(gt_boxes_img):
                iou_bin = self.computeJaccardIdxSpeedUp(gt_box, default_boxes, 0.5)
                for mask in iou_bin_masks:
                    iou_bin = tf.clip_by_value(iou_bin - mask, 0, 1)
                iou_bin_masks.append(iou_bin)
                gt_confs_per_image = gt_confs_per_image + iou_bin * classes[i][g]
                gt_locs_per_image = gt_locs_per_image + self.getLocOffsetsSpeedUp(
                    gt_box, iou_bin, default_boxes
                )
            gt_confs.append(gt_confs_per_image)
            gt_locs.append(gt_locs_per_image)

        return (
            images,
            tf.convert_to_tensor(gt_confs, dtype=tf.int16),
            tf.convert_to_tensor(gt_locs, dtype=self.floatType),
        )
# -*- coding: utf-8 -*-
"""VGG16_redefined.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zQAF-GuQW7oqH83ga2RS_WJK16SXreI3
"""

from tensorflow import keras
import tensorflow.keras.layers as tfl

"""### VGG16 Backbone"""

class VGG16_backbone(keras.Model):
    def __init__(self, input_shape=(224, 224, 3)):
        super(VGG16_backbone, self).__init__()

        '''
            Available layers
        '''
        self.conv_1_1_64 = tfl.Conv2D(
            input_shape=input_shape,
            filters=64,
            kernel_size=(3, 3),
            padding="same",
            activation="relu",
            name="Conv1_1",
        )
        self.conv_1_2_64 = tfl.Conv2D(
            filters=64, kernel_size=(3, 3), padding="same", activation="relu", name="Conv1_2"
        )
        self.maxpool_1_3_2x2 = tfl.MaxPool2D(pool_size=(2, 2), strides=(2, 2), padding='same')

        self.conv_2_1_128 = tfl.Conv2D(
            filters=128, kernel_size=(3, 3), padding="same", activation="relu", name="Conv2_1"
        )
        self.conv_2_2_128 = tfl.Conv2D(
            filters=128, kernel_size=(3, 3), padding="same", activation="relu", name="Conv2_2"
        )
        self.maxpool_2_3_2x2 = tfl.MaxPool2D(pool_size=(2, 2), strides=(2, 2), padding='same')

        self.conv_3_1_256 = tfl.Conv2D(
            filters=256, kernel_size=(3, 3), padding="same", activation="relu", name="Conv3_1"
        )
        self.conv_3_2_256 = tfl.Conv2D(
            filters=256, kernel_size=(3, 3), padding="same", activation="relu", name="Conv3_2"
        )
        self.conv_3_3_256 = tfl.Conv2D(
            filters=256, kernel_size=(3, 3), padding="same", activation="relu", name="Conv3_3"
        )
        self.maxpool_3_4_2x2 = tfl.MaxPool2D(pool_size=(2, 2), strides=(2, 2), padding='same')

        self.conv_4_1_512 = tfl.Conv2D(
            filters=512, kernel_size=(3, 3), padding="same", activation="relu", name="Conv4_1"
        )
        self.conv_4_2_512 = tfl.Conv2D(
            filters=512, kernel_size=(3, 3), padding="same", activation="relu", name="Conv4_2"
        )
        self.conv_4_3_512 = tfl.Conv2D(
            filters=512, kernel_size=(3, 3), padding="same", activation="relu", name="Conv4_3"
        )
        self.maxpool_4_4_2x2 = tfl.MaxPool2D(pool_size=(2, 2), strides=(2, 2), padding='same')

        self.conv_5_1_512 = tfl.Conv2D(
            filters=512, kernel_size=(3, 3), padding="same", activation="relu", name="Conv5_1"
        )
        self.conv_5_2_512 = tfl.Conv2D(
            filters=512, kernel_size=(3, 3), padding="same", activation="relu", name="Conv5_2"
        )
        self.conv_5_3_512 = tfl.Conv2D(
            filters=512, kernel_size=(3, 3), padding="same", activation="relu", name="Conv5_3"
        )
        self.maxpool_5_4_2x2 = tfl.MaxPool2D(pool_size=(2, 2), strides=(2, 2), padding='same')

        self.flatten_6_1 = tfl.Flatten()
        self.dense_6_2_4096 = tfl.Dense(4096, activation='relu')
        self.dense_6_3_4096 = tfl.Dense(4096, activation='relu')
        self.dense_6_4_10 = tfl.Dense(1000, activation='softmax')

    def getModel(self):
    
        return keras.models.Sequential(
            [
                self.conv_1_1_64,
                self.conv_1_2_64,
                self.maxpool_1_3_2x2,
                # Stage 2
                self.conv_2_1_128,
                self.conv_2_2_128,
                self.maxpool_2_3_2x2,
                # Stage 3
                self.conv_3_1_256,
                self.conv_3_2_256,
                self.conv_3_3_256,
                self.maxpool_3_4_2x2,
                # Stage 4
                self.conv_4_1_512,
                self.conv_4_2_512,
                self.conv_4_3_512,
                self.maxpool_4_4_2x2,
                # Stage 5
                self.conv_5_1_512,
                self.conv_5_2_512,
                self.conv_5_3_512,
                self.maxpool_5_4_2x2,
                # Stage 6
                self.flatten_6_1,
                self.dense_6_2_4096,
                self.dense_6_3_4096,
                self.dense_6_4_10,
            ]
        )
    
    def getUntilStage4(self):
        return keras.models.Sequential(
            [
                self.conv_1_1_64,
                self.conv_1_2_64,
                self.maxpool_1_3_2x2,
                # Stage 2
                self.conv_2_1_128,
                self.conv_2_2_128,
                self.maxpool_2_3_2x2,
                # Stage 3
                self.conv_3_1_256,
                self.conv_3_2_256,
                self.conv_3_3_256,
                self.maxpool_3_4_2x2,
                # Stage 4
                self.conv_4_1_512,
                self.conv_4_2_512,
                self.conv_4_3_512,
            ]
        )

    def getUntilStage5(self):
        return keras.models.Sequential(
            [
                self.conv_1_1_64,
                self.conv_1_2_64,
                self.maxpool_1_3_2x2,
                # Stage 2
                self.conv_2_1_128,
                self.conv_2_2_128,
                self.maxpool_2_3_2x2,
                # Stage 3
                self.conv_3_1_256,
                self.conv_3_2_256,
                self.conv_3_3_256,
                self.maxpool_3_4_2x2,
                # Stage 4
                self.conv_4_1_512,
                self.conv_4_2_512,
                self.conv_4_3_512,
                # Stage 5
                self.maxpool_4_4_2x2,
                self.conv_5_1_512,
                self.conv_5_2_512,
                self.conv_5_3_512,
            ]
        )

    def getStage5(self):
        return keras.models.Sequential([self.maxpool_4_4_2x2, self.conv_5_1_512, self.conv_5_2_512, self.conv_5_3_512])
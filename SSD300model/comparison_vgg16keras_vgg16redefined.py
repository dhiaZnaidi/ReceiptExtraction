# -*- coding: utf-8 -*-
"""comparison_VGG16Keras_VGG16redefined.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TiJkCqGEbNL9YBIxBW8ImxoqbHygnSOX

## Comparison between the two implemented architectures
"""

from tensorflow import keras
from tensorflow.keras.applications.vgg16 import VGG16
from vgg16_redefined import VGG16_backbone

VGG16_keras = VGG16(weights='imagenet')

VGG16_keras.summary()

VGG16_model = VGG16_backbone().getModel()
VGG16_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
                    loss=keras.losses.categorical_crossentropy,
                    metrics=['accuracy'])
VGG16_model.summary()


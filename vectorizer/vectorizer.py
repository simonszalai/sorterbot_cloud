import os
import csv
import requests
import base64
import zipfile
import time
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.autograd import Variable


class ImageFolderWithPaths(datasets.ImageFolder):
    """Custom dataset that includes image file paths. Extends
  torchvision.datasets.ImageFolder
  """

    # override the __getitem__ method. this is the method that dataloader calls
    def __getitem__(self, index):
        # this is what ImageFolder normally returns
        original_tuple = super(ImageFolderWithPaths, self).__getitem__(index)
        # the image file path
        path = self.imgs[index][0]
        # make a new tuple that includes original and the path
        tuple_with_path = original_tuple + (path,)
        return tuple_with_path


batchsize = 1024
data_transforms = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

dataset = ImageFolderWithPaths(f"/tmp/extractedzips/{zipname}", data_transforms)
dataloader = torch.utils.data.DataLoader(
    dataset, batch_size=batchsize, shuffle=False, num_workers=4
)


outputs = list()
batchnr = 1

for inputs, _, paths in dataloader:
    paths = [path.rsplit("/", 1)[-1] for path in paths]
    time1 = time.time()
    vectors = torch.zeros((batchsize, 512))

    def copy_data(m, i, o):
        vectors.copy_(o.data.squeeze())

    hook = layer.register_forward_hook(copy_data)
    #   inputs = inputs.to(device)
    model(inputs)
    hook.remove()
    full_data = np.column_stack((paths, vectors))

    with open(
        f"/dbfs/mnt/csv/{zipname}/batchOf{batchsize}_{batchnr}.csv", "w"
    ) as outcsv:
        writer = csv.writer(outcsv, delimiter=",")
        writer.writerows(full_data)

    print(((time.time() - time1) / batchsize) * 1000)
    print(f"{len(inputs)} image vectorized")
    batchnr += 1


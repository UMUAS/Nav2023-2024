import torch
from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_coords
from utils.torch_utils import select_device
from utils.augmentations import letterbox
import numpy as np
from PIL import Image

device = select_device('')
model = DetectMultiBackend('yolo5s.pt', device=device, dnn=False)
model.warmup(imgsz=(1, 3, 640, 640), half=False)

train = "../train/images"
test = "../test/images"
valid = "../valid/images"

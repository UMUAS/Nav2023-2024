import time
import cv2
import torch


class ObjectDetection:

    def __init__(self, pipe):
        self.pipe = pipe

    def getDirection(self):
        image = self.pipe.recv()
        direction = self.process(image)

        self.pipe.send(direction)

    def process(self, image):
        direction = None
        # do stuff...
        return direction
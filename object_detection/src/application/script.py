import time
import cv2
import torch
from PIL import Image
import numpy as np


class ObjectDetection:

    image_array = []

    MODEL_PATH = "../../object_detection_model/yolov5s.pt"

    def __init__(self, pipe):
        self.pipe = pipe
        # Load the model
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', self.MODEL_PATH)
        self.current_largest_area = 0  # Initialize the largest area
        self.current_largest_distance = 0  # Initialize the largest distance
        self.images = 0
        print("------ Model loaded successfully ------")

    def getDirection(self):
        while True:
            image = self.pipe.recv()
            direction = self.process(image)
            self.pipe.send(direction)

    def process(self, image):
        # Convert the received image
        # pil_image = Image.fromarray(image)

        # Perform inference
        results = self.model(image)
        bounding_boxes = results.xyxy[0]

        # Calculate the area of each bounding box
        largest_area = 0
        largest_distance = 0
        # for box in bounding_boxes:
        #     x1, y1, x2, y2, _, _ = box
        #     area = (x2 - x1) * (y2 - y1)
        #     if area > largest_area:
        #         largest_area = area

        for box in bounding_boxes:
            x1, y1, x2, y2, _, _ = box
            distance = (x2 - x1)
            self.image_array.append(distance)

        if len(self.image_array) > 10:
            largest_distance = self.image_array[-1] - self.image_array[0]
            # Update direction based on area comparison
            direction = None
            print(f"new: {largest_distance}, old: {self.current_largest_distance}")
            if largest_distance > 0:
                self.current_largest_distance = largest_distance
                direction = "moving closer"
            else:
                direction = "moving away"

            self.images += 1
            if self.images == 200:
                self.images = 0
                self.current_largest_distance = 0

            return direction
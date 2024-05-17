import time
import cv2
import torch
from PIL import Image
import numpy as np


class ObjectDetection:

    image_array = []
    currennt_direction = ""

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
           
            if(len(self.image_array) == 20):
                self.image_array.pop(0)
                self.image_array.append(image)
                direction = self.process()
                self.pipe.send(direction)
            else:
                self.image_array.append(image)
                self.pipe.send("calculating")


    def process(self):
        # Convert the received image
        # pil_image = Image.fromarray(image)

        # Perform inference
        results_start = self.model(self.image_array[0])
        results_end = self.model(self.image_array[-1])
        bounding_boxes_start = results_start.xyxy[0]
        bounding_boxes_end = results_end.xyxy[0]
       

        # Calculate the area of each bounding box
        x_distance_start = 0 
        x_distance_end = 0 

        for box in bounding_boxes_start:
            x1, y1, x2, y2, _, _ = box
           
            x_distance_start = (x2 - x1)
        
        for box in bounding_boxes_end:
            x1, y1, x2, y2, _, _ = box
            x_distance_end = (x2 - x1)

        # for box in bounding_boxes:
        #     x1, y1, x2, y2, _, _ = box
        #     area = (x2 - x1) * (y2 - y1)
        #     if area > largest_area:
        #         largest_area = area

        # for box in bounding_boxes:
        #     x1, y1, x2, y2, _, _ = box
        #     distance = (x2 - x1)
        #     if distance > largest_distance:
        #         largest_distance = distance

        # Update direction based on area comparison
        direction = None
        print(f"new: {x_distance_start}, old: {x_distance_end}")
        if x_distance_start and x_distance_end:
            if x_distance_end > x_distance_start:
                direction = "moving closer"
                self.currennt_direction = direction
            elif x_distance_end < x_distance_start:
                direction = "moving away"
                self.currennt_direction = direction
            else:
                direction = "stationary"
        else:
            direction = "could not detect box"


        return direction


class Detection:
    MODEL_PATH = "../../object_detection_model/yolov5s.pt"
    img_array = []
    current_direction = ''

    def __init__(self) -> None:
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', self.MODEL_PATH)
        
        self.target_coords = (None, None) # Initialize target coordinates to None
        print("------ Model loaded successfully ------")

    def get_direction(self, img):
        direction = "None"
        if len(self.img_array) == 50:
            self.img_array.pop(0)
            self.img_array.append(img)
            direction = self.process_frame()
        else:
            self.img_array.append(img)

        return direction

    def update_target_coords(self, coords):
        self.target_coords = coords

    def process_frame(self):
        # print('------- Performing Inference ----------')
        first_frame = self.model(self.img_array[0])
        last_frame = self.model(self.img_array[-1])

        first_bbox = first_frame.xyxy[0]
        last_bbox = last_frame.xyxy[0]


        # a1 and a2 are for using the area of the bounding box to determine
        # proximity to the landing pad
        # We can use x_width_1 or x_width_2 instead of area
        a1 = 0
        a2 = 0
        x_width_1 = 0
        x_width_2 = 0

        for box in first_bbox:
            x1, y1, x2, y2 = box[:4]
            x_width_1 = (x2 - x1)
            a1 = (x2 - x1) * (y2 - y1)

        for box in last_bbox:
            x1, y1, x2, y2 = box[:4]
            x_width_2 = (x2 - x1)
            a2 = (x2 - x1) * (y2 - y1)

        direction = None
        print(f"new: {x_width_1}, old: {x_width_2}", end = ' ')
        if a1 and a2:
            if a2 > a1:
                direction = 'moving closer'
                self.current_direction = direction
            elif a2 < a1:
                direction = 'moving away'
                self.current_direction = direction
            else:
                direction = 'stationary'
                # self.current_direction = 'stationary'
        else:
            direction = 'could not detect box'
        print(f"Direction: {direction}", end = ' ')
        return direction

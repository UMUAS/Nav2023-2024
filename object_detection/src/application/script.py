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
                direction = self.process()
                self.image_array.pop(0)
                self.image_array.append(image)
                self.pipe.send(direction)
            else:
                self.image_array.append(image)
                self.pipe.send("calculating")

    def detect_center(self,frame,x1,x2,y1,y2):
        #get midpoint
        center_x = (int(x2)+int(x1))//2
        center_y = (int(y2)+int(y1))//2
        pad_coordinates = (center_x,center_y)
        #get center of the frame
        (frame_height, frame_width) = frame.shape[:2] #w:image-width and h:image-height
        center_coordinates = (frame_width//2, frame_height//2)
        if(center_coordinates[0] == pad_coordinates[0] and center_coordinates[1] == pad_coordinates[1]):
            return (True,0,0)
        else:
            print(center_coordinates[1], center_y)
            x_distance = center_x-center_coordinates[0]
            y_distance = center_y - center_coordinates[1]
            return (False,x_distance,y_distance)
        
        
        


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
            res =self.detect_center(self.image_array[-1],x1,x2,y1,y2)
            if(res[0]):
                print("pad in the centre")
            else:
                print(f"x distance:{res[1]} y distance {res[2]}")
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

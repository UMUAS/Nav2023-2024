import cv2
import numpy as np

folder_path = (
    "mnt/c/Users/danie/Documents/Personal/UMUAS/Nav2023-2024/object_detection/assests/frame_879.jpg"
)

# for filename in os.listdir(folder_path):
# Getting path to the current image and reading it into cv, converting to right color space
# filename = os.listdir(folder_path)
# image_path = os.path.join(folder_path, filename)
image_path = "sample_path"
image = cv2.imread(image_path)
img_cnvrt = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Detecting blue color
lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])

# Reducing noise
# noice_reduce = np.ones((5,5),np.uint8)
# mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, noice_reduce)
# mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, noice_reduce)

mask = cv2.inRange(img_cnvrt, lower_blue, upper_blue)

circle_detect = cv2.HoughCircles(
    mask, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=400
)

contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    area = cv2.contourArea(cnt)

    if area > 500:
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        center = (int(x), int(y))
        radius = int(radius)

        if radius > 10:
            cv2.circle(image, center, radius, (0, 255, 0), 2)
            cv2.circle(image, center, 5, (0, 0, 255), -1)
cv2.imwrite("test_landing_pad.jpg", image)

# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""
Perform test request
"""

import pprint
import requests
import cv2

DETECTION_URL = 'http://localhost:5000/v1/object-detection/yolov5s'
IMAGE = '99.jpg'

# Read image
with open(IMAGE, 'rb') as f:
    image_data = f.read()

response = requests.post(DETECTION_URL, files={'image': image_data}).json()
print(response)

#[{'xmin': 113.3052215576, 'ymin': 69.0047912598, 'xmax': 563.3659057617, 'ymax': 494.6313171387, 'confidence': 0.5381137133, 'class': 16, 'name': 'dog'}]

counter=1
for row in response:
    print(row['xmin'], row['ymin'], row['xmax'], row['ymax'], row['confidence'])
    x1 = int(row['xmin'])
    y1 = int(row['ymin'])
    x2 = int(row['xmax'])
    y2 = int(row['ymax'])
    
    # Load the image
    image = cv2.imread('99.jpg')

    # Draw the bounding box on the image
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # (0, 255, 0) represents color in BGR format, 2 represents thickness of rectangle

    # Show the image
    cv2.imshow('Bounding Box', image)
    # Save the image to a folder
    cv2.imwrite('99_predict.jpg', image)

    cv2.waitKey(0)  # Wait for a key press
    cv2.destroyAllWindows()  # Close all windows
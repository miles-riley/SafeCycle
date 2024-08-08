from ultralytics import YOLO
import cv2
import os
from picamera2 import Picamera2

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')  # You can choose different model sizes like 'yolov8s.pt', 'yolov8m.pt', etc.

# Function to get objects using YOLOv8
def getObjects(img, conf_threshold=0.5):
    results = model(img)  # Run inference
    detections = results[0].boxes  # Access bounding boxes and related data

    objectInfo = []
    for detection in detections:
        box = detection.xyxy[0].cpu().numpy()  # Get bounding box coordinates (x1, y1, x2, y2)
        conf = detection.conf.item()  # Get confidence score
        class_id = int(detection.cls)  # Get class ID

        if conf > conf_threshold:
            x1, y1, x2, y2 = box
            box = [int(x1), int(y1), int(x2 - x1), int(y2 - y1)]
            className = model.names[class_id]
            objectInfo.append([box, className])
            print(f"{className}: {conf:.2f}, Box: {box}")
            
            if box[2] >= 200:
                print("You're too close.")

            # Draw bounding box
            cv2.rectangle(img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), (0, 255, 0), 2)
            cv2.putText(img, f'{className} {conf:.2f}', (box[0], box[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return img, objectInfo



if __name__ == "__main__":
    # Start Pi camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()

    while True:
        img = picam2.capture_array("main")
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        img = cv2.flip(img, 0)

        result, objectInfo = getObjects(img)

        cv2.imshow("Output", img)

        k = cv2.waitKey(200)
        if k == 27:    # Esc key to stop
            # EXIT
            picam2.stop()
            cv2.destroyAllWindows()
            break


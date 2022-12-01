from celery import shared_task

from yolo.models import YoloClass, YoloObject

import cv2 as cv
import numpy as np


@shared_task
def load_image(photo_id, path):
    classes = open('C://Users//idmit//GalleryAI//yolo//classes.txt').read().strip().split('\n')

    net = cv.dnn.readNetFromDarknet('C://Users//idmit//GalleryAI//yolo//yolov3.cfg', 'C://Users//idmit//GalleryAI//yolo//yolov3.weights')
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)

    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

    img0 = cv.imread(path)
    img = img0.copy()

    blob = cv.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)

    net.setInput(blob)
    outputs = net.forward(ln)

    outputs = np.vstack(outputs)
    conf = 0.3

    H, W = img.shape[:2]

    boxes = []
    confidences = []
    classIDs = []

    for output in outputs:
        scores = output[5:]
        classID = np.argmax(scores)
        confidence = scores[classID]
        if confidence > conf:
            x, y, w, h = output[:4] * np.array([W, H, W, H])
            p0 = int(x - w // 2), int(y - h // 2)
            boxes.append([*p0, int(w), int(h)])
            confidences.append(float(confidence))
            classIDs.append(classID)

    indices = cv.dnn.NMSBoxes(boxes, confidences, conf, conf - 0.1)
    if len(indices) > 0:
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            yolo_class = YoloClass.objects.get(name=classes[classIDs[i]])
            yolo_object = YoloObject.objects.create(photo_id=photo_id, yolo_class=yolo_class, x=x, y=y, width=w,
                                                    height=h, accuracy=confidences[i])
            yolo_class.photos.add(yolo_object.photo)
            yolo_class.save()

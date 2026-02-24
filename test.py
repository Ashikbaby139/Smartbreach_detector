import cv2
import numpy as np

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    print("RET:", ret, " DTYPE:", frame.dtype, " SHAPE:", frame.shape)
    print("CONTIG:", frame.flags['C_CONTIGUOUS'])
    cv2.imshow("TEST", frame)

    if cv2.waitKey(1) == 27:
        break

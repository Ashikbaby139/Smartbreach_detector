import cv2

print("🔍 Scanning for available cameras...")
for i in range(5):  # test first 5 indexes (0–4)
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Camera found at index {i}")
        cap.release()
    else:
        print(f"❌ No camera at index {i}")

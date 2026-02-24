# register_user.py
import cv2
import face_recognition
import pickle
import os
from datetime import datetime

OUT = "encodings/authorized.pkl"
os.makedirs("encodings", exist_ok=True)

def capture_and_save(name="authorized_user", samples=5):
    # ✅ Use camera index 2 instead of 0
    
    
    cap = cv2.VideoCapture(0)



    if not cap.isOpened():
        print("❌ Unable to access camera at index 2. Try another index (0, 1, etc.) if this doesn’t work.")
        return

    encodings = []
    print("Look at the camera. Press SPACE to capture (or wait for auto-capture).")
    captured = 0

    while captured < samples:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Can't read from camera.")
            break

        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow("Register - press SPACE to capture", small)
        k = cv2.waitKey(1)

        if k == 32:  # SPACE key
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            if boxes:
                enc = face_recognition.face_encodings(rgb, boxes)[0]
                encodings.append(enc)
                captured += 1
                print(f"✅ Captured {captured}/{samples}")
            else:
                print("❌ No face detected. Try again.")

    cap.release()
    cv2.destroyAllWindows()

    if encodings:
        data = {"name": name, "encodings": encodings, "registered_at": datetime.utcnow().isoformat()}
        with open(OUT, "wb") as f:
            pickle.dump(data, f)
        print("✅ Saved encodings to", OUT)
    else:
        print("⚠️ No encodings captured.")

if __name__ == "__main__":
    name = input("Enter the display name for authorized user (e.g. 'Ash'): ").strip() or "authorized"
    capture_and_save(name=name, samples=5)

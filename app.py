from flask import Flask, render_template, jsonify, request
import threading, time, cv2, numpy as np, os, pickle, base64
from datetime import datetime
from playsound3 import playsound
import mediapipe as mp
import ctypes

# ---------------- INIT ----------------
app = Flask(__name__)

AUTHORIZED = None
ENCODING_PATH = "encodings/authorized.pkl"
SNAPSHOT_DIR = "static/snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

status = {"state": "idle", "last_event": None, "last_person": None}

monitor_running = True
cap = None
CAM_INDEX = 0
MOTION_THRESHOLD = 1000

# Mediapipe detector
mp_face = mp.solutions.face_detection
detector = mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# FaceNet embedder
embedder = cv2.dnn.readNetFromTorch("openface.nn4.small2.v1.t7")

# ---------------- AUTH LOAD/SAVE ----------------
def load_authorized():
    global AUTHORIZED
    if os.path.exists(ENCODING_PATH):
        with open(ENCODING_PATH, "rb") as f:
            AUTHORIZED = pickle.load(f)
            print("✅ Authorized loaded:", AUTHORIZED.get("name"))
    else:
        AUTHORIZED = None
        print("⚠️ No authorized user registered")

def save_authorized(name, enc):
    data = {"name": name, "enc": enc}
    with open(ENCODING_PATH, "wb") as f:
        pickle.dump(data, f)
    print("✅ Saved new authorized:", name)
    load_authorized()

# ---------------- EMBEDDING ----------------
def get_embedding(face_img):
    face_img = cv2.resize(face_img, (96, 96))
    blob = cv2.dnn.blobFromImage(face_img, 1.0/255.0, (96, 96),
                                 (0, 0, 0), swapRB=True, crop=True)
    embedder.setInput(blob)
    vec = embedder.forward()
    return vec.flatten()

def cosine(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return -1
    return float(np.dot(a, b) / denom)

# ---------------- MONITOR LOOP ----------------
def monitor_loop():
    global cap, monitor_running

    load_authorized()
    print("🎥 Monitor thread started")
    status["state"] = "monitoring"

    prev_gray = None

    while True:
        if not monitor_running:
            if cap:
                cap.release()
                cap = None
            time.sleep(1)
            continue

        if cap is None:
            cap = cv2.VideoCapture(CAM_INDEX)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print("📷 Camera activated")
            time.sleep(1)

        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        # -------- Motion Detection --------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if prev_gray is None:
            prev_gray = gray
            continue

        frame_delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_score = np.sum(thresh) / 255
        prev_gray = gray

        if motion_score < MOTION_THRESHOLD:
            time.sleep(0.1)
            continue

        # -------- Face Detection --------
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector.process(rgb)

        if not results.detections:
            # NO FACE = DO NOTHING (VERY IMPORTANT FIX)
            status["state"] = "monitoring"
            status["last_person"] = None
            time.sleep(0.1)
            continue

        # We only use the FIRST detected face
        det = results.detections[0]
        bbox = det.location_data.relative_bounding_box
        h, w, _ = frame.shape

        x1 = max(0, int(bbox.xmin * w))
        y1 = max(0, int(bbox.ymin * h))
        x2 = min(w, x1 + int(bbox.width * w))
        y2 = min(h, y1 + int(bbox.height * h))

        face = frame[y1:y2, x1:x2]
        if face.size == 0:
            continue

        # -------- Embedding --------
        emb = get_embedding(face)

        # -------- Compare with authorized --------
        if AUTHORIZED and "enc" in AUTHORIZED:
            sim = cosine(emb, AUTHORIZED["enc"])
            print("Similarity:", sim)

            if sim > 0.45:
                # AUTHORIZED USER
                status["state"] = "authorized"
                status["last_person"] = AUTHORIZED["name"]
                status["last_event"] = f"Authorized recognized at {datetime.utcnow().isoformat()}"
                continue

            else:
                # UNKNOWN PERSON → BREACH
                status["state"] = "breach"
                status["last_person"] = "unknown"
                status["last_event"] = f"Breach at {datetime.utcnow().isoformat()}"
                print("🚨 Unknown face detected! Locking...")

                # Save snapshot
                fname = f"breach_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.jpg"
                cv2.imwrite(os.path.join(SNAPSHOT_DIR, fname), face)

                # Lock workstation
                try:
                    ctypes.windll.user32.LockWorkStation()
                except:
                    pass

        time.sleep(0.1)

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    global monitor_running
    monitor_running = True
    return render_template("index.html", status=status)

@app.route("/register")
def register_page():
    global monitor_running, cap
    monitor_running = False
    if cap:
        cap.release()
        cap = None
    return render_template("register.html")

@app.route("/save_face", methods=["POST"])
def save_face():
    name = request.form.get("name", "authorized")
    img_b64 = request.form.get("image")

    if not img_b64 or "," not in img_b64:
        return jsonify({"success": False, "msg": "Invalid image"})

    header, encoded = img_b64.split(",", 1)
    encoded += "=" * (-len(encoded) % 4)

    img_bytes = base64.b64decode(encoded)
    img_np = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = detector.process(rgb)
    if not results.detections:
        return jsonify({"success": False, "msg": "No face found"})

    det = results.detections[0]
    bbox = det.location_data.relative_bounding_box
    h, w, _ = frame.shape

    x1 = max(0, int(bbox.xmin * w))
    y1 = max(0, int(bbox.ymin * h))
    x2 = min(w, x1 + int(bbox.width * w))
    y2 = min(h, y1 + int(bbox.height * h))

    face = frame[y1:y2, x1:x2]
    emb = get_embedding(face)

    save_authorized(name, emb)
    return jsonify({"success": True, "msg": "Registration successful!"})

@app.route("/status")
def get_status():
    return jsonify(status)
from flask import send_from_directory, redirect, url_for

# ---------------- BREACH IMAGES PAGE ----------------
@app.route("/breaches")
def breach_images():
    folder = SNAPSHOT_DIR
    if not os.path.exists(folder):
        os.makedirs(folder)

    images = sorted(os.listdir(folder), reverse=True)
    images = [img for img in images if img.lower().endswith((".jpg", ".png"))]

    return render_template("breaches.html", images=images)


# ---------------- DELETE BREACH IMAGE ----------------
@app.route("/delete_breach/<filename>", methods=["POST"])
def delete_breach(filename):
    file_path = os.path.join(SNAPSHOT_DIR, filename)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Deleted breach image: {filename}")
        else:
            print("⚠️ File not found:", filename)
    except Exception as e:
        print("❌ Error deleting file:", e)

    return redirect(url_for('breach_images'))


# ---------------- RUN ----------------
if __name__ == "__main__":
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=False)

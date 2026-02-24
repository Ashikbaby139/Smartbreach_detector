# SecureSense – Laptop Security System


SecureSense is a computer vision–based laptop security system designed to monitor the user’s environment, authenticate the person in front of the device, and detect unauthorized access in real time.  

The system integrates facial authentication, motion detection, automated alerts, and evidence capture to provide reliable and automated physical device security.

---

## 🚀 Core Features
- 👤 Face-based user authentication  
- 🎥 Continuous real-time webcam monitoring  
- 🔎 Motion and face detection  
- 🚨 Alarm trigger for unauthorized access  
- 📸 Intruder snapshot capture with timestamp  
- 🔒 Automatic workstation lock  
- 🌐 Web interface for registration and breach management  
- ⚡ Background monitoring module  

---

## 🧠 System Workflow

### 1️⃣ User Registration
- The authorized user registers via a web interface.
- Multiple facial images are captured through the webcam.
- Images are preprocessed and normalized.
- Facial encodings are generated and securely stored.
- These encodings serve as the reference for real-time verification.

### 2️⃣ Continuous Monitoring
- The monitoring module runs in the background.
- Webcam frames are normalized for consistent processing.
- Motion detection identifies activity.
- Face detection extracts facial data from frames.
- Extracted encodings are compared with stored authorized data.

### 3️⃣ Authentication Logic
- ✅ If the face matches the stored encoding → Normal access continues.
- ❌ If no match is found or an unknown person remains present → Threat detection is triggered.

### 4️⃣ Automated Threat Response
When unauthorized access is detected:
- An alarm sound is played.
- A snapshot of the intruder is captured.
- The image is saved with a timestamp.
- The workstation is automatically locked.
- Breach images are stored in a dedicated directory.
- Images can be viewed or deleted via the web interface.

---

## 🛠 Technologies Used
- Python  
- OpenCV  
- Face Recognition (Facial Encoding & Matching)  
- Flask (Web Framework)  
- HTML / CSS  
- OS-level system locking  

---

## 📂 Project Structure

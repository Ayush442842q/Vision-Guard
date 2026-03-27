# 👁️ Vision Guard

Vision Guard is a lightweight computer vision-based anomaly detection system that monitors camera input in real-time and triggers an alert using a buzzer sound when unusual activity is detected.

---

## 🚀 Features

* 🎥 Real-time video stream processing
* ⚡ Motion / anomaly detection
* 🔊 Instant alert using buzzer sound (speaker)
* 🧠 Simple and efficient logic using OpenCV
* 🖥️ Works locally (no cloud required)

---

## 📂 Project Structure

```
Vision guard/
│── motion.py                # Core motion detection logic
│── motion_detector.py       # Main execution script
│── env/                     # Virtual environment (optional)
│── duniya/                  # Experimental / extra files
│── .vs/                     # IDE config files
```

---

## ⚙️ Installation

### 1. Clone the repository

```
git clone https://github.com/your-username/vision-guard.git
cd vision-guard
```

### 2. Create virtual environment (recommended)

```
python -m venv env
env\Scripts\activate
```

### 3. Install dependencies

```
pip install opencv-python numpy
```

---

## ▶️ Usage

Run the project:

```
python motion_detector.py
```

---

## 🧠 How It Works

1. Captures video stream from webcam or camera
2. Converts frames to grayscale and applies blur
3. Computes difference between frames
4. Detects motion based on threshold
5. Triggers buzzer alert when anomaly is detected

---

## 🔊 Alert System

When abnormal motion is detected:

* A buzzer sound is played via system speaker

You can extend it to:

* 📱 Notifications (Telegram / Email)
* 📊 Logging system
* 📸 Save snapshots

---

## 📌 Future Improvements

* 🔍 Face recognition
* 📈 Activity analytics
* 🌐 Remote monitoring
* 📦 YOLO object detection
* 📁 Save anomaly images

---

## 🤝 Contributing

Feel free to fork this repository and improve it.

---

## 📜 License

This project is licensed under the MIT License.

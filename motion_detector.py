#!/usr/bin/env python3
"""
motion_detector.py

- Detects motion from the default camera (index 0).
- When motion is detected:
  - Saves a timestamped JPEG to disk.
  - Sends the image as a Telegram message (requires bot token + chat id).
  - Rings a buzzer connected to a GPIO pin (Raspberry Pi).
- Configure variables in the CONFIG section below.

Requirements:
  pip install opencv-python numpy requests
  On Raspberry Pi: pip install RPi.GPIO
"""

import cv2
import numpy as np
import time
import os
import requests
from datetime import datetime

# CONFIG - set these values before running
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
BUZZER_PIN = 18                 # BCM pin number for buzzer (change as needed)
CAMERA_INDEX = 0                # 0 for default camera
SAVE_DIR = "captures"           # directory to save photos
MOTION_MIN_AREA = 2000          # minimum contour area in pixels to count as motion
MOTION_DELTA_THRESH = 25        # threshold for frame delta
MOTION_BLUR_SIZE = (21, 21)     # blur size used for smoothing
ALERT_COOLDOWN = 30             # seconds to wait after alert to resume detection
BUZZER_DURATION_SEC = 2         # how many seconds to ring buzzer
BUZZER_PULSE_INTERVAL = 0.05    # toggle interval while buzzing (seconds)
# END CONFIG

# Prepare save directory
os.makedirs(SAVE_DIR, exist_ok=True)

# Try to import RPi.GPIO; provide a no-op fallback for non-Pi environments
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    _HAS_GPIO = True
except Exception:
    _HAS_GPIO = False

def buzz(duration_secs: float):
    """Ring the buzzer for duration_secs. If no GPIO available, print a message."""
    if not _HAS_GPIO:
        print(f"[buzz] (GPIO not available) would buzz for {duration_secs} sec")
        return
    end = time.time() + duration_secs
    try:
        while time.time() < end:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(BUZZER_PULSE_INTERVAL)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(BUZZER_PULSE_INTERVAL)
    except KeyboardInterrupt:
        GPIO.output(BUZZER_PIN, GPIO.LOW)

def send_telegram_photo(token: str, chat_id: str, photo_path: str, caption: str = None):
    """Send a photo via Telegram bot API."""
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption
            resp = requests.post(url, files=files, data=data, timeout=20)
        resp.raise_for_status()
        print(f"[telegram] Photo sent: {photo_path}")
    except Exception as ex:
        print(f"[telegram] Failed to send photo: {ex}")

def save_frame(frame, prefix="motion"):
    """Save BGR frame to disk with timestamped name and return filepath."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{ts}.jpg"
    path = os.path.join(SAVE_DIR, filename)
    cv2.imwrite(path, frame)
    return path

def main():
    print("Starting motion detector...")
    print("Press Ctrl+C to exit.")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Failed to open camera. Exiting.")
        return

    # allow camera to warm up
    time.sleep(2.0)

    first_frame = None
    last_alert_time = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from camera.")
                break

            # Resize frame for faster processing (optional)
            # frame = cv2.resize(frame, (640, 480))

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, MOTION_BLUR_SIZE, 0)

            if first_frame is None:
                first_frame = gray.copy().astype("float")
                continue

            # Use running average background model
            cv2.accumulateWeighted(gray, first_frame, 0.5)
            background = cv2.convertScaleAbs(first_frame)

            # compute difference between current frame and background
            frame_delta = cv2.absdiff(background, gray)
            thresh = cv2.threshold(frame_delta, MOTION_DELTA_THRESH, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)

            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            motion_detected = False

            for c in contours:
                if cv2.contourArea(c) < MOTION_MIN_AREA:
                    continue
                # motion found
                motion_detected = True
                break

            now = time.time()
            if motion_detected and (now - last_alert_time) > ALERT_COOLDOWN:
                last_alert_time = now
                filepath = save_frame(frame, prefix="motion")
                caption = f"Motion detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                # Send notification (non-blocking-ish)
                try:
                    send_telegram_photo(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, filepath, caption=caption)
                except Exception as e:
                    print(f"Error sending telegram: {e}")

                # Buzz
                try:
                    buzz(BUZZER_DURATION_SEC)
                except Exception as e:
                    print(f"Error buzzing: {e}")

                print(f"[alert] Motion -> saved {filepath}")

            # small delay to reduce CPU
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        cap.release()
        if _HAS_GPIO:
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            GPIO.cleanup()
        print("Exiting.")

if __name__ == "__main__":
    main()
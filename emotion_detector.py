import cv2
import numpy as np
from fer import FER
import threading

class EmotionDetector:
    def __init__(self, video_source=0):
        self.detector = FER(mtcnn=True)
        self.cap = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)  # DirectShow for faster init
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        self.lock = threading.Lock()
        
    def get_emotion_frame(self):
        """Ultra-fast frame capture with minimal delay"""
        with self.lock:
            self.cap.grab()  # Clear buffer
            ret, frame = self.cap.read()
            if not ret:
                return None, None
            
            # Process in background thread
            emotions = None
            def detect():
                nonlocal emotions
                try:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.detector.detect_emotions(rgb)
                    if results:
                        emotions = results[0]['emotions']
                except:
                    pass
            
            t = threading.Thread(target=detect)
            t.start()
            t.join(timeout=0.3)  # Max 300ms for detection
            
            return frame, emotions

    def release(self):
        """Instant camera release"""
        with self.lock:
            if self.cap.isOpened():
                self.cap.release()
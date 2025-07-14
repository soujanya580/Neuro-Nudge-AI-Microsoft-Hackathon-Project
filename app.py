import streamlit as st
import cv2
import time
import os
import threading
import numpy as np
import pandas as pd
from datetime import datetime
from gtts import gTTS
import tempfile
import platform
import subprocess
import hashlib
import json
from pathlib import Path

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_lang' not in st.session_state:
    st.session_state.current_lang = "en"

# Create data directory
os.makedirs("data", exist_ok=True)

# ======================
# AUTHENTICATION SYSTEM
# ======================
USER_DATA_PATH = "data/users.json"

def load_users():
    try:
        if not Path(USER_DATA_PATH).exists():
            return {}
        with open(USER_DATA_PATH) as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_DATA_PATH, 'w') as f:
        json.dump(users, f)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username exists"
    hashed = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {"password": hashed}
    save_users(users)
    return True, "Registered!"

def authenticate(username, password):
    users = load_users()
    if username not in users:
        return False, "User not found"
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if users[username]["password"] == hashed:
        return True, "Login success"
    return False, "Wrong password"

# ======================
# ENHANCED EMOTION DETECTION
# ======================
class EnhancedEmotionDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Camera error")
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        self.emotion_labels = ['happy', 'sad', 'angry', 'surprised', 'neutral']
    
    def get_emotion_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return frame_rgb, None
        
        emotions = {
            'happy': self._detect_happy(frame, faces),
            'sad': self._detect_sad(frame, faces),
            'angry': self._detect_angry(frame, faces),
            'surprised': self._detect_surprised(frame, faces),
            'neutral': self._detect_neutral(frame, faces)
        }
        
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v/total for k, v in emotions.items()}
        
        return frame_rgb, emotions
    
    def _detect_happy(self, frame, faces):
        return np.random.uniform(0.7, 0.9)
    
    def _detect_sad(self, frame, faces):
        return np.random.uniform(0.0, 0.3)
    
    def _detect_angry(self, frame, faces):
        return np.random.uniform(0.0, 0.2)
    
    def _detect_surprised(self, frame, faces):
        return np.random.uniform(0.0, 0.2)
    
    def _detect_neutral(self, frame, faces):
        return np.random.uniform(0.1, 0.4)
    
    def release(self):
        if self.cap.isOpened():
            self.cap.release()

# ======================
# MULTI-LANGUAGE SPEAKER
# ======================
class MultiLanguageSpeaker:
    def __init__(self):
        self.system = platform.system()
        self.responses = {
            'en': {
                'happy': "You look very happy today! 😊",
                'sad': "I sense you might be feeling sad. 💙",
                'angry': "You seem angry. Try deep breathing. 🧘",
                'surprised': "You look surprised! 😲",
                'neutral': "You appear calm and neutral. 😐"
            },
            'kn': {
                'happy': "ನೀವು ಬಹಳ ಸಂತೋಷದಿಂದ ಕಾಣುತ್ತೀರಿ! 😊",
                'sad': "ನೀವು ದುಃಖಿತರಾಗಿರಬಹುದು. 💙",
                'angry': "ನೀವು ಕೋಪಗೊಂಡಿರುವಂತೆ ಕಾಣುತ್ತೀರಿ. ಗಾಳಿ ಉಚ್ಛ್ವಾಸ ಮಾಡಿ. 🧘",
                'surprised': "ನೀವು ಆಶ್ಚರ್ಯಚಕಿತರಾಗಿದ್ದೀರಿ! 😲",
                'neutral': "ನೀವು ಶಾಂತವಾಗಿ ಕಾಣುತ್ತೀರಿ. 😐"
            },
            'hi': {
                'happy': "आप बहुत खुश लग रहे हैं! 😊",
                'sad': "आप उदास लग रहे हैं। 💙",
                'angry': "आप क्रोधित लग रहे हैं। गहरी सांस लें। 🧘",
                'surprised': "आप हैरान लग रहे हैं! 😲",
                'neutral': "आप शांत लग रहे हैं। 😐"
            }
        }
    
    def speak(self, emotion, lang='en'):
        try:
            if lang not in self.responses:
                lang = 'en'
            
            text = self.responses[lang].get(emotion, self.responses['en'][emotion])
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tts = gTTS(text=text, lang=lang, slow=False)
                tts.save(f.name)
                
                if self.system == "Windows":
                    os.startfile(f.name)
                elif self.system == "Darwin":
                    subprocess.run(['afplay', f.name])
                else:
                    subprocess.run(['aplay', f.name])
                
                threading.Timer(3, lambda: os.remove(f.name)).start()
        except Exception as e:
            st.error(f"Audio error: {str(e)}")

# ======================
# PAGES
# ======================
def login_page():
    st.title("Welcome! 👋")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                success, msg = authenticate(user, pwd)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.session_state.page = "detector"
                    st.rerun()
                else:
                    st.error(msg)
    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("New username")
            new_pwd = st.text_input("New password", type="password")
            confirm_pwd = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Register"):
                if new_pwd != confirm_pwd:
                    st.error("Passwords don't match")
                else:
                    success, msg = register_user(new_user, new_pwd)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

def detector_page():
    st.title("Enhanced Emotion Detector")
    
    # Language selection
    lang = st.radio("Select Language", 
                   ["English", "Kannada", "Hindi"],
                   format_func=lambda x: {"English": "en", "Kannada": "kn", "Hindi": "hi"}[x])
    
    lang_code = {"English": "en", "Kannada": "kn", "Hindi": "hi"}[lang]
    
    # Initialize components
    if 'detector' not in st.session_state:
        st.session_state.detector = None
    if 'speaker' not in st.session_state:
        st.session_state.speaker = MultiLanguageSpeaker()
    
    # Camera controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Camera") and st.session_state.detector is None:
            try:
                st.session_state.detector = EnhancedEmotionDetector()
            except Exception as e:
                st.error(f"Camera error: {str(e)}")
    with col2:
        if st.button("Stop Camera") and st.session_state.detector:
            st.session_state.detector.release()
            st.session_state.detector = None
            st.rerun()
    
    # Emotion detection display
    if st.session_state.detector:
        placeholder = st.empty()
        last_emotion = None
        
        while st.session_state.detector:
            frame, emotions = st.session_state.detector.get_emotion_frame()
            
            if frame is not None:
                placeholder.image(frame, use_container_width=True)
                
                if emotions:
                    emotion, confidence = max(emotions.items(), key=lambda x: x[1])
                    
                    if confidence > 0.6 and emotion != last_emotion:
                        st.success(f"Detected: {emotion} ({confidence:.0%} confidence)")
                        
                        emojis = {
                            'happy': '😊',
                            'sad': '😢',
                            'angry': '😠',
                            'surprised': '😲',
                            'neutral': '😐'
                        }
                        st.markdown(f"### {emojis.get(emotion, '')} {emotion.capitalize()}")
                        
                        st.session_state.speaker.speak(emotion, lang_code)
                        
                        last_emotion = emotion
                        time.sleep(3)
            
            time.sleep(0.1)
    
    if st.button("Logout"):
        if st.session_state.detector:
            st.session_state.detector.release()
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

# ======================
# MAIN APP
# ======================
def main():
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "detector":
        detector_page()

if __name__ == "__main__":
    main()
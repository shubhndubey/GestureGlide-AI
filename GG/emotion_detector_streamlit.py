import streamlit as st
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

# Page setup
st.set_page_config(layout="wide")
st.title("😊 Real-Time Emotion Detection")

# Load model and cascade
model = load_model("static/emotion_model.h5")
face_cascade = cv2.CascadeClassifier("static/haarcascade_frontalface_default.xml")
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Initialize session state
if "run_camera" not in st.session_state:
    st.session_state.run_camera = False

# Layout
col1, col2 = st.columns([3, 2])
FRAME_WINDOW = col1.image([])
emotion_output = col2.empty()

# Buttons
if col1.button("Start Camera"):
    st.session_state.run_camera = True
if col1.button("Stop Camera"):
    st.session_state.run_camera = False

last_emotion = "Neutral"

def detect_emotion(frame):
    global last_emotion
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48))
        roi = roi_gray.astype("float32") / 255.0
        roi = np.expand_dims(roi, axis=0)
        roi = np.expand_dims(roi, axis=-1)
        prediction = model.predict(roi)
        label = emotion_labels[np.argmax(prediction)]
        last_emotion = label
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    return frame, last_emotion

# Video loop
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while st.session_state.run_camera:
    success, frame = cap.read()
    if not success:
        st.error("Camera not accessible.")
        break
    frame = cv2.flip(frame, 1)
    frame, detected_emotion = detect_emotion(frame)
    FRAME_WINDOW.image(frame, channels='BGR')
    emotion_output.subheader("Detected Emotion:")
    emotion_output.success(detected_emotion)

cap.release()

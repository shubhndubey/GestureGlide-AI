import streamlit as st
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from PIL import Image
import google.generativeai as genai

# Streamlit UI setup
st.set_page_config(layout="wide")
st.title("✍️ Hand Gesture Math Solver")

# Session state for camera control
if "run_camera" not in st.session_state:
    st.session_state.run_camera = False

# Layout
col1, col2 = st.columns([3, 2])
FRAME_WINDOW = col1.image([])
output_text_area = col2.empty()

# Buttons
if col1.button("Start Camera"):
    st.session_state.run_camera = True
if col1.button("Stop Camera"):
    st.session_state.run_camera = False

# Gemini AI setup
genai.configure(api_key="AIzaSyDBHwLxjpSfm_ur6ZMP0y-F7eW9U5cZB8M")
model = genai.GenerativeModel('gemini-2.0-flash')

# Hand detector
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1,
                        detectionCon=0.7, minTrackCon=0.5)

prev_pos = None
canvas = None
output_text = ""

def get_hand_info(img):
    hands, img = detector.findHands(img, draw=False, flipType=True)
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)
        return fingers, lmList
    return None

def draw(info, prev_pos, canvas):
    fingers, lmList = info
    current_pos = None
    if fingers == [0, 1, 0, 0, 0]:  # Index finger only
        current_pos = lmList[8][0:2]
        if prev_pos is None:
            prev_pos = current_pos
        cv2.line(canvas, current_pos, prev_pos, (0, 255, 0), 10)
    elif fingers == [0, 1, 0, 0, 1]:  # Index and pinky = clear
        canvas = np.zeros_like(canvas)
    return current_pos, canvas

def send_to_ai(model, canvas, fingers):
    if fingers == [1, 1, 1, 1, 0]:  # All fingers except pinky
        pil_image = Image.fromarray(canvas)
        response = model.generate_content(["Solve me a maths problem", pil_image])
        return response.text
    return ""

# Start webcam only if run_camera is True
if st.session_state.run_camera:
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    while st.session_state.run_camera:
        success, img = cap.read()
        if not success:
            st.error("Camera not accessible.")
            break
        img = cv2.flip(img, 1)

        if canvas is None:
            canvas = np.zeros_like(img)

        info = get_hand_info(img)
        if info:
            fingers, lmList = info
            prev_pos, canvas = draw(info, prev_pos, canvas)
            response = send_to_ai(model, canvas, fingers)
            if response:
                output_text = response

        image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)
        FRAME_WINDOW.image(image_combined, channels='BGR')

        if output_text:
            output_text_area.subheader("Answer:")
            output_text_area.code(output_text)

    cap.release()

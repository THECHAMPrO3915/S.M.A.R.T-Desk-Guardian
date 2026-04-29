import streamlit as st
import streamlit.components.v1 as components
from streamlit_calendar import calendar
import random
import datetime
import time

# Page configuration
st.set_page_config(layout="wide")

# Polished Dark Aesthetic CSS
st.markdown("""
    <style>
        .stApp { background-color: #0B0E14; color: white; }
        .liquid-bar-bg { background: #161B22; border-radius: 10px; height: 30px; width: 100%; overflow: hidden; margin-bottom: 20px; }
        .liquid-bar-fill { height: 100%; transition: width 0.5s; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; }
        .cred-box { background: #161B22; padding: 15px; border-radius: 10px; border: 1px solid #3FB950; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# Audio Unlock Interaction (Prevents Browser Audio Blocking)
if 'audio_unlocked' not in st.session_state:
    st.title("S.M.A.R.T. Workspace Initialization")
    if st.button("🔊 Click to Enable Sound Alerts"):
        st.session_state.audio_unlocked = True
        st.rerun()
    st.stop()

def render_kwh_gauge(value, max_val):
    current_value = round(value + random.uniform(-0.1, 0.1), 2)
    percent = (current_value / max_val) * 100
    color = "#FF4B4B" if percent > 80 else "#3FB950"
    if percent > 80: st.error("⚠️ High Electricity Usage Detected!")
        
    st.markdown(f"**Electricity Usage ({int(percent)}%)**")
    st.markdown(f"""
        <div class="liquid-bar-bg">
            <div class="liquid-bar-fill" style="width: {percent}%; background: {color};">{int(percent)}%</div>
        </div>
    """, unsafe_allow_html=True)

st.title("S.M.A.R.T. Workspace Dashboard")

left_col, center_col, right_col = st.columns([1, 2, 1])

with left_col:
    st.subheader("Workspace Metrics")
    render_kwh_gauge(4.2, 5) 
    
    st.subheader("Focus Timer")
    if 'timer_running' not in st.session_state: st.session_state.timer_running = False
    
    minutes = st.number_input("Set Minutes", 1, 120, 25)
    if st.button("Start Timer"):
        st.session_state.timer_running = True
        
    if st.session_state.timer_running:
        with st.empty():
            for seconds in range(minutes * 60, 0, -1):
                mins, secs = divmod(seconds, 60)
                st.write(f"### ⏳ {mins:02d}:{secs:02d}")
                time.sleep(1)
            # Audio trigger for timer completion
            components.html("<script>new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg').play();</script>", height=0)
            st.success("Focus Session Complete!")
            st.session_state.timer_running = False

with center_col:
    # Posture AI with cooldown logic
    components.html("""
    <div style="background:#0B0E14; padding:10px; border-radius:20px; color:white; text-align:center;">
        <video id="video" width="100%" autoplay playsinline style="border-radius:15px; border:2px solid #3FB950;"></video>
        <p id="posture" style="font-size: 1.2rem; font-weight: bold; margin-top:10px;">Analyzing Posture...</p>
    </div>
    <script type="module">
        import { PoseLandmarker, FilesetResolver } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/vision_bundle.js";
        const video = document.getElementById('video');
        const posture = document.getElementById('posture');
        let landmarker;
        let isSpeaking = false; 

        async function init() {
            const vision = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm");
            landmarker = await PoseLandmarker.createFromOptions(vision, {
                baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task" },
                runningMode: "VIDEO"
            });
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.addEventListener("loadeddata", () => { predict(); });
        }

        function predict() {
            const results = landmarker.detectForVideo(video, performance.now());
            if (results.landmarks.length > 0) {
                const nose = results.landmarks[0][0];
                const shoulder = results.landmarks[0][11];
                if (nose.y > (shoulder.y - 0.05)) {
                    posture.innerText = "Please sit straight! ❌";
                    posture.style.color = "#FF4B4B";
                    if (!isSpeaking) {
                        isSpeaking = true;
                        window.speechSynthesis.speak(new SpeechSynthesisUtterance("Please sit straight."));
                        setTimeout(() => { isSpeaking = false; }, 3000);
                    }
                } else {
                    posture.innerText = "Posture: Good ✅";
                    posture.style.color = "#3FB950";
                }
            }
            requestAnimationFrame(predict);
        }
        init();
    </script>
    """, height=400)
    
    st.subheader("📅 Schedule Manager")
    calendar(events=[], options={"editable": True, "selectable": True})

with right_col:
    st.subheader("Environment")
    st.write("### ☁️ Weather")
    st.slider("Today's Temperature (°C)", 28, 40, 32, disabled=True)
    
    st.subheader("⏰ Alarm")
    alarm_time = st.time_input("Set Alarm")
    current_time = datetime.datetime.now().time()
    
    # Alarm Logic with sound
    if alarm_time.hour == current_time.hour and alarm_time.minute == current_time.minute:
        st.balloons()
        st.warning("⏰ ALARM RINGING!")
        components.html("<script>new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg').play();</script>", height=0)
    
    st.divider()
    st.subheader("🔐 S.M.A.R.T. AI Access")
    st.markdown("""
        <div class="cred-box">
            <p><strong>Username:</strong> smart_admin</p>
            <p><strong>Password:</strong> 1234</p>
            <p><strong>Link:</strong> <a href="https://smart-desk-ai.streamlit.app" target="_blank">smart-desk-ai.streamlit.app</a></p>
        </div>
    """, unsafe_allow_html=True)
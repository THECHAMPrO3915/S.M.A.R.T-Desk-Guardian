import datetime
import os
import random
import streamlit as st
import streamlit.components.v1 as components
from streamlit_calendar import calendar

# --- FAVICON & LOGO CONFIGURATION ---
FAVICON_URL = "https://cdn.corenexis.com/f/R0lTF94ryFT.png"

# Page Configuration
st.set_page_config(
    page_title="S.M.A.R.T. Workspace",
    page_icon=FAVICON_URL if FAVICON_URL else "🛡️",
    layout="wide",
)

# Custom Head & Styling Injection
if FAVICON_URL:
  st.markdown(
      f"""
        <head>
            <link rel="icon" href="{FAVICON_URL}" type="image/png">
        </head>
    """,
      unsafe_allow_html=True,
  )

# Custom Dark Aesthetic Styling
st.markdown(
    """
    <style>
        .stApp { background-color: #0B0E14; color: white; }
        .liquid-bar-bg { background: #161B22; border-radius: 10px; height: 30px; width: 100%; overflow: hidden; margin-bottom: 20px; }
        .liquid-bar-fill { height: 100%; transition: width 0.5s; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- LOGIN GATEWAY ---
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
  login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
  with login_col2:
    st.title("🔒 S.M.A.R.T. Workspace Login")
    with st.form("login_form"):
      username_input = st.text_input("Username / Email")
      password_input = st.text_input("Password", type="password")
      login_submitted = st.form_submit_button("Sign In")

      if login_submitted:
        if (
            username_input == "smart@admin.com"
            and password_input == "smartadmin321"
        ):
          st.session_state.logged_in = True
          st.success("Login successful!")
          st.rerun()
        else:
          st.error("Invalid Username or Password")
  st.stop()

# Audio Unlock Interaction
if "audio_unlocked" not in st.session_state:
  st.title("S.M.A.R.T. Workspace Initialization")
  st.info("Click below to enable web audio synthesis and timer alert sounds.")
  if st.button("🔊 Enable Sound & Launch Dashboard"):
    st.session_state.audio_unlocked = True
    st.rerun()
  st.stop()

# Session State Initialization for Calendar & Scheduled Alarms
if "calendar_events" not in st.session_state:
  st.session_state.calendar_events = [{
      "title": "Focus Session",
      "start": str(datetime.date.today()),
      "end": str(datetime.date.today()),
      "date": datetime.date.today(),
      "time": None,
      "rang": False,
  }]


# Helper Function: kWh Gauge
def render_kwh_gauge(value, max_val):
  current_value = round(value + random.uniform(-0.1, 0.1), 2)
  percent = min((current_value / max_val) * 100, 100)
  color = "#FF4B4B" if percent > 80 else "#3FB950"

  if percent > 80:
    st.error("⚠️ High Electricity Usage Detected!")

  st.markdown(f"**Electricity Usage ({int(percent)}%)**")
  st.markdown(
      f"""
        <div class="liquid-bar-bg">
            <div class="liquid-bar-fill" style="width: {percent}%; background: {color};">{int(percent)}%</div>
        </div>
    """,
      unsafe_allow_html=True,
  )


# --- LOGO & HEADER SETUP ---
DEFAULT_LOGO_URL = user_logo_url = "https://cdn.corenexis.com/f/R0lTF94ryFT.png"

logo_to_display = user_logo_url if user_logo_url else DEFAULT_LOGO_URL

if logo_to_display:
  header_col1, header_col2, header_col3 = st.columns([1, 6, 1])
  with header_col1:
    st.image(logo_to_display, width=90)
  with header_col2:
    st.title("S.M.A.R.T. Workspace Dashboard")
  with header_col3:
    if st.button("🚪 Logout"):
      st.session_state.logged_in = False
      st.rerun()
else:
  st.title("🛡️ S.M.A.R.T. Workspace Dashboard")

left_col, center_col, right_col = st.columns([1, 2, 1])

# Left Column: Metrics & Focus Tools
with left_col:
  st.subheader("Workspace Metrics")
  render_kwh_gauge(4.2, 5.0)

  st.subheader("🎵 Focus Timer & Ambient Music")

  music_options = {
      "None": "",
      "Weightless": "https://reasonable-cyan-vsdvvtmz.edgeone.dev",
      "Rain & Thunder": (
          "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
      ),
      "Deep Focus Flow": (
          "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
      ),
      "Ambient Waves": (
          "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
      ),
  }

  selected_music = st.selectbox(
      "Select Focus Track", list(music_options.keys())
  )
  music_url = music_options[selected_music]

  st.divider()

  minutes = st.number_input("Set Minutes", 1, 120, 25)

  # Client-side Focus Timer with Full Audio Control
  timer_html = f"""
    <div style="background:#161B22; padding:15px; border-radius:10px; text-align:center; color:white; font-family:sans-serif;">
        <h3 id="timer-display" style="margin:0 0 10px 0;">⏳ {minutes:02d}:00</h3>
        <button id="start-btn" onclick="startTimer({minutes})" style="background:#3FB950; color:white; border:none; padding:8px 16px; border-radius:5px; cursor:pointer; font-weight:bold; margin-right:5px;">▶️ Start</button>
        <button id="stop-btn" onclick="stopTimer()" style="background:#FF4B4B; color:white; border:none; padding:8px 16px; border-radius:5px; cursor:pointer; font-weight:bold;">⏹️ Stop</button>
        <audio id="timer-sound" src="https://cdn.imageurlgenerator.com/uploads/1814b364-ca1b-4d96-bdf5-ed324fa03996.mp3"></audio>
        <audio id="bg-music" src="{music_url}" loop></audio>
    </div>

    <script>
        let countdown = null;
        let totalSeconds = 0;

        function stopAudio(audioId) {{
            const audioEl = document.getElementById(audioId);
            if (audioEl) {{
                audioEl.pause();
                audioEl.currentTime = 0;
            }}
        }}

        function startTimer(mins) {{
            stopTimer();
            totalSeconds = mins * 60;
            updateDisplay();

            const bgMusic = document.getElementById('bg-music');
            if (bgMusic && bgMusic.getAttribute('src')) {{
                bgMusic.play().catch(e => console.log("Audio play error:", e));
            }}

            countdown = setInterval(() => {{
                totalSeconds--;
                updateDisplay();

                if (totalSeconds <= 0) {{
                    clearInterval(countdown);
                    document.getElementById('timer-display').innerText = "🎉 Focus Session Complete!";
                    stopAudio('bg-music');
                    
                    const sound = document.getElementById('timer-sound');
                    if (sound) {{
                        sound.play().catch(e => console.log(e));
                    }}
                }}
            }}, 1000);
        }}

        function stopTimer() {{
            if (countdown) {{
                clearInterval(countdown);
                countdown = null;
            }}
            document.getElementById('timer-display').innerText = "⏳ 00:00";
            
            stopAudio('bg-music');
            stopAudio('timer-sound');
        }}

        function updateDisplay() {{
            const m = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
            const s = String(totalSeconds % 60).padStart(2, '0');
            document.getElementById('timer-display').innerText = `⏳ ${{m}}:${{s}}`;
        }}
    </script>
    """
  components.html(timer_html, height=120)

# Right Column (Environment Tools, AI Access & Ringtone Setup)
with right_col:
  st.subheader("🔑 S.M.A.R.T AI Access")
  st.info(
      "**Username / Email:** `smart_admin`  \n"
      "**Password:** `admin123`"
  )

  st.subheader("Environment")
  st.write("### ☁️ Weather")
  st.slider("Today's Temperature (°C)", 28, 40, 32, disabled=True)

  st.subheader("⏰ Alarm & Ringtone Setup")

  ringtone_options = {
      "Slow Rise (Default)": (
          "https://videotourl.com/audio/1787935980087-c3a222c1-9112-4253-9e39-d33d6571a743.mp3"
      )
  }

  selected_ringtone_name = st.selectbox(
      "Select Ringtone", list(ringtone_options.keys())
  )
  selected_ringtone_url = ringtone_options[selected_ringtone_name]

  now = datetime.datetime.now()
  alarm_time = st.time_input(
      "Set Alarm Time", value=datetime.time(now.hour, now.minute)
  )
  alarm_enabled = st.toggle("🔔 Arm Alarm", value=False)

  if alarm_enabled:
    alarm_hhmm = alarm_time.strftime("%H:%M")
    alarm_component_html = f"""
        <div id="alarm-box" style="padding: 10px; background: #161B22; border: 1px solid #3FB950; border-radius: 8px; font-family: sans-serif; text-align: center;">
            <span id="alarm-text" style="color: #3FB950; font-weight: bold; font-size: 14px;">🔔 Alarm Armed for {alarm_hhmm}</span>
            <br/><br/>
            <button id="stop-btn" onclick="stopAlarm()" style="display: none; background: #FF4B4B; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-weight: bold;">🛑 Stop Alarm</button>
        </div>

        <script>
            let sound = null;
            let alarmTimeStr = "{alarm_hhmm}";
            let triggered = false;

            function stopAlarm() {{
                if (sound) {{
                    sound.pause();
                    sound.currentTime = 0;
                }}
                document.getElementById('alarm-text').innerText = "⏹️ Alarm Stopped";
                document.getElementById('alarm-text').style.color = "#888";
                document.getElementById('stop-btn').style.display = "none";
            }}

            setInterval(() => {{
                if (triggered) return;

                const current = new Date();
                const curHH = String(current.getHours()).padStart(2, '0');
                const curMM = String(current.getMinutes()).padStart(2, '0');
                const curTimeStr = curHH + ":" + curMM;

                if (curTimeStr === alarmTimeStr) {{
                    triggered = true;
                    document.getElementById('alarm-text').innerText = "⏰ ALARM RINGING!";
                    document.getElementById('alarm-text').style.color = "#FF4B4B";
                    document.getElementById('stop-btn').style.display = "inline-block";

                    sound = new Audio('{selected_ringtone_url}');
                    sound.loop = true;
                    sound.play().catch(e => console.log("Audio block error:", e));
                }}
            }}, 1000);
        </script>
    """
    components.html(alarm_component_html, height=110)

# Center Column: Posture AI & Schedule Manager with Task Timer
with center_col:
  st.subheader("📷 Posture AI")

  posture_html = """<!DOCTYPE html>
<html>
<head>
  <style>
    body { background-color: #0B0E14; color: white; margin: 0; font-family: sans-serif; text-align: center; }
    .container { padding: 10px; border-radius: 20px; }
    video { border-radius: 15px; border: 2px solid #3FB950; width: 100%; max-height: 380px; object-fit: cover; }
    #posture { font-size: 1.1rem; font-weight: bold; margin-top: 10px; }
    button { background: #3FB950; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 5px; }
    button:hover { background: #2ea043; }
  </style>
</head>
<body>
  <div class="container">
    <video id="video" autoplay playsinline muted></video>
    <p id="posture">Click below to start Posture AI</p>
    <button id="start-btn">🎥 Enable Camera & Start AI</button>
  </div>

  <script type="module">
    import { PoseLandmarker, FilesetResolver } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/vision_bundle.js";

    const video = document.getElementById('video');
    const posture = document.getElementById('posture');
    const startBtn = document.getElementById('start-btn');
    let landmarker;
    let isSpeaking = false;
    let lastVideoTime = -1;

    async function startPostureAI() {
      startBtn.style.display = 'none';

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        posture.innerText = "❌ Camera API unavailable. Ensure app is accessed via HTTPS or http://localhost";
        posture.style.color = "#FF4B4B";
        return;
      }

      posture.innerText = "Requesting camera access...";

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: { ideal: 640 }, height: { ideal: 480 } } 
        });
        video.srcObject = stream;

        posture.innerText = "Loading Vision AI Model...";
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm"
        );
        
        landmarker = await PoseLandmarker.createFromOptions(vision, {
          baseOptions: { 
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
            delegate: "GPU"
          },
          runningMode: "VIDEO",
          numPoses: 1
        });

        posture.innerText = "Posture AI Active ✅";
        posture.style.color = "#3FB950";
        predict();
      } catch (err) {
        posture.innerText = "❌ Initialization Error: " + err.message;
        posture.style.color = "#FF4B4B";
      }
    }

    function predict() {
      if (landmarker && video.readyState >= 2 && video.currentTime !== lastVideoTime) {
        lastVideoTime = video.currentTime;
        try {
          const results = landmarker.detectForVideo(video, performance.now());
          if (results && results.landmarks && results.landmarks.length > 0) {
            const nose = results.landmarks[0][0];
            const shoulder = results.landmarks[0][11];
            
            if (nose && shoulder) {
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
          } else {
            posture.innerText = "No person detected 🔍";
            posture.style.color = "#FFC107";
          }
        } catch (err) {
          posture.innerText = "AI Frame Error: " + err.message;
          posture.style.color = "#FF4B4B";
        }
      }
      requestAnimationFrame(predict);
    }

    startBtn.addEventListener('click', startPostureAI);
  </script>
</body>
</html>"""

  components.html(posture_html, height=440)

  st.subheader("📅 Schedule Manager & To-Do Timers")

  current_time = now.time()
  current_date = now.date()
  for event in st.session_state.calendar_events:
    if (
        event.get("date") == current_date
        and event.get("time") is not None
        and not event.get("rang", False)
    ):
      task_time = event["time"]
      if (
          current_time.hour == task_time.hour
          and current_time.minute == task_time.minute
      ):
        st.warning(f"🔔 TASK TIMER ALARM: {event['title']}")
        st.balloons()
        components.html(
            f"""
            <audio autoplay loop style="display:none;">
                <source src="{selected_ringtone_url}" type="audio/mp3">
            </audio>
        """,
            height=0,
        )
        event["rang"] = True

  # Task Management: Add & Remove
  col_add, col_del = st.columns(2)

  with col_add:
    with st.expander("➕ Add Task"):
      with st.form("todo_form", clear_on_submit=True):
        task_title = st.text_input("Task Description")
        task_date = st.date_input("Scheduled Date", datetime.date.today())
        task_time = st.time_input(
            "Scheduled Time", datetime.time(now.hour, now.minute)
        )

        submitted = st.form_submit_button("Add Task")
        if submitted and task_title:
          datetime_str = f"{task_date}T{task_time.strftime('%H:%M:%S')}"
          st.session_state.calendar_events.append({
              "title": f"⏰ {task_title} ({task_time.strftime('%H:%M')})",
              "start": datetime_str,
              "end": datetime_str,
              "date": task_date,
              "time": task_time,
              "rang": False,
          })
          st.success(f"Added task '{task_title}'")
          st.rerun()

  with col_del:
    with st.expander("🗑️ Remove Task"):
      if st.session_state.calendar_events:
        task_options = {
            i: f"{e['title']} ({e['start']})"
            for i, e in enumerate(st.session_state.calendar_events)
        }
        selected_idx = st.selectbox(
            "Select Task to Delete",
            options=list(task_options.keys()),
            format_func=lambda x: task_options[x],
        )
        if st.button("🗑️ Delete Selected Task"):
          deleted = st.session_state.calendar_events.pop(selected_idx)
          st.success(f"Removed '{deleted['title']}'")
          st.rerun()
      else:
        st.info("No tasks to remove.")

  clean_events = [
      {
          "title": str(e["title"]),
          "start": str(e["start"]),
          "end": str(e["end"]),
      }
      for e in st.session_state.calendar_events
  ]

  calendar(
      events=clean_events, options={"editable": True, "selectable": True}
  )
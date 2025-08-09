
# NOTE: This app requires the Streamlit package. To run it, execute in terminal:
# pip install streamlit
# streamlit run mental_health_bot_combined.py
from dotenv import load_dotenv
import os
import openai

# Load .env file
load_dotenv()

# Get the API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Import necessary libraries
import streamlit as st

# ---- Setup ----
st.set_page_config(page_title="Mental Health First Aid Bot", layout="centered")
st.title("🧠 Mental Health First Aid Bot")
st.markdown("Welcome! This tool helps you manage your mental wellness with coping tips and gamified mental health screenings (GAD-7 & PHQ-9).")

# ---- Mood Check + Coping Suggestions ----
st.header("💬 How are you feeling right now?")
emotion = st.selectbox(
    "Choose the emotion that best describes your current state:",
    ["Select...", "Anxious", "Depressed", "Stressed", "Overwhelmed", "Angry", "Sad", "Can't Sleep"]
)

suggestions = {
    "Anxious": ["5-4-3-2-1 grounding", "2 min deep breathing", "Walk outside"],
    "Depressed": ["Drink water", "Text a friend", "Break 1 task into small step"],
    "Stressed": ["Body scan meditation", "Gratitude journaling", "Unplug 5 min"],
    "Overwhelmed": ["Prioritize 1 thing", "Write a quick list", "3-min quiet break"],
    "Angry": ["Jumping jacks", "Hold something cold", "Unsent letter exercise"],
    "Sad": ["Watch comfort content", "Cuddle pet/pillow", "Cry if you want to"],
    "Can't Sleep": ["Sleep sounds", "No screens", "Progressive muscle relaxation"]
}

if emotion != "Select...":
    st.subheader("💡 Coping Suggestions")
    for tip in suggestions[emotion]:
        st.markdown(f"- {tip}")

# ---- Gamified GAD-7 ----
st.header("😰 GAD-7 (Anxiety Screener)")
score_map = {
    "😄 Not at all": 0,
    "🙂 Several days": 1,
    "😐 More than half the days": 2,
    "😟 Nearly every day": 3
}
emoji_options = list(score_map.keys())

gad_questions = [
    "You're at work or school and feel your chest tighten for no reason. How often does this happen?",
    "You find yourself unable to stop worrying even when things are okay. How often do you feel this way?",
    "You lie awake at night thinking about worst-case scenarios. How often does this keep you up?",
    "You feel tension in your muscles or find it hard to relax during the day. How often is this true?",
    "You fidget, tap your foot, or can’t sit still for long. How often does restlessness affect you?",
    "You notice you’re more irritable than usual, snapping at small things. How often is this noticeable?",
    "You avoid certain situations or people out of fear that something bad might happen. How often do you avoid things out of worry?"
]

gad_score = 0
for i, q in enumerate(gad_questions):
    response = st.select_slider(f"{i+1}. {q}", options=emoji_options, key=f"gad_{i}")
    gad_score += score_map[response]

# ---- Gamified PHQ-9 ----
st.header("😔 PHQ-9 (Depression Screener)")

phq_questions = [
    "You’ve been invited to a dinner with friends. You used to love this. How interested are you in going?",
    "You wake up feeling low. How hard is it to get out of bed and start your day?",
    "You find yourself sleeping too much or struggling to fall asleep. How often is this happening?",
    "Tasks feel heavy, even small ones. How often do you feel physically tired or without energy?",
    "You skip meals or eat more than usual. How often is your appetite affected?",
    "You feel like you're letting others down or that you're not good enough. How often do these thoughts occur?",
    "You struggle to focus on reading, shows, or conversations. How often do you lose concentration?",
    "People comment that you're moving or speaking differently—either too slow or restless. How often do you notice this?",
    "You have thoughts that the world would be better off without you. How often do they appear?"
]

phq_score = 0
for i, q in enumerate(phq_questions):
    response = st.select_slider(f"{i+1}. {q}", options=emoji_options, key=f"phq_{i}")
    phq_score += score_map[response]

# ---- Progress Bar ----
total_possible = 21 + 27
user_score = gad_score + phq_score
completion_ratio = user_score / total_possible
st.progress(completion_ratio, text="🎯 Scoring your mental wellness check...")

# ---- Results ----
st.subheader(f"📊 GAD-7 Score: {gad_score}/21")
if gad_score <= 4:
    st.success("Minimal anxiety")
elif gad_score <= 9:
    st.info("Mild anxiety")
elif gad_score <= 14:
    st.warning("Moderate anxiety – consider professional support.")
else:
    st.error("Severe anxiety – please seek help.")

st.subheader(f"📊 PHQ-9 Score: {phq_score}/27")
if phq_score <= 4:
    st.success("Minimal depression")
elif phq_score <= 9:
    st.info("Mild depression")
elif phq_score <= 14:
    st.warning("Moderate depression – consider support.")
elif phq_score <= 19:
    st.warning("Moderately severe depression – therapy recommended.")
else:
    st.error("Severe depression – seek help immediately.")

# ---- Award Badge ----
st.header("🏅 Your Self-Care Badge")

if phq_score < 10 and gad_score < 10:
    st.success("✅ **Mindful Mover Badge** – Keep up the self-care!")
elif 10 <= phq_score < 15 or 10 <= gad_score < 15:
    st.warning("🌱 **Resilience Builder Badge** – You’re showing strength.")
else:
    st.error("🛡️ **Courageous Warrior Badge** – You're fighting hard. Please talk to someone.")

st.caption("💡 Take a screenshot or save your results to reflect later.")

# ---- Footer ----
st.markdown("---")
st.caption("📌 Disclaimer: This tool does not diagnose conditions. For professional help, contact a licensed mental health provider or helpline.")
st.markdown("🔗 [Mental Health Resources](https://www.mentalhealth.gov/get-help)")
# ---- End of the Streamlit App ----

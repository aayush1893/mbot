# gamified_mental_health_bot.py
# Author: Aayush Sisodia
# Description: Gamified GAD-7 & PHQ-9 with mood tips + AI rewording into SITUATIONAL questions.
# Run:
#   python -m pip install streamlit openai
#   python -m streamlit run gamified_mental_health_bot.py

import os
import time
import streamlit as st

# ---- API Key ----
API_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", None))
if not API_KEY:
    st.error("🚨 OPENAI_API_KEY missing. Add it to environment or .streamlit/secrets.toml.")
    st.stop()

# ---- SDK compatibility: supports openai==0.28.* and openai>=1.x ----
USE_NEW_SDK = None
try:
    from openai import OpenAI  # >=1.x
    client = OpenAI(api_key=API_KEY)
    USE_NEW_SDK = True
except Exception:
    import openai  # 0.28 fallback
    openai.api_key = API_KEY
    USE_NEW_SDK = False

# ---- Page Setup ----
st.set_page_config(page_title="Mental Health First Aid Bot", layout="centered")
st.title("🧠 Mental Health First Aid Bot")
st.markdown("Welcome! This tool offers coping tips and gamified screenings (GAD-7 & PHQ-9).")

# ---- Sidebar diagnostics ----
with st.sidebar:
    st.subheader("🔧 Diagnostics")
    try:
        import openai as _oi
        st.write("openai version:", getattr(_oi, "__version__", "unknown"))
    except Exception:
        st.write("openai version: import failed")
    st.write("Using new SDK:", USE_NEW_SDK)

# -------------------------
# Scenario-enforcing AI gen
# -------------------------
SCENARIO_TRIGGERS = [
    "when ", "while ", "before ", "after ", "at work", "in class", "on the bus",
    "in a meeting", "before bed", "waking up", "after dinner", "during a call",
    "at home", "with friends", "in public", "on your commute", "during chores",
    "with family", "on weekends"
]

def _looks_situational(line: str) -> bool:
    s = line.lower()
    return any(t in s for t in SCENARIO_TRIGGERS) and ("?" in line)

def _fewshot_messages(prompt: str, expected: int, stricter: bool = False):
    style_rules = (
        "Write FRIENDLY, SHORT questions (<= 20 words), each as a REAL-LIFE SITUATION.\n"
        "Each line must start with a context clause (e.g., 'When…', 'Before bed…', 'At work…').\n"
        "Avoid clinical/diagnostic words; keep the original meaning. One line per item. No numbering."
    )
    if stricter:
        style_rules += "\nMAKE EVERY LINE SITUATIONAL. If a line is generic, rewrite it with a concrete context."

    examples = [
        "Before bed, do your thoughts spiral about little things?",
        "At work or school, do small hassles set you on edge?",
        "When plans change suddenly, do you feel tense or restless?",
        "With friends, is it hard to enjoy what you used to?",
        "Waking up, does the day feel heavy to start?"
    ]
    return [
        {"role": "system",
         "content": "You convert validated screening items into brief, friendly, SITUATION-BASED questions that preserve meaning."},
        {"role": "user",
         "content": (
            f"{style_rules}\n\n"
            f"Examples (style only):\n- " + "\n- ".join(examples) +
            f"\n\nTask:\n{prompt}\n"
            f"Return exactly {expected} lines. No bullets, no numbering, no extra commentary."
         )},
    ]

def ai_generate_questions(prompt: str, defaults: list[str], model_candidates=None, force_refresh=False):
    """
    Returns (questions, meta) with enforced situational style.
    Tries cheap model first, then stronger fallbacks. Caches per prompt.
    meta = {"used_model": str|None, "ai_ok": bool, "reason": str}
    """
    expected = len(defaults)
    models = model_candidates or ["gpt-4.1-nano", "gpt-4o-mini", "gpt-3.5-turbo"]

    cache_key = f"ai_q::{hash(prompt)}::{expected}"
    if not force_refresh and cache_key in st.session_state:
        return st.session_state[cache_key]

    meta = {"used_model": None, "ai_ok": False, "reason": "not attempted"}

    for model_name in models:
        for strict in (False, True):  # try normal few-shot, then strict enforcement
            try:
                if USE_NEW_SDK:
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=_fewshot_messages(prompt, expected, stricter=strict),
                        temperature=0.7, max_tokens=600,
                    )
                    content = (resp.choices[0].message.content or "").strip()
                else:
                    content = (openai.ChatCompletion.create(
                        model=model_name,
                        messages=_fewshot_messages(prompt, expected, stricter=strict),
                        temperature=0.7, max_tokens=600,
                    )["choices"][0]["message"]["content"] or "").strip()

                lines = [ln.strip() for ln in content.split("\n") if ln.strip()]
                cleaned = [ln.lstrip("0123456789.)-–— •").strip() for ln in lines]
                scenario_lines = [q for q in cleaned if len(q) > 10 and _looks_situational(q)]
                questions = scenario_lines[:expected]

                if len(questions) == expected:
                    meta = {"used_model": model_name, "ai_ok": True, "reason": f"scenario-ok (strict={strict})"}
                    st.session_state[cache_key] = (questions, meta)
                    return questions, meta

                meta = {"used_model": model_name, "ai_ok": False,
                        "reason": f"got {len(questions)} valid scenario lines (strict={strict})"}
                time.sleep(0.2)  # tiny backoff
            except Exception as e:
                meta = {"used_model": model_name, "ai_ok": False, "reason": f"error: {e}"}
                continue

    # All attempts failed → soft scenario-ize defaults
    fixed_defaults = []
    for q in defaults:
        fixed_defaults.append(q if _looks_situational(q) else f"When you think about your day, {q.rstrip('?')}?")
    result = (fixed_defaults, meta)
    st.session_state[cache_key] = result
    return result

# -------------------------
# Mood Check + Suggestions
# -------------------------
st.header("💬 How are you feeling right now?")
emotion = st.selectbox(
    "Choose the emotion that best describes your current state:",
    ["Select...", "Anxious", "Depressed", "Stressed", "Overwhelmed", "Angry", "Sad", "Can't Sleep"]
)
suggestions = {
    "Anxious": ["5-4-3-2-1 grounding", "2-min deep breathing", "Walk outside"],
    "Depressed": ["Drink water", "Text a friend", "Break 1 task into a tiny step"],
    "Stressed": ["Body-scan meditation", "Gratitude note", "Unplug for 5 minutes"],
    "Overwhelmed": ["Prioritize one thing", "Quick todo list", "3-min quiet break"],
    "Angry": ["10 jumping jacks", "Hold something cold", "Write an unsent note"],
    "Sad": ["Comfort content", "Cuddle pet/pillow", "Let yourself cry"],
    "Can't Sleep": ["Sleep sounds", "No screens", "Progressive muscle relaxation"],
}
if emotion != "Select...":
    st.subheader("💡 Coping Suggestions")
    for tip in suggestions[emotion]:
        st.markdown(f"- {tip}")

# ---- Scoring Map ----
score_map = {
    "😄 Not at all": 0,
    "🙂 Several days": 1,
    "😐 More than half the days": 2,
    "😟 Nearly every day": 3,
}
emoji_options = list(score_map.keys())

# Regenerate button to force fresh AI output
regen = st.button("🔄 Regenerate AI questions")

# -------------------------
#           GAD-7
# -------------------------
st.header("😰 GAD-7 (Anxiety Screener)")
gad_prompt = (
    "Rewrite the 7 GAD-7 items as CONCRETE, REAL-LIFE SITUATIONS. "
    "Each line must start with a context like 'At work…', 'Before bed…', 'In public…', "
    "'With friends…', 'During class…', 'On your commute…'. Keep meaning; ≤20 words; one line per item."
)
gad_defaults = [
    "You’re at work or school and feel your chest tighten. How often does that happen?",
    "You worry even when everything seems fine. How often does this happen?",
    "You stay up late thinking about the worst that could happen. How often is this true?",
    "You notice your muscles tensing or struggle to relax. How often do you feel that?",
    "You fidget a lot or can’t sit still. How frequently does this affect you?",
    "You snap at small things more than usual. How often is this true?",
    "You avoid plans or places out of worry. How often do you do that?",
]
gad_questions, gad_meta = ai_generate_questions(gad_prompt, gad_defaults, force_refresh=regen)

with st.expander("ℹ️ AI status (GAD-7)"):
    st.write("Model used:", gad_meta.get("used_model"))
    st.write("AI output accepted:", gad_meta.get("ai_ok"))
    st.write("Reason:", gad_meta.get("reason"))

gad_score = 0
for i, q in enumerate(gad_questions):
    response = st.select_slider(f"{i+1}. {q}", options=emoji_options, key=f"gad_{i}")
    gad_score += score_map[response]

# -------------------------
#           PHQ-9
# -------------------------
st.header("😔 PHQ-9 (Depression Screener)")
phq_prompt = (
    "Rewrite the 9 PHQ-9 items as CONCRETE, REAL-LIFE SITUATIONS. "
    "Each line must start with a context like 'Waking up…', 'When plans fall through…', 'On weekends…', "
    "'During chores…', 'While studying…', 'With family…'. Keep meaning; ≤20 words; one line per item."
)
phq_defaults = [
    "You used to enjoy certain things—how interested are you in them lately?",
    "Do mornings feel heavy, like starting the day takes extra effort?",
    "Has your sleep been off—too much or too little?",
    "How often do you feel tired or low on energy?",
    "Has your appetite changed—eating more or less than usual?",
    "Do you find yourself feeling guilty or putting yourself down more often?",
    "Is it harder to focus on reading, shows, or conversations?",
    "Have you felt slowed down or, the opposite, unusually restless?",
    "Have you had thoughts that life isn’t worth it or that you’d be better off gone?",
]
phq_questions, phq_meta = ai_generate_questions(phq_prompt, phq_defaults, force_refresh=regen)

with st.expander("ℹ️ AI status (PHQ-9)"):
    st.write("Model used:", phq_meta.get("used_model"))
    st.write("AI output accepted:", phq_meta.get("ai_ok"))
    st.write("Reason:", phq_meta.get("reason"))

phq_score = 0
for i, q in enumerate(phq_questions):
    response = st.select_slider(f"{i+1}. {q}", options=emoji_options, key=f"phq_{i}")
    phq_score += score_map[response]

# ---- Progress ----
total_possible = 21 + 27
user_score = gad_score + phq_score
st.progress(user_score / total_possible, text="🎯 Scoring your mental wellness check...")

# ---- Results ----
st.subheader(f"📊 GAD-7 Score: {gad_score}/21")
if gad_score <= 4:
    st.success("Minimal anxiety")
elif gad_score <= 9:
    st.info("Mild anxiety")
elif gad_score <= 14:
    st.warning("Moderate anxiety — consider professional support.")
else:
    st.error("Severe anxiety — please seek help.")

st.subheader(f"📊 PHQ-9 Score: {phq_score}/27")
if phq_score <= 4:
    st.success("Minimal depression")
elif phq_score <= 9:
    st.info("Mild depression")
elif phq_score <= 14:
    st.warning("Moderate depression — consider support.")
elif phq_score <= 19:
    st.warning("Moderately severe depression — therapy recommended.")
else:
    st.error("Severe depression — seek help immediately.")

# ---- Badge ----
st.header("🏅 Your Self-Care Badge")
if phq_score < 10 and gad_score < 10:
    st.success("✅ **Mindful Mover Badge** — keep up the self-care!")
elif 10 <= phq_score < 15 or 10 <= gad_score < 15:
    st.warning("🌱 **Resilience Builder Badge** — you’re showing strength.")
else:
    st.error("🛡️ **Courageous Warrior Badge** — you’re fighting hard. Please talk to someone.")

st.markdown("---")
st.caption("📌 This tool doesn’t diagnose conditions. For professional help, contact a licensed provider.")
st.markdown("🔗 [Mental Health Resources](https://www.mentalhealth.gov/get-help)")

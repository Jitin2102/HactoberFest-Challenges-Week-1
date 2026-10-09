import os
import random
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="EcoQuest AI", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

# --- Theme ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root { --forest:#183d2b; --leaf:#38744a; --moss:#dce8d8; --paper:#f6f5ee; --sun:#e6b85c; --ink:#1c2b22; }
.stApp { background:var(--paper); color:var(--ink); }
[data-testid="stSidebar"] { background:#e8eee2; }
h1,h2,h3 { font-family:'Playfair Display',serif !important; color:var(--forest); }
p, label, div { font-family:'DM Sans',sans-serif; }
.hero { padding:2.2rem 2.4rem; border-radius:24px; background:linear-gradient(120deg,#173b2a 0%,#2d6945 68%,#678b58 100%); color:#fff; margin-bottom:1.2rem; }
.hero h1 { color:#fff !important; font-size:3.2rem; line-height:1.05; margin:0.25rem 0 0.8rem; }
.hero p { color:#e8f0e5; font-size:1.08rem; max-width:760px; }
.eyebrow { color:#e8c77b; letter-spacing:.16em; font-weight:700; font-size:.72rem; text-transform:uppercase; }
.pill { display:inline-block; padding:.32rem .7rem; border:1px solid #cbd9c5; border-radius:999px; font-size:.78rem; margin:.15rem .2rem .15rem 0; color:#264d34; background:#f3f7ef; }
.card { background:#fff; border:1px solid #e0e5da; border-radius:18px; padding:1.2rem; min-height:155px; }
.card h3 { margin:.2rem 0 .4rem; font-size:1.25rem; }
.card p { color:#5b685e; font-size:.94rem; }
.metric { background:#fff; border:1px solid #e0e5da; padding:1rem 1.1rem; border-radius:16px; }
.small-muted { color:#657266; font-size:.86rem; }
div.stButton > button { border-radius:999px; border:1px solid #b6c9b1; font-weight:600; }
div.stButton > button[kind="primary"] { background:#244f35; border-color:#244f35; color:#fff; }
hr { border-color:#dce2d7; }
</style>
""", unsafe_allow_html=True)

MISSIONS = [
    {"id":"plant-scout","title":"The Plant Scout","category":"Biodiversity","duration":15,"points":30,"icon":"🌱","description":"Find three different plants. Compare leaf shapes, edges, and textures without picking them.","steps":["Choose a safe public green space.","Observe three plants without damaging them.","Record one visible difference between each plant."],"reflection":"What was one difference you noticed between the plants?"},
    {"id":"sound-map","title":"Build a Sound Map","category":"Mindfulness","duration":10,"points":20,"icon":"🍃","description":"Pause outdoors and notice five distinct natural or environmental sounds.","steps":["Stand somewhere safe and comfortable.","Put your phone away for two minutes.","Write down five sounds and where each seemed to come from."],"reflection":"Which sound did you notice only after slowing down?"},
    {"id":"bird-watcher","title":"Birdwatcher Mini Quest","category":"Wildlife","duration":20,"points":35,"icon":"🐦","description":"Observe birds from a distance and note their color, movement, and behavior.","steps":["Find a place where you can stand without blocking a path.","Observe quietly from a distance; do not feed or approach birds.","Record up to three observations. A photo is optional."],"reflection":"What behavior or movement surprised you?"},
    {"id":"micro-forest","title":"Find a Tiny Forest","category":"Biodiversity","duration":15,"points":30,"icon":"🌳","description":"Discover a small patch of nature and count its different visible life forms.","steps":["Look for a tree base, garden bed, or patch of grass.","Notice plants, insects, fungi, and signs of animal life without touching them.","Record at least three observations."],"reflection":"How many different kinds of life or signs of life did you notice?"},
    {"id":"litter-lens","title":"Leave It Better","category":"Stewardship","duration":15,"points":25,"icon":"♻️","description":"Look for one safe, practical way to care for a shared outdoor space.","steps":["Choose a safe, permitted area.","If appropriate, collect litter only with suitable protection; avoid sharp, medical, or unknown waste.","Use the correct bin and follow local guidance. You can also report a maintenance issue instead."],"reflection":"What small action could help this place stay welcoming?"},
    {"id":"sky-journal","title":"Look Up, Look Out","category":"Mindfulness","duration":10,"points":20,"icon":"☁️","description":"Spend ten minutes noticing the sky, clouds, light, and surrounding landscape.","steps":["Choose a safe spot away from traffic and hazards.","Observe the sky and landscape for ten minutes.","Describe one change in light, cloud, or color."],"reflection":"What did you notice when you gave the view your full attention?"},
]

def init_state():
    defaults = {"completed": [], "notes": {}, "points": 0, "streak": 0, "last_date": "", "mission_of_day": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def make_mission_prompt(preferences, duration, location):
    return f"""Create one safe, screen-light outdoor nature mission.
User interests: {preferences}
Available time: {duration} minutes
Area context: {location or 'not specified'}
Return exactly these labels on separate lines:
TITLE: (short title)
GOAL: (one sentence)
STEPS: (3 short numbered steps)
REFLECTION: (one question)
POINTS: (10 to 40)
Rules: do not ask users to touch wildlife, eat wild plants, enter private land, approach traffic, or handle unknown waste. Do not claim species identification without evidence."""

def generate_with_gemma(prompt):
    model = os.getenv("GEMMA_MODEL", "gemma3:1b")
    try:
        import ollama
        response = ollama.chat(model=model, messages=[{"role":"user","content":prompt}])
        return response["message"]["content"].strip(), None
    except Exception as exc:
        return None, str(exc)

init_state()

with st.sidebar:
    st.markdown("## 🌿 EcoQuest AI")
    st.caption("Touch less screen. Explore more Earth.")
    page = st.radio("Explore", ["Home", "Find a Mission", "My Field Journal", "AI Nature Guide", "About & Setup"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Your field stats**")
    st.metric("Quests completed", len(st.session_state.completed))
    st.metric("Eco points", st.session_state.points)
    st.caption("Tip: choose a mission, put your phone away, then return to record what you noticed.")

if page == "Home":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">YOUR OUTDOOR COMPANION</div>
      <h1>Make the world<br>your next adventure.</h1>
      <p>Small missions. Real discoveries. A little more time outside. Let AI help you plan the adventure — then put your phone away and go explore.</p>
      <span class="pill">Nature-led</span><span class="pill">Screen-light</span><span class="pill">Open AI ready</span>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><h3>🌱 Explore</h3><p>Get a small, practical outdoor mission based on your interests and available time.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h3>👀 Notice</h3><p>Look closer at plants, birds, sounds, and the everyday biodiversity around you.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><h3>📓 Reflect</h3><p>Save one observation after your adventure and watch your field journal grow.</p></div>', unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.25,1])
    with left:
        st.subheader("A small quest for today")
        today_mission = next((m for m in MISSIONS if m["id"] not in st.session_state.completed), MISSIONS[0])
        st.markdown(f"### {today_mission['icon']} {today_mission['title']}")
        st.write(today_mission["description"])
        st.caption(f"⏱ {today_mission['duration']} min  ·  ✦ {today_mission['points']} points  ·  {today_mission['category']}")
        if st.button("Start this quest →", type="primary", use_container_width=True):
            st.session_state.active_mission = today_mission["id"]
            st.session_state.page_jump = "Find a Mission"
            st.rerun()
    with right:
        st.subheader("Your progress")
        total = len(MISSIONS)
        done = len(set(st.session_state.completed))
        st.progress(done/total, text=f"{done} of {total} starter quests completed")
        st.markdown(f'<div class="metric"><span class="small-muted">Eco points earned</span><h2 style="margin:.2rem 0">{st.session_state.points}</h2><span class="small-muted">Earn points by completing a quest and recording a reflection.</span></div>', unsafe_allow_html=True)
        st.write("")
        st.info("Safety first: stay on public paths, respect wildlife, and never identify or eat wild plants based only on AI advice.")

elif page == "Find a Mission":
    st.title("Find your next mission")
    st.write("Pick a ready-made quest or generate a fresh one with a local Gemma model.")
    a,b = st.columns([1,1])
    with a:
        interests = st.multiselect("What would you like to explore?", ["Plants & gardens","Birds & wildlife","Mindfulness","Environmental care","Photography"], default=["Plants & gardens","Mindfulness"])
    with b:
        duration = st.slider("How much time do you have?", 5, 60, 15, step=5)
    area = st.text_input("Optional area context", placeholder="e.g. campus garden, neighborhood park (no exact address needed)")
    st.markdown("### Ready-to-go quests")
    cols = st.columns(2)
    for idx, m in enumerate(MISSIONS):
        with cols[idx%2]:
            with st.container(border=True):
                st.markdown(f"#### {m['icon']} {m['title']}")
                st.caption(f"{m['category']} · {m['duration']} min · {m['points']} points")
                st.write(m["description"])
                if m["id"] in st.session_state.completed:
                    st.success("Completed")
                elif st.button("Open quest", key=f"open_{m['id']}", use_container_width=True):
                    st.session_state.active_mission = m["id"]
                    st.rerun()
    st.divider()
    st.markdown("### ✨ Generate a fresh quest with Gemma")
    st.caption("Requires Ollama and a compatible Gemma model running locally. A ready-made quest is always available above.")
    if st.button("Generate mission with local Gemma", type="primary"):
        interests_text = ", ".join(interests) if interests else "general nature exploration"
        prompt = make_mission_prompt(interests_text, duration, area)
        with st.spinner("Asking your local model for a mission..."):
            answer, error = generate_with_gemma(prompt)
        if answer:
            st.session_state.generated_mission = answer
            st.success("Mission generated locally.")
        else:
            st.warning("Local Gemma wasn't reachable. You can still use the ready-made quests.")
            st.code("ollama pull gemma3:1b\nollama serve")
            st.caption(f"Connection detail: {error}")
    if st.session_state.get("generated_mission"):
        st.markdown("#### Your AI-generated mission")
        st.markdown(st.session_state.generated_mission)

    active_id = st.session_state.get("active_mission")
    active = next((m for m in MISSIONS if m["id"] == active_id), None)
    if active:
        st.divider()
        st.markdown(f"## {active['icon']} {active['title']}")
        st.write(active["description"])
        st.markdown("**Your steps**")
        for step in active["steps"]:
            st.markdown(f"- {step}")
        reflection = st.text_area(active["reflection"], key=f"reflection_{active['id']}")
        if active["id"] not in st.session_state.completed:
            if st.button("Complete quest + earn points", type="primary", key=f"complete_{active['id']}"):
                st.session_state.completed.append(active["id"])
                st.session_state.points += active["points"]
                st.session_state.notes[active["id"]] = {"title": active["title"], "reflection": reflection.strip(), "date": str(date.today()), "points": active["points"]}
                st.success(f"Quest complete! +{active['points']} eco points.")
                st.rerun()
        else:
            st.success("This quest is already in your completed list.")

elif page == "My Field Journal":
    st.title("My Field Journal")
    st.write("A record of the small things you noticed outdoors.")
    if not st.session_state.notes:
        st.info("Your journal is waiting for its first entry. Complete a quest and add a reflection to begin.")
    else:
        for mission_id, entry in reversed(list(st.session_state.notes.items())):
            with st.container(border=True):
                st.caption(f"{entry.get('date','')} · +{entry.get('points',0)} points")
                st.markdown(f"### {entry.get('title','Outdoor observation')}")
                st.write(entry.get("reflection") or "No reflection added.")
    st.divider()
    st.subheader("Add a field note")
    with st.form("field_note_form", clear_on_submit=True):
        title = st.text_input("What did you notice?", placeholder="e.g. A line of ants near a tree")
        detail = st.text_area("Your note", placeholder="Describe what you saw, heard, or wondered about.")
        submitted = st.form_submit_button("Save field note", type="primary")
        if submitted:
            if title.strip() and detail.strip():
                note_id = f"note-{len(st.session_state.notes)+1}-{random.randint(100,999)}"
                st.session_state.notes[note_id] = {"title":title.strip(),"reflection":detail.strip(),"date":str(date.today()),"points":0}
                st.success("Field note saved for this session.")
                st.rerun()
            else:
                st.error("Add both a title and a note.")

elif page == "AI Nature Guide":
    st.title("AI Nature Guide")
    st.write("Ask a nature question or upload a photo for a cautious, educational starting point.")
    st.info("This prototype does not perform verified species identification. Never eat, touch, or handle a wild organism based on an AI response.")
    question = st.text_area("Ask your guide", placeholder="Why do some leaves have serrated edges?")
    uploaded = st.file_uploader("Optional photo (preview only in this starter build)", type=["png","jpg","jpeg","webp"])
    if uploaded:
        st.image(uploaded, caption="Your observation", use_container_width=True)
    if st.button("Ask local Gemma", type="primary"):
        if not question.strip():
            st.warning("Type a question first. For photo-based identification, describe the visible features in your question.")
        else:
            prompt = f"""You are EcoQuest, a cautious outdoor nature educator. Answer simply and encourage real-world observation. Do not claim certainty about species from incomplete evidence. Never recommend eating wild plants, handling wildlife, or entering unsafe/private areas. Question: {question}"""
            with st.spinner("Thinking with local Gemma..."):
                answer, error = generate_with_gemma(prompt)
            if answer:
                st.markdown(answer)
            else:
                st.warning("Gemma is not running locally. Here's a safe way to continue: observe visible features and consult a trusted local field guide.")
                st.code("ollama pull gemma3:1b\nollama serve")
                st.caption(f"Connection detail: {error}")

else:
    st.title("About EcoQuest AI")
    st.write("EcoQuest is a screen-light outdoor exploration prototype built around the idea that AI should help people experience the world, not keep them trapped inside an app.")
    st.markdown("### Open AI architecture")
    st.markdown("""
    - **Gemma (optional local runtime):** Generates missions and answers nature questions through Ollama.
    - **Streamlit:** Rapid interactive web UI for the MVP.
    - **Session state:** Stores progress for the current app session. Persistent accounts and cloud storage are not yet implemented.
    - **Offline boundary:** Ready-made quests work without a model. Gemma-powered answers require a locally running model; the app itself needs a running Streamlit process.
    """)
    st.markdown("### Run locally")
    st.code("""python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py""", language="bash")
    st.markdown("### Enable local Gemma")
    st.code("""# Install Ollama, then:
ollama pull gemma3:1b
ollama serve""", language="bash")
    st.markdown("### Current prototype boundaries")
    st.markdown("""
    - Progress is stored in Streamlit session state, not a persistent database.
    - Uploaded photos are previewed only; species recognition is not implemented.
    - Location and weather recommendations are not live integrations.
    - Voice interaction is a planned extension, not yet implemented.
    """)

st.markdown("---")
st.markdown('<p class="small-muted">EcoQuest AI · Built for the Touch Grass challenge · Go outside first; the app can wait.</p>', unsafe_allow_html=True)

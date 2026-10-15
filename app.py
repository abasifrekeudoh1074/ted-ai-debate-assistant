import streamlit as st
import os, json
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="RCCG Debate Live", layout="wide", page_icon="🎤")

role = st.query_params.get("role", "judge")
is_audience_view = (role == "audience")

CONFIG_FILE = "config.json"
VOTE_FILE = "votes.json"
SCORES_FILE = "judges_scores.json"

def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def load_config():
    return load_json(CONFIG_FILE, {"team_a": "Team A", "team_b": "Team B", "topic": "Debate Topic", "speakersA": ["Speaker 1","Speaker 2","Speaker 3"], "speakersB": ["Speaker 1","Speaker 2","Speaker 3"]})

def save_config(data):
    save_json(CONFIG_FILE, data)

def load_votes():
    return load_json(VOTE_FILE, {"A":0,"B":0})

def save_votes(v):
    save_json(VOTE_FILE, v)

config = load_config()

if os.path.exists("banner.png"):
    st.image("banner.png", use_container_width=True)

DEFINITIONS = """
**DEFINITION OF TERMS - HOW TO SCORE (Per Speaker 100)**
1. **Point (30):** 5 marks for each valid point made AND defended. Eg 2 points = 10 marks. Max 6 points = 30.
2. **Evidence (30):** Facts, stats, examples, scriptures to support points.
3. **Rebuttal (20):** Ability to counter opponent.
4. **Delivery (20):** Confidence, eye contact, composure.
**FINAL = Judges Avg scaled to 290 + Audience 10/0 = 300**
"""

if not is_audience_view:
    st.sidebar.header("SETUP")
    team_a = st.sidebar.text_input("Team A Name", config.get("team_a","Team A")).strip() or "Team A"
    team_b = st.sidebar.text_input("Team B Name", config.get("team_b","Team B")).strip() or "Team B"
    topic = st.sidebar.text_input("Topic", config.get("topic","Debate Topic"))
    sA = config.get("speakersA",["S1","S2","S3"])
    sB = config.get("speakersB",["S1","S2","S3"])
    a1 = st.sidebar.text_input(f"{team_a} S1", sA[0] if len(sA)>0 else "S1")
    a2 = st.sidebar.text_input(f"{team_a} S2", sA[1] if len(sA)>1 else "S2")
    a3 = st.sidebar.text_input(f"{team_a} S3", sA[2] if len(sA)>2 else "S3")
    b1 = st.sidebar.text_input(f"{team_b} S1", sB[0] if len(sB)>0 else "S1")
    b2 = st.sidebar.text_input(f"{team_b} S2", sB[1] if len(sB)>1 else "S2")
    b3 = st.sidebar.text_input(f"{team_b} S3", sB[2] if len(sB)>2 else "S3")
    save_config({"team_a":team_a,"team_b":team_b,"topic":topic,"speakersA":[a1,a2,a3],"speakersB":[b1,b2,b3]})
    st.sidebar.divider()
    st.sidebar.subheader("MODERATOR")
    pwd = st.sidebar.text_input("Password", type="password")
    is_moderator = (pwd == "TED2026")
else:
    team_a = config.get("team_a","Team A")
    team_b = config.get("team_b","Team B")
    topic = config.get("topic","Debate Topic")
    speakersA = config.get("speakersA",["Speaker 1","Speaker 2","Speaker 3"])
    speakersB = config.get("speakersB",["Speaker 1","Speaker 2","Speaker 3"])
    a1,a2,a3 = speakersA[0], speakersA[1], speakersA[2]
    b1,b2,b3 = speakersB[0], speakersB[1], speakersB[2]
    is_moderator = False

if not os.path.exists(VOTE_FILE): save_votes({"A":0,"B":0})
if not os.path.exists(SCORES_FILE): save_json(SCORES_FILE, {})

def speaker_block(label, key, judge_name, my_details):
    st.markdown(f"**{label}**")
    num_pts = st.number_input(f"Valid Points (5 each) - {label}", 0, 6, my_details.get(f"{key}_num",0), key=f"{judge_name}_{key}_num")
    p = num_pts * 5
    st.caption(f"{num_pts} x 5 = {p}/30")
    e = st.slider(f"Evidence (30) - {label}", 0,30, my_details.get(f"{key}_e",15), key=f"{judge_name}_{key}_e")
    r = st.slider(f"Rebuttal (20) - {label}", 0,20, my_details.get(f"{key}_r",10), key=f"{judge_name}_{key}_r")
    d = st.slider(f"Delivery (20) - {label}", 0,20, my_details.get(f"{key}_d",10), key=f"{judge_name}_{key}_d")
    total = p+e+r+d
    st.metric(f"{label} Total", f"{total}/100")
    return total, {"num":num_pts,"e":e,"r":r,"d":d}

# FIXED & SYNCED TIMER 
timer_html = f"""<div style="text-align:center; font-family:Arial; padding:20px; background:#0f172a; border-radius:15px; color:white;"><h2 id="speakerLabel" style="color:#38bdf8;">{team_a} - {a1}</h2><div id="display" style="font-size:100px; font-weight:bold; margin:15px 0;">05:00</div><div id="modeLabel" style="font-size:18px; color:#facc15;">First Speaker - 5 mins</div><select id="speakerSelect" style="padding:10px; margin:10px; border-radius:8px; min-width:200px;"><option>{team_a} - {a1}</option><option>{team_b} - {b1}</option><option>{team_a} - {a2}</option><option>{team_b} - {b2}</option><option>{team_a} - {a3}</option><option>{team_b} - {b3}</option></select><select id="timeSelect" style="padding:10px; border-radius:8px;"><option value="300">First Speaker - 5 mins</option><option value="180">Second/Third - 3 mins</option><option value="60">Summary - 1 min</option></select><br><br><button onclick="startTimer()" style="padding:12px 35px; background:#22c55e; color:white; border:none; border-radius:8px; margin:5px;">START</button><button onclick="pauseTimer()" style="padding:12px 35px; background:#f59e0b; color:white; border:none; border-radius:8px; margin:5px;">PAUSE</button><button onclick="resetTimer()" style="padding:12px 35px; background:#ef4444; color:white; border:none; border-radius:8px; margin:5px;">RESET</button><p id="status" style="color:#94a3b8; margin-top:15px;">Ready</p></div><script>
let totalSeconds=300,remaining=300,interval=null,isRunning=false,audioCtx=null;
const display=document.getElementById('display'),statusEl=document.getElementById('status'),timeSelect=document.getElementById('timeSelect'),speakerSelect=document.getElementById('speakerSelect'),speakerLabel=document.getElementById('speakerLabel'),modeLabel=document.getElementById('modeLabel');
function ensureAudio(){{ if(!audioCtx) audioCtx=new(window.AudioContext||window.webkitAudioContext)(); if(audioCtx.state==='suspended') audioCtx.resume(); }}
function playGong(t,g){{ ensureAudio(); let n=0; function h(){{ if(n>=t)return; let o=audioCtx.createOscillator(),a=audioCtx.createGain(); o.type='sine'; o.frequency.value=440; a.gain.setValueAtTime(1,audioCtx.currentTime); a.gain.exponentialRampToValueAtTime(0.01,audioCtx.currentTime+1.5); o.connect(a); a.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime+1.5); n++; setTimeout(h,g);}} h();}}
function updateDisplay(){{ let m=Math.floor(remaining/60),s=remaining%60; display.textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s; if(remaining==30){{display.style.color='#facc15';statusEl.textContent='30s left - 2 GONGS!'; playGong(2,600);}} else if(remaining==0){{display.style.color='#ef4444';statusEl.textContent='TIME UP - 5 GONGS!'; playGong(5,800);}} else if(remaining<=30){{display.style.color='#facc15';}} else {{display.style.color='white';}}}}
speakerSelect.addEventListener('change',()=>{{ speakerLabel.textContent=speakerSelect.value; }});
timeSelect.addEventListener('change',()=>{{ totalSeconds=parseInt(timeSelect.value); remaining=totalSeconds; modeLabel.textContent=timeSelect.options[timeSelect.selectedIndex].text; statusEl.textContent='Ready - '+modeLabel.textContent; updateDisplay(); }});
function startTimer(){{ ensureAudio(); if(isRunning)return; isRunning=true; statusEl.textContent='Running...'; interval=setInterval(()=>{{ if(remaining>0){{remaining--; updateDisplay();}}else{{clearInterval(interval);isRunning=false;}}}},1000);}}
function pauseTimer(){{clearInterval(interval);isRunning=false; statusEl.textContent='Paused';}}
function resetTimer(){{clearInterval(interval);isRunning=false;remaining=totalSeconds;display.style.color='white';statusEl.textContent='Reset - Ready';updateDisplay();}}
updateDisplay();
</script>"""

if is_audience_view:
    st.markdown(f"<h2 style='text-align:center'>🎤 {team_a} VS {team_b}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'><b>Topic:</b> {topic}</p>", unsafe_allow_html=True)
    st.divider()
    st.header("LIVE AUDIENCE VOTE")
    votes = load_votes()
    st.metric("Live Votes", f"{team_a}: {votes['A']} | {team_b}: {votes['B']}")
    if "has_voted" not in st.session_state: st.session_state.has_voted=False; st.session_state.voted_for=""
    if st.session_state.has_voted:
        st.success(f"You voted for {st.session_state.voted_for} - Thank you!")
    else:
        c1,c2 = st.columns(2)
        with c1:
            if st.button(f"VOTE {team_a}", use_container_width=True, type="primary"):
                v=load_votes(); v["A"]+=1; save_votes(v); st.session_state.has_voted=True; st.session_state.voted_for=team_a; st.rerun()
        with c2:
            if st.button(f"VOTE {team_b}", use_container_width=True, type="primary"):
                v=load_votes(); v["B"]+=1; save_votes(v); st.session_state.has_voted=True; st.session_state.voted_for=team_b; st.rerun()
else:
    tab_timer, tab_judge, tab_audience = st.tabs(["⏱️ TIMER + GONG", "📊 JUDGE - 3 Speakers", "👥 AUDIENCE LIVE VOTE"])
    with tab_timer:
        components.html(timer_html, height=550)
    with tab_judge:
        st.subheader(f"Topic: {topic}")
        st.info(DEFINITIONS)
        judge_name = st.text_input("Enter Your Name as Judge", placeholder="e.g Judge 1 - Pastor Abas")
        if not judge_name:
            st.warning("Enter judge name to start")
            st.stop()
        all_scores = load_json(SCORES_FILE, {})
        my_data = all_scores.get(judge_name, {"teams":{"A":[0,0,0],"B":[0,0,0]}, "details":{}})
        my_details = my_data.get("details", {})

        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"## 🎤 {team_a}")
            with st.expander(f"{a1} - S1", expanded=True):
                s1_total, s1_det = speaker_block(a1, "a1", judge_name, my_details)
                my_details.update({f"a1_num":s1_det["num"], f"a1_e":s1_det["e"], f"a1_r":s1_det["r"], f"a1_d":s1_det["d"]})
            with st.expander(f"{a2} - S2"):
                s2_total, s2_det = speaker_block(a2, "a2", judge_name, my_details)
                my_details.update({f"a2_num":s2_det["num"], f"a2_e":s2_det["e"], f"a2_r":s2_det["r"], f"a2_d":s2_det["d"]})
            with st.expander(f"{a3} - S3"):
                s3_total, s3_det = speaker_block(a3, "a3", judge_name, my_details)
                my_details.update({f"a3_num":s3_det["num"], f"a3_e":s3_det["e"], f"a3_r":s3_det["r"], f"a3_d":s3_det["d"]})
            team_a_total = s1_total+s2_total+s3_total
            st.success(f"{team_a} TOTAL (You): {team_a_total}/300")
        with colB:
            st.markdown(f"## 🎤 {team_b}")
            with st.expander(f"{b1} - S1", expanded=True):
                b_s1_total, b_s1_det = speaker_block(b1, "b1", judge_name, my_details)
                my_details.update({f"b1_num":b_s1_det["num"], f"b1_e":b_s1_det["e"], f"b1_r":b_s1_det["r"], f"b1_d":b_s1_det["d"]})
            with st.expander(f"{b2} - S2"):
                b_s2_total, b_s2_det = speaker_block(b2, "b2", judge_name, my_details)
                my_details.update({f"b2_num":b_s2_det["num"], f"b2_e":b_s2_det["e"], f"b2_r":b_s2_det["r"], f"b2_d":b_s2_det["d"]})
            with st.expander(f"{b3} - S3"):
                b_s3_total, b_s3_det = speaker_block(b3, "b3", judge_name, my_details)
                my_details.update({f"b3_num":b_s3_det["num"], f"b3_e":b_s3_det["e"], f"b3_r":b_s3_det["r"], f"b3_d":b_s3_det["d"]})
            team_b_total = b_s1_total+b_s2_total+b_s3_total
            st.success(f"{team_b} TOTAL (You): {team_b_total}/300")

        if st.button("SUBMIT MY SCORES", type="primary"):
            all_scores[judge_name] = {"teams":{"A":[s1_total,s2_total,s3_total],"B":[b_s1_total,b_s2_total,b_s3_total]}, "details":my_details}
            save_json(SCORES_FILE, all_scores)
            st.success(f"Synced for {judge_name}")

        st.divider()
        if is_moderator:
            st.subheader("MODERATOR - FINAL /300")
            all_scores = load_json(SCORES_FILE, {})
            votes_data = load_votes()
            v_a = votes_data.get("A",0); v_b = votes_data.get("B",0)
            if not all_scores: st.write("No judge yet")
            else:
                for jname, jdata in all_scores.items():
                    st.write(f"{jname}: {team_a}={sum(jdata['teams']['A'])} | {team_b}={sum(jdata['teams']['B'])}")
                avgA = sum([sum(v["teams"]["A"]) for v in all_scores.values()]) / len(all_scores)
                avgB = sum([sum(v["teams"]["B"]) for v in all_scores.values()]) / len(all_scores)
                scaledA = avgA * 290 / 300
                scaledB = avgB * 290 / 300
                if v_a > v_b: bonus_a, bonus_b = 10, 0
                elif v_b > v_a: bonus_a, bonus_b = 0, 10
                else: bonus_a, bonus_b = (5,5) if (v_a+v_b)>0 else (0,0)
                final_a = scaledA + bonus_a; final_b = scaledB + bonus_b
                st.info(f"Judges Avg: {team_a} {avgA:.1f} | {team_b} {avgB:.1f} -> Scaled to 290: {scaledA:.1f} | {scaledB:.1f}")
                st.info(f"Audience: {team_a} {v_a} vs {team_b} {v_b} -> Bonus {bonus_a}/{bonus_b}")
                st.markdown(f"## FINAL /300: {team_a} {final_a:.1f} - {final_b:.1f} {team_b}")
                if final_a>final_b: st.success(f"WINNER: {team_a}")
                elif final_b>final_a: st.success(f"WINNER: {team_b}")
                else: st.info("TIE")
                if st.button("RESET ALL"): save_json(SCORES_FILE, {}); save_votes({"A":0,"B":0}); st.rerun()

    with tab_audience:
        st.header("LIVE AUDIENCE VOTE")
        votes = load_votes()
        st.write(f"Current: {team_a} {votes['A']} - {team_b} {votes['B']}")
        if is_moderator:
            if st.button("Reset Audience Votes"): save_votes({"A":0,"B":0}); st.rerun()

st.divider()
st.markdown(f"<div style='text-align:center; padding:15px; background:#f1f5f9; border-radius:10px;'><p style='margin:0; font-weight:bold;'>TED INNOVATIONS 2026</p><p style='margin:0; font-size:12px;'>RCCG New Hope of Life Area | {datetime.now().year}</p></div>", unsafe_allow_html=True)
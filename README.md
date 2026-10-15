# RCCG Debate Live - TED INNOVATIONS 2026

Live debate scoring system with timer, judges scoring, and audience voting.

Built for **RCCG New Hope of Life Area** Debate.

### Features
- ⏱️ Timer with Gong: 5 mins (1st speaker), 3 mins (2nd/3rd), 1 min summary. 2 gongs at 30s, 5 gongs at TIME UP.
- 📊 Judge Scoring: 3 speakers per team, 100 marks per speaker (Point 30, Evidence 30, Rebuttal 20, Delivery 10, Bible Bonus +10). Total 300 per team.
- 👥 Audience Live Vote: Secret voting, one vote per device, 15 points to winner, 5 to loser.
- 🔒 Moderator View: Password protected live count.

### The 2 Links Logic
This app runs once but shows 2 different screens based on URL parameter `?role=`

- **Judge / Projector Link:** `https://your-app-name.streamlit.app/?role=judge`
    - Shows TIMER + JUDGE + AUDIENCE VOTE tabs.
    - Set Team Names, Topic, Speaker Names (syncs to audience).
    - Reset scores per team or all.

- **Audience Link:** `https://your-app-name.streamlit.app/?role=audience`
    - Shows VOTE ONLY
    - No scores, no timer, numbers hidden.
    - Names and Topic auto-sync from judge side.


### How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
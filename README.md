# ISS Bluesky Bot

Bluesky bot that posts pass predictions for Sheffield, UK. Follow over at [@isspassbot.bsky.social](https://bsky.app/profile/isspassbot.bsky.social) Fork of my
[satellite tracker](https://github.com/liampallett/satellite-tracker) project.

---

# What the Project Is

- Tracks the ISS
- Makes pass predictions
- Posts on Bluesky

---

# How It Works

- API call to Celestrak returns OMM JSON data.
- Propagates orbit forward from TLE epoch to current time.
- Converts coordinate frames into Earth latitude/longitude.
- Applies GST rotation to account for Earth's rotation.
- Computes observer position in Sheffield in ECEF and rotates into ECI using GST
- Projects satellite-observer difference vector in the local frame
- Calculate elevation and azimuth from difference vector
- Predicts future passes by iterating over future elevation/azimuth until a visible pass is found
- Posts to Bluesky

---

# Tech Stack

- Languages: Python
- Libraries: requests
- Tools: Celestrak, Bluesky

---

# What I Learned

- API calling
- Keplerian orbital mechanics
- Co-ordinate frame translation
- Orbital predictions
- AT Protocol basics
- GitHub Actions

---

# Project Structure

```
├── LICENSE.md
├── README.md
├── main.py
├── poster.py
├── predictor.py
├── propagator.py
└── requirements.txt
```

---

# How to Run the Project

```bash
git clone https://github.com/liampallett/iss-bluesky-bot.git
pip install -r requirements.txt
export BSKY_HANDLE="your-handle"
export BSKY_APP_PASSWORD="your-app-password"
python main.py
```

---

# Future Improvements

- Only post about visible passes

---

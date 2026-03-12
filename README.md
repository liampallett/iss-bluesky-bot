# Project Title

Satellite visualiser using [celestrak.org](celestrak.org) written in Python.

---

![Satellite Visualiser](images/screenshot.png)

# What the Project Is

- Tracks any satellite/group of satellites (currently configured for space stations).

---

# How It Works

- API call to Celestrak returns OMM JSON data.
- Propagates orbit forward from TLE epoch to current time.
- Converts coordinate frames into Earth latitude/longitude.
- Applies GST rotation to account for Earth's rotation.
- Displays this on a equirectangular image of the Earth.

---

# Tech Stack

- Languages: Python
- Libraries: matplotlib, requests
- Tools: Celestrak

---

# What I Learned

- API calling
- Advanced matplotlib 
- Keplerian orbital mechanics
- Co-ordinate frame translation
- Orbital predictions

---

# Project Structure

```
├── LICENSE.md
├── README.md
├── images
│   └── Blue_Marble_2002.jpg
├── main.py
├── propagator.py
├── requirements.txt
└── visualiser.py
```

---

# How to Run the Project

```bash
git clone https://github.com/liampallett/satellite_visualiser.git
pip install -r requirements.txt
python main.py
```

---

# Future Improvements

- Better UI styling
- SGP4 implementations
- Pass predictions
- Live TLE refreshing
- Multi-satellite trail mode

---

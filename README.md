# 🎯 Selectra — Smart Interview Agent + Auto Scorecard Generator

> *"Where interviews meet insight."*

**Microsoft Forge Hackathon 2026**

---

## 🔍 What is Selectra?

Selectra is a **heuristic-powered Interview Agent** that conducts **role-based, text-based interviews** and generates **real-time scorecards with explainable feedback**. It uses **rule-based scoring logic** — no ML models, no neural networks, no external APIs. Every score is computed through transparent, deterministic rules (keyword matching, sentence analysis, filler word detection), making every result fully auditable and explainable.

> ⚠️ **Note:** Selectra is **not AI-powered**. It does not use any machine learning, large language models, or external AI services. The term "intelligent" here refers to **smart rule-based heuristics** that mimic structured evaluation — every decision is transparent and reproducible.

**In short:** You pick a role → answer 5 tailored questions → get scored live across 4 dimensions → receive a detailed report with strengths, gaps, and next steps.

---

## ✨ Key Features

### 🎭 Role-Based Interviews
Choose from **7 interview tracks**, each with its own question bank:

| Role | Focus Areas |
|---|---|
| 🎨 Frontend Developer | React, CSS, accessibility, responsive design |
| ⚙️ Backend Developer | APIs, databases, authentication, scaling |
| 🔗 Full Stack Developer | End-to-end architecture, deployment |
| 📊 Data Science / ML | Pandas, model evaluation, feature engineering |
| ☁️ DevOps / Cloud | CI/CD, Docker, Kubernetes, monitoring |
| 🔒 Cybersecurity | Threat modeling, encryption, incident response |
| 💻 General / Other | Problem solving, teamwork, communication |

Each session randomly selects **2 common + 3 role-specific questions** from a bank of **38 questions** (3 common + 35 role-specific), so no two interviews are the same.

### 📊 Live Scorecard Sidebar
Four scoring dimensions update in real-time after every answer:

| Dimension | What It Measures |
|---|---|
| **Clarity** | Sentence structure, readability, vocabulary diversity |
| **Technical Accuracy** | Domain-relevant keywords and concepts |
| **Completeness** | Depth, breadth, use of examples and specifics |
| **Confidence** | Word count, assertive language, absence of filler/hesitation words |

### 🧠 Explainable Analysis Panel
Every score is backed by transparent, rule-based signal detection — **no machine learning involved**:
- Word count, sentence count, vocabulary diversity ratio
- Keyword matches against role-specific term lists
- Filler word detection (*"maybe"*, *"I guess"*, *"um"*)
- Assertive phrase detection (*"I built"*, *"I achieved"*, *"definitely"*)
- Example usage detection (*"for example"*, *"such as"*)

### 🚫 Gibberish Detection
Nonsense inputs like *"asjdhk jjdjhch"* are caught automatically. If < 40% of words are real (vowel-based heuristic), all scores return **0** and the analysis panel flags it.

### 🏅 Interview Readiness Indicator
After answering, you get a readiness badge:
- **Strong Candidate** (≥ 7.5 avg)
- **Interview Ready** (≥ 5.0 avg)
- **Needs Preparation** (< 5.0 avg)

### 📋 Final Report
A comprehensive overlay with:
- Overall score and per-dimension breakdown
- Strengths and areas for improvement
- Actionable next steps
- **JSON export** and **print-ready** formatting

### Other Features
- 🌙 **Light / Dark Mode** toggle
- 🚪 **Logout** — switch users or roles anytime (confirms if interview is in progress)
- 🔄 **New Interview** — restart without refreshing
- 📱 **Mobile Responsive** — works on tablets and phones

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13 + Flask |
| Frontend | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| Scoring | Rule-based heuristics (no ML, no external APIs) |
| Fonts | Inter, Poppins (Google Fonts) |
| Storage | In-memory Python dict (server) + LocalStorage (client auth) |

**Zero external APIs. Zero ML libraries. Fully self-contained.**

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/vikasgupta20/Selectra.git
cd Selectra
```

### 2. Set up virtual environment (recommended)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

### 5. Open in browser

```
http://127.0.0.1:5000
```

Enter your name, email, select a role, and start your interview!

---

## 📁 Project Structure

```
Selectra/
├── app.py                  # Flask backend — scoring engine, API routes, question bank
├── requirements.txt        # Python dependencies (flask>=3.0.0)
├── README.md               # This file
├── .gitignore              # Standard Python/IDE ignores
└── static/
    ├── index.html          # Login screen, chat UI, sidebar, report overlay
    ├── style.css           # Stylesheet (light/dark mode, responsive)
    └── script.js           # Frontend logic (login, chat flow, API calls, report)
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/roles` | Returns all 7 available interview roles |
| `GET` | `/api/questions?role=frontend&sessionId=xxx` | Returns 5 role-specific questions for the session |
| `POST` | `/api/evaluate` | Scores a single answer → dimensions, explanations, suggestions |
| `POST` | `/api/final-report` | Generates full report with overall insights |
| `POST` | `/api/reset` | Resets session state for a new interview |

---

## 📐 How Scoring Works

```
User Answer
    ↓
Signal Detection  →  word count, keywords, filler words, examples, assertiveness
    ↓
Gibberish Check   →  real word ratio < 40%? → all scores = 0
    ↓
Four Scorers      →  Clarity (0-10), Accuracy (0-10), Completeness (0-10), Confidence (0-10)
    ↓
Explanation       →  human-readable breakdown of why each score was assigned
    ↓
Suggestions       →  targeted advice based on score ranges (low / med / high)
    ↓
Readiness Badge   →  Strong Candidate / Interview Ready / Needs Preparation
```

All scoring is **deterministic and rule-based** — no black-box models, no randomness in evaluation.

---

## 👥 Team

Built by **Vikas Gupta** for **Microsoft Forge Hackathon 2026**.

---

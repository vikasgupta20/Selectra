# 🎯 Selectra — AI Interview + Auto Scorecard Generator

> *"Where interviews meet insight."*

**Microsoft Forge Hackathon 2026**

---

## What is Selectra?

Selectra is an intelligent, explainable AI Interview Agent that conducts text-based interviews and generates detailed scorecards with real-time feedback. It uses **heuristic-based scoring** (no ML, no external APIs) to evaluate responses across four dimensions:

| Dimension | What It Measures |
|---|---|
| **Clarity** | Sentence structure, readability, vocabulary diversity |
| **Technical Accuracy** | Presence of domain-relevant keywords and concepts |
| **Completeness** | Depth, breadth, use of examples |
| **Confidence** | Assertiveness, absence of filler/hesitation language |

---

## Features

- 🎯 **5 Interview Questions** across Introduction, Problem Solving, Technical, Teamwork & Career Goals
- 📊 **Live Scorecard Sidebar** with animated score bars updated after every answer
- 🧠 **Explainable AI Panel** showing detected signals (word count, keywords, filler words, etc.)
- 💡 **Dimension-wise Suggestions** with low / medium / high score-range advice
- 🏅 **Interview Readiness Indicator** (Strong Candidate / Interview Ready / Needs Preparation)
- 📈 **Overall Insight Summary** with strengths, improvement areas, and next steps
- 🌙 **Light & Dark Mode** with enterprise-grade UI
- 📥 **JSON Export** and 🖨️ **Print-ready Report**
- 🔄 **New Interview** — restart without refreshing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python (Flask) |
| Frontend | HTML5, CSS3, JavaScript (ES6+) |
| Fonts | Inter, Poppins (Google Fonts) |
| Storage | In-memory (Python dict), LocalStorage (auth) |

**No ML libraries. No external APIs. Just clean heuristic logic.**

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

```bash
python app.py
```

### 3. Open in browser

Navigate to **http://127.0.0.1:5000**

---

## Project Structure

```
Microsoft_forge_codeathon/
├── app.py                  # Flask backend — routes, scoring, suggestions
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── static/
    ├── index.html          # Main HTML page
    ├── style.css           # Enterprise-grade stylesheet (light/dark)
    └── script.js           # Frontend logic (fetch API, chat, sidebar, report)
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/questions` | Returns all interview questions |
| `POST` | `/api/evaluate` | Evaluates a single answer → scores + explanations + suggestions |
| `POST` | `/api/final-report` | Generates full interview report with insights |
| `POST` | `/api/reset` | Resets session for a new interview |

---

## How Scoring Works

Each answer is analyzed for **measurable signals**:

- **Word count**, sentence count, vocabulary diversity
- **Keyword matching** against question-specific term lists
- **Filler word detection** (maybe, I guess, um, etc.)
- **Assertive phrase detection** (I achieved, I built, definitely, etc.)
- **Example usage** detection (for example, such as, etc.)

These signals drive all four dimension scores (0-10), explanations, and suggestions — making every score **fully explainable**.

---

## License

Built for **Microsoft Forge Hackathon 2026**.

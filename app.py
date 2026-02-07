"""
Selectra – AI Interview + Auto Scorecard Generator
Flask Backend
"Where interviews meet insight."

A heuristic-based interview scoring engine with explainable AI feedback.
No ML libraries, no external APIs — just clean Python logic.
"""

from flask import Flask, jsonify, request, send_from_directory
import os
import re
import math
from datetime import datetime

# ─── Flask App Setup ───
app = Flask(__name__, static_folder="static", static_url_path="/static")

# ─────────────────────────────────────────────
# INTERVIEW QUESTIONS
# ─────────────────────────────────────────────
QUESTIONS = [
    {
        "id": 1,
        "text": "Tell us about yourself and your most relevant experience for this role.",
        "keywords": [
            "experience", "skills", "projects", "team", "work", "developed",
            "built", "managed", "led", "design", "engineering", "technology",
            "software", "programming", "role", "company", "university", "degree"
        ],
        "category": "Introduction"
    },
    {
        "id": 2,
        "text": "Describe a challenging technical problem you faced and how you solved it.",
        "keywords": [
            "problem", "solution", "debug", "fix", "analyze", "approach",
            "algorithm", "optimize", "issue", "resolved", "implemented",
            "strategy", "code", "tested", "performance", "architecture",
            "system", "logic"
        ],
        "category": "Problem Solving"
    },
    {
        "id": 3,
        "text": "What do you understand about data structures and when would you use a hash map vs an array?",
        "keywords": [
            "data structure", "hash", "map", "array", "lookup",
            "time complexity", "O(1)", "O(n)", "key", "value", "index",
            "search", "insert", "collision", "list", "memory",
            "performance", "access"
        ],
        "category": "Technical Knowledge"
    },
    {
        "id": 4,
        "text": "How do you approach working in a team? Can you give an example of a team collaboration?",
        "keywords": [
            "team", "collaborate", "communication", "agile", "scrum",
            "feedback", "conflict", "resolution", "together", "shared",
            "responsibility", "deadline", "meeting", "review",
            "code review", "pair", "support"
        ],
        "category": "Teamwork"
    },
    {
        "id": 5,
        "text": "Where do you see yourself in 3 years, and how does this role align with your goals?",
        "keywords": [
            "goal", "growth", "learn", "career", "leadership", "impact",
            "skill", "advance", "contribute", "develop", "mentor",
            "specialize", "expertise", "passion", "opportunity",
            "industry", "vision"
        ],
        "category": "Career Goals"
    }
]

# ─── Filler / Hesitation words (used for Confidence scoring) ───
FILLER_WORDS = [
    "maybe", "perhaps", "i think", "i guess", "not sure", "possibly",
    "kind of", "sort of", "basically", "um", "uh", "probably",
    "i don't know", "might", "could be", "not really", "unsure",
    "i suppose", "honestly", "actually"
]

# ─── Assertive phrases (boost Confidence) ───
ASSERTIVE_PHRASES = [
    "i am confident", "i believe", "i know", "i have", "i can",
    "i will", "i achieved", "i successfully", "definitely",
    "certainly", "clearly"
]

# ─── Example indicator phrases ───
EXAMPLE_PHRASES = [
    "for example", "for instance", "such as", "specifically",
    "in particular", "like when", "one time"
]

# ─── In-memory session store (simple, no database) ───
sessions = {}


# ═══════════════════════════════════════════════
# SCORING FUNCTIONS (Heuristic, Explainable)
# ═══════════════════════════════════════════════

def detect_signals(answer, question):
    """
    Detect measurable signals from an answer.
    These signals drive all scoring, explanations, and suggestions.
    Returns a dictionary of raw metrics.
    """
    lower_answer = answer.lower()
    words = [w for w in answer.split() if len(w) > 0]
    word_count = len(words)

    # Sentence detection
    sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip()]
    sentence_count = len(sentences)

    # Vocabulary diversity
    unique_words = list(set(w.lower() for w in words))
    unique_ratio = round(len(unique_words) / word_count, 2) if word_count > 0 else 0

    # Keyword matching
    matched_keywords = [
        kw for kw in question["keywords"]
        if kw.lower() in lower_answer
    ]
    keyword_match_ratio = round(
        len(matched_keywords) / len(question["keywords"]), 2
    ) if question["keywords"] else 0

    # Filler word detection
    filler_words_found = []
    filler_count = 0
    for filler in FILLER_WORDS:
        pattern = r'\b' + re.escape(filler) + r'\b'
        matches = re.findall(pattern, lower_answer, re.IGNORECASE)
        if matches:
            filler_count += len(matches)
            filler_words_found.append(filler)

    # Assertive phrase detection
    assertive_found = [
        phrase for phrase in ASSERTIVE_PHRASES
        if phrase in lower_answer
    ]

    # Example usage detection
    has_examples = any(phrase in lower_answer for phrase in EXAMPLE_PHRASES)

    # Capitalization check
    starts_with_capital = (
        len(answer) > 0 and answer[0] == answer[0].upper()
    )

    # Average sentence length
    avg_sentence_len = (
        round(word_count / sentence_count)
        if sentence_count > 0 else word_count
    )

    # Gibberish / nonsense detection
    # Check how many words are actual English-like words (3+ chars, contain vowels)
    vowels = set('aeiouAEIOU')
    real_words = [
        w for w in words
        if len(w) >= 3 and any(c in vowels for c in w)
    ]
    real_word_ratio = round(len(real_words) / word_count, 2) if word_count > 0 else 0
    is_gibberish = (real_word_ratio < 0.4) or (word_count > 0 and keyword_match_ratio == 0 and real_word_ratio < 0.6 and word_count < 15)

    return {
        "wordCount": word_count,
        "sentenceCount": sentence_count,
        "uniqueRatio": unique_ratio,
        "matchedKeywords": matched_keywords,
        "totalKeywords": len(question["keywords"]),
        "keywordMatchRatio": keyword_match_ratio,
        "fillerWordsFound": filler_words_found,
        "fillerCount": filler_count,
        "assertiveFound": assertive_found,
        "hasExamples": has_examples,
        "startsWithCapital": starts_with_capital,
        "avgSentenceLen": avg_sentence_len,
        "realWordRatio": real_word_ratio,
        "isGibberish": is_gibberish
    }


def score_clarity(signals):
    """
    CLARITY (0-10): Measures sentence structure, readability, and coherence.
    """
    # Gibberish answers get near-zero clarity
    if signals["isGibberish"]:
        return round(min(1.0, signals["realWordRatio"] * 2), 1)

    score = 5.0  # Baseline

    # Sentence count scoring
    if signals["sentenceCount"] >= 3:
        score += 2
    elif signals["sentenceCount"] >= 2:
        score += 1

    # Word count range
    wc = signals["wordCount"]
    if 30 <= wc <= 200:
        score += 2
    elif wc >= 15:
        score += 1
    else:
        score -= 2

    # Capitalization bonus
    if signals["startsWithCapital"]:
        score += 0.5

    # Penalize excessive repetition
    if signals["uniqueRatio"] < 0.4:
        score -= 2

    return round(min(10, max(0, score)), 1)


def score_accuracy(signals):
    """
    TECHNICAL ACCURACY (0-10): Measures presence of relevant keywords/concepts.
    """
    # Gibberish can't be accurate
    if signals["isGibberish"]:
        return 0.0

    ratio = signals["keywordMatchRatio"]

    if ratio >= 0.5:
        score = 9
    elif ratio >= 0.35:
        score = 7.5
    elif ratio >= 0.25:
        score = 6
    elif ratio >= 0.15:
        score = 4.5
    elif ratio >= 0.05:
        score = 3
    else:
        score = 1.5

    # Bonus for high keyword count
    if len(signals["matchedKeywords"]) >= 6:
        score = min(10, score + 1)

    return round(min(10, max(0, score)), 1)


def score_completeness(signals):
    """
    COMPLETENESS (0-10): Measures depth, breadth, and use of examples.
    """
    # Gibberish has no completeness
    if signals["isGibberish"]:
        return 0.0

    score = 3.0  # Baseline
    wc = signals["wordCount"]

    if wc >= 80:
        score += 3
    elif wc >= 50:
        score += 2.5
    elif wc >= 30:
        score += 1.5
    elif wc >= 15:
        score += 0.5
    else:
        score -= 1

    # Sentence variety
    sc = signals["sentenceCount"]
    if sc >= 5:
        score += 2.5
    elif sc >= 3:
        score += 1.5
    elif sc >= 2:
        score += 0.5

    # Example bonus
    if signals["hasExamples"]:
        score += 0.5

    return round(min(10, max(0, score)), 1)


def score_confidence(signals):
    """
    CONFIDENCE (0-10): Measures assertiveness and absence of hedging.
    """
    # Gibberish = no confidence
    if signals["isGibberish"]:
        return 0.0

    # Start at baseline — must earn confidence through real content
    score = 5.0

    # Bonus for reasonable answer length (shows commitment)
    wc = signals["wordCount"]
    if wc >= 40:
        score += 2
    elif wc >= 20:
        score += 1.5
    elif wc >= 10:
        score += 0.5
    else:
        score -= 2

    # Deduct for filler words (max -4)
    score -= min(signals["fillerCount"] * 0.8, 4)

    # Bonus for assertive language (max +2)
    score += min(len(signals["assertiveFound"]) * 0.5, 2)

    # Bonus for having real word content
    if signals["realWordRatio"] >= 0.8:
        score += 0.5

    return round(min(10, max(0, score)), 1)


def compute_scores(signals):
    """Compute all four dimension scores from signals."""
    return {
        "clarity": score_clarity(signals),
        "accuracy": score_accuracy(signals),
        "completeness": score_completeness(signals),
        "confidence": score_confidence(signals)
    }


# ═══════════════════════════════════════════════
# EXPLANATION GENERATION
# ═══════════════════════════════════════════════

def generate_explanation(dimension, score, signals):
    """
    Generate a human-readable explanation for why a score was given.
    Shows what signals were detected.
    """
    text = ""
    detected = []

    # Early return for gibberish
    if signals["isGibberish"]:
        detected.append("non-meaningful content detected")
        detected.append(f"only {round(signals['realWordRatio'] * 100)}% recognizable words")
        dim_label = dimension.replace("accuracy", "Technical Accuracy").replace("clarity", "Clarity").replace("completeness", "Completeness").replace("confidence", "Confidence")
        return {
            "dimension": dim_label,
            "score": score,
            "text": "Response appears to be nonsensical or gibberish. Please provide a meaningful answer.",
            "signalsDetected": detected
        }

    if dimension == "clarity":
        detected.append(f"{signals['sentenceCount']} sentence(s) detected")
        detected.append(f"{signals['wordCount']} words total")
        if signals["startsWithCapital"]:
            detected.append("proper capitalization")
        if signals["uniqueRatio"] < 0.4:
            detected.append("high word repetition detected")
        elif signals["uniqueRatio"] > 0.7:
            detected.append("diverse vocabulary")

        if score >= 7:
            text = "Well-structured response with clear sentence organization."
        elif score >= 4:
            text = "Adequate structure. Additional sentences would improve readability."
        else:
            text = "Response lacks sentence structure or is too brief for clear communication."

    elif dimension == "accuracy":
        matched = signals["matchedKeywords"]
        total = signals["totalKeywords"]
        detected.append(f"{len(matched)} of {total} keywords matched")
        if matched:
            preview = ", ".join(matched[:5])
            if len(matched) > 5:
                preview += "..."
            detected.append(f"Found: {preview}")

        if score >= 7:
            text = "Strong keyword presence indicates solid understanding of the topic."
        elif score >= 4:
            text = "Some relevant concepts present but key terms are missing."
        else:
            text = "Very few domain-relevant terms detected in the response."

    elif dimension == "completeness":
        detected.append(f"{signals['wordCount']} words total")
        detected.append(f"{signals['sentenceCount']} sentence(s)")
        if signals["hasExamples"]:
            detected.append("includes concrete examples")
        else:
            detected.append("no specific examples detected")

        if score >= 7:
            text = "Thorough response covering multiple facets of the question."
        elif score >= 4:
            text = "Covers the basics but could explore the topic further."
        else:
            text = "Response is too brief or narrow to be considered complete."

    elif dimension == "confidence":
        if signals["fillerCount"] == 0:
            detected.append("no filler/hesitation words")
        else:
            fillers = ", ".join(signals["fillerWordsFound"][:4])
            detected.append(f"{signals['fillerCount']} filler word(s): {fillers}")
        if signals["assertiveFound"]:
            phrases = ", ".join(signals["assertiveFound"][:3])
            detected.append(f"assertive phrases: {phrases}")
        else:
            detected.append("no assertive phrases detected")

        if score >= 7:
            text = "Confident, assertive tone with minimal hesitation."
        elif score >= 4:
            text = "Moderate confidence. Some uncertainty phrases dilute the message."
        else:
            text = "Response suggests significant uncertainty or excessive hedging."

    return {
        "dimension": dimension.replace("accuracy", "Technical Accuracy").replace("clarity", "Clarity").replace("completeness", "Completeness").replace("confidence", "Confidence"),
        "score": score,
        "text": text,
        "signalsDetected": detected
    }


# ═══════════════════════════════════════════════
# SUGGESTION GENERATION (Score-range Based)
# ═══════════════════════════════════════════════

def generate_suggestion(score, dimension, signals):
    """
    Generate actionable suggestions based on score range.
    Low (0-3): Improvement advice
    Medium (4-6): Refinement suggestions
    High (7-10): Positive reinforcement + next-level tips
    """
    if score <= 3:
        level = "low"
        icon = "⚠️"
        text = _suggestion_low(dimension, signals)
    elif score <= 6:
        level = "medium"
        icon = "💡"
        text = _suggestion_medium(dimension, signals)
    else:
        level = "high"
        icon = "✅"
        text = _suggestion_high(dimension, signals)

    dim_labels = {
        "clarity": "Clarity",
        "accuracy": "Technical Accuracy",
        "completeness": "Completeness",
        "confidence": "Confidence"
    }

    return {
        "level": level,
        "text": text,
        "icon": icon,
        "score": score,
        "dimension": dim_labels.get(dimension, dimension)
    }


def _suggestion_low(dimension, signals):
    """Low-score suggestions (0-3)."""
    if dimension == "clarity":
        if signals["wordCount"] < 15:
            return "Your response is very brief. Aim for at least 3–4 complete sentences with a clear beginning, middle, and conclusion."
        if signals["uniqueRatio"] < 0.4:
            return "There is noticeable word repetition. Vary your vocabulary and structure thoughts into distinct sentences."
        return "Improve clarity by organizing your answer into clear sentences. Start with your main point, support with details, then summarize."
    if dimension == "accuracy":
        if not signals["matchedKeywords"]:
            return "Your answer did not include key technical terms. Review the topic and incorporate specific terminology and concepts."
        return f"Only {len(signals['matchedKeywords'])} relevant term(s) detected. Use more domain-specific vocabulary and reference concrete concepts."
    if dimension == "completeness":
        if signals["wordCount"] < 15:
            return "Your response is too brief. Expand with at least 3–5 sentences covering different aspects of the question."
        return "Your answer covers limited ground. Address multiple facets and include specific examples to demonstrate depth."
    # confidence
    if signals["fillerCount"] > 3:
        fillers = "', '".join(signals["fillerWordsFound"][:3])
        return f"Multiple hesitation phrases detected ('{fillers}'). Practice delivering answers with direct, assertive language."
    return "The response conveys uncertainty. Use definitive statements like 'I achieved...' or 'I built...' to project confidence."


def _suggestion_medium(dimension, signals):
    """Medium-score suggestions (4-6)."""
    if dimension == "clarity":
        if signals["sentenceCount"] < 3:
            return "Your answer is reasonably clear but could benefit from additional sentences to fully develop your point."
        return "Good clarity foundation. Ensure each sentence transitions smoothly to the next for a cohesive narrative."
    if dimension == "accuracy":
        return f"You referenced {len(signals['matchedKeywords'])} of {signals['totalKeywords']} expected concepts. Mentioning more domain-specific terms would elevate accuracy."
    if dimension == "completeness":
        if not signals["hasExamples"]:
            return "Solid answer overall. Adding a concrete example or use case would make it more complete and convincing."
        return "Good detail level. Consider expanding on additional angles or trade-offs to demonstrate comprehensive understanding."
    # confidence
    if signals["fillerCount"] > 0:
        return f"Your answer is confident overall, but reducing hesitation phrases like '{signals['fillerWordsFound'][0]}' would strengthen delivery."
    return "Confident tone detected. Adding a personal achievement statement would further reinforce self-assurance."


def _suggestion_high(dimension, signals):
    """High-score suggestions (7-10)."""
    if dimension == "clarity":
        return "Excellent clarity! Well-structured and easy to follow. To reach the next level, consider using transition phrases between ideas."
    if dimension == "accuracy":
        return f"Strong technical accuracy with {len(signals['matchedKeywords'])} relevant concepts. For even greater impact, relate concepts to real-world applications."
    if dimension == "completeness":
        if signals["hasExamples"]:
            return "Very thorough response with examples included. Exceptional completeness — maintain this standard across all answers."
        return "Comprehensive answer. Adding a brief example would make it truly outstanding."
    # confidence
    if signals["assertiveFound"]:
        return "Highly confident delivery with assertive language. This projects professionalism — keep this approach."
    return "Strong confident tone. Consider adding quantified achievements to amplify impact."


# ═══════════════════════════════════════════════
# OVERALL INSIGHTS (Post-Interview Summary)
# ═══════════════════════════════════════════════

def get_readiness_indicator(overall):
    """Determine interview readiness badge based on overall score."""
    if overall >= 7.5:
        return {
            "label": "Strong Candidate",
            "level": "high",
            "description": "Demonstrates excellent interview skills across all dimensions.",
            "className": "readiness-high"
        }
    elif overall >= 5:
        return {
            "label": "Interview Ready",
            "level": "medium",
            "description": "Solid performance with room for targeted improvement.",
            "className": "readiness-medium"
        }
    else:
        return {
            "label": "Needs Preparation",
            "level": "low",
            "description": "Additional practice recommended before proceeding to interviews.",
            "className": "readiness-low"
        }


def compute_overall_insights(answers_data):
    """
    Generate a final interview insight summary from all answer data.
    Returns strengths, improvements, next steps, and readiness.
    """
    if not answers_data:
        return None

    count = len(answers_data)
    totals = {"clarity": 0, "accuracy": 0, "completeness": 0, "confidence": 0}

    for entry in answers_data:
        scores = entry["scores"]
        totals["clarity"] += scores["clarity"]
        totals["accuracy"] += scores["accuracy"]
        totals["completeness"] += scores["completeness"]
        totals["confidence"] += scores["confidence"]

    avg = {k: round(v / count, 1) for k, v in totals.items()}
    overall = round(sum(avg.values()) / 4, 1)

    # Sort dimensions by score
    dim_list = [
        {"name": "Clarity", "key": "clarity", "score": avg["clarity"]},
        {"name": "Technical Accuracy", "key": "accuracy", "score": avg["accuracy"]},
        {"name": "Completeness", "key": "completeness", "score": avg["completeness"]},
        {"name": "Confidence", "key": "confidence", "score": avg["confidence"]},
    ]
    dim_list.sort(key=lambda d: d["score"], reverse=True)

    # Top 2 = strengths
    strengths = []
    for d in dim_list[:2]:
        if d["score"] >= 5:
            strengths.append({
                "name": d["name"],
                "score": d["score"],
                "note": _strength_note(d["key"], d["score"])
            })

    # Bottom 2 = improvement areas
    improvements = []
    for d in dim_list[-2:]:
        if d["score"] < 8:
            improvements.append({
                "name": d["name"],
                "score": d["score"],
                "note": _improvement_note(d["key"], d["score"])
            })

    # Next steps
    next_steps = _generate_next_steps(avg, answers_data)

    readiness = get_readiness_indicator(overall)

    return {
        "overall": overall,
        "averages": avg,
        "strengths": strengths,
        "improvements": improvements,
        "nextSteps": next_steps,
        "readiness": readiness
    }


def _strength_note(key, score):
    notes = {
        "clarity": "Responses are well-structured and easy to follow." if score >= 7
            else "Answers show reasonable clarity in communication.",
        "accuracy": "Demonstrates strong domain knowledge with relevant terminology." if score >= 7
            else "Shows adequate understanding of technical concepts.",
        "completeness": "Provides thorough, multi-faceted responses with supporting detail." if score >= 7
            else "Covers the essential points in each answer.",
        "confidence": "Communicates with conviction and assertive, professional language." if score >= 7
            else "Maintains a generally confident tone throughout."
    }
    return notes.get(key, "")


def _improvement_note(key, score):
    notes = {
        "clarity": "Needs significantly more structure — practice organizing thoughts before responding." if score < 4
            else "Could benefit from more polished sentence transitions and flow.",
        "accuracy": "Technical vocabulary is lacking — review core concepts for the target role." if score < 4
            else "Incorporating more specific terms and concepts would strengthen responses.",
        "completeness": "Answers are too brief — practice expanding with examples and multiple perspectives." if score < 4
            else "Adding concrete examples and covering more angles would improve depth.",
        "confidence": "Excessive use of hedging language — practice direct, assertive phrasing." if score < 4
            else "Minor hesitation phrases can be eliminated for a more polished delivery."
    }
    return notes.get(key, "")


def _generate_next_steps(avg, answers_data):
    """Generate 2-3 actionable next steps."""
    steps = []

    # Step 1: Address weakest dimension
    weakest = min(avg, key=avg.get)
    step_map = {
        "clarity": "Practice the STAR method (Situation, Task, Action, Result) to structure answers more clearly.",
        "accuracy": "Review key technical concepts for your target role and practice using specific terminology.",
        "completeness": "Before answering, mentally outline 2–3 points to cover, then expand each with detail.",
        "confidence": "Record yourself answering practice questions and identify filler words to eliminate."
    }
    steps.append(step_map[weakest])

    # Step 2: General improvement
    total_words = sum(entry["signals"]["wordCount"] for entry in answers_data)
    avg_words = round(total_words / len(answers_data))
    has_any_examples = any(entry["signals"]["hasExamples"] for entry in answers_data)

    if avg_words < 40:
        steps.append(
            f"Your average response length is {avg_words} words. "
            "Aim for 50–100 words per answer for more thorough coverage."
        )
    elif not has_any_examples:
        steps.append(
            "None of your answers included specific examples. "
            "Practice incorporating real experiences to make responses more compelling."
        )
    else:
        steps.append(
            "Continue preparing with mock interviews to build consistency across all dimensions."
        )

    # Step 3: Reinforce strongest
    strongest = max(avg, key=avg.get)
    reinforce_map = {
        "clarity": "Your communication clarity is a strength — leverage it in presentations and demos.",
        "accuracy": "Your technical knowledge is solid — consider deepening into specialized areas.",
        "completeness": "Your thoroughness stands out — channel this skill into technical documentation.",
        "confidence": "Your confident delivery is impressive — consider mentoring peers on interview prep."
    }
    steps.append(reinforce_map[strongest])

    return steps


# ═══════════════════════════════════════════════
# FLASK API ROUTES
# ═══════════════════════════════════════════════

@app.route("/")
def serve_index():
    """Serve the main HTML page."""
    return send_from_directory("static", "index.html")


@app.route("/api/questions", methods=["GET"])
def get_questions():
    """Return all interview questions."""
    questions_out = []
    for q in QUESTIONS:
        questions_out.append({
            "id": q["id"],
            "text": q["text"],
            "category": q["category"]
        })
    return jsonify({"questions": questions_out, "total": len(questions_out)})


@app.route("/api/evaluate", methods=["POST"])
def evaluate_answer():
    """
    Evaluate a single answer.
    Expects JSON: { "sessionId": "...", "questionId": 1, "answer": "..." }
    Returns scores, explanations, suggestions, and signals.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    session_id = data.get("sessionId", "default")
    question_id = data.get("questionId")
    answer = data.get("answer", "").strip()

    if not answer:
        return jsonify({"error": "Answer cannot be empty"}), 400

    # Find the question
    question = None
    for q in QUESTIONS:
        if q["id"] == question_id:
            question = q
            break

    if not question:
        return jsonify({"error": f"Question {question_id} not found"}), 404

    # Detect signals
    signals = detect_signals(answer, question)

    # Compute scores
    scores = compute_scores(signals)

    # Generate explanations
    explanations = []
    for dim in ["clarity", "accuracy", "completeness", "confidence"]:
        explanations.append(generate_explanation(dim, scores[dim], signals))

    # Generate suggestions
    suggestions = {}
    for dim in ["clarity", "accuracy", "completeness", "confidence"]:
        suggestions[dim] = generate_suggestion(scores[dim], dim, signals)

    # Store in session
    if session_id not in sessions:
        sessions[session_id] = {"answers": [], "user": None}

    sessions[session_id]["answers"].append({
        "questionId": question_id,
        "question": question,
        "answer": answer,
        "scores": scores,
        "explanations": explanations,
        "suggestions": suggestions,
        "signals": signals
    })

    # Compute running averages
    all_answers = sessions[session_id]["answers"]
    running_avg = _compute_running_averages(all_answers)

    return jsonify({
        "questionId": question_id,
        "scores": scores,
        "explanations": explanations,
        "suggestions": suggestions,
        "signals": {
            "wordCount": signals["wordCount"],
            "sentenceCount": signals["sentenceCount"],
            "matchedKeywords": signals["matchedKeywords"],
            "fillerWordsFound": signals["fillerWordsFound"],
            "hasExamples": signals["hasExamples"],
            "isGibberish": signals["isGibberish"],
            "realWordRatio": signals["realWordRatio"]
        },
        "runningAverages": running_avg,
        "readiness": get_readiness_indicator(running_avg["overall"])
    })


@app.route("/api/final-report", methods=["POST"])
def final_report():
    """
    Generate the final interview report.
    Expects JSON: { "sessionId": "...", "interviewer": { "name": "...", "email": "..." } }
    """
    data = request.get_json() or {}
    session_id = data.get("sessionId", "default")
    interviewer = data.get("interviewer", {})

    if session_id not in sessions or not sessions[session_id]["answers"]:
        return jsonify({"error": "No interview data found for this session"}), 404

    answers_data = sessions[session_id]["answers"]
    insights = compute_overall_insights(answers_data)

    # Build response list
    responses = []
    for entry in answers_data:
        responses.append({
            "questionId": entry["questionId"],
            "category": entry["question"]["category"],
            "question": entry["question"]["text"],
            "answer": entry["answer"],
            "scores": entry["scores"],
            "explanations": entry["explanations"],
            "suggestions": entry["suggestions"]
        })

    return jsonify({
        "appName": "Selectra",
        "tagline": "Where interviews meet insight.",
        "generatedAt": datetime.now().isoformat(),
        "interviewer": interviewer,
        "overallScore": insights["overall"],
        "dimensionAverages": insights["averages"],
        "readinessIndicator": insights["readiness"],
        "interviewInsights": {
            "strengths": insights["strengths"],
            "improvementAreas": insights["improvements"],
            "actionableNextSteps": insights["nextSteps"]
        },
        "responses": responses
    })


@app.route("/api/reset", methods=["POST"])
def reset_session():
    """Reset a session for a new interview."""
    data = request.get_json() or {}
    session_id = data.get("sessionId", "default")
    sessions[session_id] = {"answers": [], "user": None}
    return jsonify({"message": "Session reset successfully"})


def _compute_running_averages(answers_data):
    """Compute running average scores across all answered questions."""
    count = len(answers_data)
    totals = {"clarity": 0, "accuracy": 0, "completeness": 0, "confidence": 0}
    for entry in answers_data:
        for dim in totals:
            totals[dim] += entry["scores"][dim]
    avg = {k: round(v / count, 1) for k, v in totals.items()}
    avg["overall"] = round(sum(avg.values()) / 4, 1)
    return avg


# ═══════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    # Create static folder if it doesn't exist
    os.makedirs("static", exist_ok=True)
    print("\n  🎯 Selectra is running!")
    print("  Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)

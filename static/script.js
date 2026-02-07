/**
 * ════════════════════════════════════════════════════
 * SELECTRA – AI Interview Agent  (Frontend Logic)
 * "Where interviews meet insight."
 *
 * Connects to Flask backend via fetch() API
 * Handles: Login, Chat Conversation, Live Scorecard,
 *          XAI Panel, Suggestions, Report Generation
 * ════════════════════════════════════════════════════
 */

// ─── State ───
const state = {
    sessionId: "session_" + Date.now(),
    user: null,
    role: "general",
    questions: [],
    currentQuestionIndex: 0,
    answers: [],
    isWaiting: false,
    interviewComplete: false,
    reportData: null,
    latestScores: null,
    latestSuggestions: null,
    latestExplanations: null,
    readiness: null
};

// ─── DOM References ───
const $ = (id) => document.getElementById(id);

const DOM = {
    // Login
    loginScreen: $("loginScreen"),
    loginName: $("loginName"),
    loginEmail: $("loginEmail"),
    loginRole: $("loginRole"),
    loginBtn: $("loginBtn"),
    // App
    appContainer: $("appContainer"),
    headerUser: $("headerUser"),
    themeToggle: $("themeToggle"),
    logoutBtn: $("logoutBtn"),
    // Chat
    chatMessages: $("chatMessages"),
    answerInput: $("answerInput"),
    sendBtn: $("sendBtn"),
    inputHint: $("inputHint"),
    // Sidebar
    progressText: $("progressText"),
    progressDetail: $("progressDetail"),
    progressRingFill: $("progressRingFill"),
    progressRingText: $("progressRingText"),
    overallScoreCard: $("overallScoreCard"),
    overallScoreValue: $("overallScoreValue"),
    scoresContainer: $("scoresContainer"),
    readinessBadge: $("readinessBadge"),
    suggestionsContainer: $("suggestionsContainer"),
    xaiPanel: $("xaiPanel"),
    // Report
    reportSection: $("reportSection"),
    reportContent: $("reportContent")
};

// ═══════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    bindEvents();
    checkExistingSession();
});

function bindEvents() {
    DOM.loginBtn.addEventListener("click", handleLogin);
    DOM.sendBtn.addEventListener("click", sendAnswer);
    DOM.themeToggle.addEventListener("click", toggleTheme);
    DOM.logoutBtn.addEventListener("click", handleLogout);

    DOM.answerInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendAnswer();
        }
    });

    // Auto-resize textarea
    DOM.answerInput.addEventListener("input", () => {
        DOM.answerInput.style.height = "auto";
        DOM.answerInput.style.height = DOM.answerInput.scrollHeight + "px";
    });

    // Login form enter key
    DOM.loginEmail.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleLogin();
    });

    DOM.loginRole.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleLogin();
    });
}

function checkExistingSession() {
    const saved = localStorage.getItem("selectra_user");
    if (saved) {
        state.user = JSON.parse(saved);
        state.role = localStorage.getItem("selectra_role") || "general";
        startApp();
    }
}

function handleLogout() {
    if (state.answers.length > 0 && !state.interviewComplete) {
        if (!confirm("You have an interview in progress. Are you sure you want to logout?")) return;
    }
    localStorage.removeItem("selectra_user");
    localStorage.removeItem("selectra_role");
    state.user = null;
    state.role = "general";
    state.questions = [];
    state.answers = [];
    state.currentQuestionIndex = 0;
    state.isWaiting = false;
    state.interviewComplete = false;
    state.reportData = null;
    state.latestScores = null;
    state.latestSuggestions = null;
    state.latestExplanations = null;
    state.readiness = null;
    state.sessionId = "session_" + Date.now();

    DOM.chatMessages.innerHTML = "";
    DOM.answerInput.value = "";
    DOM.answerInput.disabled = true;
    DOM.sendBtn.disabled = true;
    DOM.inputHint.textContent = "Waiting to start...";
    DOM.loginName.value = "";
    DOM.loginEmail.value = "";
    DOM.loginRole.value = "general";

    DOM.loginScreen.style.display = "flex";
    DOM.appContainer.style.display = "none";
    document.getElementById("reportSection").style.display = "none";
}

// ═══════════════════════════════════════════════
// THEME MANAGEMENT
// ═══════════════════════════════════════════════

function initTheme() {
    const saved = localStorage.getItem("selectra_theme") || "light";
    document.documentElement.setAttribute("data-theme", saved);
    updateThemeIcon(saved);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("selectra_theme", next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    DOM.themeToggle.textContent = theme === "dark" ? "☀️" : "🌙";
}

// ═══════════════════════════════════════════════
// LOGIN
// ═══════════════════════════════════════════════

function handleLogin() {
    const name = DOM.loginName.value.trim();
    const email = DOM.loginEmail.value.trim();

    if (!name || !email) {
        shakeElement(DOM.loginBtn);
        return;
    }

    if (!email.includes("@")) {
        shakeElement(DOM.loginEmail);
        return;
    }

    state.user = { name, email };
    state.role = DOM.loginRole.value;
    localStorage.setItem("selectra_user", JSON.stringify(state.user));
    localStorage.setItem("selectra_role", state.role);
    startApp();
}

function shakeElement(el) {
    el.style.animation = "none";
    el.offsetHeight; // trigger reflow
    el.style.animation = "shake 0.4s ease";
    setTimeout(() => { el.style.animation = ""; }, 400);
}

// ═══════════════════════════════════════════════
// APP START
// ═══════════════════════════════════════════════

async function startApp() {
    DOM.loginScreen.style.display = "none";
    DOM.appContainer.classList.add("active");
    DOM.headerUser.textContent = state.user.name;

    // Fetch questions from backend
    try {
        const res = await fetch(`/api/questions?role=${state.role}&sessionId=${state.sessionId}`);
        const data = await res.json();
        state.questions = data.questions;
    } catch (err) {
        addMessage("ai", "⚠️ Failed to load questions. Please refresh the page.");
        return;
    }

    // Role label for display
    const roleLabels = {
        frontend: "Frontend Developer",
        backend: "Backend Developer",
        fullstack: "Full Stack Developer",
        data_science: "Data Science / ML",
        devops: "DevOps / Cloud",
        cybersecurity: "Cybersecurity",
        general: "General"
    };
    const roleDisplay = roleLabels[state.role] || state.role;

    // Welcome message
    addMessage("ai",
        `Welcome to <strong>Selectra</strong>, ${state.user.name}! 🎯<br><br>
        I'm your AI Interview Agent. You've selected the <strong>${roleDisplay}</strong> track.<br>
        I'll ask you <strong>${state.questions.length} questions</strong> tailored to this role 
        and provide real-time scoring with explainable feedback.<br><br>
        Let's begin when you're ready!`
    );

    setTimeout(() => askNextQuestion(), 1200);
}

// ═══════════════════════════════════════════════
// CHAT – MESSAGE HANDLING
// ═══════════════════════════════════════════════

function addMessage(sender, content, category) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = sender === "ai" ? "S" : state.user.name[0].toUpperCase();

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (category) {
        const catBadge = document.createElement("div");
        catBadge.className = "question-category";
        catBadge.textContent = category;
        bubble.appendChild(catBadge);
    }

    const textSpan = document.createElement("div");
    textSpan.innerHTML = content;
    bubble.appendChild(textSpan);

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    DOM.chatMessages.appendChild(msgDiv);

    scrollToBottom();
    return bubble;
}

function addTypingIndicator() {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message ai";
    msgDiv.id = "typingIndicator";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "S";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    const typing = document.createElement("div");
    typing.className = "typing-indicator";
    typing.innerHTML = "<span></span><span></span><span></span>";
    bubble.appendChild(typing);

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    DOM.chatMessages.appendChild(msgDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById("typingIndicator");
    if (el) el.remove();
}

function scrollToBottom() {
    setTimeout(() => {
        DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
    }, 50);
}

// ═══════════════════════════════════════════════
// INTERVIEW FLOW
// ═══════════════════════════════════════════════

function askNextQuestion() {
    if (state.currentQuestionIndex >= state.questions.length) {
        finishInterview();
        return;
    }

    const q = state.questions[state.currentQuestionIndex];
    addMessage(
        "ai",
        `<strong>Question ${q.id} of ${state.questions.length}:</strong><br>${q.text}`,
        q.category
    );

    DOM.answerInput.disabled = false;
    DOM.sendBtn.disabled = false;
    DOM.answerInput.focus();
    DOM.inputHint.textContent = `Question ${q.id} of ${state.questions.length} · Press Enter to submit`;
}

async function sendAnswer() {
    if (state.isWaiting || state.interviewComplete) return;

    const answer = DOM.answerInput.value.trim();
    if (!answer) return;

    const question = state.questions[state.currentQuestionIndex];

    // Show user message
    addMessage("user", answer);
    DOM.answerInput.value = "";
    DOM.answerInput.style.height = "auto";
    DOM.answerInput.disabled = true;
    DOM.sendBtn.disabled = true;
    state.isWaiting = true;

    // Typing indicator
    addTypingIndicator();

    try {
        // Send to backend
        const res = await fetch("/api/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                sessionId: state.sessionId,
                questionId: question.id,
                answer: answer
            })
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || "Evaluation failed");
        }

        removeTypingIndicator();

        // Store response
        state.answers.push({
            question,
            answer,
            scores: data.scores,
            explanations: data.explanations,
            suggestions: data.suggestions,
            signals: data.signals,
            runningAverages: data.runningAverages,
            readiness: data.readiness
        });

        state.latestScores = data.scores;
        state.latestSuggestions = data.suggestions;
        state.latestExplanations = data.explanations;
        state.readiness = data.readiness;

        // Show feedback message
        showFeedbackMessage(data);

        // Update sidebar
        updateSidebar(data);

        // Move to next question
        state.currentQuestionIndex++;
        state.isWaiting = false;

        setTimeout(() => askNextQuestion(), 1500);

    } catch (err) {
        removeTypingIndicator();
        addMessage("ai", `⚠️ Error: ${err.message}. Please try again.`);
        DOM.answerInput.disabled = false;
        DOM.sendBtn.disabled = false;
        state.isWaiting = false;
    }
}

function showFeedbackMessage(data) {
    const avg = (data.scores.clarity + data.scores.accuracy +
        data.scores.completeness + data.scores.confidence) / 4;

    let feedbackClass, feedbackText;
    if (avg >= 7) {
        feedbackClass = "feedback-great";
        feedbackText = "Excellent response! 🌟";
    } else if (avg >= 4.5) {
        feedbackClass = "feedback-good";
        feedbackText = "Good answer 👍";
    } else {
        feedbackClass = "feedback-improve";
        feedbackText = "Room for improvement 📝";
    }

    const bubble = addMessage("ai",
        `${feedbackText}<br><br>` +
        `<strong>Scores:</strong> ` +
        `Clarity ${data.scores.clarity}/10 · ` +
        `Accuracy ${data.scores.accuracy}/10 · ` +
        `Completeness ${data.scores.completeness}/10 · ` +
        `Confidence ${data.scores.confidence}/10`
    );

    const badge = document.createElement("span");
    badge.className = `answer-feedback ${feedbackClass}`;
    badge.textContent = `Average: ${avg.toFixed(1)}/10`;
    bubble.appendChild(badge);
}

// ═══════════════════════════════════════════════
// SIDEBAR UPDATES
// ═══════════════════════════════════════════════

function updateSidebar(data) {
    updateProgress();
    updateScoreBars(data.runningAverages);
    updateOverallScore(data.runningAverages.overall);
    updateReadinessBadge(data.readiness);
    updateSuggestions(data.suggestions);
    updateXAIPanel(data.explanations, data.signals);
}

function updateProgress() {
    const answered = state.currentQuestionIndex + 1;
    const total = state.questions.length;
    const pct = Math.round((answered / total) * 100);

    DOM.progressText.textContent = `${answered} of ${total} Answered`;
    DOM.progressDetail.textContent = `${pct}% Complete`;
    DOM.progressRingText.textContent = `${answered}/${total}`;

    // Update SVG ring
    const radius = 22;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (pct / 100) * circumference;
    DOM.progressRingFill.style.strokeDasharray = circumference;
    DOM.progressRingFill.style.strokeDashoffset = offset;
}

function updateScoreBars(averages) {
    const dims = [
        { key: "clarity", label: "Clarity" },
        { key: "accuracy", label: "Technical Accuracy" },
        { key: "completeness", label: "Completeness" },
        { key: "confidence", label: "Confidence" }
    ];

    DOM.scoresContainer.innerHTML = "";

    dims.forEach(({ key, label }) => {
        const score = averages[key];
        const level = score >= 7 ? "high" : score >= 4 ? "medium" : "low";

        const item = document.createElement("div");
        item.className = `score-item score-${level} score-flash`;

        item.innerHTML = `
            <div class="score-label-row">
                <span class="score-dim-name">${label}</span>
                <span class="score-value">${score}/10</span>
            </div>
            <div class="score-bar">
                <div class="score-bar-fill" style="width: ${score * 10}%"></div>
            </div>
        `;

        DOM.scoresContainer.appendChild(item);
    });
}

function updateOverallScore(overall) {
    DOM.overallScoreCard.style.display = "block";
    DOM.overallScoreValue.textContent = overall;
    DOM.overallScoreCard.classList.add("score-flash");
    setTimeout(() => DOM.overallScoreCard.classList.remove("score-flash"), 800);
}

function updateReadinessBadge(readiness) {
    if (!readiness) return;
    DOM.readinessBadge.style.display = "flex";
    DOM.readinessBadge.className = `readiness-badge ${readiness.className}`;
    DOM.readinessBadge.innerHTML = `
        <div class="readiness-dot"></div>
        <div class="readiness-info">
            <div class="readiness-label">${readiness.label}</div>
            <div class="readiness-desc">${readiness.description}</div>
        </div>
    `;
}

function updateSuggestions(suggestions) {
    DOM.suggestionsContainer.innerHTML = "";

    Object.entries(suggestions).forEach(([dim, s]) => {
        const card = document.createElement("div");
        card.className = `suggestion-card suggestion-level-${s.level}`;
        card.innerHTML = `
            <div class="suggestion-header">
                <span class="suggestion-icon">${s.icon}</span>
                <span class="suggestion-dim">${s.dimension}</span>
            </div>
            <div class="suggestion-text">${s.text}</div>
        `;
        DOM.suggestionsContainer.appendChild(card);
    });
}

function updateXAIPanel(explanations, signals) {
    DOM.xaiPanel.innerHTML = `
        <h4>🔍 Explainable AI Analysis</h4>
    `;

    explanations.forEach((exp) => {
        const item = document.createElement("div");
        item.className = "xai-item";

        let signalsHtml = "";
        if (exp.signalsDetected && exp.signalsDetected.length > 0) {
            signalsHtml = `<div class="xai-signals">
                ${exp.signalsDetected.map(s => `<span class="xai-signal-tag">${s}</span>`).join("")}
            </div>`;
        }

        item.innerHTML = `
            <div class="xai-dim">${exp.dimension} — ${exp.score}/10</div>
            <div class="xai-explanation">${exp.text}</div>
            ${signalsHtml}
        `;
        DOM.xaiPanel.appendChild(item);
    });

    // Add key signal summary
    if (signals) {
        const summary = document.createElement("div");
        summary.className = "xai-item";
        summary.style.marginTop = "8px";
        summary.style.paddingTop = "8px";
        summary.style.borderTop = "1px solid var(--border-light)";
        summary.innerHTML = `
            <div class="xai-dim">Signal Summary</div>
            <div class="xai-signals">
                <span class="xai-signal-tag">📝 ${signals.wordCount} words</span>
                <span class="xai-signal-tag">📄 ${signals.sentenceCount} sentences</span>
                <span class="xai-signal-tag">🔑 ${signals.matchedKeywords.length} keywords</span>
                ${signals.hasExamples ? '<span class="xai-signal-tag">✅ Has examples</span>' : ''}
                ${signals.fillerWordsFound.length > 0 ? `<span class="xai-signal-tag">⚠️ ${signals.fillerWordsFound.length} filler words</span>` : ""}
                ${signals.isGibberish ? '<span class="xai-signal-tag" style="background:rgba(239,68,68,0.1);color:var(--score-low);">🚫 Gibberish detected</span>' : ""}
            </div>
        `;
        DOM.xaiPanel.appendChild(summary);
    }
}

// ═══════════════════════════════════════════════
// INTERVIEW COMPLETION & REPORT
// ═══════════════════════════════════════════════

async function finishInterview() {
    state.interviewComplete = true;
    DOM.answerInput.disabled = true;
    DOM.sendBtn.disabled = true;
    DOM.inputHint.textContent = "Interview complete!";

    addMessage("ai",
        `🎉 <strong>Interview Complete!</strong><br><br>
        Thank you, ${state.user.name}! All ${state.questions.length} questions have been answered.<br>
        Your final report is being generated...<br><br>
        <em>Click the button below to view your full scorecard report.</em>`
    );

    // Add report button in chat
    const btnWrapper = document.createElement("div");
    btnWrapper.style.cssText = "text-align: left; margin-top: 8px;";

    const btn = document.createElement("button");
    btn.className = "btn-primary";
    btn.style.cssText = "width: auto; padding: 10px 24px; font-size: 0.88rem;";
    btn.textContent = "📊 View Full Report";
    btn.addEventListener("click", generateReport);

    btnWrapper.appendChild(btn);

    const lastMsg = DOM.chatMessages.lastElementChild;
    if (lastMsg) {
        lastMsg.querySelector(".message-bubble").appendChild(btnWrapper);
    }
}

async function generateReport() {
    try {
        const res = await fetch("/api/final-report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                sessionId: state.sessionId,
                interviewer: state.user
            })
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || "Report generation failed");
        }

        state.reportData = data;
        renderReport(data);

    } catch (err) {
        alert("Failed to generate report: " + err.message);
    }
}

function renderReport(data) {
    DOM.reportSection.classList.add("active");

    const readiness = data.readinessIndicator;
    const insights = data.interviewInsights;

    let html = `
        <div class="report-container">
            <!-- Header -->
            <div class="report-header">
                <h1>Selectra</h1>
                <p class="report-tagline">${data.tagline}</p>
                <div class="report-meta">
                    <span class="report-meta-item"><strong>Candidate:</strong> ${data.interviewer.name}</span>
                    <span class="report-meta-item"><strong>Email:</strong> ${data.interviewer.email}</span>
                    <span class="report-meta-item"><strong>Date:</strong> ${new Date(data.generatedAt).toLocaleDateString()}</span>
                </div>
            </div>

            <!-- Overall Score -->
            <div class="report-card">
                <h3>📊 Overall Performance</h3>
                <div class="report-dim-grid">
                    <div class="report-dim-card">
                        <div class="report-dim-score" style="color: ${getScoreColor(data.dimensionAverages.clarity)}">${data.dimensionAverages.clarity}</div>
                        <div class="report-dim-name">Clarity</div>
                    </div>
                    <div class="report-dim-card">
                        <div class="report-dim-score" style="color: ${getScoreColor(data.dimensionAverages.accuracy)}">${data.dimensionAverages.accuracy}</div>
                        <div class="report-dim-name">Technical Accuracy</div>
                    </div>
                    <div class="report-dim-card">
                        <div class="report-dim-score" style="color: ${getScoreColor(data.dimensionAverages.completeness)}">${data.dimensionAverages.completeness}</div>
                        <div class="report-dim-name">Completeness</div>
                    </div>
                    <div class="report-dim-card">
                        <div class="report-dim-score" style="color: ${getScoreColor(data.dimensionAverages.confidence)}">${data.dimensionAverages.confidence}</div>
                        <div class="report-dim-name">Confidence</div>
                    </div>
                </div>

                <div style="text-align: center; margin-top: 12px;">
                    <div class="readiness-badge ${readiness.className}" style="display: inline-flex;">
                        <div class="readiness-dot"></div>
                        <div class="readiness-info">
                            <div class="readiness-label">${readiness.label} — Overall: ${data.overallScore}/10</div>
                            <div class="readiness-desc">${readiness.description}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Insights -->
            <div class="report-card">
                <h3>💡 Interview Insights</h3>
                <div class="report-insights-grid">
                    <div class="insight-block strengths">
                        <h4>🌟 Strengths</h4>
                        ${insights.strengths.map(s => `
                            <div class="insight-item">
                                <span class="insight-icon">✅</span>
                                <div><strong>${s.name}</strong> (${s.score}/10): ${s.note}</div>
                            </div>
                        `).join("")}
                        ${insights.strengths.length === 0 ? '<div class="insight-item"><span class="insight-icon">—</span><div>Keep practicing to build strengths!</div></div>' : ""}
                    </div>
                    <div class="insight-block improvements">
                        <h4>📈 Areas for Improvement</h4>
                        ${insights.improvementAreas.map(s => `
                            <div class="insight-item">
                                <span class="insight-icon">🔧</span>
                                <div><strong>${s.name}</strong> (${s.score}/10): ${s.note}</div>
                            </div>
                        `).join("")}
                    </div>
                </div>
            </div>

            <!-- Next Steps -->
            <div class="report-card">
                <h3>🚀 Actionable Next Steps</h3>
                <ol class="next-steps-list">
                    ${insights.actionableNextSteps.map((step, i) => `
                        <li>
                            <span class="step-number">${i + 1}</span>
                            <span>${step}</span>
                        </li>
                    `).join("")}
                </ol>
            </div>

            <!-- Detailed Responses -->
            <div class="report-card">
                <h3>📝 Detailed Responses</h3>
                ${data.responses.map((r, i) => `
                    <div class="report-qa-item">
                        <div class="report-qa-header">
                            <span class="report-qa-q">Q${i + 1}: ${r.question}</span>
                            <span class="report-qa-cat">${r.category}</span>
                        </div>
                        <div class="report-qa-answer">${r.answer}</div>
                        <div class="report-qa-scores">
                            <span class="report-qa-score-chip" style="color: ${getScoreColor(r.scores.clarity)}">Clarity: ${r.scores.clarity}</span>
                            <span class="report-qa-score-chip" style="color: ${getScoreColor(r.scores.accuracy)}">Accuracy: ${r.scores.accuracy}</span>
                            <span class="report-qa-score-chip" style="color: ${getScoreColor(r.scores.completeness)}">Completeness: ${r.scores.completeness}</span>
                            <span class="report-qa-score-chip" style="color: ${getScoreColor(r.scores.confidence)}">Confidence: ${r.scores.confidence}</span>
                        </div>
                        <!-- Suggestions for this response -->
                        ${Object.entries(r.suggestions).map(([dim, s]) => `
                            <div class="suggestion-card suggestion-level-${s.level}" style="margin-top: 8px;">
                                <div class="suggestion-header">
                                    <span class="suggestion-icon">${s.icon}</span>
                                    <span class="suggestion-dim">${s.dimension}</span>
                                </div>
                                <div class="suggestion-text">${s.text}</div>
                            </div>
                        `).join("")}
                    </div>
                `).join("")}
            </div>

            <!-- Actions -->
            <div class="report-actions">
                <button class="btn-report btn-report-primary" onclick="exportJSON()">📥 Export JSON</button>
                <button class="btn-report btn-report-primary" onclick="printReport()">🖨️ Print Report</button>
                <button class="btn-report btn-report-secondary" onclick="closeReport()">← Back to Chat</button>
                <button class="btn-report btn-report-secondary" onclick="newInterview()">🔄 New Interview</button>
            </div>
        </div>
    `;

    DOM.reportContent.innerHTML = html;
}

function getScoreColor(score) {
    if (score >= 7) return "var(--score-high)";
    if (score >= 4) return "var(--score-medium)";
    return "var(--score-low)";
}

// ═══════════════════════════════════════════════
// EXPORT & ACTIONS
// ═══════════════════════════════════════════════

function exportJSON() {
    if (!state.reportData) return;

    const blob = new Blob(
        [JSON.stringify(state.reportData, null, 2)],
        { type: "application/json" }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Selectra_Report_${state.user.name.replace(/\s/g, "_")}_${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function printReport() {
    window.print();
}

function closeReport() {
    DOM.reportSection.classList.remove("active");
}

async function newInterview() {
    // Reset session on backend
    try {
        await fetch("/api/reset", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sessionId: state.sessionId })
        });
    } catch (e) { /* ignore */ }

    // Reset frontend state
    state.sessionId = "session_" + Date.now();
    state.currentQuestionIndex = 0;
    state.answers = [];
    state.isWaiting = false;
    state.interviewComplete = false;
    state.reportData = null;
    state.latestScores = null;
    state.latestSuggestions = null;
    state.latestExplanations = null;
    state.readiness = null;
    state.role = localStorage.getItem("selectra_role") || "general";

    // Reset UI
    DOM.chatMessages.innerHTML = "";
    DOM.scoresContainer.innerHTML = "";
    DOM.suggestionsContainer.innerHTML = "";
    DOM.xaiPanel.innerHTML = '<h4>🔍 Explainable AI Analysis</h4><p style="font-size:0.78rem;color:var(--text-muted);">Submit your first answer to see analysis.</p>';
    DOM.overallScoreCard.style.display = "none";
    DOM.readinessBadge.style.display = "none";
    DOM.reportSection.classList.remove("active");
    DOM.answerInput.disabled = false;
    DOM.sendBtn.disabled = false;

    // Reset progress
    DOM.progressText.textContent = "0 of 0 Answered";
    DOM.progressDetail.textContent = "0% Complete";
    DOM.progressRingText.textContent = "0/0";
    DOM.progressRingFill.style.strokeDashoffset = 2 * Math.PI * 22;

    // Restart
    startApp();
}

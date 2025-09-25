let questions = [];
let sessionId = null;
let currentQuestionIndex = 0;
let totalQuestions = 0;
let isRetry = false;
let quizFinished = false;
let pendingCompletion = null;

const questionNumberElement = document.getElementById("question-number");
const questionElement = document.getElementById("question");
const optionsContainer = document.getElementById("options-container");
const feedbackElement = document.getElementById("feedback-message");
const nextButton = document.getElementById("next-btn");
const progressBar = document.getElementById("progress-bar");

// CSRF helper (optional for proxy)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize quiz on page load
document.addEventListener("DOMContentLoaded", () => {
    if (QUIZ_DATA && QUIZ_DATA.questions) {
        sessionId = QUIZ_DATA.session_id;
        questions = QUIZ_DATA.questions;
        totalQuestions = QUIZ_DATA.total_questions;
        currentQuestionIndex = QUIZ_DATA.current_question_index || 0;
        isRetry = QUIZ_DATA.is_retry || false;
        showQuestion();
    }
});

function updateProgressBar() {
    const progress = (currentQuestionIndex / totalQuestions) * 100;
    progressBar.style.width = `${progress}%`;
}

// --- Helper: Auto-format code by language with indentation ---
function autoFormatCode(code, lang) {
    let formatted = code.trim();
    let lines = [];

    if (lang.includes("java") || lang.includes("javascript") || lang.includes("js") || lang.includes("c") || lang.includes("cpp")) {
        formatted = formatted
            .replace(/;/g, ";\n")
            .replace(/{/g, "{\n")
            .replace(/}/g, "\n}")
            .replace(/\)\s*{/g, ")\n{")
            .replace(/\n\s*\n/g, "\n");

        lines = formatted.split("\n");

        let indent = 0;
        lines = lines.map(line => {
            line = line.trim();
            if (line.endsWith("}")) indent -= 1;
            let indented = "    ".repeat(Math.max(indent, 0)) + line;
            if (line.endsWith("{")) indent += 1;
            return indented;
        });
    } 
    else if (lang.includes("python")) {
        formatted = formatted
            .replace(/:/g, ":\n")
            .replace(/def /g, "\ndef ")
            .replace(/class /g, "\nclass ")
            .replace(/\n\s*\n/g, "\n");

        lines = formatted.split("\n");

        let indent = 0;
        lines = lines.map(line => {
            line = line.trim();
            let indented = "    ".repeat(indent) + line;
            if (line.endsWith(":")) indent += 1;
            return indented;
        });
    } 
    else {
        formatted = formatted.replace(/;/g, ";\n").replace(/{/g, "{\n").replace(/}/g, "\n}");
        lines = formatted.split("\n");
    }

    return lines.join("\n");
}

// --- Escape HTML ---
function escapeHTML(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function showQuestion() {
    if (currentQuestionIndex < totalQuestions) {
        const currentQuestion = questions[currentQuestionIndex];
        questionNumberElement.textContent = `Question ${currentQuestionIndex + 1} of ${totalQuestions}`;

        let rawText = currentQuestion.text;

        // --- Handle [mycode] markers ---
        rawText = rawText.replace(
            /\[mycode(.*?)\]([\s\S]*?)\[\/mycode\]/g,
            (match, attrs, codeContent) => {
                const langMatch = attrs.match(/class="([^"]+)"/);
                const langClass = langMatch ? langMatch[1] : "language-java";

                let formattedCode = autoFormatCode(codeContent, langClass);

                // Add scroll or wrap style depending on lang
                const style = (langClass.includes("java") || langClass.includes("js") || langClass.includes("cpp"))
                    ? "style='white-space: pre; overflow-x: auto;'"
                    : "style='white-space: pre-wrap; word-wrap: break-word;'";

                return `<pre ${style}><code class="${langClass}">${escapeHTML(formattedCode)}</code></pre>`;
            }
        );

        questionElement.innerHTML = rawText;

        if (window.Prism) Prism.highlightAll();

        optionsContainer.innerHTML = "";
        feedbackElement.classList.add("d-none");
        nextButton.style.display = "none";

        currentQuestion.options.forEach(option => {
            const optionElement = document.createElement("a");
            optionElement.href = "#";
            optionElement.textContent = option;
            optionElement.classList.add("list-group-item", "list-group-item-action", "option");
            optionElement.addEventListener("click", (e) => {
                e.preventDefault();
                checkAnswer(option);
            });
            optionsContainer.appendChild(optionElement);
        });

        updateProgressBar();
    } else {
        questionNumberElement.textContent = "Quiz Completed!";
        questionElement.textContent = "You have finished the quiz.";
        optionsContainer.innerHTML = "";
        feedbackElement.classList.add("d-none");
        nextButton.style.display = "none";
        progressBar.style.width = "100%";
    }
}



function checkAnswer(selectedOption) {
    const currentQuestion = questions[currentQuestionIndex];
    const endpoint = isRetry 
        ? "/api/quiz/submit_retry_answer/" 
        : "/api/quiz/submit_quiz_answer/";

    fetch(`/proxy/?endpoint=${encodeURIComponent(endpoint)}&endpoint_type=private`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            session_id: sessionId,
            question_index: currentQuestionIndex,
            answer: selectedOption
        })
    })
    .then(res => res.json())
    .then(result => {
        const correctAnswer = result.correct_answer;

        // Disable options
        Array.from(optionsContainer.children).forEach(option => {
            option.classList.remove("list-group-item-action");
            option.style.pointerEvents = "none";
            if (option.textContent === correctAnswer) {
                option.classList.add("correct");
            } else if (option.textContent === selectedOption) {
                option.classList.add("incorrect");
            }
        });

        // Show feedback for the answer
        feedbackElement.classList.remove("d-none", "feedback-correct", "feedback-incorrect");
        if (result.correct) {
            feedbackElement.textContent = "Correct! 🎉";
            feedbackElement.classList.add("feedback-correct");
        } else {
            feedbackElement.textContent = `Incorrect. Correct Answer is: "${result.correct_answer}"`;
            feedbackElement.classList.add("feedback-incorrect");
        }

        nextButton.style.display = "block";

        // If this was the final response, store completion result
        if (result.type === "complete") {
            pendingCompletion = result;
            quizFinished = true;
        } else if (currentQuestionIndex === totalQuestions - 1) {
            quizFinished = true;
        }
    })
    .catch(err => {
        console.error("Error submitting answer:", err);
        feedbackElement.classList.remove("d-none");
        feedbackElement.textContent = "Error submitting answer. Please try again.";
        nextButton.style.display = "block";
    });
}

// Next button click
nextButton.addEventListener("click", () => {
    if (quizFinished) {
        // If backend sent a final message, use it
        const completionMessage = pendingCompletion ? pendingCompletion.message : "You have finished the quiz.";
        pendingCompletion = null; // reset

        questionNumberElement.textContent = "Quiz Completed!";
        questionElement.textContent = "";

        optionsContainer.innerHTML = "";

        // Show backend message
        feedbackElement.classList.remove("d-none");
        feedbackElement.innerHTML = completionMessage;

        // Show final buttons
        const buttonsHtml = `
            <div class="mt-3 d-flex gap-2 flex-wrap">
                <a href="${URLS.startQuiz}" class="btn btn-primary">
                    <i class="bi bi-play-circle"></i> Start New Quiz
                </a>
                <a href="${URLS.retryQuizzes}" class="btn btn-warning">
                    <i class="bi bi-arrow-clockwise"></i> Retry Missed Questions
                </a>
                <a href="${URLS.manageQuiz}" class="btn btn-secondary">
                    <i class="bi bi-gear"></i> Manage My Quiz
                </a>
            </div>
        `;
        feedbackElement.insertAdjacentHTML('beforeend', buttonsHtml);

        nextButton.style.display = "none";
        progressBar.style.width = "100%";
        quizFinished = false; // reset flag
        return;
    }

    currentQuestionIndex++;
    showQuestion();
});

const categoryFilter = document.getElementById("categoryFilter");
if (categoryFilter) {
    categoryFilter.addEventListener("change", function() {
        const selectedCategory = this.value;
        const params = new URLSearchParams(window.location.search);

        if (selectedCategory) {
            params.set("category_id", selectedCategory);
            params.delete("page"); // reset to page 1
        } else {
            params.delete("category_id");
        }

        window.location.search = params.toString();
    });
}

const quizSearchBtn = document.getElementById("quizSearchBtn");
const quizSearchInput = document.getElementById("quizSearchInput");

if (quizSearchBtn && quizSearchInput) {
    quizSearchBtn.addEventListener("click", function() {
        const searchValue = quizSearchInput.value.trim();
        const params = new URLSearchParams(window.location.search);

        if (searchValue) {
            params.set("search", searchValue);
            params.delete("page"); // reset to page 1
        } else {
            params.delete("search");
        }

        window.location.search = params.toString();
    });

    quizSearchInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            quizSearchBtn.click();
        }
    });
}

questionElement.innerHTML = currentQuestion.text;

// Convert <mycode> into <pre><code>
questionElement.querySelectorAll("mycode").forEach(el => {
    const codeBlock = document.createElement("pre");
    const code = document.createElement("code");
    const lang = el.getAttribute("class") || "language-java";
    code.className = lang;
    code.textContent = el.innerText.trim();
    codeBlock.appendChild(code);
    el.replaceWith(codeBlock);
});

// Re-highlight syntax
if (window.Prism) Prism.highlightAll();

let questions = [];
let sessionId = null;
let currentQuestionIndex = 0;
let totalQuestions = 0;

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
        showQuestion();
    }
});

function updateProgressBar() {
    const progress = (currentQuestionIndex / totalQuestions) * 100;
    progressBar.style.width = `${progress}%`;
}

function showQuestion() {
    if (currentQuestionIndex < totalQuestions) {
        const currentQuestion = questions[currentQuestionIndex];
        questionNumberElement.textContent = `Question ${currentQuestionIndex + 1} of ${totalQuestions}`;
        questionElement.textContent = currentQuestion.text;
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
        // Quiz complete
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

    // Send answer through proxy
    fetch(`/proxy/?endpoint=/api/quiz/submit_quiz_answer/&endpoint_type=private`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            session_id: sessionId,
            question_number: currentQuestion.number,
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

        // Show feedback
        feedbackElement.classList.remove("d-none", "feedback-correct", "feedback-incorrect");
        if (result.correct) {
            feedbackElement.textContent = "Correct! 🎉";
            feedbackElement.classList.add("feedback-correct");
        } else {
            feedbackElement.textContent = `Incorrect. Correct Answer is: "${result.correct_answer}"`;
            feedbackElement.classList.add("feedback-incorrect");
        }

        nextButton.style.display = "block";
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
    currentQuestionIndex++;
    showQuestion();
});

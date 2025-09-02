const questions = [
    {
        question: "What is the capital of France?",
        options: ["Berlin", "Madrid", "Paris", "Rome"],
        correctAnswer: "Paris"
    },
    {
        question: "Which planet is known as the 'Red Planet'?",
        options: ["Jupiter", "Mars", "Venus", "Saturn"],
        correctAnswer: "Mars"
    }
];

let currentQuestionIndex = 0;
const totalQuestions = questions.length;

const questionNumberElement = document.getElementById("question-number");
const questionElement = document.getElementById("question");
const optionsContainer = document.getElementById("options-container");
const feedbackElement = document.getElementById("feedback-message");
const nextButton = document.getElementById("next-btn");
const progressBar = document.getElementById("progress-bar");

function updateProgressBar() {
    const progress = (currentQuestionIndex / totalQuestions) * 100;
    progressBar.style.width = `${progress}%`;
}

function showQuestion() {
    if (currentQuestionIndex < totalQuestions) {
        const currentQuestion = questions[currentQuestionIndex];
        questionNumberElement.textContent = `Question ${currentQuestionIndex + 1} of ${totalQuestions}`;
        questionElement.textContent = currentQuestion.question;
        optionsContainer.innerHTML = ''; // Clear previous options
        feedbackElement.classList.add('d-none');
        nextButton.style.display = 'none';

        currentQuestion.options.forEach(option => {
            const optionElement = document.createElement("a");
            optionElement.href = "#";
            optionElement.textContent = option;
            optionElement.classList.add("list-group-item", "list-group-item-action", "option");
            optionElement.addEventListener("click", (e) => {
                e.preventDefault(); // Prevent default link behavior
                checkAnswer(option);
            });
            optionsContainer.appendChild(optionElement);
        });

        updateProgressBar();
    } else {
        // End of quiz
        questionNumberElement.textContent = `Quiz Completed!`;
        questionElement.textContent = "You have finished the quiz.";
        optionsContainer.innerHTML = '';
        feedbackElement.classList.add('d-none');
        nextButton.style.display = 'none';
        updateProgressBar();
    }
}

function checkAnswer(selectedOption) {
    const currentQuestion = questions[currentQuestionIndex];
    const isCorrect = (selectedOption === currentQuestion.correctAnswer);
    
    // Disable all options after selection
    Array.from(optionsContainer.children).forEach(option => {
        option.classList.remove('list-group-item-action');
        option.style.pointerEvents = 'none';
        if (option.textContent === currentQuestion.correctAnswer) {
            option.classList.add('correct');
        } else if (option.textContent === selectedOption) {
            option.classList.add('incorrect');
        }
    });

    // Display feedback
    feedbackElement.classList.remove('d-none', 'feedback-correct', 'feedback-incorrect');
    if (isCorrect) {
        feedbackElement.textContent = "Correct! 🎉 Congratulations!";
        feedbackElement.classList.add('feedback-correct');
    } else {
        feedbackElement.textContent = `Incorrect. The correct answer was "${currentQuestion.correctAnswer}".`;
        feedbackElement.classList.add('feedback-incorrect');
    }

    // Show next button
    nextButton.style.display = 'block';
}

nextButton.addEventListener("click", () => {
    currentQuestionIndex++;
    showQuestion();
});

// Initial load
showQuestion();
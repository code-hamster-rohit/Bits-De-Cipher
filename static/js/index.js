function getHandle(selector) {
    return document.querySelector(selector);
}

function getHandles(selector) {
    return document.querySelectorAll(selector);
}

function changeView(hiddenClasses, showClass) {
    hiddenClasses.forEach(cls => getHandle(cls).classList.add('hidden'));
    if (showClass) getHandle(showClass).classList.remove('hidden');
}

const navButtons = getHandles('.nav-wrapper .btn');
navButtons.forEach(btn => {
    btn.addEventListener('click', function() {
        changeView(['.questions', '.rules', '.sign-in', '.leaderboard'], `.${btn.id}`);
    });
});

function sendRequest(rollNumber) {
    fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'roll_number': rollNumber })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === 200) {
            changeView(['.sign-in'], '.questions');
            getHandle('#sign-in').classList.add('hidden');
            getHandle('#questions').disabled = false;
            getHandle('#leaderboard').disabled = false;
            checkProgress();
        }
    });
}

function registerContestant() {
    const rollNumber = getHandle('#rollNumber').value;
    if (rollNumber.length === 8) {
        sendRequest(rollNumber);
    } else {
        alert("Invalid Roll Number");
    }
}

getHandle('.submitBtn').addEventListener('click', registerContestant);

function checkProgress() {
    fetch('/load_progress', { method: 'GET' })
    .then(response => response.json())
    .then(data => {
        if (data.status === 200) {
            getHandle('#sign-in').classList.add('hidden');
            updateQuestion(data.data);
        } else if (data.status === 300) {
            changeView(['.questions'], '.sign-in');
            getHandle('#sign-in').classList.remove('hidden');
            disableButtons();
        }
    });
}

function updateQuestion(questionData) {
    getHandle('.ques-img').src = `https://code-hamster-rohit.github.io/Temp_De_Cipher/assets/${questionData.qno}.png`;
    getHandle('.question-text').textContent = questionData.qn;
    checkHints();
}

function disableButtons() {
    getHandle('#questions').disabled = true;
    getHandle('#leaderboard').disabled = true;
}

function checkHints() {
    fetch('/get_hint', { method: 'GET' })
    .then(response => response.json())
    .then(data => {
        if (data.status === 200) {
            alert(`Hint: ${data.message}`);
        }
    });
}

window.onload = checkProgress;

getHandle('#submit-answer').addEventListener('click', function() {
    const answer = getHandle('#answer').value.trim();
    if (answer) {
        fetch('/submit_answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'ans': answer, 'qno': getHandle('.ques-img').src.split('/').pop().split('.')[0] })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.status === 200) {
                checkProgress();
                getHandle('#answer').value = '';
            }
        });
    } else {
        alert("Please enter an answer");
    }
});

let questionIndex = 0;
let selectedConditions = [];
sessionStorage.clear();
let jsonData;
let currentConditionF, currentConditionJ;
let shuffledTargets = []; // This will hold the randomized order of your 50 targets

const attentionChecks = {
    9: {
        target: "Price",
        features: [
            { label: "Price", F: "25", J: "40" },
            { label: "Value", F: "30", J: "22" }
        ],
        correct: "J"
    },
    19: {
        target: "Weight",
        features: [
            { label: "Weight", F: "15kg", J: "7kg" },
            { label: "Durability", F: "30", J: "18" }
        ],
        correct: "F"
    },
    29: {
        target: "Speed",
        features: [
            { label: "Speed", F: "100km/h", J: "120km/h" },
            { label: "Efficiency", F: "63", J: "50" }
        ],
        correct: "J"
    },
    39: {
        target: "Cost",
        features: [
            { label: "Cost", F: "$100", J: "$80" },
            { label: "Rating", F: "3", J: "4" }
        ],
        correct: "F"
    }
};

// Show only the requested page
function showPage(pageId) {
    document.querySelectorAll(".container").forEach(page => page.style.display = "none");
    document.getElementById(pageId).style.display = "block";
}

// Load JSON based on sequential assignment
async function loadJSON() {
    try {
        let submissionCount = await getCurrentParticipantCount();
        let group = "ranking_A"; // Default
        if (submissionCount >= 31 && submissionCount < 61) {
            group = "ranking_B";
        } else if (submissionCount >= 61) {
            group = submissionCount % 2 === 0 ? "ranking_A" : "ranking_B";
        }
        
        sessionStorage.setItem("conditionGroup", group);
        sessionStorage.setItem("submissionNumber", submissionCount + 1);

        const response = await fetch(`${group}.json`);
        jsonData = await response.json();
        console.log(`Assigned to group: ${group}, submission number: ${submissionCount + 1}`);
        
    } catch (error) {
        console.error("Error loading JSON:", error);
    }
}

// Function to get current submission count
async function getCurrentParticipantCount() {
    try {
        if (typeof jatos !== 'undefined' && jatos.studySessionData) {
            return await jatos.getSubmissionCount() || 0;
        }
        const storedCount = localStorage.getItem('submissionCount') || '0';
        const currentCount = parseInt(storedCount);
        localStorage.setItem('submissionCount', (currentCount + 1).toString());
        return currentCount;
    } catch (error) {
        console.error("Error getting submission count:", error);
        return 0; // Fallback
    }
}

// Move from Welcome → Task Introduction
document.getElementById("buttonConsent").addEventListener("click", function () {
    showPage("pageTaskIntro");
});

// --- MODIFIED ---
// Move from Task Introduction → First Question
document.getElementById("buttonTaskIntroNext").addEventListener("click", function () {
    // 1. Get a list of all unique target names from the loaded JSON
    const uniqueTargets = [...new Set(jsonData.features.map(item => item.target))];

    // 2. Shuffle this list to create the random order for the experiment
    shuffledTargets = uniqueTargets.sort(() => 0.5 - Math.random());
    
    // 3. Show the page and ask the first question
    document.getElementById("progressWrapper").style.display = "block";
    showPage("page3");
    askNextQuestion();
});


// --- REPLACED WITH CORRECT LOGIC ---
// Ask the next question
function askNextQuestion() {
    console.log(`askNextQuestion called with questionIndex: ${questionIndex}`);

    // --- 1) STOP CONDITION ---
    if (questionIndex >= shuffledTargets.length || questionIndex >= 50) {
        showPage("pageEnd");
        return;
    }

    // --- 2) ATTENTION CHECK ---
    if (attentionChecks.hasOwnProperty(questionIndex) && !sessionStorage.getItem(`attentionShown_${questionIndex}`)) {
        const currentCheck = attentionChecks[questionIndex];
        document.getElementById("attentionQuestion").innerHTML = `Which of the following two items has the higher <strong>${currentCheck.target}</strong>?`;
        
        const tbody = document.getElementById("attentionTableBody");
        tbody.innerHTML = "";
        currentCheck.features.forEach(f => {
            const row = document.createElement("tr");
            row.innerHTML = `<td>${f.label}</td><td>${f.F}</td><td>${f.J}</td>`;
            tbody.appendChild(row);
        });

        sessionStorage.setItem(`attentionShown_${questionIndex}`, "true");
        sessionStorage.setItem("currentAttentionIndex", questionIndex);
        showPage("pageAttentionCheck");
        return;
    }
    
    // --- 3) CORRECT PAIRING LOGIC ---
    const currentTargetName = shuffledTargets[questionIndex];
    document.getElementById("targetName").textContent = currentTargetName;

    const itemsForThisTarget = jsonData.features.filter(item => item.target === currentTargetName);
    const shuffledVariations = itemsForThisTarget.sort(() => 0.5 - Math.random());
    
    currentConditionF = shuffledVariations[0];
    currentConditionJ = shuffledVariations[1];

    // --- 4) DISPLAY THE TABLE ---
    const progressPercent = ((questionIndex + 1) / 50) * 100;
    document.getElementById("progressBar").style.width = `${progressPercent}%`;

    let table = document.getElementById("dynamicTable");
    while (table.rows.length > 1) { table.deleteRow(1); }
    
    let valuesBObj = {};
    currentConditionJ.options.forEach((feat, idx) => {
        valuesBObj[feat] = currentConditionJ.values.split(", ")[idx];
    });

    for (let i = 0; i < currentConditionF.options.length; i++) {
        let row = document.createElement("tr");
        let featureName = currentConditionF.options[i];
        row.innerHTML = `<td>${featureName}</td><td>${currentConditionF.values.split(", ")[i]}</td><td>${valuesBObj[featureName] || "-"}</td>`;
        table.appendChild(row);
    }

    document.getElementById("btnF").onclick = () => selectCondition("F");
    document.getElementById("btnJ").onclick = () => selectCondition("J");
}

// When user selects an answer
function selectCondition(choice) {
    console.log(`selectCondition called with choice: ${choice}, questionIndex: ${questionIndex}`);
    
    selectedConditions.push({
        question: questionIndex + 1,
        target: currentConditionF.target,
        options: currentConditionF.options,
        optionA: {
            trial_id: currentConditionF.trial_id,
            task_id: currentConditionF.task_id,
            values: currentConditionF.values,
            target_value: currentConditionF.target_value
        },
        optionB: {
            trial_id: currentConditionJ.trial_id,
            task_id: currentConditionJ.task_id,
            values: currentConditionJ.values,
            target_value: currentConditionJ.target_value
        },
        choice: {
            button: choice,
            selected_option: choice == "F" ? "OptionA" : "OptionB",
        }
    });

    questionIndex++;
    console.log(`After increment, questionIndex is now: ${questionIndex}`);
    askNextQuestion();
}

// Save user responses
document.getElementById("buttonSaveResponses").addEventListener("click", function () {
    const finalData = {
        condition_group: sessionStorage.getItem("conditionGroup"),
        submission_number: sessionStorage.getItem("submissionNumber"),
        responses: selectedConditions
    };

    console.log("Submitting data:", finalData);

    if (typeof jatos !== 'undefined') {
        jatos.submitResultData(finalData)
            .then(() => {
                window.location.href = "https://app.prolific.com/submissions/complete?cc=C1CLHWV3";
            })
            .catch((err) => {
                console.error("Error submitting to JATOS:", err);
                alert("Something went wrong while submitting your data. Please try again.");
            });
    } else {
        console.log("JATOS not found. Final data:", finalData);
        alert("Study complete! (JATOS not connected)");
    }
});

// Handle keypresses
document.addEventListener("keydown", function (event) {
    const key = event.key.toLowerCase();
    if (document.getElementById("page3").style.display === "block") {
        if (key === "f") {
            event.preventDefault();
            selectCondition("F");
        }
        if (key === "j") {
            event.preventDefault();
            selectCondition("J");
        }
    }    
    else if (document.getElementById("pageAttentionCheck").style.display === "block") {
        if (key === "f") {
            event.preventDefault();
            document.getElementById("btnAttentionF").click();
        } else if (key == "j") {
            event.preventDefault();
            document.getElementById("btnAttentionJ").click();
        }
    }
});

// Setup Attention Check Buttons
document.addEventListener("DOMContentLoaded", function () {
    loadJSON();

    function handleAttentionClick(choice) {
        const index = sessionStorage.getItem("currentAttentionIndex");
        const check = attentionChecks[index];
        const passed = choice === check.correct;

        selectedConditions.push({
            question: `attention_check_${index}`,
            choice: choice,
            passed: passed,
            timestamp: Date.now()
        });

        sessionStorage.removeItem("currentAttentionIndex");
        showPage("page3");
        askNextQuestion();
    }

    document.getElementById("btnAttentionF").addEventListener("click", () => handleAttentionClick("F"));
    document.getElementById("btnAttentionJ").addEventListener("click", () => handleAttentionClick("J"));
});
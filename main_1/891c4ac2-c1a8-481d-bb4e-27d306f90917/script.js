let questionIndex = 0;
let selectedConditions = [];
let jsonData;
let currentConditionA, currentConditionB;

// Show only the requested page
function showPage(pageId) {
    document.querySelectorAll(".container").forEach(page => page.style.display = "none");
    document.getElementById(pageId).style.display = "block";
}

// Load JSON once and store it
async function loadJSON() {
    try {
        let response = await fetch("main.json");
        jsonData = await response.json();
    } catch (error) {
        console.error("Error loading JSON:", error);
    }
}

// Move from Welcome → Task Introduction
document.getElementById("buttonConsent").addEventListener("click", function () {
    showPage("pageTaskIntro");
});

// Move from Task Introduction → First Question
document.getElementById("buttonTaskIntroNext").addEventListener("click", function () {
    showPage("page3");
    askNextQuestion();
});

// Ask the next question
function askNextQuestion() {
    if (questionIndex === 25) {
        showPage("pageAttentionCheck");
        document.getElementById("progressTextAttention").textContent = `Attention Check (Question ${questionIndex + 1} of 50)`;
        return;
    }

    if (questionIndex >= 50) {
        showPage("pageEnd");
        return;
    }

    document.getElementById("progressText").textContent = `Question ${questionIndex + 1} of 50`;

    let shuffledData = jsonData.features.sort(() => 0.5 - Math.random());
    currentConditionA = shuffledData[0];

    // Only pick B that uses the same feature labels as A
    let compatibleB = jsonData.features.filter(item =>
    item.options.join() === currentConditionA.options.join()
    );

    currentConditionB = compatibleB[Math.floor(Math.random() * compatibleB.length)];
    if (!currentConditionB) {
        console.warn("No compatible condition B found — skipping this trial.");
        questionIndex++;
        askNextQuestion();
        return;
    }


    document.getElementById("targetName").textContent = currentConditionA.target;

    let table = document.getElementById("dynamicTable");

    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    // Align valuesB with the order of options in conditionA
    let valuesBObj = {};
    currentConditionB.options.forEach((feat, idx) => {
        valuesBObj[feat] = currentConditionB.values.split(", ")[idx];
    });

    for (let i = 0; i < currentConditionA.options.length; i++) {
        let row = document.createElement("tr");

        let labelCell = document.createElement("td");
        labelCell.textContent = currentConditionA.options[i];
        row.appendChild(labelCell);

        let valueA = document.createElement("td");
        valueA.textContent = currentConditionA.values.split(", ")[i];
        row.appendChild(valueA);

    let valueB = document.createElement("td");
    valueB.textContent = valuesBObj[currentConditionA.options[i]] || "-";
        row.appendChild(valueB);

        table.appendChild(row);
}


    // Reset buttons
    let btnA = document.getElementById("btnA");
    let btnB = document.getElementById("btnB");

    btnA.replaceWith(btnA.cloneNode(true));
    btnB.replaceWith(btnB.cloneNode(true));

    document.getElementById("btnA").onclick = function () {
        selectCondition("A");
    };
    document.getElementById("btnB").onclick = function () {
        selectCondition("B");
    };
}

// When user selects an answer
function selectCondition(choice) {
    selectedConditions.push({
        question: questionIndex + 1,
        target: currentConditionA.target,
        options: currentConditionA.options,
        optionA: {
            trial_id: currentConditionA.trial_id,
            task_id: currentConditionA.task_id,
            values: currentConditionA.values
        },
        optionB: {
            trial_id: currentConditionB.trial_id,
            task_id: currentConditionB.task_id,
            values: currentConditionB.values
        },
        choice: choice
    });
    questionIndex++;
    askNextQuestion();
}


// Save user responses
document.getElementById("buttonSaveResponses").addEventListener("click", function () {
    const prolificID = sessionStorage.getItem('prolific_id') || "UNKNOWN";

    const finalData = {
        prolific_id: prolificID,
        responses: selectedConditions
    };

    // Save data to JATOS
    jatos.submitResultData(finalData)
        .then(() => {
            // Redirect to Prolific completion page
            window.location.href = "https://app.prolific.com/submissions/complete?cc=YOUR_COMPLETION_CODE";
        })
        .catch((err) => {
            console.error("Error submitting to JATOS:", err);
            alert("Something went wrong while submitting your data. Please try again.");
        });
});

// Handle keypresses
document.addEventListener("keydown", function (event) {
    let key = event.key.toLowerCase();

    if (document.getElementById("page3").style.display === "block") {
        if (key === "a") document.getElementById("btnA").click();
        if (key === "b") document.getElementById("btnB").click();
    }

    if (document.getElementById("pageAttentionCheck").style.display === "block") {
        if (key === "a") document.getElementById("btnAttentionA").click();
    }
});

// Setup Attention Check Button
document.addEventListener("DOMContentLoaded", function () {
    loadJSON();

    let btnAttentionA = document.getElementById("btnAttentionA");
    if (btnAttentionA) {
        btnAttentionA.addEventListener("click", function () {
            selectedConditions.push({
                question: "attention_check",
                passed: true,
                timestamp: Date.now()
            });
            questionIndex++; // move on to next real question
            showPage("page3");
            askNextQuestion();
        });
    }
});

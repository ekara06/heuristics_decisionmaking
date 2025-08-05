let questionIndex = 0;
let selectedConditions = [];
sessionStorage.clear();
let jsonData;
let currentConditionF, currentConditionJ;

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

// Load JSON once and store it
async function loadJSON() {
    try {
        // Randomly assign to one group
        const group = Math.random() < 0.5 ? "ranking" : "direction";
        sessionStorage.setItem("conditionGroup", group); // Save group for later 

        const response = await fetch(`${group}.json`);
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
    document.getElementById("progressWrapper").style.display = "block";
    showPage("page3");
    askNextQuestion();
});


// Ask the next question
function askNextQuestion() {
    console.log(`askNextQuestion called with questionIndex: ${questionIndex}`);

    // ─── 1) STOP AT 50 ───
    if (questionIndex >= 50) {
        showPage("pageEnd");
        return;
    }

    // ─── 2) ATTENTION CHECK ───
    if (
        attentionChecks.hasOwnProperty(questionIndex) &&
        !sessionStorage.getItem(`attentionShown_${questionIndex}`)
    ) {
        const currentCheck = attentionChecks[questionIndex];

        // attention question
        document.getElementById("attentionQuestion").innerHTML = 
        `Which of the following two items has the higher <strong>${currentCheck.target}</strong>?`;
                      

        // build the F vs. J table
        const tbody = document.getElementById("attentionTableBody");
        tbody.innerHTML = "";
        currentCheck.features.forEach(f => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${f.label}</td>
              <td>${f.F}</td>
              <td>${f.J}</td>
            `;
            tbody.appendChild(row);
        });

        // mark it shown so it only fires once
        sessionStorage.setItem(`attentionShown_${questionIndex}`, "true");
        sessionStorage.setItem("currentAttentionIndex", questionIndex);

        showPage("pageAttentionCheck");
        return;
    }

    const progressPercent = ((questionIndex + 1) / 50) * 100;
    document.getElementById("progressBar").style.width = `${progressPercent}%`;


    let shuffledData = jsonData.features.sort(() => 0.5 - Math.random());
    currentConditionF = shuffledData[0];

    // Only pick B that uses the same feature labels as A
    let compatibleJ = jsonData.features.filter(item =>
        item.options.join() === currentConditionF.options.join()
    );

    currentConditionJ = compatibleJ[Math.floor(Math.random() * compatibleJ.length)];
    if (!currentConditionJ) {
        console.warn("No compatible condition J found — skipping this trial.");
        questionIndex++;
        askNextQuestion();
        return;
    }

    document.getElementById("targetName").textContent = currentConditionF.target;

    let table = document.getElementById("dynamicTable");

    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    // Align valuesB with the order of options in conditionA
    let valuesBObj = {};
    currentConditionJ.options.forEach((feat, idx) => {
        valuesBObj[feat] = currentConditionJ.values.split(", ")[idx];
    });

    for (let i = 0; i < currentConditionF.options.length; i++) {
        let row = document.createElement("tr");

        let labelCell = document.createElement("td");
        labelCell.textContent = currentConditionF.options[i];
        row.appendChild(labelCell);

        let valueA = document.createElement("td");
        valueA.textContent = currentConditionF.values.split(", ")[i];
        row.appendChild(valueA);

        let valueB = document.createElement("td");
        valueB.textContent = valuesBObj[currentConditionF.options[i]] || "-";
        row.appendChild(valueB);

        table.appendChild(row);
    }

    // Reset buttons
    let btnF = document.getElementById("btnF");
    let btnJ = document.getElementById("btnJ");

    btnF.onclick = function () {
        selectCondition("F");
    };
    btnJ.onclick = function () {
        selectCondition("J");
    };
}

// When user selects an answer
function selectCondition(choice) {
    console.log(`selectCondition called with choice: ${choice}, questionIndex: ${questionIndex}`);
    
    selectedConditions.push({
        question: questionIndex + 1,
        target: currentConditionF.target,
        target_value: currentConditionF.target_value,
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

    questionIndex++; // Increment question index after recording the response
    console.log(`After increment, questionIndex is now: ${questionIndex}`);
    askNextQuestion(); // Move to next question (or attention check)
}

// Save user responses
document.getElementById("buttonSaveResponses").addEventListener("click", function () {
    const prolificID = window.prolificID || "UNKNOWN";

    const finalData = {
        prolific_id: prolificID,
        condition_group: sessionStorage.getItem("conditionGroup"),
        responses: selectedConditions
    };

    // Save data to JATOS
    jatos.submitResultData(finalData)
        .then(() => {
            // Redirect to Prolific completion page
            window.location.href = "https://app.prolific.com/submissions/complete?cc=C1IW5H1T";
        })
        .catch((err) => {
            console.error("Error submitting to JATOS:", err);
            alert("Something went wrong while submitting your data. Please try again.");
        });
});

// Handle keypresses
document.addEventListener("keydown", function (event) {
    const key = event.key.toLowerCase();
    console.log(`Key pressed: ${key}`);

    if (document.getElementById("page3").style.display === "block") {
        if (key === "f") {
            console.log("F key pressed, calling selectCondition('F')");
            event.preventDefault(); // Prevent any default behavior
            selectCondition("F");
        }
        if (key === "j") {
            console.log("J key pressed, calling selectCondition('J')");
            event.preventDefault(); // Prevent any default behavior
            selectCondition("J");
        }
    }    
    else if (document.getElementById("pageAttentionCheck").style.display === "block") {
        if (key === "f") {
            event.preventDefault(); // Prevent any default behavior
            document.getElementById("btnAttentionF").click();
        } else if (key == "j") {
            event.preventDefault(); // Prevent any default behavior
            document.getElementById("btnAttentionJ").click();
        }
    }
});

// Setup Attention Check Buttons (handles all 4 checks)
document.addEventListener("DOMContentLoaded", function () {
    loadJSON();

    let btnAttentionF = document.getElementById("btnAttentionF");
    let btnAttentionJ = document.getElementById("btnAttentionJ");

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

        sessionStorage.removeItem("currentAttentionIndex"); // clear flag
        showPage("page3");
        askNextQuestion();  // no questionIndex++ here!

    }

    if (btnAttentionF) btnAttentionF.addEventListener("click", () => handleAttentionClick("F"));
    if (btnAttentionJ) btnAttentionJ.addEventListener("click", () => handleAttentionClick("J"));
});

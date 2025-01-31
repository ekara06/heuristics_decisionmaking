let allQuestions = []; 
let randomizedQuestions = []; // Randomization
const targetQuestionCount = 50; // How many questions there will be
let prolificID = null; // ProlificID

function getProlificID() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("PROLIFIC_PID") || "unknown"; // ProlificID'yi alın veya 'unknown' yapın
}

function initializeProlificID() {
    prolificID = getProlificID(); // ProlificID'yi ayarla
    console.log(`Prolific ID initialized: ${prolificID}`);
}

// Soruları JSON'dan yükle
function loadQuestions() {
    fetch("even1.json")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            allQuestions = data.features; // "features" anahtarından verileri al
            console.log("All Questions Count:", allQuestions.length); // Toplam soru sayısını kontrol et

            randomizedQuestions = getRandomQuestions(allQuestions, targetQuestionCount); // Rastgele 50 soru seç
            console.log("Selected Questions:", randomizedQuestions); // Seçilen soruları kontrol et
            showQuestion(); // İlk soruyu başlatmak için çağır
        })
        .catch(error => console.error("Error loading questions:", error));
}

// Rastgele soruları seçmek için düzenlenmiş fonksiyon
function getRandomQuestions(questions, count) {
    const shuffled = [...questions].sort(() => 0.5 - Math.random()); 
    return shuffled.slice(0, count);
}

let currentQuestionIndex = 0; // Şu anki soru indeksi
const userResponses = []; // Kullanıcı cevaplarını saklayın
let currentCertainty = null; // Certainty (kesinlik) yanıtını saklayın

// Sayfalar arası geçiş fonksiyonu
function showPage(pageId) {
    const pages = ["pageIntro", "pageTaskIntro", "page1", "page2", "pageEnd"];
    pages.forEach(page => {
        document.getElementById(page).style.display = page === pageId ? "block" : "none";
    });
}

// Soruyu göster
function showQuestion() {
    if (currentQuestionIndex >= randomizedQuestions.length) {
        showEndOfStudy();
        return;
    }

    const question = randomizedQuestions[currentQuestionIndex];
    const targetElements = document.querySelectorAll("#target");
    targetElements.forEach(element => {
        element.textContent = question.target;
    });
    
    // Rastgele olarak option1 veya option2'yi seç
    const randomOptionIndex = Math.floor(Math.random() * 2);
    const selectedOption = question.options[randomOptionIndex];
    document.getElementById("shownOption").textContent = selectedOption;
    
    // Hangi option'ın gösterildiğini kaydet
    question.currentShownOption = selectedOption;

    showPage("page1");
}

// Veriyi kaydet
function saveData(filedata) {
    const filename = `./data/${prolificID}.json`; // ProlificID'yi kullan
    $.post("save_data.php", { postresult: filedata, postfile: filename })
        .done(() => {
            console.log(`Data saved successfully for ${prolificID}!`);
        })
        .fail((error) => {
            console.error("Error saving data:", error);
        });
}

// Cevapları kaydetmek için kullanılacak fonksiyon
function saveResponses() {
    const dataToSave = {
        prolificID: prolificID, // Prolific ID
        responses: userResponses, 
        timestamp: new Date().toISOString(), 
    };
    const jsonData = JSON.stringify(dataToSave);
    saveData(jsonData); // Veriyi kaydet
}

function saveResponse(choice) {
    const question = randomizedQuestions[currentQuestionIndex];
    const choiceOption = choice === "D" ? "High" : "Low";
    
    userResponses.push({
        prolificID: prolificID,
        questionId: question.id,
        target: question.target,
        shownOption: `${question.currentShownOption === question.options[0] ? "Option1" : "Option2"}: ${question.currentShownOption}`,
        choice: `${choice} - ${choiceOption}`,
        certainty: null,
        timestamp: new Date().toISOString()
    });

    showPage("page2");
}

function saveCertainty(certainty) {
    userResponses[userResponses.length - 1].certainty = certainty;

    const dataToSave = {
        latestResponse: userResponses[userResponses.length - 1] // Sadece en son yanıtı kaydediyoruz
    };

    jatos.appendResultData(JSON.stringify(dataToSave))
        .then(() => {
            console.log("Certainty and choice saved successfully.");
        })
        .catch((error) => {
            console.error("Error saving certainty:", error);
        });

    currentQuestionIndex++;

    if (currentQuestionIndex >= randomizedQuestions.length) {
        showEndOfStudy();
    } else {
        showQuestion();
    }
}

// Çalışmayı sonlandır ve bitiş ekranını göster
function showEndOfStudy() {
    const finalDataToSave = {
        prolificID: prolificID,
        responses: userResponses, 
        timestamp: new Date().toISOString()
    };

    jatos.submitResultData(JSON.stringify(finalDataToSave))
        .then(() => {
            console.log("Final data saved successfully.");
        })
        .catch((error) => {
            console.error("Error saving final data:", error);
        });

    showPage("pageEnd"); 
}


// "I Consent" butonu için event listener ekle
function addConsentListener() {
    document.getElementById("buttonConsent").addEventListener("click", function () {
        initializeProlificID(); // Prolific ID'yi başlat
        showPage("pageTaskIntro"); // Görev tanıtım sayfasını göster
    });
}

// Task Introduction butonu için event listener ekle
function addTaskIntroListener() {
    document.getElementById("buttonTaskIntroNext").addEventListener("click", function () {
        showPage("page1"); // Soruları göster
        loadQuestions(); // Soruları yükle ve başlat
    });
}

// Klavye olayları için dinleyici ekle
function addKeyboardListeners() {
    document.addEventListener("keydown", function (event) {
        if (document.getElementById("page1").style.display === "block") {
            if (event.key === "d" || event.key === "D") {
                saveResponse("D");
            } else if (event.key === "k" || event.key === "K") {
                saveResponse("K");
            }
        } else if (document.getElementById("page2").style.display === "block") {
            if (event.key >= "1" && event.key <= "5") {
                saveCertainty(event.key);
            }
        }
    });
}

// Başlangıç fonksiyonları
addConsentListener();
addTaskIntroListener();
addKeyboardListeners();

let allQuestions = []; // Tüm soruları global olarak tanımlayın
let randomizedQuestions = []; // Rastgele seçilen sorular
const targetQuestionCount = 50; // Kaç soru gösterileceğini buradan kontrol edebilirsiniz
let prolificID = null; // ProlificID'yi global olarak tanımlayın

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
    const shuffled = [...questions].sort(() => 0.5 - Math.random()); // Orijinal sırayı bozmamak için [...questions]
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
        showEndOfStudy(); // If all questions are answered, show the end screen
        return;
    }

    const question = randomizedQuestions[currentQuestionIndex];
    const targetText = question.target; // Use the "target" from the question
    const options = question.options; // Get the options

    // Randomly decide which option to display in the sentence
    const chosenOption = Math.random() < 0.5 ? options[0] : options[1];

    // Set target text and option in the question
    document.getElementById("target").textContent = targetText;
    document.getElementById("target2").textContent = targetText;
    document.getElementById("option-placeholder").textContent = chosenOption;

    // Set static button labels
    document.getElementById("buttonD").textContent = "D";
    document.getElementById("buttonK").textContent = "K";

    showPage("page1"); // Show the question page
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
        responses: userResponses, // Tüm kullanıcı cevapları
        timestamp: new Date().toISOString(), // Zaman damgası
    };
    const jsonData = JSON.stringify(dataToSave);
    saveData(jsonData); // Veriyi kaydet
}

function saveResponse(choice) {
    const question = randomizedQuestions[currentQuestionIndex];
    const selectedChoice = choice === "D" ? question.options[0] : question.options[1]; // Seçimin metnini belirle

    userResponses.push({
        id: question.id, // Soru ID'si
        question: question.target, // Soru başlığı
        choice: selectedChoice, // Metinsel seçim ("Studyhours" gibi)
        certainty: null, // Certainty (kesinlik)
        time: new Date().toISOString(), // Yanıt zamanı
    });

    showPage("page2"); // Certainty sayfasına geç
}

function saveCertainty(certainty) {
    const lastResponse = userResponses[userResponses.length - 1];
    lastResponse.certainty = certainty; // Certainty güncelleme

    const dataToSave = {
        prolificID: prolificID,
        latestResponse: lastResponse, // Güncellenmiş yanıt
    };

    jatos.appendResultData(JSON.stringify(dataToSave))
        .then(() => {
            console.log("Certainty and choice saved successfully.");
        })
        .catch((error) => {
            console.error("Error saving certainty:", error);
        });

    currentQuestionIndex++; // Bir sonraki soruya geç

    // Tüm sorular bitti mi kontrol et
    if (currentQuestionIndex >= randomizedQuestions.length) {
        showEndOfStudy(); // Çalışmayı bitir
    } else {
        showQuestion(); // Bir sonraki soruyu göster
    }
}

// Çalışmayı sonlandır ve bitiş ekranını göster
function showEndOfStudy() {
    const finalDataToSave = {
        prolificID: prolificID, // Prolific ID
        responses: userResponses, // Tüm kullanıcı yanıtları
        timestamp: new Date().toISOString(), // Çalışma bitiş zamanı
    };

    jatos.submitResultData(JSON.stringify(finalDataToSave))
        .then(() => {
            console.log("Final data saved successfully.");
        })
        .catch((error) => {
            console.error("Error saving final data:", error);
        });

    showPage("pageEnd"); // Katılımcıya teşekkür ekranını göster
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

let allQuestions = []; // Tüm soruları global olarak tanımlayın
let randomizedQuestions = []; // Rastgele seçilen sorular
targetQuestionCount = 50; // Kaç soru gösterileceğini buradan kontrol edebilirsiniz

// Global değişken olarak prolificID ekleyelim
let prolificID = null;

// ProlificID alma fonksiyonu
function getProlificID() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("PROLIFIC_PID") || "unknown";
}

// Initialize fonksiyonu
function initializeProlificID() {
    prolificID = getProlificID();
    console.log(`Prolific ID initialized: ${prolificID}`);
}

// Soruları JSON'dan yükle
function loadQuestions() {
    fetch("even0.json")
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
        showEndOfStudy(); // Eğer tüm sorular bittiyse bitiş ekranını göster
        return;
    }

    const question = randomizedQuestions[currentQuestionIndex];
    const targetText = question.target;

    // Target'ı göster
    document.getElementById("target").textContent = targetText;
    
    // Options'ları göster
    document.getElementById("option1").textContent = question.options[0];
    document.getElementById("option2").textContent = question.options[1];

    // Buton etiketlerini ayarla
    document.getElementById("buttonD").textContent = "D";
    document.getElementById("buttonK").textContent = "K";

    showPage("page1"); // Soru sayfasını göster
}

// Kullanıcı cevabını kaydet ve certainty (kesinlik) sayfasına geç
function saveResponse(choice) {
    const question = randomizedQuestions[currentQuestionIndex];
    const selectedChoice = choice === "D" ? question.options[0] : question.options[1];

    userResponses.push({
        id: question.id,
        targetitem: question.target,
        options: {
            D: question.options[0],
            K: question.options[1]
        },
        choice: `${choice} (${selectedChoice})`,
        certainty: null,
        time: new Date().toISOString()
    });

    showPage("page2");
}

// Certainty (kesinlik) yanıtını kaydet ve bir sonraki soruya geç
function saveCertainty(certainty) {
    userResponses[userResponses.length - 1].certainty = certainty;
    
    // Her yanıt için JATOS'a veri gönder
    const lastResponse = userResponses[userResponses.length - 1];
    const responseData = {
        prolificID: prolificID,
        latestResponse: lastResponse
    };

    jatos.appendResultData(JSON.stringify(responseData))
        .then(() => {
            console.log("Response saved to JATOS");
        })
        .catch(error => {
            console.error("Error saving to JATOS:", error);
        });

    currentQuestionIndex++;
    showQuestion();
}

// Çalışmayı sonlandır ve bitiş ekranını göster
function showEndOfStudy() {
    // Final veriyi JATOS'a gönder
    const finalData = {
        prolificID: prolificID,
        responses: userResponses,
        timestamp: new Date().toISOString()
    };

    jatos.submitResultData(JSON.stringify(finalData))
        .then(() => {
            console.log("Final data submitted to JATOS");
            showPage("pageEnd");
        })
        .catch(error => {
            console.error("Error submitting to JATOS:", error);
            showPage("pageEnd");
        });
}

// "I Consent" butonu için event listener ekle
function addConsentListener() {
    document.getElementById("buttonConsent").addEventListener("click", function () {
        initializeProlificID(); // ProlificID'yi başlat
        showPage("pageTaskIntro");
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

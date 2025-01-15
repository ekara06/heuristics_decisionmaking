let allQuestions = []; // Tüm soruları global olarak tanımlayın
let randomizedQuestions = []; // Rastgele seçilen sorular
const targetQuestionCount = 50; // Kaç soru gösterileceğini buradan kontrol edebilirsiniz
let subjectID = null; // Global olarak tanımla

// subjectID'yi başlat
function initializeSubjectID() {
    subjectID = "participant_" + Math.floor(Math.random() * 1000); // Rastgele bir ID oluştur
    console.log(`Subject ID initialized: ${subjectID}`);
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
    const filename = `./data/${subjectID}.json`; // Aynı subjectID'yi kullan
    $.post("save_data.php", { postresult: filedata, postfile: filename })
        .done(() => {
            console.log(`Data saved successfully for ${subjectID}!`);
        })
        .fail((error) => {
            console.error("Error saving data:", error);
        });
}

// Cevapları kaydetmek için kullanılacak fonksiyon
function saveResponses() {
    const dataToSave = {
        responses: userResponses, // Tüm kullanıcı cevapları
        timestamp: new Date().toISOString(), // Zaman damgası
    };
    const jsonData = JSON.stringify(dataToSave);
    saveData(jsonData); // Veriyi kaydet
}

// Cevapları ve certainty değerini saklayan fonksiyon
function saveResponse(choice) {
    const question = randomizedQuestions[currentQuestionIndex];
    userResponses.push({
        question: question.target,
        choice: choice,
        time: new Date().toISOString(), // Cevap verildiği zaman
    });

    // Eğer son soruya geldiysek cevapları kaydet
    if (currentQuestionIndex === randomizedQuestions.length - 1) {
        saveResponses(); // Tüm cevapları kaydet
    }

    showPage("page2"); // Certainty sayfasına geç
    currentCertainty = null; // Certainty sıfırla
}

// Certainty yanıtını kaydeden fonksiyon
function saveCertainty(certainty) {
    userResponses[userResponses.length - 1].certainty = certainty; // Certainty güncelle
    currentQuestionIndex++; // Bir sonraki soruya geç

    // Eğer tüm sorular bittiyse
    if (currentQuestionIndex >= randomizedQuestions.length) {
        saveResponses(); // Cevapları kaydet ve bitir
        showEndOfStudy(); // Deney bitiş ekranını göster
    } else {
        showQuestion(); // Bir sonraki soruyu göster
    }
}

// Çalışmayı sonlandır ve bitiş ekranını göster
function showEndOfStudy() {
    showPage("pageEnd");
    console.log("User Responses:", userResponses); // Kullanıcı yanıtlarını kontrol et
}

// "I Consent" butonu için event listener ekle
function addConsentListener() {
    document.getElementById("buttonConsent").addEventListener("click", function () {
        initializeSubjectID(); // Katılımcı ID'sini başlat
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

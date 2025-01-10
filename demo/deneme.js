// JavaScript kodunda gerekli düzenlemeler:

let allQuestions = []; // Tüm soruları global olarak tanımlayın
let randomizedQuestions = []; // Rastgele seçilen sorular
targetQuestionCount = 50; // Kaç soru gösterileceğini buradan kontrol edebilirsiniz

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

            showQuestion(); // İlk soruyu göster
        })
        .catch(error => console.error("Error loading questions:", error));
}

// Rastgele soruları seçmek için düzenlenmiş fonksiyon
function getRandomQuestions(questions, count) {
    const shuffled = questions.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

let currentQuestionIndex = 0; // Şu anki soru indeksi
const userResponses = []; // Kullanıcı cevaplarını saklayın
let currentCertainty = null; // Certainty (kesinlik) yanıtını saklayın

// Soruyu göster
function showQuestion() {
    if (currentQuestionIndex >= randomizedQuestions.length) {
        showEndOfStudy(); // Eğer tüm sorular bittiyse bitiş ekranını göster
        return;
    }

    const question = randomizedQuestions[currentQuestionIndex];
    document.getElementById("target").textContent = question.target;
    document.getElementById("option1").textContent = question.options[0];
    document.getElementById("option2").textContent = question.options[1];

    document.getElementById("page1").style.display = "block";
    document.getElementById("page2").style.display = "none";
}

// Kullanıcı cevabını kaydet ve certainty (kesinlik) sayfasına geç
function saveResponse(choice) {
    const question = randomizedQuestions[currentQuestionIndex];
    userResponses.push({
        question: question.target,
        choice: choice,
        time: new Date().toISOString(),
    });
    document.getElementById("page1").style.display = "none";
    document.getElementById("page2").style.display = "block";
    currentCertainty = null; // Certainty sıfırla
}

// Certainty (kesinlik) yanıtını kaydet ve bir sonraki soruya geç
function saveCertainty(certainty) {
    userResponses[userResponses.length - 1].certainty = certainty; // Son yanıtı güncelle
    currentQuestionIndex++; // Bir sonraki soruya geç
    showQuestion();
}

// Çalışmayı sonlandır ve bitiş ekranını göster
function showEndOfStudy() {
    document.getElementById("page1").style.display = "none";
    document.getElementById("page2").style.display = "none";
    document.getElementById("pageEnd").style.display = "block";
    console.log("User Responses:", userResponses); // Kullanıcı yanıtlarını kontrol et
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
loadQuestions();
addKeyboardListeners();

function mysubmit() {

    myDataRef = {
        "certainty": userResponses.certainty,
        "choice": userResponses.choice,
    };
    // save data as JSONs
    saveData(JSON.stringify(myDataRef))
}

function saveData(filedata) {
    var filename = "./data/" + subjectID + ".json";
    $.post("save_data.php", { postresult: filedata + "\n", postfile: filename })
}
document.querySelectorAll(".projcard-description").forEach(function (box) {
    $clamp(box, {clamp: 3});
});

document.getElementById("submit-button").addEventListener("click", savePref);
document.getElementById("ref_button").addEventListener("click", getHistoryKeywords);


document.addEventListener('DOMContentLoaded', function () {

});

function showLoading(){
    var loading_indicator = document.createElement('div');
    loading_indicator.id = 'loading-indicator';
    var hourglass = document.createElement('div');
    hourglass.className = 'lds-hourglass';
    loading_indicator.appendChild(hourglass);
    document.body.appendChild(loading_indicator);
}

function hideLoading(){
    var loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.parentNode.removeChild(loadingIndicator);
    }
}

function getHistoryKeywords() {
    showLoading();
    chrome.history.search({ text: '', maxResults: 10 }, function (data) {
        var historyData = [];

        data.forEach(function (page) {
            // Check if the visit count is greater than or equal to 3
            if (page.visitCount >= 3) {
                // Extract important information from each history entry
                var pageData = {
                    url: page.url,
                    title: page.title,
                };
                historyData.push(pageData);
            }
        });
        console.log('History Data:', historyData);
        var requestData = {
            historyData: historyData
        };
        
        // Make a POST request to the backend endpoint
        fetch('http://127.0.0.1:5000/history', {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            data.forEach(resData => {
                displayNews(resData.news);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    });
}

function displayNews(news) {
    // Get the container element
    var container = document.getElementById('news-container');
    container.className = 'projcard-conatiner'
    // Iterate over each news article and create a card for it
    news.forEach(article => {
        // Create elements for each piece of information
        var card = document.createElement('div');
        card.className = 'projcard projcard-blue';

        var bar = document.createElement('div');
        bar.className = 'projcard-bar'

        var innerBox = document.createElement('div');
        innerBox.className = 'projcard-innerbox';

        var image = document.createElement('img');
        image.className = 'projcard-img';
        image.src = article.image;
        image.alt = 'News Image';

        var textBox = document.createElement('div');
        textBox.className = 'projcard-textbox';

        var title = document.createElement('div');
        title.className = 'projcard-title';
        title.textContent = article.title;

        var subtitle = document.createElement('div');
        subtitle.className = 'projcard-subtitle';
        subtitle.textContent = article.media;

        var description = document.createElement('div');
        description.className = 'projcard-description';
        description.textContent = article.description;

        // Append elements to the card
        container.appendChild(card);
        card.appendChild(innerBox);
        innerBox.appendChild(image);
        innerBox.appendChild(textBox);
        textBox.appendChild(title);
        textBox.appendChild(subtitle);
        textBox.appendChild(bar);
        textBox.appendChild(description);
    });
}

function savePref() {
    const userInput = document.getElementById('search').value;

    // Save data to extension storage
    if (userInput) {
        var pref = { preferences: userInput }
        chrome.storage.local.set(pref, function () {
            console.log('Data saved:', userInput);
            location.reload();
        });
    }
}


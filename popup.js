document.querySelectorAll(".projcard-description").forEach(function (box) {
    // $clamp(box, {clamp: 6});
});

document.getElementById("submit-button").addEventListener("click", savePref);

document.addEventListener('DOMContentLoaded', function () {
    chrome.storage.local.get(['preferences'], function (result) {
        const storedValue = result.preferences;
        var preferences = {
            "preferences": storedValue
        };

        var urlParams = new URLSearchParams(preferences);

        fetch('http://127.0.0.1:5000/fetch?' + urlParams, {
            method: 'GET',
            mode: 'cors',
            credentials: 'include'
        })
            .then(response => response.json())
            .then(data => {
                // Process the JSON data and render it in the DOM
                displayNews(data.news);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    });

    getHistory();

});

function getHistory() {
    chrome.history.search({ text: '', maxResults: 10 }, function (data) {
        var historyData = [];

        data.forEach(function (page) {
            // Extract important information from each history entry
            var pageData = {
                url: page.url,
                title: page.title,
                lastVisitTime: page.lastVisitTime,
                visitCount: page.visitCount
                // Add more properties as needed
            };

            historyData.push(pageData);

            // Log extracted information
            console.log('URL:', pageData.url);
            console.log('Title:', pageData.title);
            console.log('Last Visit Time:', new Date(pageData.lastVisitTime));
            console.log('Visit Count:', pageData.visitCount);
            console.log('---');
        });

        // Use historyData array for further processing or personalization
        // For example, send it to your server or analyze it to understand user behavior
        console.log('History Data:', historyData);
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
            // var urlParams = new URLSearchParams(pref);
            
            // fetch('http://127.0.0.1:5000/fetch?' + urlParams, {
            //     method: 'GET',
            //     mode: 'cors',
            //     credentials: 'include'
            // })
            //     .then(response => response.json())
            //     .then(data => {
            //         // Process the JSON data and render it in the DOM
            //         displayNews(data.news);
            //     })
            //     .catch(error => {
            //         console.error('Error fetching data:', error);
            //     });
        });

    }

}


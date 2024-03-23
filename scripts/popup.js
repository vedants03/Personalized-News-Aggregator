var news_response;
let submit_button_clicked = false;
let ref_button_clicked = false;

document.querySelectorAll(".projcard-description").forEach(function (box) {
    $clamp(box, { clamp: 3 });
});

document.getElementById("submit-button").addEventListener("click", savePref);
document.getElementById("ref_button").addEventListener("click", getHistoryKeywords);
document.getElementById("search").addEventListener("keypress", function (event) {
    if(event.key === "Enter"){
        savePref();
    }
});

document.addEventListener('DOMContentLoaded', function () {
    chrome.storage.local.get(['news'], function(result){
        const storedValue = result.news;
        if(storedValue){
            displayNews(storedValue);
        }
    })
});

function showLoading() {
    var loading_indicator = document.createElement('div');
    loading_indicator.id = 'loading-indicator';
    var hourglass = document.createElement('div');
    hourglass.className = 'lds-hourglass';
    loading_indicator.appendChild(hourglass);
    document.body.appendChild(loading_indicator);
}

function hideLoading() {
    var loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.parentNode.removeChild(loadingIndicator);
    }
}

function getHistoryKeywords() {
    if(!ref_button_clicked){
        ref_button_clicked = true;
        var news_container = document.getElementById('news-container');
        news_container.innerHTML = '';
        showLoading();
        chrome.history.search({ text: '', maxResults: 20 }, function (data) {
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
                    news_response = data;
                    console.log(news_response)
                    hideLoading();
                    // data.forEach(resData => {
                    //     displayNews(resData.news);
                    // });
                    saveNews(news_response.news);
                    displayNews(news_response.news);
                    ref_button_clicked = false;
                })
                .catch(error => {
                    ref_button_clicked = false;
                    console.error('Error fetching data:', error);
                });
        });

    }
}

function displaySummary(title){
    var container = document.createElement('div');
    container.className = 'summary-container';

    const existingContent = document.getElementById('news-container');
    if (existingContent) {
        existingContent.remove();
        showLoading();
    }
    else{
        console.error("Not found")
    }

    var backButton = document.createElement('button');
    backButton.className = 'button-17';
    backButton.id = 'back-button';
    backButton.textContent = 'Back'
    backButton.addEventListener('click',function(){
        container.remove();
        document.body.appendChild(existingContent);
        news_response.forEach(item =>{
            displayNews(item.news);
        })
    })

    var heading_div = document.createElement('div');
    heading_div.id = 'summary-heading'
    heading_div.className = 'heading-div'

    var heading = document.createElement('h2');
    heading.className = 'article-title';
    heading.innerText = title;
    heading_div.appendChild(heading);

    var bar = document.createElement('div');
    bar.className = 'projcard-bar'
    bar.style.width = '100%';    

    var content_div = document.createElement('div');
    content_div.id = 'summary-content'
    content_div.className = 'content-div'

    var content = document.createElement('p');
    content.className = 'summary-text';
    content_div.appendChild(content);
    heading_div.appendChild(bar);

    fetch('http://127.0.0.1:5000/summarize', {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(title),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        content.innerText = data;
        hideLoading();
        container.appendChild(heading_div);
        container.appendChild(content_div);
        container.appendChild(backButton);
        document.body.appendChild(container);
        submit_button_clicked = false;
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        submit_button_clicked = false;
    });
}

function displayNews(news) {
    // Get the container element
    var container = document.getElementById('news-container');
    container.className = 'projcard-container'
    container.innerHTML = ''
    // Iterate over each news article and create a card for it
    news.forEach(article => {
        // Create elements for each piece of information
        var card = document.createElement('div');
        card.className = 'projcard projcard-blue';
        card.addEventListener("click",function(){
            displaySummary(article.title);      
        });
        var bar = document.createElement('div');
        bar.className = 'projcard-bar'
        
        var innerBox = document.createElement('div');
        innerBox.className = 'projcard-innerbox';

        var image = document.createElement('img');
        image.className = 'projcard-img';
        image.src = 'data:image/png;base64,' + article.image;
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
    var news_container = document.getElementById('news-container');
    news_container.innerHTML = '';

    if (!submit_button_clicked && userInput) {
        submit_button_clicked = true;
        var pref = { preferences: userInput }
        var urlParams = new URLSearchParams(pref);
        showLoading();
        fetch('http://127.0.0.1:5000/fetch?' + urlParams, {
            method: 'GET',
            mode: 'cors',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            // Process the JSON data and render it in the DOM
            news_response = data;
            hideLoading();
            displayNews(data.news);
            submit_button_clicked = false;
        })
        .catch(error => {
            submit_button_clicked = false;
            console.error('Error fetching data:', error);
        });
        // chrome.storage.local.set(pref, function () {
        //     console.log('Data saved:', userInput);
        // });
        // chrome.storage.local.get(['preferences'], function(result) {
        //     const storedValue = result.preferences;
        //     var preferences = {
        //         "preferences": storedValue
        //     };
    
        //     var urlParams = new URLSearchParams(preferences);
        //     showLoading();
        //     fetch('http://127.0.0.1:5000/fetch?' + urlParams, {
        //         method: 'GET',
        //         mode: 'cors',
        //         credentials: 'include'
        //     })
        //     .then(response => response.json())
        //     .then(data => {
        //         // Process the JSON data and render it in the DOM
        //         news_response = data;
        //         hideLoading();
        //         displayNews(data.news);
        //         submit_button_clicked = false;
        //     })
        //     .catch(error => {
        //         submit_button_clicked = false;
        //         console.error('Error fetching data:', error);
        //     });
        // });
    }
}

function saveNews(data){
    var news = {
        news : data
    }
    chrome.storage.local.set(news, function () {
        console.log('Data saved:', news);
    });
}
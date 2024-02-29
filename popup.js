document.querySelectorAll(".projcard-description").forEach(function(box) {
	// $clamp(box, {clamp: 6});
});

document.getElementById("submit-button").addEventListener("click", savePref);

document.addEventListener('DOMContentLoaded', function () {
	chrome.storage.local.get(['preferences'], function(result) {
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

});

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
	if(userInput){
		chrome.storage.local.set({ preferences: userInput }, function() {
		  console.log('Data saved:', userInput);
		});

		chrome.storage.local.get(['preferences'], function(result) {
			const storedValue = result.preferences;
			console.log('Retrieved value:', storedValue);
	
			// You can use the retrieved value as needed, e.g., update the UI.
		  });
	}
  }


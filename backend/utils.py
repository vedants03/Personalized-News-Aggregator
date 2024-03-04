import requests
from fake_useragent import UserAgent
from newspaper import fulltext
import itertools
from transformers import BertTokenizer, BertForSequenceClassification
import torch


model_directory = model_directory = r"C:\Users\vedan\OneDrive\Documents\GitHub\Personalized-News-Aggregator\trained_model"

# Load tokenizer and model
tokenizer = BertTokenizer.from_pretrained(model_directory)
model = BertForSequenceClassification.from_pretrained(model_directory)

# Example path to the config file
config_path = r"C:\Users\vedan\OneDrive\Documents\GitHub\Personalized-News-Aggregator\trained_model\config.json"
label_mapping = model.config.id2label

def classify_history_titles(titles, model, tokenizer, label_mapping):
    # Tokenize input titles
    tokens = tokenizer(titles, padding=True, truncation=True, return_tensors="pt")

    # Make predictions
    with torch.no_grad():
        logits = model(**tokens).logits

    # Apply softmax to obtain probabilities
    probabilities = torch.nn.functional.softmax(logits, dim=1)

    # Get predicted label indices
    predicted_labels = torch.argmax(probabilities, dim=1).tolist()
    print(titles)
    print(predicted_labels)

    # Map label indices to category labels using the provided label_mapping
    predicted_categories = [label_mapping.get(label_idx, f"Unknown Category {label_idx}") for label_idx in predicted_labels]
    
    return set(predicted_categories)

def extract_categories_from_history(history_data):
    titles_list = []
    for entry in history_data:
        title = entry.get('title', '')
        titles_list.append(title)    
    predicted_catgeories = classify_history_titles(titles_list, model, tokenizer, label_mapping)
    print(predicted_catgeories)
    return predicted_catgeories


def generate_news(keywords):
    api_key = '516a5432d67e4f3ab8e139113a353941'
    all_news_data = []

    for keyword in keywords:
        # Make a request to the News API
        url = f'https://newsapi.org/v2/top-headlines?country=in&q={keyword}&apiKey={api_key}'
        response = requests.get(url)
        data = response.json()

        # Extract relevant information from the API response
        articles = data.get('articles', [])

        ua = UserAgent()
        news_data_list = []

        for article in itertools.islice(articles, 1):
            news_title = article.get('title', '')
            news_media = article.get('source', {}).get('name', '')
            news_description = article.get('description', '')
            news_link = article.get('url', '')
            news_img = article.get('urlToImage', '')

            try:
                html = requests.get(news_link, headers={'User-Agent': ua.chrome}, timeout=5).text
                text = fulltext(html)
                print('Text Content Scraped')
            except:
                print('Text Content Scraped Error, Skipped')
                text = None

            news_data_list.append({
                'title': news_title,
                'media': news_media,
                'description': news_description,
                'link': news_link,
                'image': news_img,
                'text_content': text
            })

        # Append news data for the current keyword
        all_news_data.append({
            'keyword': keyword,
            'news': news_data_list
        })

    return all_news_data






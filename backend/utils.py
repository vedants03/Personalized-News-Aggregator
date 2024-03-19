import requests
from fake_useragent import UserAgent
from newspaper import fulltext,Article
import itertools
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import nltk
from nltk.tokenize import word_tokenize
from GoogleNews import GoogleNews
import pandas as pd
from transformers import pipeline
from pygooglenews import GoogleNews
import os
from dotenv import load_dotenv
from urllib.request import urlopen
from PIL import Image
import io


load_dotenv()

gemini_key = os.environ.get('GEMINI_API_KEY')


gn = GoogleNews()
model_directory = r"C:\Users\vedan\OneDrive\Documents\GitHub\Personalized-News-Aggregator\trained_model"
summarizer = pipeline("summarization", model="Falconsai/text_summarization")
# Load tokenizer and model
tokenizer = BertTokenizer.from_pretrained(model_directory)
model = BertForSequenceClassification.from_pretrained(model_directory)


label_mapping = model.config.id2label

def classify_history_titles(titles, model, tokenizer, label_mapping):
    tokens = tokenizer(titles, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        logits = model(**tokens).logits

    probabilities = torch.nn.functional.softmax(logits, dim=1)

    predicted_labels = torch.argmax(probabilities, dim=1).tolist()
    print(titles)
    print(predicted_labels)

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

        all_news_data.append({
            'keyword': keyword,
            'news': news_data_list
        })

    return all_news_data

def scrape_news(title):
    article_count = 0
    search = gn.search(title, when = '1m')
    news_text = ""
    for entry in search["entries"]:
        url = entry["link"]
        print(url)
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
        except Exception as e:
            print(e)

        cleaned_summary = article.text
        news_text += cleaned_summary

        article_count += 1

        if article_count >= 4:
            break
    news_text = news_text.replace("\n", "")
    news_text = news_text.replace('"', "")
    
    return summarization(news_text)
    

def summarization(scrapped_text):
    # chunk_size = 500
    # chunks = []
    # start = 0
    # while start < len(scrapped_text):
    #     end = start + chunk_size
    #     if end >= len(scrapped_text):
    #         end = len(scrapped_text)
    #     else:
    #         end = scrapped_text.rfind(' ', start, end)
    #         if end == -1:
    #             end = start + chunk_size
    #     chunks.append(scrapped_text[start:end])
    #     start = end + 1
    # summary_text = ""
    # for chunk in chunks:
    #     chunk_summary = " ".join(item.get('summary_text', '') for item in summarizer(chunk, max_length=100, min_length=100, do_sample=False))
    #     summary_text += chunk_summary
    # print(summary_text)

    # URL of the API endpoint you want to send the POST request to
    summary_text = ""
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + str(gemini_key)

    prompt = "Summarize the following text: " + scrapped_text
    # Data to be sent in the POST request (in JSON format)
    data = {
        "contents": [{
        "parts":[{
          "text": prompt}]}]
    }

    headers = {
        'Content-Type': 'application/json',
    }

    # Send the POST request
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response from the API
        print('Response:', response.json())
        response_data = response.json()
        summary_text = response_data['candidates'][0]['content']['parts'][0]['text']
    else:
        # Print the error message if the request was not successful
        print('Error:', response.text)
        summary_text = response.text

    return summary_text


    

    
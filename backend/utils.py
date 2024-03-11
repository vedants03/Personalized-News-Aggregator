import requests
from fake_useragent import UserAgent
from newspaper import fulltext
import itertools
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import nltk
from nltk.tokenize import word_tokenize
from GoogleNews import GoogleNews
import pandas as pd
from transformers import pipeline
import openai

openai.api_key = "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"

model_directory = model_directory = r"C:\Users\vedan\OneDrive\Documents\GitHub\Personalized-News-Aggregator\trained_model"
summarizer = pipeline("summarization", model="Falconsai/text_summarization")
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

def scrape_news(title):
    googlenews = GoogleNews(lang='en', region='US', period='1d', encode='utf-8')
    googlenews.clear()
    googlenews.search(title)
    googlenews.get_page(2)
    news_result = googlenews.result(sort=True)
    news_data_df = pd.DataFrame.from_dict(news_result)

    ua = UserAgent()
    news_text_string = ""  # Initialize an empty string to store news text

    for index, headers in itertools.islice(news_data_df.iterrows(), 8):        
        news_title = str(headers['title'])
        news_media = str(headers['media'])
        news_update = str(headers['date'])
        news_timestamp = str(headers['datetime'])
        news_description = str(headers['desc'])
        news_link = str(headers['link'])
        print(news_link)
        news_img = str(headers['img'])
        try:
            html = requests.get(news_link, headers={'User-Agent': ua.chrome}, timeout=5).text
            text = fulltext(html)
            print('Text Content Scraped')
            # Concatenate the text content to the string
            if(len(text) > 50):
                news_text_string += text
        except:
            print('Text Content Scraped Error, Skipped')
            pass
    return summarization(news_text_string)
    

def break_up_file(tokens, chunk_size, overlap_size):
    if len(tokens) <= chunk_size:
        yield tokens
    else:
        chunk = tokens[:chunk_size]
        yield chunk
        yield from break_up_file(tokens[chunk_size-overlap_size:], chunk_size, overlap_size)

def break_up_file_to_chunks(stringname, chunk_size=500, overlap_size=100):
    tokens = word_tokenize(stringname)
    return list(break_up_file(tokens, chunk_size, overlap_size))


def convert_to_detokenized_text(tokenized_text):
    prompt_text = " ".join(tokenized_text)
    prompt_text = prompt_text.replace(" 's", "'s")
    return prompt_text

def break_up_text(text, window_size=300, stride=50):
    windows = [text[i:i + window_size] for i in range(0, len(text) - window_size + 1, stride)]
    print(windows)
    return windows

def summarization(scrapped_text):
    summary = summarizer(scrapped_text, max_length=400, min_length=100, do_sample=False)
    return summary

    # response = openai.Completion.create(
    # engine="gpt-3.5-turbo-instruct",
    # prompt="Summarize the following text: \n" + scrapped_text,
    # max_tokens=1000,
    # n=1,
    # stop=None,
    # temperature=0.7,
    # )

    # summary = response['choices'][0]['text']
    # print(summary)
    # return summary


    # openai.api_type = "azure"
    # openai.api_base = "https://PLESAE_ENTER_YOUR_OWNED_AOAI_RESOURCE_NAME.openai.azure.com/"
    # openai.api_version = "2022-12-01"
    # openai.api_key = "PLEASE_ENTER_YOUR_OWNED_AOAI_SERVICE_KEY"
    # Perform news text content summarization by Azure OpenAI Service (GPT3) for each chunk.



    # prompt_response = []
    # chunks = break_up_file_to_chunks(stringname)

    # for i, chunk in enumerate(chunks):
    #     print("Processing chunk " + str(i))
    #     prompt_request = "Summarize this news content: " + convert_to_detokenized_text(chunks[i])
    #     response = openai.Completion.create(
    #             engine="eason-text-davinci-002",
    #             prompt=prompt_request,
    #             temperature=.5, # Default is 1.
    #             max_tokens=500,
    #             top_p=1 # Default is 0.5.
    #     )
        
    #     prompt_response.append(response["choices"][0]["text"].strip())

    # # Define the prompt to perform summarization into 1,500 words for each summarized content.
    # prompt_request = "Consolidate these news content summaries into 1500 words sentences: " + str(prompt_response)
    # # Perform summarization by Azure OpenAI Service (GPT3) for each chunk of summarized content.
    # response = openai.Completion.create(
    #         engine="PLEASE_ENTER_YOUR_AOAI_MODEL_DEPLOYMENT_NAME",
    #         prompt=prompt_request,
    #         temperature=.5, # Default is 1.
    #         max_tokens=1000,
    #         top_p=1 # Default is 0.5.
    #     )
    # # Display the final summary from the top 10 news record's text content.
    # news_content_summary = response["choices"][0]["text"].strip()
    
    #open ai se kiya hua code 
    # openai.api_key = "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"

    # try:
    #     # response = openai.Completion.create(
    #     #     engine="davinci",
    #     #     prompt=stringname,
    #     #     max_tokens=1000
    #     # )
    #     response = openai.ChatCompletion.create(
    #         model="text-davinci-003",
    #         messages=[{"role":"user", "content":stringname}],
    #         max_tokens=1024,
    #         temperature=0.5
    #     )
    #     summary = response.choices[0].message.content
    #     print(summary)
    #     return summary
    # except Exception as e:
    #     print("Error:", e)
    #     return None

# Define the function to count the number of tokens.
# def count_tokens(stringname):
#     tokens = word_tokenize(stringname)
#     return len(tokens)
#     # Display the number of tokens from the top 10 news record's text content.
#     stringname = news_text_content_string

#     token_count = count_tokens(stringname)
#     print(f"Number of tokens: {token_count}")

    
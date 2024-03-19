from flask_cors import CORS, cross_origin
from flask import Flask ,render_template, request, jsonify
import requests
from fake_useragent import UserAgent
from newspaper import fulltext,Article
import itertools
from utils import generate_news, extract_categories_from_history, scrape_news
import pandas as pd
from PIL import Image
import base64
import io
from pygooglenews import GoogleNews

gn = GoogleNews(lang='en',country='IN')


app = Flask(__name__,template_folder='template')
CORS(app,supports_credentials=True)

@app.route('/history', methods = ['POST'])
def getHistoryNews():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract historyData from the JSON data
        history_data = data.get('historyData', [])

        # Extract keywords using rake-nltk
        keywords_list = extract_categories_from_history(history_data)

        # Prepare response data
        response_data = generate_news(keywords_list)

        return response_data


    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/summarize', methods=['POST'])
@cross_origin(supports_credentials=True)
def getSummarize():
    data = request.get_json()
    summary = scrape_news(data)
    response = jsonify(summary)
    return response

@app.route('/fetch', methods = ['GET'])
def get_news():
    keyword = request.args.get('preferences', '')
    # googlenews = GoogleNews(lang='en', region='US', period='1d', encode='utf-8')
    # googlenews.clear()
    # googlenews.search(keyword)
    # googlenews.get_page(2)
    # news_result = googlenews.result(sort=True)
    # # print(news_result)
    # news_data_df = pd.DataFrame.from_dict(news_result)

    # ua = UserAgent()
    # news_data_list = []

    # for index,headers in itertools.islice(news_data_df.iterrows(), 4):
    #     news_title = str(headers['title'])
    #     news_media = str(headers['media'])
    #     news_description = str(headers['desc'])
    #     news_link = str(headers['link'])
    #     news_data = Article(news_link)
    #     try:
    #         news_data.download()
    #         news_data.parse()
    #         print(news_data.top_image)
    #     except:
    #         print("error")
    #     news_img = fetch_news_poster(news_data.top_image)

    #     img_byte_array = io.BytesIO()
    #     news_img.save(img_byte_array, format='PNG')

    #     # Convert the byte array to a base64-encoded string
    #     base64_str = base64.b64encode(img_byte_array.getvalue()).decode('utf-8')
    # news_data_list = []
    # search = gn.search(keyword, when = '1m')
    # print(search)
    # news_text = ""
    # article_count = 0
    # for entry in search["entries"]:
    #     news_link = str(entry['link'])
    #     news_title = str(entry['title'])
    #     news_media = str(entry['source']['title'])
    #     try:
    #         article = Article(news_link)
    #         article.download()
    #         article.parse()
    #         article.nlp()
    #         news_image = fetch_news_poster(article.top_image)
    #         img_byte_array = io.BytesIO()
    #         news_image.save(img_byte_array, format='PNG')

    #     # Convert the byte array to a base64-encoded string
    #         base64_str = base64.b64encode(img_byte_array.getvalue()).decode('utf-8')
    #     except Exception as e:
    #         print(e)


    #     try:
    #         # html = requests.get(news_link, headers={'User-Agent': ua.chrome}, timeout=5).text
    #         # text = fulltext(html)
    #         print('Text Content Scraped')
    #     except:
    #         print('Text Content Scraped Error, Skipped')
    #         text = None

    #     news_data_list.append({
    #         'title': news_title,
    #         'media': news_media,
    #         'description': news_title,
    #         'link': news_link,
    #         'image': base64_str
    #     })

    #     article_count = article_count+1
    #     if(article_count >= 4):
    #         break

    # # Create a JSON response
    # response_data = {
    #     'keyword': keyword,
    #     'news': news_data_list
    # }


    # return jsonify(response_data)
    # Replace 'YOUR_API_KEY' with your actual News API key
    api_key = '516a5432d67e4f3ab8e139113a353941'

    # Make a request to the News API
    url = f'https://newsapi.org/v2/everything?q={keyword}&apiKey={api_key}'
    response = requests.get(url)
    data = response.json()

    # Extract relevant information from the API response
    articles = data.get('articles', [])

    ua = UserAgent()
    news_data_list = []

    for article in itertools.islice(articles, 4):
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

    # Create a JSON response
    response_data = {
        'keyword': keyword,
        'news': news_data_list
    }
    print(response_data)
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
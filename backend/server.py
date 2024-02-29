from flask_cors import CORS, cross_origin
from flask import Flask ,render_template, request, jsonify
from GoogleNews import GoogleNews
import pandas as pd
import requests
from fake_useragent import UserAgent
import newspaper
from newspaper import fulltext
import re
import json
import itertools

app = Flask(__name__,template_folder='template')
CORS(app,supports_credentials=True)

@app.route('/fetch', methods = ['GET'])
def get_news():
    keyword = request.args.get('preferences', '')
    googlenews = GoogleNews(lang='en', region='US', period='1d', encode='utf-8')
    googlenews.clear()
    googlenews.search(keyword)
    googlenews.get_page(2)
    news_result = googlenews.result(sort=True)
    print(news_result)
    news_data_df = pd.DataFrame.from_dict(news_result)

    ua = UserAgent()
    news_data_list = []

    for index, headers in itertools.islice(news_data_df.iterrows(), 4):
        news_title = str(headers['title'])
        news_media = str(headers['media'])
        news_description = str(headers['desc'])
        news_link = str(headers['link'])
        news_img = str(headers['img'])

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

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
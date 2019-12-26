
from pathlib import Path
from flask import request, Response
from sejong.items import items
from sejong import app
import requests
import json
import datetime
from flask_cors import CORS

cors = CORS(app, resources={
  r"/db/*": {"origin": "*"},
  r"/api/*": {"origin": "*"},
})

def myconverter(o):
    if isinstance(o, datetime.date):
        return o.__str__()
    elif isinstance(o, datetime.timedelta):
        return o.__str__()

@app.route("/")
def main():
    return "hello world 2"

@app.route("/book/isbn", methods=['GET'])
def get_book_info():
    response = {
        'success': True,
        'data' : {},
    }

    if request.method == 'GET':
        data = request
        isbn = data.args.get('isbn')

        url = "https://openapi.naver.com/v1/search/book_adv"
        params = {'d_isbn': isbn, 'display': '100'}
        header = {'X-Naver-Client-Id': 'Lv5kVN8rjERQA76WMpen',
                'X-Naver-Client-Secret': 'EloLcTPux5'}
        book_response = requests.get(url, params=params, headers=header)
        data = json.loads(book_response.text)
        item = data['items'][0]

        response['data'] = item
        response['success'] = True
        return Response(json.dumps(response, indent=4, default=myconverter), mimetype='application/json')

@app.route("/items", methods=['POST', 'GET'])
def get_items():
    response = {
            'success': True,
            'data' : {},
    }

    if request.method == 'POST':
        data = request

        # item_info = {
        #     'author_id' : data.args.get('author_id'),
        #     'title' : data.args.get('title'),
        #     'price' : data.args.get('price'),
        #     'image' : data.args.get('image'),
        #     'description' : data.args.get('description'),
        #     'trade_type' : data.args.get('trade_type'),
        #     'category' : data.args.get('category'),
        #     'pub_date' : data.args.get('pub_date'),
        # }

        item_info = data.form("photo")

        print(item_info)
        # item = items.Item()
        # item.assgin_trade(item_info)
        response['data'] = item_info
        response['success'] = True
        return Response(json.dumps(response, indent=4, default=myconverter), mimetype='application/json')


    if request.method == 'GET':
        
        item = items.Item()
        response['data'] = item.show_trade()
        print(response['data'])
        response['success'] = True
        return Response(json.dumps(response, indent=4, default=myconverter), mimetype='application/json')

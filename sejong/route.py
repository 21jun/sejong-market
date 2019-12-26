
from pathlib import Path
from flask import request, Response
from sejong import app
import requests
import json
import datetime

def myconverter(o):
    if isinstance(o, datetime.date):
        return o.__str__()
    elif isinstance(o, datetime.timedelta):
        return o.__str__()

@app.route("/")
def main():
    return "hello world 2"

@app.route("/book/isbn", methods=['GET'])
def get_book_info(isbn):

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

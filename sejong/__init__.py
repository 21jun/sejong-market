from flask import Flask

app = Flask(__name__)

# app.config.from_object('config.BasicConfig')

# print(app.config)

from sejong import route
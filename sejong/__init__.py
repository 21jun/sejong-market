from flask import Flask

app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='1qazxc'

app.config['MYSQL_DATABASE_DB'] ='market'

from sejong import route
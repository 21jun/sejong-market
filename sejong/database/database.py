from flaskext.mysql import MySQL
from monthly import app

class DataBase:

    def __init__(self):
        self.mysql = MySQL(app=app)
        self.mysql.init_app(app)
        # print(self.mysql.app.config)
        self.conn = self.mysql.connect()
        self.cur = self.conn.cursor()
    
    
    def __call__(self):
        pass
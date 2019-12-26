from sejong.database import database


class Trade:

    def __init__(self):
        self.db = database.DataBase()


class Item:

    def __init__(self):
        self.db = database.DataBase()

        self.author_id = None
        self.title = None
        self.price = None
        self.image = None
        self.description = None
        self.trade_type = None
        self.category = None
        self.pub_date = None
        self.name = None

    def load_item(self, item_info):
        self.author_id = item_info['author_id']
        self.title = item_info['title']
        self.price = item_info['price']
        self.image = item_info['image']
        self.description = item_info['description']
        self.trade_type = item_info['trade_type']
        self.category = item_info['category']
        self.pub_date = item_info['pub_date']
        self.name = item_info['name']

    def save_item(self):
        SQL = """INSERT INTO item VALUES(NULL, {author_id}, '{title}', {price}, '{image}', '{description}','{trade_type}', '{category}', '{pub_date}', '{name}');"""
        # print(SQL.format(author_id=self.author_id, title=self.title, price=int(self.price), image=self.image, description=self.description, trade_type=self.trade_type, category=self.category, pub_date=self.pub_date))
        self.db.cur.execute(SQL.format(author_id=self.author_id, title=self.title, price=int(self.price), image=self.image, description=self.description, trade_type=self.trade_type, category=self.category, pub_date=self.pub_date, name =self.name))

        self.db.conn.commit()
        
    def assgin_trade(self, item_info):
        # print(item_info)
        self.load_item(item_info)
        self.save_item()

    def show_trade(self):
        SQL = """SELECT * FROM item;"""
        self.db.cur.execute(SQL)
        data = self.db.cur.fetchall()
        
        return data

    def get_single_item(self, item_num):
        SQL= "SELECT * FROM item where id='{item_num}'"
        self.db.cur.execute(SQL.format(item_num=item_num))
        data = self.db.cur.fetchall()

        return data
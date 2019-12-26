from pathlib import Path
from monthly.codef.connectedId import ConnectedID
from monthly.codef.codef import get_client_key, get_public_key
from monthly.codef.token import Token
from monthly.database.database import DataBase


class Auth:
    
    def __init__(self):
        self.client_id, self.client_secret = get_client_key()
        self.public_key = get_public_key()
        self.token = Token(self.client_secret, self.client_secret, issue_token=False)

        self.db = DataBase()
        self.user_id = None
        self.user_data = None

    def regist(self, id, pw, name, simple, gender, birthday, phone, region, job):
        # id 중복검사
        SQL = "select EXISTS (select * from user where auth_id='{id}') as success;"
        self.db.cur.execute(SQL.format(id=str(id)))
        data = self.db.cur.fetchall()
   
        if data[0][0] == 1:
            print("이미 등록된 사용자")
            return False
        
        SQL = "INSERT INTO user VALUES (NULL, '{auth_id}', '{auth_pw}', '{auth_simple}', '{user_name}', '{birthday}', '{gender}', '{phone}', '{region}', '{job}',TIMESTAMP(NOW()), NULL);"
        self.db.cur.execute(SQL.format(auth_id=id, auth_pw=pw, auth_simple=simple, user_name=name, gender=gender, birthday=birthday, phone=phone, region=region, job=job))
        self.db.conn.commit()
        return True


    def login(self, id, pw):
        SQL = "SELECT * FROM user where auth_id = '{id}' and auth_password = '{pw}';"
        # print(SQL.format(id=str(id), pw=str(pw)))
        self.db.cur.execute(SQL.format(id=str(id), pw=str(pw)))
        data = self.db.cur.fetchall()

        # 회원 정보 없음
        if data == ():
            return False

        user_data = {}
        user_data['user_id']        = data[0][0]
        user_data['auth_id']        = data[0][1]
        user_data['auth_password']  = data[0][2]
        user_data['auth_simple']    = data[0][3]
        user_data['name']           = data[0][4]
        user_data['birthday']       = data[0][5]
        user_data['gender']         = data[0][6]
        user_data['phone']          = data[0][7]
        user_data['region']         = data[0][8]
        user_data['job']            = data[0][9]
        user_data['timestamp']      = data[0][10]
        user_data['connectedID']    = data[0][11]

        self.user_data = user_data
        return True
        
    def login_simple(self, user_id, simple):
        SQL = "SELECT * FROM user where user_id = '{user_id}' and auth_simple = '{simple}';"
        self.db.cur.execute(SQL.format(user_id=str(user_id), simple=str(simple)))
        data = self.db.cur.fetchall()

        # 회원 정보 없음
        if data == ():
            return False

        user_data = {}
        user_data['user_id']        = data[0][0]
        user_data['auth_id']        = data[0][1]
        user_data['auth_password']  = data[0][2]
        user_data['auth_simple']    = data[0][3]
        user_data['name']           = data[0][4]
        user_data['birthday']       = data[0][5]
        user_data['gender']         = data[0][6]
        user_data['phone']          = data[0][7]
        user_data['region']         = data[0][8]
        user_data['job']            = data[0][9]
        user_data['timestamp']      = data[0][10]
        user_data['connectedID']    = data[0][11]

        self.user_data = user_data
        return True

        
    def logout(self):
        pass
    
    def create_connected_id(self, account_list_json):
        pass
        # self.con_id.create_accounts(account_list_json)

    def add_connected_id(self):
        pass
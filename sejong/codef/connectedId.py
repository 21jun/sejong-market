import monthly.codef.codef as codef
import requests
import json
import urllib
from pathlib import Path
from monthly.codef.codef import get_client_key, get_public_key
from monthly.codef.token import Token
from monthly.database.database import DataBase

class Account:

    def __init__(self, name, account_info):
        self.account_info = account_info
        self.account_info['name'] = name
    
    def __getitem__(self, key):
        return self.__dict__['account_info'][key]


class AccountList:

    def __init__(self, account_list_json : str):
        self.account_list_json = account_list_json
        self.user_name = self.account_list_json['name']
        
        self.num_accounts = len(self.account_list_json['accountList'])
        self.accounts = []
        for account_info in self.account_list_json['accountList']:
            self.accounts.append(Account(self.user_name, account_info))
        
    def __getitem__(self, i):
        return self.accounts[i]

    def __iter__(self):
        for i in range(0, self.num_accounts, 1):
            yield self.accounts[i]


class OrganizationAccountList:

    def __init__(self, organization_account_list_json : str):
        self.organization_account_list_json = json.loads(organization_account_list_json)
        self.accounts = []
        for account_info in self.organization_account_list_json['data']['resDepositTrust']:
            self.accounts.append(account_info)
        self.num_accounts = len(self.organization_account_list_json['data']['resDepositTrust'])

    def __getitem__(self, i):
        return self.accounts[i]

    def get_balance(self):
        balances = []
        for account in self.accounts:
            balances.append(account['resAccountDisplay'], account['resAccountBalance'])
        return balances


class ConnectedID:

    def __init__(self, user_id):
        # init params
        self.account_create_url = 'https://api.codef.io/v1/account/create'
        self.account_add_url = 'https://api.codef.io/v1/account/add'
        self.account_delete_url = 'https://api.codef.io/v1/account/delete'
        self.account_list_url = 'https://api.codef.io/v1/account/list'
        self.account_organization_list = 'https://development.codef.io/v1/kr/bank/p/account/account-list'
        self.transaction_list_url = 'https://development.codef.io/v1/kr/bank/p/account/transaction-list'
        self.user_id = user_id
        self.db = DataBase()

        self.connected_id = self._load_connected_id()

        self.client_id, self.client_secret = get_client_key()
        self.public_key = get_public_key()
        self.token = Token(self.client_secret, self.client_secret, issue_token=False).token

        
    def _load_connected_id(self):
        """
        connectedID DB에서 가져옴
        """
        SQL = "SELECT connectedID FROM user WHERE user_id = '{user_id}';"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()

        if data[0][0] is None:
            print("No ConnectedID")
            return None
        else:
            return data[0][0]
        

    def _save_connected_id(self):
        """
        connectedID DB에 저장
        """
        if self.connected_id is None:
            return False

        SQL = "UPDATE user SET connectedID = '{connected_id}' WHERE user_id = '{user_id}'"
        self.db.cur.execute(SQL.format(connected_id=self.connected_id,user_id=self.user_id))
        self.db.conn.commit()


    def create_connected_id(self, account_list_json):
        """
        connectedID 발급 (신규 유저)

        params:
        accountList : 계정목록
        countryCode : 국가코드
        businessType : 비즈니스 구분
        clientType : 고객구분(P: 개인, B: 기업)
        organization : 기관코드
        loginType : 로그인타입 (0: 인증서, 1: ID/PW)
        password : 인증서 비밀번호
        derFile : 인증서 derFile
        keyFile : 인증서 keyFile
        """
        accountList = []
        for account in AccountList(account_list_json):
            accountList.append(
                {
                    'countryCode': account['countryCode'],
                    'businessType':account['businessType'],
                    'clientType':account['clientType'],
                    'organization':account['organization'],
                    'loginType':account['loginType'],
                    'password':codef.publicEncRSA(self.public_key, account['password']),
                    'id': account['id'],
                    'birthday':account['birthday'],
                }
            )

        account_create_body = {
            'accountList': accountList
        }

        response_account_create = codef.http_sender(self.account_create_url, self.token, account_create_body)
        print(urllib.parse.unquote_plus(response_account_create.text))

        if response_account_create.status_code == 200:      # success

            dict = json.loads(urllib.parse.unquote_plus(response_account_create.text))
            if 'data' in dict and str(dict['data']) != '{}':
                data = dict['data']
                if 'connectedId' in data:
                    self.connected_id = data['connectedId']
                    print('connected_id = ' + self.connected_id)
                    
                    if dict['result']['code'] == 'CF-04004':    
                        print('이미 등록된 계정입니다.')
                    else:   
                        print('계정생성 정상처리')
            else:
                print(urllib.parse.unquote_plus(response_account_create.text))
                print('계정생성 오류')

        elif response_account_create.status_code == 401:    # token error
            print('token error')

        # 발급받은 connected_id 저장
        self._save_connected_id()

    def account_add(self, account_list_json):
        
        accountList = []
        for account in AccountList(account_list_json):
            accountList.append(
                {
                    'countryCode': account['countryCode'],
                    'businessType':account['businessType'],
                    'clientType':account['clientType'],
                    'organization':account['organization'],
                    'loginType':account['loginType'],
                    'password':codef.publicEncRSA(self.public_key, account['password']),
                    'id': account['id'],
                    'birthday':account['birthday'],
                }
            )

        account_add_body = {
            'connectedId': self.connected_id,
            'accountList': accountList
        }

        response_account_add = codef.http_sender(self.account_add_url, self.token, account_add_body)
        # print(urllib.parse.unquote_plus(response_account_create.text))

    def account_delete(self, account_list_json):
        accountList = []
        for account in AccountList(account_list_json):
            accountList.append(
                {
                    'countryCode': account['countryCode'],
                    'businessType':account['businessType'],
                    'clientType':account['clientType'],
                    'organization':account['organization'],
                    'loginType':account['loginType'],
                    'password':codef.publicEncRSA(self.public_key, account['password']),
                    'id': account['id'],
                    'birthday':account['birthday'],
                }
            )

        account_delete_body = {
            'connectedId': self.connected_id,
            'accountList': accountList
        }

        response_account_delete = codef.http_sender(self.account_delete_url, self.token, account_delete_body)

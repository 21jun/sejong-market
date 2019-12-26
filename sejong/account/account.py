from monthly.codef.connectedId import OrganizationAccountList
from monthly.codef.connectedId import ConnectedID
from monthly.codef.codef import get_client_key, get_public_key
from monthly.codef.token import Token
from monthly.database.database import DataBase
from datetime import date, timedelta, datetime
import monthly.codef.codef as codef
import requests
import json
import urllib


class BankAccount:

    def __init__(self, user_id):
        '''
        유저의 등록된 은행계좌(bank_accounts)를 가져온다.
        '''
        self.user_id = user_id
        self.con_id = ConnectedID(user_id)
        self.db = DataBase()
        self.bank_account_list_url = 'https://api.codef.io/v1/account/list'
        self.bank_accounts = self._load_bank_account()

    def _load_bank_account(self):
        SQL = "SELECT * FROM bank_accounts WHERE user_id ='{user_id}';"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()
        response = {}
        account_list = []
        for account in data:
            account_dict = {}
            account_dict['organization_code'] = account[2]
            account_dict['business_type'] = account[3]
            account_dict['login_type'] = account[4]
            account_list.append(account_dict)
        response['user_id'] = self.user_id
        response['account_list'] = account_list

        return response

    def _save_bank_account(self, organization_code, business_type, login_type):
        """
        BankAccount 정보를 DB에 저장
        """

        # 데이터 삽입
        # REPLACE INTO:
        # https://til.songyunseop.com/mysql/some_case_insert_with_duplicated_key.html
        SQL = "INSERT IGNORE INTO bank_accounts VALUES(NULL, '{user_id}', '{organization_code}', '{business_type}', '{login_type}')"
        self.db.cur.execute(SQL.format(user_id=self.user_id, organization_code = organization_code, business_type = business_type, login_type= login_type))
        self.db.conn.commit()

    def update_bank_account_list(self):
        if self.con_id.connected_id is None:
            print(self.user_id," 유저의 ConnectedID 가 없음")
            return False

        bank_account_list_body = {
            'connectedId':self.con_id.connected_id
        }

        bank_account_list = codef.http_sender(self.bank_account_list_url, self.con_id.token, bank_account_list_body)
        bank_account_list = json.loads(urllib.parse.unquote_plus(bank_account_list.text))

        print(bank_account_list)
        for bank_account in bank_account_list['data']['accountList']:
            organization_code = bank_account['organizationCode']
            business_type = bank_account['businessType']
            login_type = bank_account['loginType']
            self._save_bank_account(organization_code, business_type, login_type)

        self.bank_accounts = self._load_bank_account()


class AccountDeposit:

    def __init__(self, user_id):
        self.user_id = user_id
        self.con_id = ConnectedID(user_id)
        self.db = DataBase()
        self.account_url = 'https://development.codef.io/v1/kr/bank/p/account/account-list'
        
        self.accounts = self._load_account()

    def _load_account(self):
        SQL = "SELECT * FROM account_deposit WHERE user_id = '{user_id}'"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        result = self.db.cur.fetchall()
        
        if result == ():
            return None

        response = {}
        deposit_list = []
        for deposit in result:
            deposit_dict = {}
            deposit_dict['account_num'] = deposit[1]
            deposit_dict['account_num_display'] = deposit[2]
            deposit_dict['account_name'] = deposit[3]
            deposit_dict['organization_code'] = deposit[4]
            deposit_dict['account_deposit_type'] = deposit[5]
            deposit_dict['account_balance'] = deposit[7]
            deposit_list.append(deposit_dict)

        response['user_id'] = self.user_id
        response['deposit_list'] = deposit_list
        return response


    def _save_account(self, account_num, account_num_display, accout_name, organization_code, account_deposit_type, account_balance):

        # 데이터 삽입 (account_password는 NULL 처리, 추후 거래내역 조회에서 입력받아야 할 듯)
        # REPLACE INTO:
        # https://til.songyunseop.com/mysql/some_case_insert_with_duplicated_key.html
        SQL = "REPLACE INTO account_deposit VALUES('{user_id}', '{account_num}', '{account_num_display}', '{accout_name}', '{organization_code}', '{account_deposit_type}', NULL, '{account_balance}')"
        self.db.cur.execute(SQL.format(user_id=self.user_id, account_num = account_num, account_num_display = account_num_display, accout_name= accout_name, organization_code=organization_code, account_deposit_type= account_deposit_type,account_balance= account_balance))
        self.db.conn.commit()


    def update_account_list(self, organization_code):
        """
        사용자의 계좌 정보를 업데이트한다.
        """

        

        account_list_body = {
            'connectedId': self.con_id.connected_id,
            'organization': organization_code
        }

        account_list = codef.http_sender(self.account_url, self.con_id.token, account_list_body)
        account_list = json.loads(urllib.parse.unquote_plus(account_list.text))

        print(account_list)

        if account_list['data'] == {}:
            print("이 유저는 해당 기관의 계좌가 없음")
            return False
        
        for account in account_list['data']['resDepositTrust']:
            account_num = account['resAccount']
            account_num_display = account['resAccountDisplay']
            accout_name = account['resAccountName']
            organization_code = organization_code
            account_deposit_type = account['resAccountDeposit']
            account_balance = account['resAccountBalance']
            self._save_account(account_num, account_num_display, accout_name, organization_code, account_deposit_type, account_balance)

        self.accounts = self._load_account()

        return True

class Transaction:
    def __init__(self, user_id, date_from, date_to):
        self.db = DataBase()
        self.user_id = user_id
        self.date_from, self.date_to = date_from, date_to # 반환할 거래내역 기간
        self.con_id = ConnectedID(user_id)
        self.bank_account = BankAccount(self.user_id)
        self.account_deposit = AccountDeposit(self.user_id)
        self.transaction_list_url = 'https://development.codef.io/v1/kr/bank/p/account/transaction-list'

        if date_from:
            self.transactions = self._load_transaction()
        else:
            self.transactions = None

        SQL = "SELECT MAX(tran_date) from transaction_deposit WHERE user_id ='{user_id}';"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()

        if data[0][0] == None: # 저장된 transaction이 없는 경우  
            six_month_ago = date.today() - timedelta(days=180)
            six_month_ago = six_month_ago.strftime('%Y%m%d')
            self.start_date = str(six_month_ago)
        else:
            last_date = str(data[0][0])
            self.start_date = str(last_date[0:4]+last_date[5:7]+last_date[8:])
        self.end_date = str(datetime.today().strftime("%Y%m%d"))

    def _load_transaction(self):
        SQL = "SELECT * FROM transaction_deposit where user_id = '{user_id}' AND DATEDIFF(tran_date, '{date_from}') >= 0 and DATEDIFF(tran_date, '{date_to}') <= 0 ORDER BY tran_date desc, tran_time desc;"
        self.db.cur.execute(SQL.format(user_id=self.user_id, date_from = self.date_from, date_to=self.date_to ))
        result = self.db.cur.fetchall()
        
        if result == ():
            return None
        
        response = {}
        transaction_list = []
        for transaction in result:
            transaction_dict = {}
            transaction_dict['organization_code'] = transaction[2]
            transaction_dict['account_num'] = transaction[3]
            transaction_dict['tran_date'] = transaction[4]
            transaction_dict['tran_time'] = transaction[5]
            transaction_dict['tran_in'] = transaction[6]
            transaction_dict['tran_out'] = transaction[7]
            transaction_dict['tran_after_balance'] = transaction[8]
            transaction_dict['tran_desc2'] = transaction[10]
            transaction_dict['tran_desc3'] = transaction[11]
            transaction_dict['tran_desc4'] = transaction[12]
            transaction_list.append(transaction_dict)
        response['user_id'] = self.user_id
        response['transaction_list'] = transaction_list
        return response

    def _save_transaction(self, account_num, organization_code, tran_date, tran_time, tran_in, tran_out, tran_after_balance, resAccountDesc1, resAccountDesc2, resAccountDesc3, resAccountDesc4):
        SQL = '''
            INSERT IGNORE INTO transaction_deposit(
                `tran_id`,
                `user_id`,
                `account_num`,
                `organization_code`,
                `tran_date`,
                `tran_time`,
                `tran_in`,
                `tran_out`,
                `tran_after_balance`,
                `tran_desc1`,
                `tran_desc2`,
                `tran_desc3`,
                `tran_desc4`
            )
            VALUES(
                NULL, 
                '{user_id}',
                '{account_num}', 
                '{organization_code}', 
                '{tran_date}', 
                '{tran_time}', 
                '{tran_in}', 
                '{tran_out}', 
                '{tran_after_balance}', 
                '{resAccountDesc1}', 
                '{resAccountDesc2}', 
                '{resAccountDesc3}', 
                '{resAccountDesc4}'
                )
        '''
        self.db.cur.execute(SQL.format(user_id=self.user_id, account_num = account_num, organization_code = organization_code, tran_date = tran_date, tran_time= tran_time, tran_in=tran_in, tran_out= tran_out,tran_after_balance= tran_after_balance, resAccountDesc1=resAccountDesc1, resAccountDesc2=resAccountDesc2, resAccountDesc3=resAccountDesc3, resAccountDesc4=resAccountDesc4))
        self.db.conn.commit()

    def _get_max_date_time(self, account_num):
        SQL = "SELECT MAX(tran_time), tran_date FROM transaction_deposit WHERE tran_date = (SELECT MAX(tran_date) FROM transaction_deposit) and user_id='{user_id}' and account_num='{account_num}';"
        self.db.cur.execute(SQL.format(user_id = self.user_id, account_num = account_num))
        data = self.db.cur.fetchall()
        time = str(data[0][0])
        date = str(data[0][1])

        return date, time

    def update_transaction_list(self):
        SQL = "SELECT * FROM account_deposit WHERE user_id ='{user_id}';"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()

        account_list = []
        for i in range(len(data)):
            if data[i][5] == '11':
                account_list.append([data[i][1], data[i][4]])    

        # account_list 예시 [['0400', '47940104308639'], ['0400', '47940304141038']]
        for res_account, organization in account_list:
            transaction_list_body = {
                'connectedId': self.con_id.connected_id,
                'organization': organization,
                'account': res_account,
                'startDate': str(self.start_date),
                'endDate': str(self.end_date),
                'orderBy': '1',
                'inquiryType': '1',
                'accountPass': ''
                }
            # print(self.con_id.connected_id)
            response_transaction = codef.http_sender(self.transaction_list_url, self.con_id.token, transaction_list_body)
            response_transaction = json.loads(urllib.parse.unquote_plus(response_transaction.text))
            
            # print(response_transaction)
            # print(self.start_date)
            # print(self.end_date)

            max_date, max_time = self._get_max_date_time(res_account)
            max_date = max_date.replace('-', '')
            max_time = max_time.replace(':', '')
            
            for transaction in response_transaction['data']['resTrHistoryList']:
                account_num = res_account
                organization_code = organization
                tran_date = transaction['resAccountTrDate']
                tran_time = transaction['resAccountTrTime']
                tran_in = transaction['resAccountIn']
                tran_out = transaction['resAccountOut']
                tran_after_balance = transaction['resAfterTranBalance']
                resAccountDesc1 = transaction['resAccountDesc1']
                resAccountDesc2 = transaction['resAccountDesc2']
                resAccountDesc3 = transaction['resAccountDesc3']
                resAccountDesc4 = transaction['resAccountDesc4']

                if str(tran_date) == str(max_date):
                    if str(tran_time) > str(max_time):
                        self._save_transaction(account_num, organization_code, tran_date, tran_time, tran_in, tran_out, tran_after_balance, resAccountDesc1, resAccountDesc2, resAccountDesc3, resAccountDesc4)    
                else:
                    self._save_transaction(account_num, organization_code, tran_date, tran_time, tran_in, tran_out, tran_after_balance, resAccountDesc1, resAccountDesc2, resAccountDesc3, resAccountDesc4)

        self.transactions = self._load_transaction()

        return True


    def get_monthly_tran(self):
        SQL = "SELECT MONTH(tran_date), SUM(tran_out), SUM(tran_in)  FROM transaction_deposit where user_id = {user_id} group by MONTH(tran_date);"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        fetch = self.db.cur.fetchall()

        data = {}
        data['user_id'] = self.user_id
        data['tran'] = []
        for month, tran_out, tran_in in fetch:
            data['tran'].append({"month": month, "tran_out": int(tran_out), "tran_in": int(tran_in)})

        return data

    



class Installment:
    def __init__(self, user_id, date_from, date_to):
        self.db = DataBase()
        self.user_id = user_id
        self.date_from, self.date_to = date_from, date_to # 반환할 거래내역 기간
        self.con_id = ConnectedID(user_id)
        self.bank_account = BankAccount(self.user_id)
        self.account_deposit = AccountDeposit(self.user_id)
        self.transaction_list_url = 'https://development.codef.io/v1/kr/bank/p/installment-savings/transaction-list'

        self.installment_transaction = self._load_installment_transaction()

        SQL = "SELECT MAX(tran_date) from transaction_installment WHERE user_id ='{user_id}';"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()

        if data[0][0] == None: # 저장된 transaction이 없는 경우  
            six_month_ago = date.today() - timedelta(days=180)
            six_month_ago = six_month_ago.strftime('%Y%m%d')
            self.start_date = str(six_month_ago)
        else:
            last_date = str(data[0][0])
            self.start_date = str(last_date[0:4]+last_date[5:7]+last_date[8:])
        self.end_date = str(datetime.today().strftime("%Y%m%d"))

    def _load_installment_transaction(self):
        SQL = "SELECT * FROM transaction_installment where user_id = '{user_id}' AND DATEDIFF(tran_date, '{date_from}') >= 0 and DATEDIFF(tran_date, '{date_to}') <= 0;"
        self.db.cur.execute(SQL.format(user_id=self.user_id, date_from = self.date_from, date_to=self.date_to ))
        result = self.db.cur.fetchall()
        
        if result == ():
            return None
        
        response = {}
        transaction_list = []
        for transaction in result:
            transaction_dict = {}
            transaction_dict['account_num'] = transaction[2]
            transaction_dict['tran_date'] = transaction[3]
            transaction_dict['tran_time'] = transaction[4]
            transaction_dict['tran_monthly_payment'] = transaction[5]
            transaction_dict['tran_balance'] = transaction[6]
            transaction_dict['tran_round_no'] = transaction[7]
            transaction_dict['tran_in'] = transaction[8]
            transaction_dict['tran_desc1'] = transaction[9]
            transaction_dict['tran_desc2'] = transaction[10]
            transaction_dict['tran_desc3'] = transaction[11]
            transaction_dict['tran_desc4'] = transaction[12]
            transaction_list.append(transaction_dict)
        response['user_id'] = self.user_id
        response['installment_transaction_list'] = transaction_list
        return response

    def _save_installment_transaction(self, account_num, tran_date, tran_balance, tran_round_no, tran_in, tran_desc1, tran_desc2, tran_desc3, tran_desc4):
        SQL = '''INSERT IGNORE INTO transaction_installment
            VALUES(
                NULL, 
                '{user_id}', 
                '{account_num}', 
                '{tran_date}', 
                NULL,
                NULL, 
                '{tran_balance}', 
                '{tran_round_no}', 
                '{tran_in}', 
                '{tran_desc1}', 
                '{tran_desc2}', 
                '{tran_desc3}', 
                '{tran_desc4}'
                )
        '''
        self.db.cur.execute(SQL.format(user_id=self.user_id, account_num = account_num, tran_date = tran_date, tran_balance = tran_balance, tran_round_no = tran_round_no, tran_in = tran_in, tran_desc1 = tran_desc1, tran_desc2 = tran_desc2, tran_desc3 = tran_desc3, tran_desc4 = tran_desc4))
        self.db.conn.commit()

    def _save_installment(self, account_num, account_num_display, account_name, organization_code, account_start_date, account_deposit_type, account_balance, account_valid_period, account_rate):
        SQL = '''INSERT IGNORE INTO account_installment VALUES('{user_id}', '{account_num}', '{account_num_display}', '{account_name}', '{organization_code}', '{account_start_date}','{account_deposit_type}', NULL,'{account_balance}', NULL,'{account_valid_period}', '{account_rate}', NULL, NULL)'''
        self.db.cur.execute(SQL.format(user_id=self.user_id, account_num = account_num, account_num_display = account_num_display, account_name = account_name, organization_code = organization_code, account_start_date = account_start_date, account_deposit_type = account_deposit_type, account_balance = account_balance, account_valid_period = account_valid_period, account_rate = account_rate))
        self.db.conn.commit()

    def update_installment_transaction_list(self):
        SQL = "SELECT * FROM account_deposit WHERE user_id ='{user_id}';"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()

        account_list = []
        for i in range(len(data)):
            if data[i][5] == '12' or data[i][5] == '14':
                account_list.append([data[i][1], data[i][4]])    

        # account_list 예시 [['0400', '47940104308639'], ['0400', '47940304141038']]
        for res_account, organization in account_list:
            installment_transaction_list_body = {
                'connectedId': self.con_id.connected_id,
                'organization': organization,
                'account': res_account,
                'startDate': str(self.start_date),
                'endDate': str(self.end_date),
                'orderBy': '1',
                'inquiryType': '1'
                }
            
            response_installment_transaction = codef.http_sender(self.transaction_list_url, self.con_id.token, installment_transaction_list_body)
            response_installment_transaction = json.loads(urllib.parse.unquote_plus(response_installment_transaction.text))
            
            print(response_installment_transaction)

            print(self.start_date)
            print(self.end_date)

            # update installment list
            SQL = "SELECT * FROM account_installment WHERE user_id ='{user_id}';"
            self.db.cur.execute(SQL.format(user_id=self.user_id))
            data = self.db.cur.fetchall()

            flag = 0 # 적금 저장되어있나 확인
            for i in range(len(data)):
                if data[i][1] == res_account:
                    flag = 1

            if flag == 0:
                account_num = res_account
                account_num_display = response_installment_transaction['data']['resAccountDisplay']
                account_name = response_installment_transaction['data']['resAccountName']
                organization_code = organization
                account_start_date = response_installment_transaction['data']['resAccountStartDate']
                account_deposit_type = response_installment_transaction['data']['resPaymentMethods']
                account_balance = response_installment_transaction['data']['resAccountBalance']
                account_valid_period = response_installment_transaction['data']['resValidPeriod']
                account_rate = response_installment_transaction['data']['resRate']

                self._save_installment(account_num, account_num_display, account_name, organization_code, account_start_date, account_deposit_type, account_balance, account_valid_period, account_rate)
            
            # update transaction
            for transaction in response_installment_transaction['data']['resTrHistoryList']:
                account_num = res_account
                tran_round_no = transaction['resRoundNo']
                tran_date = transaction['resAccountTrDate']
                tran_in = transaction['resAccountIn']
                tran_desc1 = transaction['resAccountDesc1']
                tran_desc2 = transaction['resAccountDesc2']
                tran_desc3 = transaction['resAccountDesc3']
                tran_desc4 = transaction['resAccountDesc4']
                tran_balance = transaction['resAfterTranBalance']

                self._save_installment_transaction(account_num, tran_date, tran_balance, tran_round_no, tran_in, tran_desc1, tran_desc2, tran_desc3, tran_desc4)

        self.transactions = self._load_installment_transaction()

        return True
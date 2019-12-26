from monthly.database.database import DataBase
import monthly.codef.codef as codef
import requests
import json
import urllib

class Subscription:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = DataBase()
        self.subscriptions = self._load_subscription()

    def _load_subscription(self):
        SQL = "SELECT *, DAY(sub_date) as payday FROM user_subscription WHERE user_id = '{user_id}'"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        result = self.db.cur.fetchall()

        if result == ():
            return None
        
        response = {}
        subscription_list = []
        for subscription in result:

            print(subscription)

            subscription_dict = {}
            subscription_dict['sub_id'] = subscription[2]
            subscription_dict['sub_name'] = subscription[3]
            subscription_dict['sub_date'] = subscription[4]
            subscription_dict['sub_price'] = subscription[5]
            subscription_dict['account_num'] = subscription[6]
            subscription_dict['organization_code'] = subscription[7]
            subscription_dict['icon'] = subscription[8]
            subscription_dict['pay_day'] = subscription[9]
            subscription_list.append(subscription_dict)
        response['user_id'] = self.user_id
        response['subscription_list'] = subscription_list

        return response

    def _save_user_subscription(self, sub_id, sub_name, sub_date, sub_price, account_num, organization_code, icon):
        SQL = "INSERT IGNORE INTO user_subscription VALUES(NULL, '{user_id}', '{sub_id}', '{sub_name}', '{sub_date}', '{sub_price}', '{account_num}', '{organization_code}', '{icon}')"
        self.db.cur.execute(SQL.format(user_id=self.user_id, sub_id = sub_id, sub_name = sub_name, sub_date = sub_date, sub_price= sub_price, account_num = account_num, organization_code = organization_code, icon=icon))
        self.db.conn.commit()

    def track_subscription(self):
        SQL = "SELECT subscription.sub_id, subscription.name, transaction_deposit.tran_date, transaction_deposit.tran_out, transaction_deposit.account_num, transaction_deposit.organization_code, subscription.icon FROM transaction_deposit, subscription WHERE user_id='{user_id}' AND transaction_deposit.tran_desc3 = subscription.name;"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()

        data = list(data)
        data.sort(key = lambda x : x[2], reverse=True)

        sub_duplicate = [] # 가장 최근 거래 날짜와 금액이 저장되도록 하기 위하여 만든 리스트, 리스트에 들어있는 sub_id면 저장X
        for sub in data:
            sub_id = sub[0]
            sub_name = sub[1]
            sub_date = sub[2]
            sub_price = sub[3]
            account_num = sub[4]
            organization_code = sub[5]
            icon = sub[6]

            if sub_id not in sub_duplicate:
                sub_duplicate.append(sub_id)
                self._save_user_subscription(sub_id, sub_name, sub_date, sub_price, account_num, organization_code, icon)

        self.subscriptions = self._load_subscription()
        return True

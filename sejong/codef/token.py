import monthly.codef.codef as codef
import requests
import json
from pathlib import Path

from monthly import app

class Token:
    def __init__(self, client_id, client_secret, issue_token = False, token_path="./res/TOKEN"):
        # init params
        self.url = "https://oauth.codef.io/oauth/token"
        self.client_id, self.client_secret = client_id, client_secret
        self.token = None
        self.path = Path(token_path)

        if issue_token:
            self._get_new_token()
        else:
            # load token from TOKEN file
            self._load_token()

        
    # TODO: 토큰 저장/불러오기 DB로 하자.
    def _load_token(self):
        self.token = app.config['TOKEN']

    def _save_token(self):
        pass

    def _request_token(self, url, client_id, client_secret):
        authHeader = codef.stringToBase64(client_id + ":" + client_secret).decode(
            "utf-8"
        )

        headers = {
            "Acceppt": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + authHeader,
        }

        response = requests.post(
            url, headers=headers, data="grant_type=client_credentials&scope=read"
        )

        return response

    def _get_new_token(self):
        response_oauth = self._request_token(
            self.url, self.client_id, self.client_secret
        )
        if response_oauth.status_code == 200:
            dict = json.loads(response_oauth.text)
            self.token = dict["access_token"]
            print("access_token = " + self.token)
            print("new token issued")
            self._save_token()
        else:
            print("token issue error!!!")

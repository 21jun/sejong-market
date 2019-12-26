from monthly.codef.token import Token
from monthly.codef.connectedId import ConnectedID
from monthly.codef.codef import get_client_key, get_public_key
from pathlib import Path
import json

CLIENT_ID, CLIENT_SECRET = get_client_key()
PUBKEY = get_public_key()

t = Token(CLIENT_ID, CLIENT_SECRET, issue_token=True)

print(t.token)
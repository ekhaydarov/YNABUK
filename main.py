import json
import requests as r

from enum import Enum
from environment import TL_CLIENT, TL_SECRET

DATA_PATH = './data'


def check_connection(f):
    def wrapper(*args):
        try:
            print(f'querying {f.__name__}')
            return f(*args)
        except Exception as e:
            print(str(e))
            args[0].renew_access_token()
        return f(*args)
    return wrapper


class TruelayerAPI:

    class URI(Enum):
        DOMAIN = 'https://api.truelayer.com'
        AUTH = 'connect/token'
        DATA = 'data/v1'
        DATA_API = f'{DOMAIN}/{DATA}'
        META = 'me'
        ACCOUNTS = 'accounts'
        CARDS = 'cards'

        def __str__(self):
            return str(self.value)

    @property
    def creds_file(self):
        # raise RuntimeError('Please provide Credentials file obtained from truelayer')
        return 'santander.json'

    def creds(self):
        self.creds_path = f'{DATA_PATH}/{self.creds_file}'

        with open(self.creds_path) as f:
            return json.loads(f.read())

    def save_creds(self, creds):
        with open(self.creds_path, 'w') as f:
            f.write(json.dumps(creds))

    def access_token(self):
        self._access_token = self.creds()['access_token']
        return self._access_token

    def auth_header(self):
        return {'Authorization': f'Bearer {self.access_token()}'}

    def renew_access_token(self):
        auth_url = str(self.URI.DOMAIN).replace('api', 'auth')

        res = r.post(
            url=f'{auth_url}/{self.URI.AUTH}',
            data={
                'grant_type': 'refresh_token',
                'client_id': TL_CLIENT,
                'client_secret': TL_SECRET,
                'refresh_token': self.creds()['refresh_token']
            }
        )

        self.save_creds(res.json())
        print(f'access_token refreshed {self.access_token()}')

    @check_connection
    def access_token_metadata(self):
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.META}',
            headers=self.auth_header()
        ).json()

    @check_connection
    def list_all_cards(self):
        print()
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.CARDS}',
            headers=self.auth_header()
        ).json()

    @check_connection
    def list_all_accounts(self):
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}',
            headers=self.auth_header()
        ).json()

    @check_connection
    def account(self, account_id):
        print()
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}/{account_id}',
            headers=self.auth_header()
        ).json()

    @check_connection
    def account_balance(self, account_id):
        print()
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}/{account_id}/balance',
            headers=self.auth_header()
        ).json()

    @check_connection
    def account_txs(self, account_id):
        print()
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}/{account_id}/transactions',
            headers=self.auth_header()
        ).json()

    @check_connection
    def account_pending_txs(self, account_id):
        print()
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}/{account_id}/transactions/pending',
            headers=self.auth_header()
        ).json()

    def connect(self):
        print(self.access_token())
        self._access_token = 'new'
        print(self.access_token())


if __name__ == "__main__":
    print(TruelayerAPI().list_all_cards())

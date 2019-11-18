import json
import requests as r
from datetime import datetime
from dateutil.parser import parse
from tools.enums import BaseEnum, TimeFormats
from environment import TL_CLIENT, TL_SECRET, TL_ACCESS_CODE

DATA_PATH = './data'


def check_connection(f):
    def wrapper(*args):
        try:
            print(f'querying {f.__name__}')
            return f(*args)
        except Exception as e:
            print(f'request failed: {str(e)}')
            args[0].renew_access_token()
        return f(*args)
    return wrapper


class TruelayerAPI:

    class URI(BaseEnum):
        DOMAIN = 'https://api.truelayer.com'
        AUTH = 'connect/token'
        DATA = 'data/v1'
        DATA_API = f'{DOMAIN}/{DATA}'
        META = 'me'
        ACCOUNTS = 'accounts'
        CARDS = 'cards'

    @property
    def creds_file(self):
        raise RuntimeError('Please provide Credentials file obtained from truelayer')

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

    def auth_url(self):
        return str(self.URI.DOMAIN).replace('api', 'auth')

    def account_details(self, account):
        provider_id = account['provider']['provider_id']
        name = account['display_name']
        account_type = account['account_type']
        account_id = account['account_id']
        return provider_id, account_type, name, account_id

    def authorize(self):
        res = r.post(
            url=f'{self.auth_url()}/{self.URI.AUTH}',
            data={
                'grant_type': 'authorization_code',
                'client_id': TL_CLIENT,
                'client_secret': TL_SECRET,
                'redirect_uri': 'https://console.truelayer.com/redirect-page',
                'code': TL_ACCESS_CODE
            }
        )
        print(res.raise_for_status())
        self.save_creds(res.json())

    def renew_access_token(self):
        res = r.post(
            url=f'{self.auth_url()}/{self.URI.AUTH}',
            data={
                'grant_type': 'refresh_token',
                'client_id': TL_CLIENT,
                'client_secret': TL_SECRET,
                'refresh_token': self.creds()['refresh_token']
            }
        )

        self.save_creds(res.json())
        print(f'access_token refreshed')

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
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}/{account_id}',
            headers=self.auth_header()
        ).json()

    @check_connection
    def account_balance(self, account_id):
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}/{account_id}/balance',
            headers=self.auth_header()
        ).json()

    @check_connection
    def account_txs(self, account_id):
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}/{account_id}/transactions',
            headers=self.auth_header()
        ).json()['results']

    @check_connection
    def account_pending_txs(self, account_id):
        return r.get(
            url=f'{self.URI.DATA_API}/{self.URI.ACCOUNTS}/{account_id}/transactions/pending',
            headers=self.auth_header()
        ).json()

    def process_txs(self, txs):
        return [
            tx
            for tx in txs
            if parse(tx['timestamp']).date() == datetime.now().date()
        ]

    def todays_txs(self):
        result = {}
        accounts = self.list_all_accounts()

        if accounts['status'] != 'Succeeded':
            raise Exception(
                f'List accounts request did not succeed: {accounts["status"]}'
            )

        for account in accounts['results']:
            account_id = account['account_id']
            provider_id, account_type, name, aid = self.account_details(account)
            print(f'working on {provider_id} {account_type} {name}')

            txs = self.account_txs(account_id)

            account_name = f'{provider_id}--{aid}'
            result[account_name] = self.process_txs(txs)

        return result


class Santander(TruelayerAPI):

    @property
    def creds_file(self):
        return 'santander.json'


class Monzo(TruelayerAPI):

    @property
    def creds_file(self):
        return 'monzo.json'


class Revolut(TruelayerAPI):

    @property
    def creds_file(self):
        return 'revolut.json'


if __name__ == "__main__":
    print(TruelayerAPI().list_all_cards())

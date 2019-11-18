import requests as r

from datetime import datetime
from dateutil.parser import parse

from tools.enums import BaseEnum, TimeFormats, APIMethods
from environment import YNAB_TOKEN, BUDGET_NAME


class YNABAPI:
    def __init__(self):
        self.budget_id = self.get_budget_id()

    class YNABURI(BaseEnum):
        DOMAIN = 'https://api.youneedabudget.com/v1'
        BUDGETS = 'budgets'
        ACCOUNTS = 'budgets/{BUDGET_ID}/accounts'
        TXS = 'budgets/{BUDGET_ID}/transactions'
        PAYEES = 'budgets/{BUDGET_ID}/payees'

        budgets_list = f'{DOMAIN}/{BUDGETS}'
        accounts_list = f'{DOMAIN}/{ACCOUNTS}'
        payees_list = f'{DOMAIN}/{PAYEES}'
        insert_txs = f'{DOMAIN}/{TXS}'

    @property
    def headers(self):
        return {
            'Authorization': f'Bearer {YNAB_TOKEN}',
            'Content-Type': 'application/json'
        }

    def get_budget_id(self):
        res = self.request(APIMethods.GET, self.YNABURI.budgets_list)

        return [
            budget['id']
            for budget in res['data']['budgets']
            if budget['name'] == BUDGET_NAME
        ][0]

    def request(self, method, url, data=None):
        request = getattr(r, str(method))

        if '{BUDGET_ID}' in str(url):
            url = str(url).format(BUDGET_ID=self.budget_id)

        return request(
            url=url,
            json=data,
            headers=self.headers
        ).json()


class YNABInserter(YNABAPI):
    def __init__(self):
        super().__init__()

    @property
    def account_ids(self):
        res = self.request(APIMethods.GET, self.YNABURI.accounts_list)
        return {
            account['name']: account['id']
            for account in res['data']['accounts']
        }

    def build_tx(self, account_id, tx):
        date = (
            parse(tx['timestamp'])
            .date()
            .strftime(str(TimeFormats.DATE))
        )

        memo = (
            f"{tx['description']} | "
            f"{tx['transaction_type']} | "
            f"{tx['transaction_category']} | "
            f"{' | '.join(tx['transaction_classification'])}"
        )

        return {
            "account_id": account_id,
            "date": date,
            "amount": int(tx['amount']*1000),
            "payee_id": None,
            "payee_name": tx.get('merchant_name',[])[:50],
            "category_id": None,
            "memo": memo,
            "cleared": "uncleared",
            "approved": True,
            "flag_color": "blue",
            "import_id": tx['transaction_id']
        }

    def build_txs(self, account_name, txs):
        name = account_name.split('--')[0]
        return {
            "transactions": [
                self.build_tx(self.account_ids[name], tx)
                for tx in txs
            ]
        }

    def run(self, account_name, txs):
        txs = self.build_txs(account_name, txs)
        print(txs)

        if not txs['transactions']:
            return 'Nothing to update'

        res = self.request(
            APIMethods.POST,
            self.YNABURI.insert_txs,
            data=txs
        )
        print(res)

        if res.get('duplicate_import_ids'):
            print('duplicates', res.get('duplicate_import_ids'))

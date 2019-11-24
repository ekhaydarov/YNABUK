import click

from apis.truelayer import Santander, Monzo, Revolut
from apis.ynab import YNABInserter

BANKS = [
    Santander, Monzo, Revolut
]


@click.command()
@click.option('--days', default=0, help='number of tx days')
def import_transaction(days):

    data = [
        bank().get_txs(days)
        for bank in BANKS
    ]

    print(data)
    for bank in data:
        for account, txs in bank.items():
            print(txs)
            if txs:
                x = YNABInserter().run(account, txs)
                print(x)


if __name__ == '__main__':
    import_transaction()

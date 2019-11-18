from apis.ynab import YNABInserter, YNABAPI
from apis.truelayer import Santander, Monzo, Revolut

BANKS = [
    Santander, Monzo, Revolut
]

if __name__ == "__main__":
    data = [
        bank().todays_txs()
        for bank in BANKS
    ]

    print(data)
    for bank in data:
        for account, txs in bank.items():
            print(txs)
            if txs:
                x = YNABInserter().run(account, txs)
                print(x)

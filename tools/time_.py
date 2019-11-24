from typing import List
from datetime import date, timedelta
from tools.enums import TimeFormats


def list_of_dates(days: int) -> List[str]:
    sdate = date.today() - timedelta(days=days)
    tdelta = date.today() - sdate

    return [
        (sdate + timedelta(days=i)).strftime(str(TimeFormats.DATE))
        for i in range(tdelta.days + 1)
    ]


if __name__ == '__main__':
    print(list_of_dates(0))
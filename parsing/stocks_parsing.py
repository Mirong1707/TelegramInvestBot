import time
import tinvest as tinvest
from mytoken import token
from data_base import sqlite_db

start_time = time.time()
c = tinvest.SyncClient(token)  # для брокерского счета
usd = float(c.get_market_orderbook("BBG0013HGFT4", 1).payload.last_price)  # цена доллара из стакана, имхо

r = c.get_market_stocks()

profit = []
sales = []


async def fict():
    for p in r.payload.instruments:
        # print('||||||||||||||||||||')
        # print('figi = ', p.figi)
        await sqlite_db.check_and_add(p.name, p.figi, p.currency.name, p.ticker)

    print("--- %s seconds ---" % (time.time() - start_time))


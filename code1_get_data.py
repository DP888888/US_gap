from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import datetime


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.results = []

    def error(self, reqId, errorCode, errorString):
        if reqId == -1:
            return
        if errorCode == 162 or errorCode == 200:
            self.disconnect()

        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def historicalData(self, reqId, bar):
        d = datetime.datetime.strptime(bar.date, "%Y%m%d").strftime("%Y-%m-%d")
        self.results.append([reqId, d, bar.open, bar.high, bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId, start, end):
        self.disconnect()


def get_candles(code, span, time_frame):
    app = TestApp()
    contract = Contract()
    contract.symbol = code
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    app.connect("127.0.0.1", 7496, 0)
    app.reqHistoricalData(0, contract, "", span, time_frame, "TRADES", 1, 1, False, [])
    app.run()
    results = pd.DataFrame(app.results, columns=['id', '交易日期', '开盘价', '最高价', '最低价', '收盘价', '成交量'])
    results = results[['交易日期', '开盘价', '最高价', '最低价', '收盘价', '成交量']]
    return results


if __name__ == "__main__":
    codes = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 'FB', 'NVDA', 'BRK A', 'TSM', 'TCEHY', 'JPM', 'V', 'UNH', 'HD', 'JNJ', 'LVMUY', 'WMT', 'BABA', 'PG', 'BAC', 'NSRGY', 'RHHBY', 'MA', 'ASML', 'ADBE', 'PFE', 'NFLX', 'DIS', 'NKE', 'XOM', 'CRM', 'TM', 'NVO', 'TMO', 'ORCL', 'CSCO', 'AVGO', 'KO', 'COST', 'ACN', 'ABT', 'LLY', 'PEP', 'CVX', 'CMCSA', 'PYPL', 'DHR', 'INTC', 'ABBV', 'VZ', 'QCOM', 'WFC', 'MCD', 'SHOP', 'INTU', 'MPNGF', 'HESAF', 'MS', 'TXN', 'MRK', 'NVS', 'UPS', 'RYDAF', 'NEE', 'AMD', 'LOW', 'CICHY', 'LIN', 'AZN', 'T', 'SAP', 'UNP', 'SONY', 'ACGBY', 'KYCCF', 'SCHW', 'MDT', 'RY', 'BHP', 'TMUS', 'HON', 'PNGAY', 'PM', 'AMAT', 'SE', 'BLK', 'PTR', 'SIEGY']
    for code in codes:
        df = get_candles(code, "15 Y", "1 day")
        df.to_csv('data1/{}.csv'.format(code), encoding='gbk', index=False)
        print(df)

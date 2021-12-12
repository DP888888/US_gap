import pandas as pd
import matplotlib.pyplot as plt
import glob
plot_flag = 0
if __name__ == '__main__':
    pd.set_option('max_columns', None)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 1000)

    filename = 'data1\QQQ.csv'
    df = pd.read_csv(filename, encoding='gbk')
    code = filename.split('\\')[1].replace('.csv', '')
    holding = 0
    net_value = 1.0
    benchmark_net_value = 1.0
    results = []
    for i in range(2, df.shape[0]):
        buy_condition = df.iloc[i - 2, :]['最高价'] < df.iloc[i - 1, :]['最低价']
        buy_condition = buy_condition and df.iloc[i - 2, :]['最高价'] < df.iloc[i, :]['最低价']
        buy_condition = buy_condition and holding == 0

        sell_condition = df.iloc[i - 2, :]['最低价'] > df.iloc[i - 1, :]['最高价']
        sell_condition = sell_condition and df.iloc[i - 2, :]['最低价'] > df.iloc[i, :]['最高价']
        sell_condition = sell_condition and holding == 1

        if holding == 1:
            net_value = net_value * df.iloc[i, :]['收盘价'] / df.iloc[i - 1, :]['收盘价']

        if buy_condition:
            holding = 1

        if sell_condition:
            holding = 0

        benchmark_net_value = benchmark_net_value * df.iloc[i, :]['收盘价'] / df.iloc[i - 1, :]['收盘价']
        results.append(
            df.iloc[i, :].to_list() + [buy_condition, sell_condition, holding, net_value, benchmark_net_value])
    results = pd.DataFrame(results, columns=df.columns.to_list() + ['买点', '卖点', '仓位', '净值', '持有净值'])
    results['最大回撤'] = results['净值'] / results['净值'].rolling(252, min_periods=1).max() - 1
    results['持有最大回撤'] = results['持有净值'] / results['持有净值'].rolling(252, min_periods=1).max() - 1
    QQQ = results

    output = []
    for filename in glob.glob('data1/*.csv'):
        df = pd.read_csv(filename, encoding='gbk')
        if df.empty:
            continue

        code = filename.split('\\')[1].replace('.csv', '')
        print(code)
        df = df.merge(QQQ[['交易日期', '买点', '卖点', '仓位']], how='inner', left_on='交易日期', right_on='交易日期')
        df['净值'] = 1.0
        df['持有净值'] = 1.0
        for i in range(1, df.shape[0]):
            if df.iloc[i - 1, :]['仓位'] == 1:
                df.loc[i, '净值'] = df.iloc[i - 1, :]['净值'] / df.iloc[i - 1, :]['收盘价'] * df.iloc[i, :]['收盘价']
            else:
                df.loc[i, '净值'] = df.iloc[i - 1, :]['净值']
            df.loc[i, '持有净值'] = df.iloc[i - 1, :]['持有净值'] / df.iloc[i - 1, :]['收盘价'] * df.iloc[i, :]['收盘价']
        df['最大回撤'] = df['净值'] / df['净值'].rolling(252, min_periods=1).max() - 1
        df['持有最大回撤'] = df['持有净值'] / df['持有净值'].rolling(252, min_periods=1).max() - 1
        df.to_csv('data2/{}.csv'.format(code), encoding='gbk', index=False)

        temp = [code]
        r = 100.0 * df['净值'].to_list()[-1]
        d = 100.0 * df['最大回撤'].min()
        print('择时收益率：{:.1f}%'.format(r))
        print('择时最大回撤：{:.1f}%'.format(d))
        print('择时收益率/最大回撤：{:.2f}'.format(abs(r / d)))
        temp += [r, d, abs(r/d)]
        print()
        r = 100.0 * df['持有净值'].to_list()[-1]
        d = 100.0 * df['持有最大回撤'].min()
        print('不择时收益率：{:.1f}%'.format(r))
        print('不择时最大回撤：{:.1f}%'.format(d))
        print('不择时收益率/最大回撤：{:.2f}'.format(abs(r / d)))
        temp += [r, d, abs(r/d)]
        print()
        print()
        output.append(temp)

        if plot_flag:
            fig, ax1 = plt.subplots()
            ax1.set_xlabel('X-axis')
            ax1.set_ylabel('Y1-axis', color='tab:red')
            ax1.plot(pd.to_datetime(df['交易日期']), df['最大回撤'], color='tab:red')
            ax1.tick_params(axis='y', labelcolor='tab:red')
            ax2 = ax1.twinx()
            ax2.set_ylabel('Y2-axis', color='tab:blue')
            ax2.plot(pd.to_datetime(df['交易日期']), df['净值'] * 100.0, color='tab:blue')
            ax2.tick_params(axis='y', labelcolor='tab:blue')
            plt.title('{} with timing strategy'.format(code), fontweight="bold")
            plt.show()

            fig, ax1 = plt.subplots()
            ax1.set_xlabel('X-axis')
            ax1.set_ylabel('Y1-axis', color='tab:red')
            ax1.plot(pd.to_datetime(df['交易日期']), df['持有最大回撤'], color='tab:red')
            ax1.tick_params(axis='y', labelcolor='tab:red')
            ax2 = ax1.twinx()
            ax2.set_ylabel('Y2-axis', color='tab:blue')
            ax2.plot(pd.to_datetime(df['交易日期']), df['持有净值'] * 100.0, color='tab:blue')
            ax2.tick_params(axis='y', labelcolor='tab:blue')
            plt.title('{} buy and hold'.format(code), fontweight="bold")
            plt.show()
    output = pd.DataFrame(output, columns=['股票代码', '收益率', '最大回撤', '收益率/最大回撤', '不择时收益率', '不择时最大回撤', '不择时收益率/最大回撤'])
    output['择时效率'] = output['收益率/最大回撤'] / output['不择时收益率/最大回撤']
    output = output.sort_values(by='择时效率', ascending=False)
    output.to_csv('data2_results.csv', encoding='gbk', index=False)
    print(output)
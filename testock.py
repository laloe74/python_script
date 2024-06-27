import requests
import efinance as ef

# 设置 Telegram API 
bot_token = '***'
channel_id = '***'

# 设置展示股票
stock_code = ['1810', 'AAPL', '02015', '09866', '002594', '00700', '09868']

# 汇率API 自备/购买(1分钱10000次): https://www.tanshuapi.com/market/detail-84
api_usd_to_hkd = "***"
api_cny_to_hkd = "***"


def get_exchange_rates(api_urls):
    rates = {}
    success = True

    for api_url in api_urls:
        response = requests.get(api_url)
        data = response.json()

        if data['code'] == 1:
            rates[api_url] = float(data['data']['exchange'])
        else:
            print(f"获取失败({api_url}): {data['msg']}")
            success = False

    if success:
        print("成功(1/3): 获取汇率")
    else:
        print("失败(1/3): 获取汇率, 请检查汇率API")

    return rates


def get_stock_data(stock_code):
    df = ef.stock.get_latest_quote(stock_code)
    if not df.empty:
        # 汇率换算 USD to HKD
        df.loc[df['名称'] == '苹果', '总市值'] = (
            df.loc[df['名称'] == '苹果', '总市值'] * uh_rate
        ).astype(int)
        # 汇率换算 CNY to HKD
        df.loc[df['名称'] == '比亚迪', '总市值'] = (
            df.loc[df['名称'] == '比亚迪', '总市值'] * ch_rate
        ).astype(int)
        # 将所有总市值的单位换成10亿并保留整数部分
        df['总市值'] = (df['总市值'] / 1e9).astype(int)
        # 按市值排序
        df = df.sort_values(by='总市值', ascending=False)
        # 名称只取前两个汉字，除了比亚迪。
        df['名称'] = df['名称'].apply(
            lambda name: name if '比亚迪' in name else name[:2]
            )
        print("成功(2/3): 获取股票原始数据")
        return df
    else:
        print("失败(2/3): 获取原始股票数据, 请检查股票API")
        return None


def splice(stock_data, xiaomi_exceeds_apple):
    data = f"{'✅ 是的' if xiaomi_exceeds_apple else '❌ 没有'}\n\n"
    data += f"📈 今日市值排行: \n"
    for index, row in stock_data.iterrows():
        data += (
            f"{row['名称']} ${row['最新价']:.2f} ({row['涨跌幅']:.2f}%) "
            f"${row['总市值']:,.0f}B\n"
        )
    data += f"\n"
    data += (
    f"USD/HKD: {'=1 Error!!!' if uh_rate == 1 else uh_rate:.2f}\n"
    f"CNY/HKD: {'=1 Error!!!' if ch_rate == 1 else ch_rate:.2f}"
    )

    return data


# 获取汇率
exchange_rates = get_exchange_rates([api_usd_to_hkd, api_cny_to_hkd])
uh_rate = exchange_rates.get(api_usd_to_hkd, 1.0)
ch_rate = exchange_rates.get(api_cny_to_hkd, 1.0)

# 获取股票数据
stock_data = get_stock_data(stock_code)

# 判断小米市值是否超过苹果市值
xiaomi_exceeds_apple = (
    stock_data[stock_data['名称'] == '小米']['总市值'].values[0] >
    stock_data[stock_data['名称'] == '苹果']['总市值'].values[0]
)

# 拼接信息
message = splice(stock_data, xiaomi_exceeds_apple)

# 发送到 Telegram 
try:
    telegram_api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {'chat_id': channel_id, 'text': message}
    response = requests.post(telegram_api_url, data=payload)
    response.raise_for_status()
    print("成功(3/3): 发送 Telegram 消息")
except requests.exceptions.RequestException as e:
    print('失败(3/3): 发送 Telegram 消息, 请检查电报API')

# Python檢測http代理代碼
# https://free.socks.network/?=nodeseek

import requests

# 設置代理信息爲http類型
proxy = {
    'http': 'http://free-residential.socks.network:10001',
    'https': 'http://free-residential.socks.network:10001'
}

# 要測試的目標URL
test_url = 'https://one.one.one.one'
ip_info_url = 'https://api.myip.com'  # 獲取IP信息的URL

try:
    # 獲取原始IP信息（不通過代理）
    original_ip_response = requests.get(ip_info_url, timeout=10)
    original_ip_info = original_ip_response.json()
    print(f"原始IP信息: {original_ip_info}")

    # 通過代理獲取IP信息
    proxy_ip_response = requests.get(ip_info_url, proxies=proxy, timeout=10)
    proxy_ip_info = proxy_ip_response.json()
    print(f"代理IP信息: {proxy_ip_info}")

    # 訪問目標URL以測試代理是否可用
    response = requests.get(test_url, proxies=proxy, timeout=10)

    if response.status_code == 200:
        print(f"代理可用，訪問{test_url}成功！")
    else:
        print(f"代理返回了非200的響應碼: {response.status_code}")

except requests.exceptions.ProxyError:
    print("無法通過代理服務器連接到目標URL。")
except requests.exceptions.Timeout:
    print("請求超時，代理服務器可能不可用或網絡較慢。")
except requests.exceptions.RequestException as e:
    print(f"請求過程中發生錯誤: {e}")
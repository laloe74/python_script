'''
代碼解釋
抓取內容並保存到1.txt，同時去重：

從指定的URL列表中獲取內容。
使用requests模塊抓取數據。
將抓取的數據保存到集合中以去重。
將去重後的代理列表保存到1.txt文件中。
輸出抓取的代理數量和去重後的代理數量。
驗證代理可用性：

定義函數check_proxy，使用指定的socks5代理訪問目標網站（https://one.one.one.one）。
若代理可用，則返回代理，否則返回None。
使用progress_bar函數動態顯示驗證進度條。
記錄驗證開始和結束時間，並計算驗證總耗時。
使用1000線程並發驗證代理：

讀取1.txt中的代理列表。
使用concurrent.futures.ThreadPoolExecutor創建1000線程的線程池。
並發驗證每個代理的可用性。
將可用的代理保存到2.txt文件中。
輸出可用代理數量和驗證總耗時。

主函數：
記錄腳本啓動時間。
調用fetch_and_save函數抓取並保存代理。
調用validate_proxies函數驗證代理的可用性並保存結果。
記錄腳本結束時間，並計算總耗時。

以上代碼需要安裝以下依賴項：

requests：用于發送HTTP請求和獲取代理列表。
concurrent.futures：Python標准庫的壹部分，不需要額外安裝，用于並發處理。
sys 和 time：Python標准庫的壹部分，不需要額外安裝。
妳可以使用 pip 來安裝 requests 模塊。以下是安裝 requests 的命令：

pip install -U 'requests[socks]'
其余的模塊 concurrent.futures、sys 和 time 是Python標准庫的壹部分，所以不需要額外安裝。

在這個腳本中，socket 模塊實際上沒有被使用到，所以即使導入也沒有實際用途。如果在未來需要處理網絡相關的低級操作時，才需要用到 socket 模塊。

當前腳本所依賴的第三方庫只有 requests，而 concurrent.futures、sys 和 time 都是 Python 標准庫的壹部分，不需要額外安裝。
'''

import requests
import concurrent.futures
import time
import sys
import socket

# 定義要抓取內容的URL列表
urls = [
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
    "https://yakumo.rei.my.id/SOCKS5",
    "https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/data.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt",
    "https://raw.githubusercontent.com/0x1337fy/fresh-proxy-list/archive/storage/classic/socks5.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt"
]

# 從多個URL抓取代理列表並去重，保存到1.txt文件
def fetch_and_save():
    all_proxies = []  # 存儲所有抓取的代理
    proxies = set()  # 使用集合去重

    for url in urls:
        try:
            response = requests.get(url)  # 發送HTTP GET請求
            response.raise_for_status()  # 檢查請求是否成功
            proxy_list = response.text.splitlines()  # 將內容按行分割
            all_proxies.extend(proxy_list)  # 添加到所有抓取的代理列表中
            proxies.update(proxy_list)  # 添加到集合中以去重
            print(f"從 {url} 獲取並添加代理成功")
        except Exception as e:
            print(f"抓取 {url} 時出錯: {e}")
    
    with open("1.txt", "w") as f:
        f.write("\n".join(proxies))  # 將去重後的代理列表寫入1.txt文件
    
    print("代理列表已保存到 1.txt")
    print(f"壹共收集了 {len(all_proxies)} 個代理")
    print(f"去重後剩余 {len(proxies)} 個代理")
    return all_proxies, proxies

# 驗證代理的可用性
def check_proxy(proxy):
    try:
        socks5_proxy = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}"
        }
        response = requests.get("https://one.one.one.one", proxies=socks5_proxy, timeout=5)  # 使用代理訪問目標網站
        if response.status_code == 200:  # 檢查HTTP響應狀態碼是否爲200
            return proxy  # 返回可用的代理
    except Exception:
        return None  # 返回None表示代理不可用

# 使用1000線程並發驗證代理可用性
def validate_proxies():
    with open("1.txt", "r") as f:
        proxies = f.read().splitlines()  # 讀取1.txt中的代理列表

    valid_proxies = []  # 存儲可用的代理
    total_proxies = len(proxies)
    
    def progress_bar(current, total, bar_length=40):
        progress = current / total
        block = int(bar_length * progress)
        bar = "#" * block + "-" * (bar_length - block)
        text = f"\r驗證進度: [{bar}] {current}/{total} ({progress:.2%})"
        sys.stdout.write(text)
        sys.stdout.flush()

    start_time = time.time()  # 記錄驗證開始時間
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        results = executor.map(check_proxy, proxies)
        for i, result in enumerate(results):
            progress_bar(i + 1, total_proxies)
            if result:
                valid_proxies.append(result)  # 添加可用的代理到列表中
    end_time = time.time()  # 記錄驗證結束時間

    with open("2.txt", "w") as f:
        f.write("\n".join(valid_proxies))  # 將可用的代理保存到2.txt文件中
    
    print("\n可用代理已保存到 2.txt")
    print(f"驗證過後共有 {len(valid_proxies)} 個可用代理")
    print(f"驗證代理花費了 {end_time - start_time:.2f} 秒")

# 主函數
if __name__ == "__main__":
    start_time = time.time()  # 記錄腳本啓動時間
    print("開始抓取代理並保存到 1.txt")
    all_proxies, unique_proxies = fetch_and_save()
    print("開始驗證代理可用性")
    validate_proxies()
    end_time = time.time()  # 記錄腳本結束時間
    print(f"所有操作完成，共花費了 {end_time - start_time:.2f} 秒")
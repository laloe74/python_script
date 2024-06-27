# 自用Python工具脚本

---

### h2m.py
将「诗歌网页的HTML文件」批量转换成「Markdown格式」

### testock.py
在Telegram频道每天定时发送指定股票涨跌信息

**使用**
1. 填入 Telegram 的 bot_token 和 channel_id
2. 有汇率转换功能，需填入自备/[购买](https://www.tanshuapi.com/market/detail-84)的汇率API
3. 填写股票代码，具体参考第三方库 [efinance](https://github.com/Micro-sheep/efinance)
```
pip install efinance
python3 TeleShare.py
```
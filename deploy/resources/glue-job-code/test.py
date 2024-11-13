#!/usr/bin/env python3# coding:utf-8# feishu.pyimport base64
import hashlib
import hmac
from datetime import datetime
import base64

import requests

WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/aa8867b0-a0a4-4704-b18c-e7eea05418c7"
WEBHOOK_SECRET = "IZfPccQJ3PxWDB4I6zN3ke"
timestamp = int(datetime.now().timestamp())

def gen_sign(secret):# 拼接时间戳以及签名校验
    string_to_sign = '{}\n{}'.format(timestamp, secret)

    # 使用 HMAC-SHA256 进行加密
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()

    # 对结果进行 base64 编码
    sign = base64.b64encode(hmac_code).decode('utf-8')

    return sign

def main():
    sign = gen_sign(WEBHOOK_SECRET)
    params = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "text",
        "content": {"text": "点火发射！"},
    }

    resp = requests.post(WEBHOOK_URL, json=params)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") and result.get("code") != 0:
        print(f"发送失败：{result['msg']}")
        return
    print("消息发送成功")

if __name__ == '__main__':
    main()
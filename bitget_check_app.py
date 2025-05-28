
import streamlit as st
import requests
import time

# Streamlit Secrets에서 API 키 관리 권장
api_key = st.secrets["BITGET_API_KEY"]
secret_key = st.secrets["BITGET_SECRET_KEY"]
passphrase = st.secrets["BITGET_PASSPHRASE"]

BASE_URL = "https://api.bitget.com/api/v2"

import hmac
import hashlib
import base64
import datetime

# Bitget 전용 서명 생성 함수
def generate_signature(api_secret, timestamp, method, request_path, body=""):
    message = f'{timestamp}{method.upper()}{request_path}{body}'
    mac = hmac.new(bytes(api_secret, encoding='utf-8'), bytes(message, encoding='utf-8'), digestmod=hashlib.sha256)
    d = mac.digest()
    return base64.b64encode(d).decode()

def get_timestamp():
    return datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"

# 공통 요청 함수
def send_request(method, path, params=None):
    timestamp = get_timestamp()
    body = "" if not params else json.dumps(params)
    sign = generate_signature(secret_key, timestamp, method, path, body)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json"
    }

    url = BASE_URL + path
    response = requests.request(method, url, headers=headers, json=params)
    return response.json()

st.title("🔐 Bitget 실시간 확인")

# 자산 조회
def get_balance():
    response = send_request("GET", "/account/margin/coins?productType=umcbl")
    assets = response.get("data", [])
    usdt = next((item for item in assets if item["marginCoin"] == "USDT"), None)
    return usdt

balance = get_balance()
if balance:
    st.success(f'잔고: {balance["available"]} USDT (총: {balance["total"]})')
else:
    st.error("잔고를 불러올 수 없습니다.")

# 인기 종목 가격 조회
def get_top_price():
    response = requests.get(f"{BASE_URL}/mix/market/tickers?productType=umcbl").json()
    top = sorted(response['data'], key=lambda x: float(x['quoteVolume']), reverse=True)[0]
    return top['symbol'], float(top['lastPr'])

symbol, price = get_top_price()
st.info(f"📈 최상위 거래량 종목: {symbol} / 현재가: {price} USDT")

import streamlit as st
import requests
import hmac
import hashlib
import time

# ✅ Streamlit Secrets 사용 권장
API_KEY = st.secrets["BITGET_API_KEY"]
SECRET_KEY = st.secrets["BITGET_SECRET_KEY"]
PASSPHRASE = st.secrets["BITGET_PASSPHRASE"]

BASE_URL = "https://api.bitget.com"

# 🔐 Bitget 서명 생성 함수
def generate_signature(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    signature = hmac.new(
        bytes(SECRET_KEY, "utf-8"),
        msg=bytes(message, "utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
    return signature

# 📦 자산 조회 함수 (선물)
def get_balance():
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    path = "/api/v2/mix/account/accounts?productType=USDT-FUTURES"
    url = BASE_URL + path
    sign = generate_signature(timestamp, method, path)

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    res = requests.get(url, headers=headers)
    res_json = res.json()

    if res_json.get("code") != "00000":
        return None

    assets = res_json["data"]
    usdt = next((item for item in assets if item["marginCoin"] == "USDT"), None)
    return float(usdt["available"]) if usdt else None

# 📈 BTC 현재가 조회
def get_btc_price():
    url = f"{BASE_URL}/api/v2/mix/market/ticker?symbol=BTCUSDT&productType=USDT-FUTURES"
    res = requests.get(url).json()
    return float(res["data"]["lastPr"]) if res.get("data") else None

# ✅ Streamlit 인터페이스
st.title("🔐 Bitget 실시간 확인")

balance = get_balance()
price = get_btc_price()

if balance is None:
    st.error("잔고 정보를 불러오지 못했습니다.")
else:
    st.success(f"✅ 현재 USDT 가용 잔고: {balance:,.2f} USDT")

if price is None:
    st.error("BTC 현재가 정보를 불러오지 못했습니다.")
else:
    st.info(f"📈 BTC 현재가: {price:,.2f} USDT")


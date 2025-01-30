import re  # 정규식 모듈 추가
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

NAVER_CLIENT_ID = "8eesQ8IzEGDS4dHlqgqi"
NAVER_CLIENT_SECRET = "hFGQkC2ErG"

# 🔹 HTML 태그 제거 함수 추가
def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text)  # HTML 태그 제거

# 🔹 네이버 쇼핑 API 호출 함수 (수정된 버전)
def get_naver_price(query):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=5&sort=asc"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        results = []
        for item in items:
            results.append({
                "쇼핑몰": item["mallName"],
                "상품명": strip_tags(item["title"]),  # 🔥 HTML 태그 제거
                "가격": int(item["lprice"]),
                "링크": item["link"]
            })
        return results
    return []

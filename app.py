import os
from dotenv import load_dotenv
import requests
import re
import pandas as pd
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# 🔹 환경 변수 로드
load_dotenv()
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 🔹 네이버 API 호출 함수
def get_naver_price(query):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=10&sort=asc"
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
            title = re.sub(r"<[^>]+>", "", item["title"])  # HTML 태그 제거
            price = int(item["lprice"])
            delivery_fee = int(item.get("deliveryFee", 0)) if item.get("deliveryFee") else 0
            total_price = price + delivery_fee

            results.append({
                "상품명": title,
                "가격": price,
                "택배비": delivery_fee,
                "총 가격": total_price,
                "링크": item["link"]
            })

        return results
    return []

# 🔹 검색 API 엔드포인트
from flask import Flask, request, render_template, jsonify
import json

@app.route("/search", methods=["GET"])
def search():
    product = request.args.get("product", "")
    if not product:
        return jsonify({"error": "검색어를 입력하세요"}), 400

    results = get_naver_price(product)

    # 🔹 JSON을 한글 그대로 출력하도록 설정
    return app.response_class(
        response=json.dumps(results, ensure_ascii=False, indent=2), 
        mimetype="application/json"
    )


# 🔹 메인 페이지 (검색창 포함)
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

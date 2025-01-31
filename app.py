import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# 🔹 네이버 API 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 🔹 네이버 쇼핑 API 호출 함수
def get_naver_price(query):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=5&sort=asc"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        return []

# 🔹 기본 페이지 (`/`)
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# 🔹 검색 API (`/search`)
@app.route("/search", methods=["GET"])
def search():
    product = request.args.get("product", "")
    if not product:
        return jsonify({"error": "검색어를 입력하세요"}), 400
    
    results = get_naver_price(product)
    return jsonify(results)

# 🔹 Flask 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

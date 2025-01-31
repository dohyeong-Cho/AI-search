import re
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

NAVER_CLIENT_ID = "8eesQ8IzEGDS4dHlqgqi"
NAVER_CLIENT_SECRET = "hFGQkC2ErG"

# 🔹 HTML 태그 제거 함수
def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text)

# 🔹 네이버 쇼핑 API에서 "과자" 관련 제품만 필터링하는 함수
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
            title = strip_tags(item["title"])  # 🔹 HTML 태그 제거
            mall_name = item["mallName"]
            price = int(item["lprice"])
            link = item["link"]

            # 🔹 "과자", "스낵", "칩" 키워드가 포함된 상품만 필터링
            if any(keyword in title for keyword in ["과자", "스낵", "칩"]):
                results.append({
                    "쇼핑몰": mall_name,
                    "상품명": title,
                    "가격": price,
                    "링크": link
                })
        
        return results  # 🔹 필터링된 결과만 반환
    return []

# 🔹 메인 페이지 (검색 폼 제공)
@app.route("/")
def home():
    return render_template("index.html")

# 🔹 검색 요청을 처리하는 API 엔드포인트
@app.route("/search", methods=["GET"])
def search():
    product = request.args.get("product", "")
    if not product:
        return render_template("index.html", results=[])

    results = get_naver_price(product)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

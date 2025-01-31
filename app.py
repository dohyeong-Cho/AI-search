import re
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

NAVER_CLIENT_ID = "8eesQ8IzEGDS4dHlqgqi"
NAVER_CLIENT_SECRET = "hFGQkC2ErG"

# 🔹 HTML 태그 제거 함수
def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text)

# 🔹 "과자(스낵류)" 카테고리 ID 목록 (네이버 쇼핑 API 기준)
VALID_CATEGORY_IDS = ["50000169", "50000205", "50000206"]  # (예: 스낵, 감자칩, 과자)

# 🔹 네이버 쇼핑 API에서 "과자 카테고리" 제품만 가져오는 함수
def get_naver_price(query):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=20&sort=asc"
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
            category = item.get("category4", "")  # 🔹 제품의 카테고리 ID 가져오기
            mall_name = item["mallName"]
            price = int(item["lprice"])
            link = item["link"]

            # ✅ 카테고리 ID가 과자(스낵류)인지 확인
            if category in VALID_CATEGORY_IDS:
                results.append({
                    "쇼핑몰": mall_name,
                    "상품명": title,
                    "가격": price,
                    "링크": link
                })

        # ✅ 최저가 기준 정렬 (가격 순으로 정렬)
        results = sorted(results, key=lambda x: x["가격"])

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

import re
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

NAVER_CLIENT_ID = "8eesQ8IzEGDS4dHlqgqi"
NAVER_CLIENT_SECRET = "hFGQkC2ErG"

# 🔹 HTML 태그 제거 함수
def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text)

# 🔹 네이버 쇼핑 API에서 제품 정보 가져오기 (디버깅 추가)
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
            category = item.get("category4", "없음")  # 🔹 카테고리 ID 가져오기 (없으면 "없음" 표시)
            mall_name = item["mallName"]
            price = int(item["lprice"])
            link = item["link"]

            # 🔹 검색 결과 디버깅용 출력 (category4 값 확인)
            print(f"상품명: {title}, 쇼핑몰: {mall_name}, 가격: {price}원, 카테고리: {category}")

            # ✅ 카테고리 값 확인을 위해 필터링 없이 모든 데이터를 반환
            results.append({
                "쇼핑몰": mall_name,
                "상품명": title,
                "가격": price,
                "카테고리": category,
                "링크": link
            })

        return results  # 🔹 필터링 없이 결과 반환하여 category4 값 확인
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

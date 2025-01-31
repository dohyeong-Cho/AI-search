import re
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

NAVER_CLIENT_ID = "8eesQ8IzEGDS4dHlqgqi"
NAVER_CLIENT_SECRET = "hFGQkC2ErG"

# 🔹 HTML 태그 제거 함수
def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text)

# 🔹 개수 추출 함수 (예: "썬칩 3개 묶음" → 3, "썬칩 24개입" → 24)
def extract_quantity(title):
    match = re.search(r'(\d+)[개입묶봉팩박스]', title)
    return int(match.group(1)) if match else 1  # 기본값 1개

# 🔹 신뢰도 점수 계산 함수
def calculate_trust_score(price, delivery_fee, quantity, mall_name, title):
    score = 0

    # ✅ 가격 점수 (30점)
    total_price = price + delivery_fee
    per_unit_price = total_price / quantity
    if per_unit_price < 2000:  # 썬칩 개당 가격이 2000원 미만이면 높은 점수
        score += 30
    elif per_unit_price < 3000:
        score += 20
    elif per_unit_price < 4000:
        score += 10

    # ✅ 판매자 신뢰도 (40점)
    trusted_malls = ["쿠팡", "11번가", "네이버스토어", "G마켓", "롯데ON"]
    if mall_name in trusted_malls:
        score += 30
    else:
        score += 10  # 일반 쇼핑몰은 기본 점수만 부여

    # ✅ 상품 인기 점수 (30점)
    if quantity > 3:
        score += 20  # 묶음 상품일 경우 추가 점수
    if "베스트" in title or "인기" in title or "많이 판매됨" in title:
        score += 10  # 인기 키워드 포함 제품 가산점

    return score

# 🔹 네이버 쇼핑 API에서 데이터 가져오기 및 신뢰도 점수 계산
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
            mall_name = item["mallName"]
            price = int(item["lprice"])
            delivery_fee = int(item.get("deliveryFee", 0))  # 🚚 택배비 (없으면 0)
            quantity = extract_quantity(title)  # 🔹 개수 추출
            trust_score = calculate_trust_score(price, delivery_fee, quantity, mall_name, title)  # 🔹 신뢰도 점수 계산
            link = item["link"]

            results.append({
                "쇼핑몰": mall_name,
                "상품명": title,
                "개수": quantity,
                "가격": price,
                "택배비": delivery_fee,
                "총 가격": price + delivery_fee,
                "개당 가격": round((price + delivery_fee) / quantity, 2),
                "신뢰도 점수": trust_score,
                "링크": link
            })

        # ✅ 신뢰도 점수가 높은 순으로 정렬
        results = sorted(results, key=lambda x: x["신뢰도 점수"], reverse=True)

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

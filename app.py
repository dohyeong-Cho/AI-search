import re
import requests
import numpy as np
import pandas as pd
from flask import Flask, request, render_template
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

NAVER_CLIENT_ID = "8eesQ8IzEGDS4dHlqgqi"
NAVER_CLIENT_SECRET = "hFGQkC2ErG"

# HTML 태그 제거 함수
def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text)

# 개수 추출 함수 (예: "썬칩 3개 묶음" → 3, "썬칩 24개입" → 24)
def extract_quantity(title):
    match = re.search(r'(\d+)[개입묶봉팩박스]', title)
    return int(match.group(1)) if match else 1  # 기본값 1개

# 정품 키워드 포함 여부 (1 = 정품, 0 = 일반)
def check_official(title):
    return 1 if any(keyword in title for keyword in ["정품", "공식", "오리지널"]) else 0

# 신뢰도 점수 계산 AI 모델 (랜덤 포레스트)
def train_ai_model():
    # 샘플 학습 데이터
    train_data = pd.DataFrame([
        [2500, 3000, 5500, 1, 40],
        [1800, 2500, 4300, 0, 35],
        [7500, 0, 2500, 1, 70],
        [32000, 0, 1333, 1, 90],
        [2000, 2000, 4000, 0, 50],
        [5000, 0, 5000, 1, 75],
    ], columns=["가격", "택배비", "개당 가격", "정품 여부", "신뢰도 점수"])

    X = train_data.drop("신뢰도 점수", axis=1)  # 입력값
    y = train_data["신뢰도 점수"]  # 출력값

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# AI 모델 학습
model = train_ai_model()

# 네이버 쇼핑 API에서 데이터 가져오기 + AI 신뢰도 점수 적용
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
            title = strip_tags(item["title"])  # HTML 태그 제거
            price = int(item["lprice"])
            delivery_fee = int(item.get("deliveryFee", 0))  # 택배비 (없으면 0)
            quantity = extract_quantity(title)  # 개수 추출
            per_unit_price = (price + delivery_fee) / quantity  # 개당 가격 계산
            official = check_official(title)  # 정품 여부
            
            # AI 신뢰도 점수 예측
            X_new = np.array([[price, delivery_fee, per_unit_price, official]])
            trust_score = model.predict(X_new)[0]

            results.append({
                "쇼핑몰": item["mallName"],
                "상품명": title,
                "개수": quantity,
                "가격": price,
                "택배비": delivery_fee,
                "총 가격": price + delivery_fee,
                "개당 가격": round(per_unit_price, 2),
                "신뢰도 점수": round(trust_score, 2),
                "링크": item["link"]
            })

        # ✅ 신뢰도 점수가 높은 순으로 정렬
        results = sorted(results, key=lambda x: x["신뢰도 점수"], reverse=True)

        return results
    return []

# 메인 페이지 (검색 폼 제공)
@app.route("/")
def home():
    return render_template("index.html")

# 검색 요청을 처리하는 API 엔드포인트
@app.route("/search", methods=["GET"])
def search():
    product = request.args.get("product", "")
    if not product:
        return render_template("index.html", results=[])

    results = get_naver_price(product)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

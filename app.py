import difflib  # 문자열 유사도 비교
from flask import Flask, request, jsonify
import requests
import pickle  # 저장된 모델 로드
import numpy as np

app = Flask(__name__)

# 🔹 네이버 API 설정
import os
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 🔹 저장된 머신러닝 모델 로드
with open("trust_score_model.pkl", "rb") as f:
    model = pickle.load(f)

# 🔹 신뢰도 점수 예측 함수 (AI 기반)
def predict_trust_score(item, query):
    가격 = int(item["가격"])
    택배비 = int(item["택배비"])
    리뷰수 = int(item.get("리뷰수", 0))
    평점 = float(item.get("평점", 0))
    쇼핑몰 = item["쇼핑몰"]
    상품명 = item["상품명"]

    # 🔹 쇼핑몰을 숫자로 변환 (쿠팡=3, 네이버=2, 개인=0, 11번가=1, G마켓=4)
    쇼핑몰_코드 = {"개인": 0, "11번가": 1, "네이버": 2, "쿠팡": 3, "G마켓": 4}.get(쇼핑몰, 0)

    # 🔹 상품명 유사도 점수 계산
    유사도 = difflib.SequenceMatcher(None, query, 상품명).ratio() * 100

    # 🔹 AI 모델 입력 데이터 생성
    input_data = np.array([[가격, 택배비, 리뷰수, 평점, 쇼핑몰_코드, 유사도]])

    # 🔹 AI 모델로 신뢰도 점수 예측
    predicted_score = model.predict(input_data)[0]
    return max(0, min(int(predicted_score), 100))  # 0~100 범위로 제한

# 🔹 네이버 쇼핑 API 호출 함수
def get_naver_price(query):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=10&sort=asc"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json().get("items", [])
        results = []
        for item in items:
            product = {
                "쇼핑몰": item["mallName"],
                "상품명": item["title"],
                "가격": int(item["lprice"]),
                "링크": item["link"],
                "택배비": 0,
                "리뷰수": int(item.get("reviewCount", 0)),
                "평점": float(item.get("reviewScore", 0)),
            }
            product["신뢰도 점수"] = predict_trust_score(product, query)
            results.append(product)

        results.sort(key=lambda x: x["신뢰도 점수"], reverse=True)
        return results
    return []

# 🔹 검색 API 엔드포인트
@app.route("/search", methods=["GET"])
def search():
    product = request.args.get("product", "")
    if not product:
        return jsonify({"error": "검색어를 입력하세요"}), 400
    
    results = get_naver_price(product)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import os
import requests
import pickle
import numpy as np
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# 🔹 네이버 API 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 🔹 신뢰도 점수 AI 모델 로드
with open("trust_score_model.pkl", "rb") as f:
    model = pickle.load(f)

# 🔹 네이버 쇼핑 API 호출 함수
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
            try:
                price = int(item["lprice"])
                shipping_fee = 3000  # 🔹 기본 택배비 설정 (API에서 지원 안함)
                total_price = price + shipping_fee
                review_count = np.random.randint(10, 500)  # 🔹 리뷰 개수 (임의 값)
                rating = np.random.uniform(3.0, 5.0)  # 🔹 평점 (임의 값)

                # 🔹 AI 모델을 사용해 신뢰도 점수 예측
                features = np.array([[price, shipping_fee, review_count, rating]])
                trust_score = round(model.predict(features)[0], 2)

                results.append({
                    "쇼핑몰": item["mallName"],
                    "상품명": item["title"],
                    "가격": price,
                    "택배비": shipping_fee,
                    "총 가격": total_price,
                    "신뢰도 점수": trust_score,
                    "링크": item["link"]
                })
            except:
                continue

        # 🔹 신뢰도 점수를 기준으로 정렬
        results = sorted(results, key=lambda x: x["신뢰도 점수"], reverse=True)
        return results
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

# 🔹 응답 api 출력
def get_naver_price(query):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=10&sort=asc"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, headers=headers)
    
    print("네이버 API 응답 코드:", response.status_code)  # 추가된 로그
    print("네이버 API 응답 내용:", response.json())  # 추가된 로그

    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        return []


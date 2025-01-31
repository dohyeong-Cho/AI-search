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
        items = response.json().get("items", [])
        filtered_items = []

        for item in items:
            category1 = item.get("category1", "")
            category2 = item.get("category2", "")
            category3 = item.get("category3", "")
            category4 = item.get("category4", "")

            # ✅ 필터링 기준: "과자/베이커리" & "스낵"만 포함
            if category1 == "식품" and category2 == "과자/베이커리" and category3 == "스낵":
                filtered_items.append({
                    "쇼핑몰": item["mallName"],
                    "상품명": item["title"].replace("<b>", "").replace("</b>", ""),  # 🔥 HTML 태그 제거
                    "가격": int(item["lprice"]),
                    "링크": item["link"],
                    "택배비": 0,  # 네이버 API에는 택배비 정보 없음
                    "총 가격": int(item["lprice"]),  # 기본적으로 가격과 동일
                    "신뢰도 점수": None  # AI 모델 적용 전 None
                })
        
        return filtered_items
    else:
        return []


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


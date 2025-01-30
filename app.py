from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# 🔹 네이버 API 키 설정 (네가 발급받은 값으로 변경해야 함!)
NAVER_CLIENT_ID = "8eesQ8IzEGDS4dHlqgqi"
NAVER_CLIENT_SECRET = "hFGQkC2ErG"

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
        items = data.get("items", [])
        results = []
        for item in items:
            results.append({
                "쇼핑몰": item["mallName"],
                "상품명": item["title"],
                "가격": int(item["lprice"]),
                "링크": item["link"]
            })
        return results
    return []

# 🔹 메인 페이지 (검색 폼 제공)
@app.route("/", methods=["GET"])
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

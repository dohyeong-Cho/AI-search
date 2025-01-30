from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

NAVER_CLIENT_ID = "네이버_Client_ID"
NAVER_CLIENT_SECRET = "네이버_Client_Secret"

def get_naver_price(query):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=5&sort=asc"
    headers = {
        "X-Naver-Client-Id": 8eesQ8IzEGDS4dHlqgqi,
        "X-Naver-Client-Secret": hFGQkC2ErG
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

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search():
    product = request.args.get("product", "")
    if not product:
        return render_template("index.html", results=[])

    results = get_naver_price(product)
    return render_template("index.html", results=results)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

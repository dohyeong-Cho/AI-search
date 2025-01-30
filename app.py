from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "과자 가격 비교 웹사이트입니다!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

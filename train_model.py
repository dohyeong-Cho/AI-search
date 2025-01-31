import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import pickle  # 🔹 모델 저장을 위한 pickle 라이브러리 추가

# 🔹 학습 데이터 생성
data = {
    "가격": [1200, 1100, 900, 950, 1300, 1250, 800],
    "택배비": [3000, 2500, 5000, 3000, 3500, 4000, 6000],
    "리뷰수": [150, 100, 10, 200, 300, 250, 20],
    "평점": [4.5, 4.2, 3.0, 4.8, 4.7, 4.6, 3.2],
    "쇼핑몰": ["쿠팡", "네이버", "개인", "11번가", "쿠팡", "G마켓", "개인"],
    "상품명 유사도": [95, 92, 70, 97, 96, 94, 60],
    "신뢰도 점수": [88, 82, 40, 91, 85, 87, 35],
}

df = pd.DataFrame(data)

# 🔹 쇼핑몰을 숫자로 변환 (쿠팡=3, 네이버=2, 개인=0, 11번가=1, G마켓=4)
df["쇼핑몰"] = df["쇼핑몰"].map({"개인": 0, "11번가": 1, "네이버": 2, "쿠팡": 3, "G마켓": 4})

# 🔹 입력 데이터(X)와 정답 데이터(y) 분리
X = df.drop(columns=["신뢰도 점수"])
y = df["신뢰도 점수"]

# 🔹 데이터셋 분할 (훈련 80%, 테스트 20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 랜덤포레스트 모델 생성 & 훈련
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 🔹 모델 성능 평가
y_pred = model.predict(X_test)
print("MAE (평균 절대 오차):", mean_absolute_error(y_test, y_pred))

# 🔹 학습된 모델 저장 (wb = 바이너리 쓰기 모드)
with open("trust_score_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ 랜덤포레스트 신뢰도 점수 모델 저장 완료 (trust_score_model.pkl)")

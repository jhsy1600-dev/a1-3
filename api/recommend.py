from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 없습니다.")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-3.6-flash")


@app.route("/recommend", methods=["POST", "OPTIONS"])
def recommend_menu():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json()

    print("받은 데이터:", data)

    meal_style = data.get("mealStyle", "")
    preferred_food = data.get("preferredFood", "")
    avoid_food = data.get("avoidFood", "")

    try:
        budget = int(data.get("budget", 0))
    except:
        budget = 0

    prompt = f"""
너는 사용자의 조건에 맞춰 하루 식단을 추천하는 AI야.

사용자 조건:
- 원하는 식단 스타일: {meal_style}
- 좋아하는 음식: {preferred_food}
- 피하고 싶은 음식: {avoid_food}
- 예산: {budget}원

아침, 점심, 저녁 메뉴를 각각 추천해줘.

반드시 아래 JSON 형식으로만 답변해.
설명 문장이나 ```json 같은 마크다운은 절대 넣지 마.

{{
  "breakfast": {{
    "menu": "아침 메뉴 이름",
    "description": "추천 이유",
    "cost": 예상비용숫자
  }},
  "lunch": {{
    "menu": "점심 메뉴 이름",
    "description": "추천 이유",
    "cost": 예상비용숫자
  }},
  "dinner": {{
    "menu": "저녁 메뉴 이름",
    "description": "추천 이유",
    "cost": 예상비용숫자
  }}
}}
"""

    try:
        response = model.generate_content(prompt)

        ai_text = response.text.strip()

        print("Gemini 응답:", ai_text)

        result = json.loads(ai_text)

        return jsonify(result)

    except Exception as e:
        print("오류 발생:", e)

        return jsonify({
            "error": "AI 추천을 생성하는 중 오류가 발생했습니다.",
            "detail": str(e)
        }), 500


if __name__ == "__main__":
    print("등록된 라우트 목록:")
    print(app.url_map)
    app.run(debug=True, port=5000)
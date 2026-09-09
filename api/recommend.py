import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "success": True,
        "message": "Today Menu AI API is running"
    })


@app.route("/", methods=["GET", "POST", "OPTIONS"])
@app.route("/api/recommend", methods=["GET", "POST", "OPTIONS"])
def recommend():
    if request.method == "OPTIONS":
        return "", 204

    try:
        if not GEMINI_API_KEY:
            return jsonify({
                "success": False,
                "message": "GEMINI_API_KEY 환경변수가 설정되지 않았습니다."
            }), 500

        genai.configure(api_key=GEMINI_API_KEY)

        # 기존 gemini-3.6-flash는 잘못된 모델명일 가능성이 큽니다.
        model = genai.GenerativeModel("gemini-1.5-flash")

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "입력 데이터가 없습니다."
            }), 400

        meal_style = str(data.get("mealStyle", "")).strip()
        preferred_food = str(data.get("preferredFood", "")).strip()
        avoid_food = str(data.get("avoidFood", "")).strip()
        budget = str(data.get("budget", "")).strip()

        if not meal_style or not budget:
            return jsonify({
                "success": False,
                "message": "식사 스타일과 예산을 입력해주세요."
            }), 400

        prompt = f"""
당신은 식단 추천 전문가입니다.

사용자 조건:
- 식사 스타일: {meal_style}
- 선호 음식: {preferred_food}
- 피하고 싶은 음식: {avoid_food}
- 하루 예산: {budget}원

사용자 조건에 맞춰 아침, 점심, 저녁 식단을 추천해주세요.

반드시 아래 형식으로 답변하세요.

아침
메뉴:
설명:
예상 비용:

점심
메뉴:
설명:
예상 비용:

저녁
메뉴:
설명:
예상 비용:
"""

        response = model.generate_content(
            prompt,
            request_options={"timeout": 30}
        )

        if not response.text:
            return jsonify({
                "success": False,
                "message": "추천 결과를 생성하지 못했습니다."
            }), 500

        return jsonify({
            "success": True,
            "recommendation": response.text
        })

    except Exception as e:
        print("서버 오류:", e)

        return jsonify({
            "success": False,
            "message": f"식단 추천 중 오류가 발생했습니다: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/css/<path:filename>", methods=["GET"])
def css_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "css"), filename)


@app.route("/js/<path:filename>", methods=["GET"])
def js_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "js"), filename)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 없습니다.")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-3.6-flash")


@app.route("/recommend", methods=["POST", "OPTIONS"])
def recommend_menu():
    # CORS preflight 요청 처리
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json()

        # 1. 입력 데이터가 아예 없는 경우
        if not data:
            return jsonify({
                "success": False,
                "message": "입력 데이터가 없습니다."
            }), 400

        meal_style = data.get("mealStyle", "").strip()
        preferred_food = data.get("preferredFood", "").strip()
        avoid_food = data.get("avoidFood", "").strip()
        budget = data.get("budget", "").strip()

        print("받은 데이터:", data)

        # 2. 필수 입력값이 비어 있는 경우
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
        - 예산: {budget}원

        아침, 점심, 저녁 식단을 추천해주세요.

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

        # 3. Gemini API 호출
        response = model.generate_content(
            prompt,
            request_options={"timeout": 30}
        )

        # 4. Gemini 응답이 비어 있는 경우
        if not response.text:
            return jsonify({
                "success": False,
                "message": "추천 결과를 생성하지 못했습니다. 다시 시도해주세요."
            }), 500

        return jsonify({
            "success": True,
            "recommendation": response.text
        })

    except Exception as e:
        print("서버 오류:", e)

        return jsonify({
            "success": False,
            "message": "식단 추천 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        }), 500


if __name__ == "__main__":
    print("등록된 라우트 목록:")
    print(app.url_map)
    app.run(debug=True, port=5000)
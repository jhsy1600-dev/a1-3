from flask import Flask, request, jsonify
import os
import traceback
from google import genai

app = Flask(__name__)

@app.route("/api/recommend", methods=["GET", "POST"])
@app.route("/recommend", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def recommend():
    try:
        data = request.get_json(silent=True) or {}

        meal_style = data.get("mealStyle", "")
        prefer = data.get("prefer", "")
        avoid = data.get("avoid", "")
        budget = data.get("budget", "")

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY가 없습니다."}), 500

        client = genai.Client(api_key=api_key)

        prompt = f"""
        너는 식단 추천 AI야.

        아래 조건에 맞춰 하루 식단을 추천해줘.

        식사 스타일: {meal_style}
        선호 음식 또는 재료: {prefer}
        피하고 싶은 음식: {avoid}
        하루 예산: {budget}원

        아침, 점심, 저녁으로 나눠서 추천하고,
        각 메뉴를 추천한 이유도 짧게 설명해줘.
        한국어로 답변해줘.
        """

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return jsonify({
            "recommendation": response.text
        })

    except Exception as e:
        print("===== SERVER ERROR =====")
        print(str(e))
        print(traceback.format_exc())

        return jsonify({
            "error": "서버 응답 오류",
            "detail": str(e)
        }), 500
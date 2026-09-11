import os
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

@app.route("/")
@app.route("/api/recommend", methods=["GET", "POST"])
@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if request.method == "GET":
        return jsonify({
            "success": True,
            "message": "Today Menu AI API is running"
        })

    try:
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            return jsonify({
                "success": False,
                "error": "GEMINI_API_KEY 환경변수가 없습니다."
            }), 500

        data = request.get_json(silent=True) or {}

        style = data.get("style", "")
        preferred = data.get("preferred", "")
        avoid = data.get("avoid", "")
        budget = data.get("budget", "")

        prompt = f"""
        하루 식단을 추천해줘.

        식사 스타일: {style}
        선호 음식 또는 재료: {preferred}
        피하고 싶은 음식: {avoid}
        하루 예산: {budget}원

        아침, 점심, 저녁으로 나누어 추천하고,
        간단한 이유도 함께 설명해줘.
        """

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        return jsonify({
            "success": True,
            "result": response.text
        })

    except Exception as e:
        print("===== SERVER ERROR =====")
        print(str(e))
        print(traceback.format_exc())

        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


@app.route("/", methods=["GET", "POST", "OPTIONS"])
@app.route("/api/recommend", methods=["GET", "POST", "OPTIONS"])
@app.route("/recommend", methods=["GET", "POST", "OPTIONS"])
def recommend():
    if request.method == "OPTIONS":
        return "", 204

    if request.method == "GET":
        return jsonify({
            "success": True,
            "message": "Today Menu AI API is running"
        })

    try:
        data = request.get_json()

        style = data.get("style", "")
        prefer = data.get("prefer", "")
        avoid = data.get("avoid", "")
        budget = data.get("budget", "")

        prompt = f"""
        사용자의 조건에 맞는 하루 식단을 추천해줘.

        식사 스타일: {style}
        선호 음식 또는 재료: {prefer}
        피하고 싶은 음식: {avoid}
        하루 예산: {budget}원

        아침, 점심, 저녁 식단을 추천해줘.
        각 식사는 메뉴, 설명, 예상 비용을 포함해줘.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        return jsonify({
            "success": True,
            "recommendation": response.text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
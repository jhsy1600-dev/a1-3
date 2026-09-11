import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

MODEL_NAME = "gemini-3.6-flash"


@app.route("/", methods=["GET"])
@app.route("/api/recommend", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Today Menu AI API is running",
        "model": MODEL_NAME
    })


@app.route("/", methods=["POST"])
@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()

        style = data.get("style", "")
        prefer = data.get("prefer", "")
        avoid = data.get("avoid", "")
        budget = data.get("budget", "")

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            return jsonify({
                "error": "GEMINI_API_KEY 환경변수가 설정되지 않았습니다."
            }), 500

        prompt = f"""
너는 식단 추천 전문가야.

아래 조건에 맞춰 하루 식단표를 한국어로 추천해줘.

식사 스타일: {style}
선호 음식 또는 재료: {prefer}
피하고 싶은 음식: {avoid}
하루 예산: {budget}원

아침, 점심, 저녁으로 나눠서 추천하고,
각 식사의 간단한 설명과 예상 비용도 포함해줘.
"""

        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{"gemini-3.6-flash"}:generateContent"
            f"?key={api_key}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        gemini_response = requests.post(url, json=payload)

        if gemini_response.status_code != 200:
            return jsonify({
                "error": "Gemini API 호출에 실패했습니다.",
                "status_code": gemini_response.status_code,
                "detail": gemini_response.text
            }), 500

        result = gemini_response.json()

        answer = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({
            "result": answer
        })

    except Exception as e:
        return jsonify({
            "error": "서버 내부 오류가 발생했습니다.",
            "detail": str(e)
        }), 500
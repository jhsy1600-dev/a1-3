import os
import traceback
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
@app.route("/api/recommend", methods=["GET"])
@app.route("/recommend", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Today Menu AI API is running"
    })


@app.route("/api/recommend", methods=["POST"])
@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # 1. 요청 데이터 받기
        data = request.get_json(silent=True) or {}

        meal_style = data.get("mealStyle", "")
        preferred_food = data.get("preferredFood", "")
        avoid_food = data.get("avoidFood", "")
        budget = data.get("budget", "")

        # 2. 기본 검증
        if not meal_style:
            return jsonify({
                "error": "식사 스타일이 없습니다."
            }), 400

        if not budget:
            return jsonify({
                "error": "예산이 없습니다."
            }), 400

        # 3. 환경변수 확인
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            return jsonify({
                "error": "GEMINI_API_KEY 환경변수가 설정되지 않았습니다."
            }), 500

        # 4. 프롬프트 작성
        prompt = f"""
너는 식단 추천 AI야.

아래 정보를 바탕으로 하루 식단을 추천해줘.

식사 스타일: {meal_style}
선호 음식 또는 재료: {preferred_food}
피하고 싶은 음식: {avoid_food}
하루 예산: {budget}원

조건:
- 아침, 점심, 저녁을 추천해줘.
- 예산을 고려해줘.
- 피하고 싶은 음식은 제외해줘.
- 한국어로 답변해줘.
- 너무 길지 않게 보기 좋게 정리해줘.

답변 형식:

아침:
메뉴:
이유:
예상 비용:

점심:
메뉴:
이유:
예상 비용:

저녁:
메뉴:
이유:
예상 비용:
"""

        # 5. Gemini REST API 호출
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-2.0-flash:generateContent"
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

        headers = {
            "Content-Type": "application/json"
        }

        gemini_response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        # 6. Gemini API 오류 처리
        if not gemini_response.ok:
            return jsonify({
                "error": "Gemini API 호출에 실패했습니다.",
                "status_code": gemini_response.status_code,
                "detail": gemini_response.text
            }), 500

        gemini_data = gemini_response.json()

        # 7. 응답 텍스트 추출
        try:
            recommendation = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return jsonify({
                "error": "Gemini 응답 형식이 예상과 다릅니다.",
                "detail": gemini_data
            }), 500

        # 8. 프론트 main.js가 기대하는 형태로 반환
        return jsonify({
            "recommendation": recommendation
        })

    except Exception as e:
        print("SERVER ERROR")
        print(traceback.format_exc())

        return jsonify({
            "error": "서버 내부 오류가 발생했습니다.",
            "detail": str(e),
            "trace": traceback.format_exc()
        }), 500
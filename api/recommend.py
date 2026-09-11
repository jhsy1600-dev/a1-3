import os
import traceback
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

        # 4. google-genai import
        # import를 함수 안에서 해야 import 실패도 JSON으로 확인할 수 있습니다.
        try:
            from google import genai
        except Exception as import_error:
            return jsonify({
                "error": "google-genai import에 실패했습니다.",
                "detail": str(import_error)
            }), 500

        # 5. Gemini 클라이언트 생성
        client = genai.Client(api_key=api_key)

        # 6. 프롬프트 작성
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

        # 7. Gemini 호출
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        recommendation = response.text

        # 8. 프론트 main.js가 기대하는 recommendation 형태로 반환
        return jsonify({
            "recommendation": recommendation
        })

    except Exception as e:
        # Vercel 로그에도 찍히게 함
        print("SERVER ERROR")
        print(traceback.format_exc())

        # 브라우저에도 JSON으로 에러 반환
        return jsonify({
            "error": "서버 내부 오류가 발생했습니다.",
            "detail": str(e),
            "trace": traceback.format_exc()
        }), 500
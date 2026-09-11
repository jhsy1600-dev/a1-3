document.addEventListener("DOMContentLoaded", () => {
  const recommendBtn = document.getElementById("recommendBtn");
  const mealStyleInput = document.getElementById("mealStyle");
  const preferredFoodInput = document.getElementById("preferredFood");
  const avoidFoodInput = document.getElementById("avoidFood");
  const budgetInput = document.getElementById("budget");
  const loadingText = document.getElementById("loading");
  const resultBox = document.getElementById("result");

  // Flask/Vercel API 주소
  const API_URL = "/api/recommend";

  // HTML 특수문자 처리 함수
  // Gemini 응답에 <, > 같은 문자가 있어도 HTML로 실행되지 않게 막아줍니다.
  function escapeHTML(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  // 줄바꿈을 <br>로 바꾸는 함수
  function formatText(text) {
    return escapeHTML(text).replace(/\n/g, "<br>");
  }

  recommendBtn.addEventListener("click", async () => {
    const mealStyle = mealStyleInput.value.trim();
    const preferredFood = preferredFoodInput.value.trim();
    const avoidFood = avoidFoodInput.value.trim();
    const budgetText = budgetInput.value.trim();

    // 결과창 초기화
    resultBox.innerHTML = "";

    // 1. 식사 스타일 검사
    if (!mealStyle) {
      resultBox.innerHTML = `
        <p style="color: red;">식사 스타일을 입력해주세요.</p>
      `;
      mealStyleInput.focus();
      return;
    }

    // 2. 예산 빈 값 검사
    if (!budgetText) {
      resultBox.innerHTML = `
        <p style="color: red;">예산을 입력해주세요.</p>
      `;
      budgetInput.focus();
      return;
    }

    // 3. 예산 숫자 검사
    const budget = Number(budgetText);

    if (Number.isNaN(budget)) {
      resultBox.innerHTML = `
        <p style="color: red;">예산은 숫자로 입력해주세요.</p>
      `;
      budgetInput.focus();
      return;
    }

    // 4. 예산 0 이하 검사
    if (budget <= 0) {
      resultBox.innerHTML = `
        <p style="color: red;">예산은 1원 이상 입력해주세요.</p>
      `;
      budgetInput.focus();
      return;
    }

    // 5. 로딩 표시
    loadingText.style.display = "block";
    recommendBtn.disabled = true;
    recommendBtn.textContent = "추천받는 중...";

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          mealStyle,
          preferredFood,
          avoidFood,
          budget
        })
      });

      /*
        중요:
        response.json()을 바로 쓰지 않고 response.text()로 먼저 받습니다.
        이유:
        서버가 500 에러를 낼 때 JSON이 아닌 일반 텍스트를 보내면
        response.json()에서 SyntaxError가 발생하기 때문입니다.
      */
      const responseText = await response.text();

      let data = null;

      try {
        data = JSON.parse(responseText);
      } catch (jsonError) {
        console.error("JSON 파싱 실패:", jsonError);
        console.error("서버 원본 응답:", responseText);

        throw new Error(
          `서버가 JSON이 아닌 응답을 반환했습니다. 응답 내용: ${responseText.slice(0, 200)}`
        );
      }

      // 서버 응답이 200번대가 아닐 때
      if (!response.ok) {
        throw new Error(
          data.detail ||
          data.message ||
          data.error ||
          `서버 오류가 발생했습니다. 상태 코드: ${response.status}`
        );
      }

      // 6. Gemini가 recommendation 문자열로 보내는 경우
      if (data.recommendation) {
        resultBox.innerHTML = `
          <h2>✨ 추천 식단</h2>
          <div class="recommendation">
            ${formatText(data.recommendation)}
          </div>
        `;
        return;
      }

      // 7. 백엔드가 result 문자열로 보내는 경우
      // 이전에 작성한 Flask 예시에서는 result로 응답할 수 있습니다.
      if (data.result) {
        resultBox.innerHTML = `
          <h2>✨ 추천 식단</h2>
          <div class="recommendation">
            ${formatText(data.result)}
          </div>
        `;
        return;
      }

      // 8. breakfast/lunch/dinner 구조로 보내는 경우
      if (data.breakfast && data.lunch && data.dinner) {
        resultBox.innerHTML = `
          <h2>✨ 추천 식단</h2>

          <div class="menu-card">
            <h3>아침</h3>
            <p><strong>메뉴:</strong> ${formatText(data.breakfast.menu || "")}</p>
            <p>${formatText(data.breakfast.description || "")}</p>
            <p><strong>예상 비용:</strong> ${formatText(data.breakfast.cost || "")}원</p>
          </div>

          <div class="menu-card">
            <h3>점심</h3>
            <p><strong>메뉴:</strong> ${formatText(data.lunch.menu || "")}</p>
            <p>${formatText(data.lunch.description || "")}</p>
            <p><strong>예상 비용:</strong> ${formatText(data.lunch.cost || "")}원</p>
          </div>

          <div class="menu-card">
            <h3>저녁</h3>
            <p><strong>메뉴:</strong> ${formatText(data.dinner.menu || "")}</p>
            <p>${formatText(data.dinner.description || "")}</p>
            <p><strong>예상 비용:</strong> ${formatText(data.dinner.cost || "")}원</p>
          </div>
        `;
        return;
      }

      // 9. 예상하지 못한 응답 구조
      console.log("예상하지 못한 서버 응답:", data);

      resultBox.innerHTML = `
        <p style="color: red;">
          서버 응답 형식이 올바르지 않습니다.<br>
          콘솔에서 서버 응답을 확인해주세요.
        </p>
      `;

    } catch (error) {
      console.error("요청 오류:", error);

      resultBox.innerHTML = `
        <p style="color: red;">
          서버 요청 중 오류가 발생했습니다.<br>
          오류 내용: ${formatText(error.message)}
        </p>
      `;

    } finally {
      loadingText.style.display = "none";
      recommendBtn.disabled = false;
      recommendBtn.textContent = "추천받기";
    }
  });
});
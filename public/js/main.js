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

      const data = await response.json();

if (!response.ok) {
  throw new Error(data.message || "서버 응답 오류");
}

      // 6. Gemini가 recommendation 문자열로 보내는 경우
      if (data.recommendation) {
        resultBox.innerHTML = `
          <h2>✨ 추천 식단</h2>
          <div class="recommendation">
            ${data.recommendation.replace(/\n/g, "<br>")}
          </div>
        `;
        return;
      }

      // 7. breakfast/lunch/dinner 구조로 보내는 경우
      if (data.breakfast && data.lunch && data.dinner) {
        resultBox.innerHTML = `
          <h2>✨ 추천 식단</h2>

          <div class="menu-card">
            <h3>아침</h3>
            <p><strong>메뉴:</strong> ${data.breakfast.menu}</p>
            <p>${data.breakfast.description}</p>
            <p><strong>예상 비용:</strong> ${data.breakfast.cost}원</p>
          </div>

          <div class="menu-card">
            <h3>점심</h3>
            <p><strong>메뉴:</strong> ${data.lunch.menu}</p>
            <p>${data.lunch.description}</p>
            <p><strong>예상 비용:</strong> ${data.lunch.cost}원</p>
          </div>

          <div class="menu-card">
            <h3>저녁</h3>
            <p><strong>메뉴:</strong> ${data.dinner.menu}</p>
            <p>${data.dinner.description}</p>
            <p><strong>예상 비용:</strong> ${data.dinner.cost}원</p>
          </div>
        `;
        return;
      }

      // 8. 예상하지 못한 응답 구조
      resultBox.innerHTML = `
        <p style="color: red;">
          서버 응답 형식이 올바르지 않습니다.
        </p>
      `;

   } catch (error) {
    console.error("요청 오류:", error);

    resultBox.innerHTML = `
        <p style="color: red;">
            서버 요청 중 오류가 발생했습니다.<br>
            오류 내용: ${error.message}
        </p>
    `;
    
    } finally {
      loadingText.style.display = "none";
      recommendBtn.disabled = false;
      recommendBtn.textContent = "추천받기";
    }
  });
});
// 當整個頁面內容載入完成後才執行程式碼。
document.addEventListener('DOMContentLoaded', function() {

  // 定義一個可供全域使用的函式 switchForm，用來切換登入與註冊表單。
  window.switchForm = function(target) {
    // 取得包裹表單的滑動容器。
    const slider = document.getElementById('sliderWrapper');

    // 取得單一表單區塊（假設登入與註冊表單寬度相同）。
    const formSlide = document.querySelector('.form-slide');

    // 確保 DOM 元素存在後再執行滑動操作。
    if (slider && formSlide) {
      // 取得單一表單區塊的寬度，用於計算滑動距離。
      const slideWidth = formSlide.offsetWidth;

      // 如果目標是註冊表單，將容器向左滑動一個表單寬度。
      if (target === 'register') {
        slider.style.transform = `translateX(-${slideWidth}px)`;
      }
      // 否則回到登入表單（將容器滑動回原位）。
      else {
        slider.style.transform = 'translateX(0)';
      }
    }
  };
});

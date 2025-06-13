/* 載入縣市與鄉鎮市區資料。 */
document.addEventListener('DOMContentLoaded', () => {
  // 從後端載入 Taiwan_dist.json（縣市與鄉鎮市區對應資料）。
  fetch('/static/json/Taiwan_dist.json')
    .then(res => res.ok ? res.json() : Promise.reject(`HTTP ${res.status}`))
    .then(data => {
      // 取得縣市與鄉鎮的下拉選單元素。
      const county = document.getElementById('lost_county');
      const district = document.getElementById('lost_district');

      // 如果縣市選單尚未有選項（只有預設項），就載入所有縣市名稱。
      if (county.options.length <= 1) {
        for (const city in data) {
          county.appendChild(new Option(city, city));
        }
      }

      // 當使用者選擇縣市後，更新對應的鄉鎮市區選單。
      county.addEventListener('change', () => {
        // 清空鄉鎮選單（保留第一個預設選項）。
        district.length = 1;
        // 根據所選縣市取得鄉鎮清單，並加入選單中。
        const districts = data[county.value] || [];
        districts.forEach(d => district.appendChild(new Option(d, d)));
      });
    })
    .catch(err => console.error('載入縣市資料失敗:', err));
});

/* 載入失物類別資料。 */
document.addEventListener('DOMContentLoaded', () => {
  // 從後端載入 categories.json（失物類別資料）。
  fetch('/static/json/categories.json')
    .then(res => res.ok ? res.json() : Promise.reject(`HTTP ${res.status}`))
    .then(data => {
      // 取得類別選單元素。
      const categoriesSelect = document.getElementById('lost_category');

      // 如果選單中尚未加載選項（只有預設 option），就加入所有類別。
      if (categoriesSelect.options.length <= 1) {
        data.categories.forEach(category => {
          const option = new Option(category, category);
          categoriesSelect.appendChild(option);
        });
      }
    })
    .catch(err => console.error('載入分類資料失敗:', err));
});

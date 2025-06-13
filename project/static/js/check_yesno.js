// 當使用者點擊「全部勾選」按鈕時，
// 將所有具有 .form-check-input 類別的 checkbox 勾選。
document.querySelector('.btn-check-all').addEventListener('click', function() {
  document.querySelectorAll('.form-check-input').forEach(function(checkbox) {
    checkbox.checked = true;
  });
});

// 當使用者點擊「全部取消」按鈕時，
// 將所有具有 .form-check-input 類別的 checkbox 取消勾選。
document.querySelector('.btn-uncheck-all').addEventListener('click', function() {
  document.querySelectorAll('.form-check-input').forEach(function(checkbox) {
    checkbox.checked = false;
  });
});

// 當使用者點擊「帳號審核通過」按鈕時觸發。
document.querySelector('.btn-agree').addEventListener('click', function() {
  // 找出所有已被勾選的 checkbox。
  const checkedBoxes = document.querySelectorAll('.form-check-input:checked');

  // 從每個 checkbox 的 id 中取出數字部分 (例如 check-1 → 1)。
  const ids = Array.from(checkedBoxes).map(cb => {
    return cb.id.split('-')[1];
  });

  // 如果沒有勾選任何帳號，就提示使用者。
  if (ids.length === 0) {
    alert('請先勾選帳號');
    return;
  }

  // 將勾選的帳號 id 傳送到後端 /passed 路由進行審核處理。
  fetch('/passed', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ids: ids
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // 審核成功後，從畫面移除對應的帳號卡片。
        checkedBoxes.forEach(cb => {
          const card = cb.closest('.col-12');
          if (card) card.remove();
        });
        alert('帳號已通過審核');
      } else {
        // 若後端回傳錯誤訊息，則顯示錯誤內容。
        alert('操作失敗: ' + data.message);
      }
    });
});

// 當使用者點擊「帳號審核未通過」按鈕時觸發。
document.querySelector('.btn-disagree').addEventListener('click', function() {
  // 找出所有已被勾選的 checkbox。
  const checkedBoxes = document.querySelectorAll('.form-check-input:checked');

  // 從每個 checkbox 的 id 中取出數字部分。
  const ids = Array.from(checkedBoxes).map(cb => {
    return cb.id.split('-')[1];
  });

  // 如果沒有勾選任何帳號，就提示使用者。
  if (ids.length === 0) {
    alert('請先勾選帳號');
    return;
  }

  // 將勾選的帳號 id 傳送到後端 /failed 路由進行審核處理。
  fetch('/failed', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ids: ids
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // 審核未通過後，從畫面移除對應的帳號卡片。
        checkedBoxes.forEach(cb => {
          const card = cb.closest('.col-12');
          if (card) card.remove();
        });
        alert('帳號未通過審核');
      } else {
        // 若後端回傳錯誤訊息，則顯示錯誤內容。
        alert('操作失敗: ' + data.message);
      }
    });
});

document.addEventListener('DOMContentLoaded', () => {
  const phoneInput = document.getElementById('phone');
  console.log("хуй тебе а не рабочий код")
  // Инициализация маски
  Inputmask({
    mask: "+7 (999) 999-99-99", // Маска для номера телефона
    placeholder: "_", // Заменяет пустые места
    clearIncomplete: true, // Очищает поле, если пользователь ввел неполный номер
    showMaskOnHover: false // Не показывать маску при наведении
  }).mask(phoneInput);
});
function show_hide_password(target){
  console.log("GO!")
	let input = document.getElementById('password-input');
	if (input.getAttribute('type') == 'password') {
    console.log("TEXT")
		target.classList.add('view');
		input.setAttribute('type', 'text');
	} else {
    console.log("PASS")
		target.classList.remove('view');
		input.setAttribute('type', 'password');
	}
	return false;
}

document.addEventListener('DOMContentLoaded', () => {
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const usernameError = document.getElementById('username-error');
  const passwordError = document.getElementById('password-error');
  const form = document.querySelector('form');

  // Функция для тряски
  const shakeElement = (element) => {
    element.classList.add('shake');
    setTimeout(() => element.classList.remove('shake'), 300);
  };

  form.addEventListener('submit', (event) => {
    let valid = true;

    // Проверка логина
    if (!usernameInput.value.trim()) {
      usernameError.textContent = 'Поле "Логин" обязательно для заполнения.';
      usernameInput.classList.add('error-field');
      shakeElement(usernameInput);
      valid = false;
    } else {
      usernameError.textContent = '';
      usernameInput.classList.remove('error-field');
    }

    // Проверка пароля
    if (!passwordInput.value.trim()) {
      passwordError.textContent = 'Поле "Пароль" обязательно для заполнения.';
      passwordInput.classList.add('error-field');
      shakeElement(passwordInput);
      valid = false;
    } else {
      passwordError.textContent = '';
      passwordInput.classList.remove('error-field');
    }

    if (!valid) {
      event.preventDefault(); // Останавливаем отправку формы, если невалидно
    }
  });
});
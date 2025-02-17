document.addEventListener('DOMContentLoaded', () => {
  const emailInput = document.getElementById('email');
  const phoneInput = document.getElementById('phone');
  const loginInput = document.getElementById('username');
  const password1Input = document.getElementById('password1');
  const password2Input = document.getElementById('password2');

  const submitButton = document.getElementById('submit-btn');

  const emailError = document.getElementById('email-error');
  const loginError = document.getElementById('username-error');
  const phoneError = document.getElementById('phone-error');
  const passwordError = document.getElementById('password-error');
  const password2Error = document.getElementById('password2-error');
  const agreementCheckbox = document.getElementById('agreement-checkbox');
  const checkboxError = document.getElementById('checkbox-error');

  // Устанавливаем маску для телефона
  Inputmask("+7 (999) 999-99-99").mask(phoneInput);

  // Функция для тряски элемента
  const shakeElement = (element) => {
    element.classList.add('shake');
    setTimeout(() => {
      element.classList.remove('shake');
    }, 300);
  };

  // Функция для проверки уникальности
  const checkUnique = async (field, value, errorElement, inputElement) => {
    try {
      const response = await fetch(`/check-unique?field=${field}&value=${encodeURIComponent(value)}`);
      const data = await response.json();

      if (!data.unique) {
        errorElement.textContent = `Такой ${field} уже существует.`;
        errorElement.style.display = 'block';
        inputElement.classList.add('input-error');
        return false;
      } else {
        errorElement.style.display = 'none';
        inputElement.classList.remove('input-error');
        return true;
      }
    } catch (error) {
      console.error('Ошибка при проверке уникальности:', error);
      return false;
    }
  };

  // Валидация логина
  loginInput.addEventListener('input', async () => {
    const value = loginInput.value.trim();

    if (!value) {
      loginError.textContent = 'Поле "Логин" обязательно для заполнения.';
      loginError.style.display = 'block';
      loginInput.classList.add('input-error');
    } else if (/\s/.test(value)) {
      loginError.textContent = 'Логин не должен содержать пробелов.';
      loginError.style.display = 'block';
      loginInput.classList.add('input-error');
    } else {
      const isUnique = await checkUnique('username', value, loginError, loginInput);
      if (isUnique) {
        loginError.style.display = 'none';
        loginInput.classList.remove('input-error');
      }
    }
  });

  // Валидация почты
  emailInput.addEventListener('input', async () => {
    const value = emailInput.value.trim();

    if (!value) {
      emailError.textContent = 'Поле "Почта" обязательно для заполнения.';
      emailError.style.display = 'block';
      emailInput.classList.add('input-error');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      emailError.textContent = 'Введите корректный Email.';
      emailError.style.display = 'block';
      emailInput.classList.add('input-error');
    } else {
      const isUnique = await checkUnique('email', value, emailError, emailInput);
      if (isUnique) {
        emailError.style.display = 'none';
        emailInput.classList.remove('input-error');
      }
    }
  });

  // Валидация телефона в реальном времени
  phoneInput.addEventListener('input', () => {
    const value = phoneInput.inputmask.unmaskedvalue(); // Получаем только цифры без маски

    if (value.length > 0 && value.length < 10) {  // В маске +7 уже есть, проверяем только 10 цифр
      phoneError.textContent = 'Недостаточно цифр для номера.';
      phoneError.style.display = 'block';
      phoneInput.classList.add('input-error');
    } else {
      phoneError.style.display = 'none';
      phoneInput.classList.remove('input-error');
    }
  });

  // Валидация пароля в реальном времени
  password1Input.addEventListener('input', () => {
    const value = password1Input.value.trim();
  if (!value) {
    passwordError.textContent = 'Поле "Пароль" обязательно для заполнения.';
    passwordError.style.display = 'block';
    password1Input.classList.add('input-error');
  }
  // Минимальная длина пароля
  else if (value.length < 8) {
    passwordError.textContent = 'Пароль должен содержать минимум 8 символов.';
    passwordError.style.display = 'block';
    password1Input.classList.add('input-error');
  }
  // Наличие хотя бы одной буквы
  else if (!/[a-zA-Z]/.test(value)) {
    passwordError.textContent = 'Пароль должен содержать хотя бы одну латинскую букву.';
    passwordError.style.display = 'block';
    password1Input.classList.add('input-error');
  }
  // Проверка на слишком простой пароль
  else if (/^\d+$/.test(value) || /^(.)\1+$/.test(value)) {
    passwordError.textContent = 'Пароль слишком простой. Используйте разные символы.';
    passwordError.style.display = 'block';
    password1Input.classList.add('input-error');
  } else {
      passwordError.style.display = 'none';
      password1Input.classList.remove('input-error');
    }
  });

  // Валидация подтверждения пароля в реальном времени
  password2Input.addEventListener('input', () => {
    const value = password2Input.value.trim();

    if (value !== password1Input.value.trim()) {
      password2Error.textContent = 'Пароли должны совпадать.';
      password2Error.style.display = 'block';
      password2Input.classList.add('input-error');
    } else {
      password2Error.style.display = 'none';
      password2Input.classList.remove('input-error');
    }
  });


  submitButton.addEventListener('click', async (event) => {
  event.preventDefault();
  let valid = true;

  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  // Проверка всех полей перед отправкой
  if (!loginInput.value.trim()) {
    loginError.textContent = 'Поле "Логин" обязательно для заполнения.';
    loginError.style.display = 'block';
    loginInput.classList.add('input-error');
    shakeElement(loginInput);
    valid = false;
  }

  if (!emailInput.value.trim()) {
    emailError.textContent = 'Поле "Почта" обязательно для заполнения.';
    emailError.style.display = 'block';
    emailInput.classList.add('input-error');
    shakeElement(emailInput);
    valid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim())) {
    emailError.textContent = 'Введите корректный Email.';
    emailError.style.display = 'block';
    emailInput.classList.add('input-error');
    shakeElement(emailInput);
    valid = false;
  }

  if (!password1Input.value.trim()) {
    passwordError.textContent = 'Поле "Пароль" обязательно для заполнения.';
    passwordError.style.display = 'block';
    password1Input.classList.add('input-error');
    shakeElement(password1Input);
    valid = false;
  }

  if (password2Input.value.trim() !== password1Input.value.trim()) {
    password2Error.textContent = 'Пароли должны совпадать.';
    password2Error.style.display = 'block';
    password2Input.classList.add('input-error');
    shakeElement(password2Input);
    valid = false;
  }

  if (!agreementCheckbox.checked) {
    checkboxError.textContent = 'Вы должны согласиться с пользовательским соглашением.';
    checkboxError.style.display = 'block';
    shakeElement(agreementCheckbox);
    valid = false;
  }

  // Если все проверки пройдены, отправляем данные на сервер
  if (valid) {
    const formData = new FormData();
    formData.append('username', loginInput.value.trim());
    formData.append('email', emailInput.value.trim());
    formData.append('password1', password1Input.value.trim());
    formData.append('password2', password2Input.value.trim());
    formData.append('phone', phoneInput.value.trim());

    try {
      const response = await fetch('/register/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken, // Заголовок с токеном
  },
  body: formData,
      });
      const data = await response.json();
      if (data.success) {
        // Редирект на страницу логина
        window.location.href = '/login';
      } else {

        alert('Ошибка регистрации');
      }
    } catch (error) {
      console.error('Ошибка при отправке данных:', error);
    }
  }
});

  /* ГЛАЗ */
  const eye = document.querySelector('.eye');
  const iris = document.querySelector('.iris');
  const pupil = document.querySelector('.pupil');

  // Функция для моргания
  function blink() {
    eye.style.transition = '0.2s';
    eye.style.height = '0px';
    setTimeout(() => {
      eye.style.height = '150px';
    }, 200);
  }

  // Случайное моргание
  setInterval(blink, 3000);

  // Движение радужки и зрачка
  document.addEventListener('mousemove', (event) => {
    const eyeRect = eye.getBoundingClientRect();
    const eyeCenterX = eyeRect.left + eyeRect.width / 2;
    const eyeCenterY = eyeRect.top + eyeRect.height / 2;

    const irisRadius = 40; // Максимальное движение радужки
    const pupilRadius = 15; // Максимальное движение зрачка

    // Координаты курсора относительно центра глаза
    const deltaX = event.clientX - eyeCenterX;
    const deltaY = event.clientY - eyeCenterY;

    // Угол и расстояние
    const angle = Math.atan2(deltaY, deltaX);
    const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY), irisRadius);

    // Новые координаты для радужки
    const irisX = Math.cos(angle) * distance;
    const irisY = Math.sin(angle) * distance;

    // Новые координаты для зрачка
    const pupilX = Math.cos(angle) * Math.min(distance, pupilRadius);
    const pupilY = Math.sin(angle) * Math.min(distance, pupilRadius);

    iris.style.transform = `translate(${irisX}px, ${irisY}px) translate(-50%, -50%)`;
    pupil.style.transform = `translate(${pupilX}px, ${pupilY}px) translate(-50%, -50%)`;
  });

  // Закрытие глаза при фокусе на поле пароля
  password1Input.addEventListener('focus', () => {
    eye.style.height = '0px'; // Закрываем глаз
  });

  // Открытие глаза при потере фокуса с поля пароля
  password1Input.addEventListener('blur', () => {
    eye.style.height = '150px'; // Открываем глаз
  });
});

document.getElementById('agreement-link').addEventListener('click', function(e) {
  e.preventDefault(); // предотвращаем переход по ссылке
  document.getElementById('agreement-modal').style.display = 'block'; // показываем модальное окно
});

document.querySelector('.close').addEventListener('click', function() {
  document.getElementById('agreement-modal').style.display = 'none'; // скрываем модальное окно
});
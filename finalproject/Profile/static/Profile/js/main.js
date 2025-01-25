/* таинственный текст */

const btm = document.getElementById('btm-fog');
const text1 = document.getElementById("text1")
const text2 = document.getElementById('text2');

btm.addEventListener('click', () => {
  console.log("жмяк")
  text1.style.opacity = '0';
  text1.style.filter = 'blur(20px)'; // Эффект тумана
  setTimeout(() => {
    text2.style.opacity = '1';
    text2.style.transform = 'scale(1)';
  }, 1500); // Задержка для показа текста2
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
  const distance = Math.min(Math.sqrt(deltaX ** 2 + deltaY ** 2), irisRadius);

  // Новые координаты для радужки
  const irisX = Math.cos(angle) * distance;
  const irisY = Math.sin(angle) * distance;

  // Новые координаты для зрачка
  const pupilX = Math.cos(angle) * Math.min(distance, pupilRadius);
  const pupilY = Math.sin(angle) * Math.min(distance, pupilRadius);

  iris.style.transform = `translate(${irisX}px, ${irisY}px) translate(-50%, -50%)`;
  pupil.style.transform = `translate(${pupilX}px, ${pupilY}px) translate(-50%, -50%)`;
});


/* ЭКСПЕРЕМЕНТ */
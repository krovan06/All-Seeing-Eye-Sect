// звезды
const starCounts = { stars: 500, stars2: 300, stars3: 300 };
console.log("Это начало")

// Генерация случайных звезд
function generateStars(containerId, count) {
  const container = document.getElementById(containerId);
  for (let i = 0; i < count; i++) {
    const star = document.createElement("div");
    star.classList.add("star");

    // Случайное положение
    const x = Math.random() * 100; // От 0 до 100%
    const y = Math.random() * 200; // Выше экрана для анимации

    star.style.left = `${x}%`;
    star.style.top = `${y}%`;

    container.appendChild(star);
  }
}

// Генерация звезд для всех слоев
Object.entries(starCounts).forEach(([id, count]) => generateStars(id, count));
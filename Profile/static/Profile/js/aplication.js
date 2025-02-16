document.addEventListener("DOMContentLoaded", function() {
    let commentForm = document.getElementById("commentForm");
    let commentText = document.getElementById("commentText");
    let parentInput = document.getElementById("parent_id");

    document.querySelectorAll(".reply-button").forEach(button => {
        button.addEventListener("click", function() {
            let commentId = this.getAttribute("data-id");

            // Если уже есть активное поле ввода — убираем его
            let existingInput = document.querySelector(".reply-input");
            let existingButton = document.querySelector(".send-reply");

            if (existingInput) existingInput.remove();
            if (existingButton) existingButton.remove();

            // Создаём новое поле ввода под комментарием
            let inputField = document.createElement("textarea");
            inputField.classList.add("reply-input");
            inputField.placeholder = "Ваш ответ...";

            let submitButton = document.createElement("button");
            submitButton.textContent = "Отправить";
            submitButton.classList.add("send-reply");

            let commentBlock = this.closest(".comment");
            commentBlock.appendChild(inputField);
            commentBlock.appendChild(submitButton);

            parentInput.value = commentId; // Указываем ID родительского комментария
            inputField.focus();

            // Назначаем обработчик кнопке "Отправить"
            submitButton.addEventListener("click", function() {
                commentText.value = inputField.value; // Передаем текст в основное поле формы
                commentForm.dispatchEvent(new Event("submit")); // Отправляем форму
            });
        });
    });

    // Обработчик отправки формы (без перезагрузки)
    commentForm.addEventListener("submit", function(event) {
        event.preventDefault();

        let body = commentText.value;
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        let requestId = document.getElementById("request_id").value;
        let parentId = parentInput.value;

        fetch(window.location.pathname, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({ body: body, request_id: requestId, parent_id: parentId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let newComment = document.createElement("div");
                newComment.classList.add("comment");
                newComment.setAttribute("data-id", data.comment_id); // ID нового комментария
                newComment.innerHTML = `
                    <p><strong>${data.username}</strong>:</p>
                    <p>${data.body}</p>
                    <p><small>Только что</small></p>
                    <button class="reply-button" data-id="${data.comment_id}">Ответить</button>
                    <div class="replies"></div>
                `;

                if (data.parent_id) {
                    let parentComment = document.querySelector(`.comment[data-id='${data.parent_id}'] .replies`);
                    if (parentComment) {
                        parentComment.appendChild(newComment);
                    }
                } else {
                    document.getElementById("commentsContainer").prepend(newComment);
                }

                commentText.value = "";
                parentInput.value = "";

                // Удаляем временное поле ввода после отправки
                let existingInput = document.querySelector(".reply-input");
                let existingButton = document.querySelector(".send-reply");
                if (existingInput) existingInput.remove();
                if (existingButton) existingButton.remove();
            } else {
                alert("Ошибка при добавлении комментария.");
            }
        })
        .catch(error => console.error("Ошибка:", error));
    });
});






(function() {
  const canvas = document.getElementById("particlesCanvas");
  const ctx = canvas.getContext("2d");
  const particleCount = 50;
  const particles = [];

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  class Particle {
    constructor() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.radius = Math.random() * 4 + 1;
      this.vx = (Math.random() - 0.5) * 0.8;
      this.vy = (Math.random() - 0.5) * 0.7;
      this.color = this.color = 'rgba(200, 188, 92, 0.8)';
    }

    move() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x > canvas.width) this.x = 0;
      if (this.x < 0) this.x = canvas.width;
      if (this.y > canvas.height) this.y = 0;
      if (this.y < 0) this.y = canvas.height;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = this.color;
      ctx.fill();
    }
  }

  function createParticles() {
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(particle => {
      particle.move();
      particle.draw();
    });
    requestAnimationFrame(animate);
  }

  createParticles();
  animate();

  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    particles.length = 0;
    createParticles();
  });
})();
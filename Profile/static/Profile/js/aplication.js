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


document.addEventListener("DOMContentLoaded", function () {
    let editingInProgress = {}; // Сохраняем состояния редактирования для каждого комментария

    document.querySelectorAll(".edit-button").forEach(button => {
        button.addEventListener("click", function () {
            let commentId = this.dataset.id;
            let commentElement = this.closest(".comment").querySelector("p:nth-of-type(2)"); // Второй <p>, где текст

            if (!commentElement || editingInProgress[commentId]) return;

            // Сохраняем старый текст
            let oldText = commentElement.textContent;
            let textarea = document.createElement("textarea");
            textarea.classList.add("edit-textarea");
            textarea.value = oldText;

            commentElement.replaceWith(textarea);

            let saveButton = document.createElement("button");
            saveButton.textContent = "Сохранить";
            saveButton.classList.add("save-button");
            saveButton.dataset.id = commentId;

            textarea.after(saveButton);
            editingInProgress[commentId] = true;

            saveButton.addEventListener("click", function () {
                let newText = textarea.value.trim();
                if (!newText) {
                    alert("Комментарий не может быть пустым!");
                    return;
                }

                fetch(`/edit_comment/${commentId}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({ body: newText })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let newParagraph = document.createElement("p");
                        newParagraph.classList.add("comment-body");
                        newParagraph.textContent = newText;
                        textarea.replaceWith(newParagraph);
                        saveButton.remove();
                        editingInProgress[commentId] = false;
                    } else {
                        alert("Ошибка при сохранении: " + (data.error || "Неизвестная ошибка"));
                    }
                })
                .catch(error => {
                    console.error("Ошибка запроса:", error);
                    alert("Ошибка при сохранении комментария");
                });
            });
        });
    });
});




document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".mark-read-btn").forEach(button => {
        button.addEventListener("click", function () {
            let commentId = this.getAttribute("data-comment-id");

            fetch("/mark-comment-read/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("input[name='csrfmiddlewaretoken']").value
                },
                body: JSON.stringify({ comment_id: commentId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`indicator-${commentId}`).remove();
                    this.remove();
                }
            })
            .catch(error => console.error("Ошибка:", error));
        });
    });
});


// Обработчик нажатия на кнопку удаления комментария
document.querySelectorAll('.delete-comment-btn').forEach(button => {
    button.addEventListener('click', function() {
        const commentId = this.getAttribute('data-comment-id');
        if (confirm('Вы уверены, что хотите удалить этот комментарий?')) {
            fetch(`/delete-comment/${commentId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                }
            })
            .then(response => {
                if (response.ok) {
                    // Удаляем строку комментария из таблицы
                    this.closest('tr').remove();
                } else {
                    alert('Ошибка при удалении комментария.');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
        }
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
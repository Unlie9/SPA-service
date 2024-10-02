<template>
  <div class="comments-section">
    <!-- Основной список комментариев -->
    <ul class="comments-list">
      <li v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-box">
          <strong>{{ comment.username }}</strong> ({{ formatDate(comment.created_at) }}):
          <p>{{ comment.text }}</p>
          <a v-if="comment.home_page" :href="comment.home_page" class="home-page-link">{{ comment.home_page }}</a>
          <br />
          <button @click="setReply(comment.id)" class="reply-button">Ответить</button>

          <!-- Кнопка для отображения комментариев -->
          <button v-if="!comment.showReplies" @click="toggleReplies(comment)" class="view-replies-button">
            Посмотреть комментарии ({{ comment.replies.length }})
          </button>

          <!-- Кнопка для скрытия комментариев -->
          <button v-else @click="toggleReplies(comment)" class="hide-replies-button">
            Скрыть комментарии
          </button>

          <!-- Отображение ответов для данного комментария -->
          <ul v-if="comment.showReplies" class="reply-list">
            <li v-for="reply in comment.replies" :key="reply.id" class="reply-item">
              <div class="reply-box">
                <strong>{{ reply.username }}</strong> ({{ formatDate(reply.created_at) }}):
                <p>{{ reply.text }}</p>
                <a v-if="reply.home_page" :href="reply.home_page" class="home-page-link">{{ reply.home_page }}</a>
              </div>
            </li>
          </ul>
        </div>
      </li>
    </ul>

    <!-- Форма для добавления нового родительского комментария -->
    <form @submit.prevent="sendCommentOrReply" class="comment-form">
      <textarea v-model="newComment" placeholder="Напишите сообщение..." class="textarea"></textarea>
      <input v-model="homePage" placeholder="Ваш сайт (опционально)" type="url" class="input" />

      <!-- Индикация, что идет ответ на комментарий -->
      <div v-if="replyTo" class="reply-indicator">
        Ответ на комментарий ID: {{ replyTo }}
        <button @click="cancelReply" class="cancel-reply">Отменить</button>
      </div>

      <button type="submit" class="submit-button">
        {{ replyTo ? 'Ответить' : 'Make a Post' }}
      </button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      comments: [],  // Основные комментарии
      newComment: "",
      homePage: "",
      replyTo: null,  // ID комментария, на который отвечаем (если есть)
      socket: null
    };
  },
  methods: {
    connectWebSocket() {
      const token = localStorage.getItem('jwt');
      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        // Запрашиваем комментарии при подключении
        this.socket.send(JSON.stringify({action: "list_comments"}));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === "list_comments") {
          // Добавляем поле showReplies для каждого комментария, чтобы управлять отображением ответов
          this.comments = data.comments.map(comment => ({
            ...comment,
            showReplies: false  // Изначально ответы скрыты
          }));
        }
      };

      this.socket.onerror = (error) => {
        console.error("Ошибка WebSocket:", error);
      };

      this.socket.onclose = () => {
        console.log("WebSocket отключен");
      };
    },

    sendCommentOrReply() {
      if (this.newComment.trim()) {
        const action = this.replyTo ? "reply_comment" : "create_comment";
        const payload = {
          action,
          text: this.newComment,
          home_page: this.homePage
        };

        // Если это ответ на комментарий, добавляем ID родительского комментария
        if (this.replyTo) {
          payload.reply_id = this.replyTo;
        }

        this.socket.send(JSON.stringify(payload));

        // Очищаем форму после отправки
        this.newComment = "";
        this.homePage = "";
        this.replyTo = null;
      }
    },

    setReply(commentId) {
      this.replyTo = commentId;  // Устанавливаем ID комментария, на который отвечаем
    },

    cancelReply() {
      this.replyTo = null;  // Сбрасываем состояние ответа
    },

    toggleReplies(comment) {
      comment.showReplies = !comment.showReplies;  // Переключаем отображение ответов
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}`;
    }
  },
  mounted() {
    this.connectWebSocket();
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  }
};
</script>

<style scoped>
.comments-section {
  max-width: 800px;
  margin: 0 auto;
}

.comments-list {
  list-style-type: none;
  padding: 0;
}

.comment-item {
  margin-bottom: 20px;
}

.comment-box {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.reply-box {
  padding-left: 30px;
  margin-top: 10px;
  border-left: 3px solid #007bff;
  background-color: #f1f1f1;
}

.reply-list {
  list-style-type: none;
  padding-left: 0;
}

.textarea, .input {
  width: 100%;
  margin-bottom: 10px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.submit-button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
}

.submit-button:hover {
  background-color: #218838;
}

.home-page-link {
  color: #007bff;
  text-decoration: underline;
}

.reply-indicator {
  margin-bottom: 10px;
  font-size: 0.9em;
  color: #007bff;
}

.cancel-reply {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
  font-size: 0.9em;
}

.reply-button {
  background-color: transparent;
  border: none;
  color: #007bff;
  cursor: pointer;
}

.reply-button:hover {
  text-decoration: underline;
}

.view-replies-button, .hide-replies-button {
  background-color: transparent;
  border: none;
  color: #007bff;
  cursor: pointer;
}

.view-replies-button:hover, .hide-replies-button:hover {
  text-decoration: underline;
}
</style>

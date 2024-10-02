<template>
  <div>
    <!-- Основной список комментариев -->
    <ul>
      <li v-for="comment in comments" :key="comment.id">
        <!-- Отображение основного комментария -->
        <div class="comment-box">
          <strong>{{ comment.username }}</strong> ({{ formatDate(comment.created_at) }}):
          <p>{{ comment.text }}</p>
          <a v-if="comment.home_page" :href="comment.home_page">{{ comment.home_page }}</a>
          <br />
          <button @click="setReply(comment.id)">Ответить</button>
        </div>

        <!-- Отображение ответов на комментарий -->
        <ul v-if="comment.replies && comment.replies.length > 0" class="reply-list">
          <li v-for="reply in comment.replies" :key="reply.id">
            <div class="reply-box">
              <strong>{{ reply.username }}</strong> ({{ formatDate(reply.created_at) }}):
              <p>{{ reply.text }}</p>
              <a v-if="reply.home_page" :href="reply.home_page">{{ reply.home_page }}</a>
              <br />
              <button @click="setReply(reply.id)">Ответить</button>
              <comment-list :comments="reply.replies"></comment-list>
            </div>
          </li>
        </ul>
      </li>
    </ul>

    <!-- Форма для добавления нового комментария или ответа -->
    <form @submit.prevent="sendCommentOrReply" class="comment-form">
      <textarea v-model="newComment" placeholder="Напишите комментарий..." class="textarea"></textarea>
      <input v-model="homePage" placeholder="Ваш сайт (опционально)" type="url" class="input"/>

      <!-- Индикация, что идет ответ на комментарий -->
      <div v-if="replyTo" class="reply-indicator">
        Ответ на комментарий ID: {{ replyTo }}
        <button @click="cancelReply" class="cancel-reply">Отменить</button>
      </div>

      <button type="submit" class="submit-button">
        {{ replyTo ? 'Ответить' : 'Отправить' }}
      </button>
    </form>
  </div>
</template>

<script>
import CommentList from './CommentList.vue';  // Импортируем рекурсивный компонент

export default {
  components: {
    CommentList  // Регистрируем компонент
  },
  data() {
    return {
      comments: [],  // Основные комментарии
      replies: [],   // Ответы на комментарии
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
        // Запрашиваем как комментарии, так и ответы при подключении
        this.socket.send(JSON.stringify({action: "list_comments"}));
        this.socket.send(JSON.stringify({action: "list_replies"}));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket received data:', data);

        if (data.action === "list_comments") {
          this.comments = data.comments; // Получаем основные комментарии
        } else if (data.action === "list_replies") {
          this.replies = data.replies || []; // Получаем ответы
          console.log('Replies:', this.replies);
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


    getRepliesForComment(commentId) {
      return this.replies ? this.replies.filter(reply => {
        // Если поле reply содержит объект с id или это просто id
        return reply.reply === commentId || (reply.reply && reply.reply.id === commentId);
      }) : [];
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
.comment-box {
  padding: 10px;
  border-bottom: 1px solid #ccc;
}

.reply-box {
  padding-left: 20px;
  margin-top: 10px;
  border-left: 2px solid #007bff;
}

.reply-list {
  list-style-type: none;
  margin-left: 20px;
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
}
</style>

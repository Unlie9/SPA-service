<template>
  <div class="comments-container">
    <div class="comments-section">
      <ul class="comments-list">
        <li v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-box">
            <div class="comment-header">
              <div class="avatar">{{ comment.username.charAt(0).toUpperCase() }}</div>
              <strong class="comment-username">{{ comment.username }}</strong>
              <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              <div class="comment-actions">
                <button @click="setReply(comment.id, comment.username, comment.text)" class="reply-button">Reply</button>
              </div>
            </div>

            <p class="comment-text">{{ comment.text }}</p>

            <!-- Вложенные комментарии -->
            <ul v-if="comment.replies && comment.replies.length > 0" class="reply-list">
              <li v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                <div class="reply-box">
                  <strong>{{ reply.username }}</strong>
                  <span class="comment-date">{{ formatDate(reply.created_at) }}</span>:
                  <p>{{ reply.text }}</p>
                  <button @click="setReply(reply.id, reply.username, reply.text)" class="reply-button">Reply</button>

                  <!-- Рекурсивное отображение вложенных ответов -->
                  <ul v-if="reply.replies && reply.replies.length > 0" class="reply-list">
                    <li v-for="nestedReply in reply.replies" :key="nestedReply.id" class="reply-item">
                      <div class="reply-box">
                        <strong>{{ nestedReply.username }}</strong>
                        <span class="comment-date">{{ formatDate(nestedReply.created_at) }}</span>:
                        <p>{{ nestedReply.text }}</p>
                        <button @click="setReply(nestedReply.id, nestedReply.username, nestedReply.text)" class="reply-button">Reply</button>
                      </div>
                    </li>
                  </ul>
                </div>
              </li>
            </ul>
          </div>
        </li>
      </ul>

      <!-- Форма для добавления комментария с отступом -->
      <form @submit.prevent="sendCommentOrReply" class="comment-form">
        <textarea v-model="newComment" placeholder="Write a message..." class="textarea"></textarea>
        <input v-model="homePage" placeholder="Your website (optional)" type="url" class="input"/>

        <div v-if="replyTo" class="reply-indicator">
          <span class="replying-text">
            Replying to "{{ replyToUsername }}" comment
            <br>
            "{{ replyToText }}"
          </span>
          <button @click="cancelReply" class="cancel-reply">Cancel</button>
        </div>

        <button type="submit" class="submit-button">
          {{ replyTo ? 'Reply' : 'Make a Post' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      comments: [],
      newComment: "",
      homePage: "",
      replyTo: null,
      replyToUsername: null,
      replyToText: null,
      socket: null,
    };
  },
  methods: {
    connectWebSocket() {
      const token = localStorage.getItem('jwt');
      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        this.socket.send(JSON.stringify({ action: "list_comments" }));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === "list_comments") {
          this.comments = data.comments;
        }
      };

      this.socket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      this.socket.onclose = () => {
        console.log("WebSocket disconnected");
      };
    },

    sendCommentOrReply() {
      if (this.newComment.trim()) {
        // Убираем условие с action "reply_comment"
        const payload = {
          action: "create_comment",  // Всегда используем "create_comment"
          text: this.newComment,
          home_page: this.homePage
        };

        if (this.replyTo) {
          payload.reply_id = this.replyTo;  // Если это ответ, добавляем reply_id
        }

        this.socket.send(JSON.stringify(payload));

        // Сбрасываем поля после отправки
        this.newComment = "";
        this.homePage = "";
        this.replyTo = null;
        this.replyToUsername = null;
        this.replyToText = null;
      }
    },

    setReply(commentId, username, text) {
      this.replyTo = commentId;
      this.replyToUsername = username;
      this.replyToText = text.slice(0, 20) + (text.length > 20 ? "..." : "");
    },

    cancelReply() {
      this.replyTo = null;
      this.replyToUsername = null;
      this.replyToText = null;
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = String(date.getFullYear()).slice(2);
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${day}.${month}.${year} at ${hours}:${minutes}`;
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

.comments-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  overflow: hidden;
}

.comments-section {
  background-color: #fff;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  height: 80vh;
  overflow-y: auto;
  position: relative;
}

.comments-list {
  list-style-type: none;
  padding: 0;
  margin: 20px 0;
}

.comment-item {
  margin-bottom: 20px;
}

.comment-box {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ddd;
  text-align: left;
  word-wrap: break-word;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.comment-username {
  font-size: 1.2rem;
  color: #333;
}

.comment-date {
  font-size: 0.9rem;
  color: #777;
}

.comment-text {
  margin: 15px 0;
  font-size: 1rem;
  color: #444;
}

.comment-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.avatar {
  width: 40px;
  height: 40px;
  background-color: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.textarea, .input {
  width: 100%;
  margin-bottom: 10px;
  padding: 16px;
  border-radius: 5px;
  border: 1px solid #ddd;
  font-size: 1.1rem;
  font-family: 'Roboto', sans-serif;
  word-wrap: break-word;
  resize: none;
  max-height: 200px;
  overflow-y: auto;
}

.submit-button {
  background-color: #764ba2;
  color: white;
  padding: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  width: 100%;
}

.submit-button:hover {
  background-color: #5e3c96;
}

.reply-list {
  padding-left: 20px;
  margin-top: 15px;
}

.reply-box {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 10px;
}

.comment-form {
  margin-top: 30px; /* Отступ перед формой */
}
</style>

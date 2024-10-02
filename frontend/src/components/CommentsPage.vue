<template>
  <div class="comments-section">
    <ul class="comments-list">
      <li v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-box">
          <div class="comment-header">
            <div class="avatar">{{ comment.username.charAt(0).toUpperCase() }}</div>
            <strong>{{ comment.username }}</strong>
            <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
          </div>

          <button @click="toggleEmail(comment.id)" class="info-button">Email</button>
          <div v-if="comment.showEmail" class="email-info">{{ comment.email }}</div>

          <button @click="toggleHomepage(comment.id)" class="info-button">Homepage</button>
          <div v-if="comment.showHomepage" class="homepage-info">{{ comment.home_page }}</div>

          <button @click="setReply(comment.id)" class="reply-button">Reply</button>

          <button v-if="!comment.showReplies && comment.replies && comment.replies.length > 0"
                  @click="toggleReplies(comment)" class="view-replies-button">
            View comments ({{ comment.replies.length }})
          </button>

          <button v-if="comment.showReplies && comment.replies && comment.replies.length > 0"
                  @click="toggleReplies(comment)" class="hide-replies-button">
            Hide comments
          </button>
          <p>{{ comment.text }}</p>

          <ul v-if="comment.showReplies && comment.replies && comment.replies.length > 0" class="reply-list">
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

    <form @submit.prevent="sendCommentOrReply" class="comment-form">
      <textarea v-model="newComment" placeholder="Write a message..." class="textarea"></textarea>
      <input v-model="homePage" placeholder="Your website (optional)" type="url" class="input"/>

      <div v-if="replyTo" class="reply-indicator">
        Replying to comment ID: {{ replyTo }}
        <button @click="cancelReply" class="cancel-reply">Cancel</button>
      </div>

      <button type="submit" class="submit-button">
        {{ replyTo ? 'Reply' : 'Make a Post' }}
      </button>
    </form>
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
      socket: null
    };
  },
  methods: {
    connectWebSocket() {
      const token = localStorage.getItem('jwt');
      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        this.socket.send(JSON.stringify({action: "list_comments"}));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === "list_comments") {
          const updatedComments = data.comments.map(comment => {
            const existingComment = this.comments.find(c => c.id === comment.id);
            return {
              ...comment,
              showReplies: existingComment ? existingComment.showReplies : false,
              replies: comment.replies || []
            };
          });

          this.comments = updatedComments;
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
        const action = this.replyTo ? "reply_comment" : "create_comment";
        const payload = {
          action,
          text: this.newComment,
          home_page: this.homePage
        };

        if (this.replyTo) {
          payload.reply_id = this.replyTo;
          const parentComment = this.comments.find(comment => comment.id === this.replyTo);
          if (parentComment) {
            parentComment.showReplies = true;
          }
        }

        this.socket.send(JSON.stringify(payload));

        this.newComment = "";
        this.homePage = "";
        this.replyTo = null;
      }
    },

    setReply(commentId) {
      this.replyTo = commentId;
    },

    cancelReply() {
      this.replyTo = null;
    },

    toggleReplies(comment) {
      comment.showReplies = !comment.showReplies;
    },

    toggleEmail(commentId) {
      const comment = this.comments.find(c => c.id === commentId);
      comment.showEmail = !comment.showEmail;
    },

    toggleHomepage(commentId) {
      const comment = this.comments.find(c => c.id === commentId);
      comment.showHomepage = !comment.showHomepage;
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
/* Общий фон */
body {
  background: linear-gradient(to right, #e0e0e0, #ffffff, #e0e0e0);
}

/* Основной контейнер комментариев */
.comments-section {
  background-color: #fff;
  padding: 2vw;
  max-width: 80%;
  margin: 2vw auto;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Список комментариев */
.comments-list {
  list-style-type: none;
  padding: 0;
}

.comment-item {
  margin-bottom: 2vw;
}

.comment-box {
  padding: 2vw;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  opacity: 0;
  animation: fadeIn 0.7s forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Секция ответа */
.reply-box {
  padding-left: 30px;
  margin-top: 10px;
  border-left: 3px solid #007bff;
  background-color: #f1f1f1;
}

/* Плавный скролл ответов */
.reply-list {
  list-style-type: none;
  padding-left: 0;
  max-height: 300px;
  overflow-y: auto;
  transition: max-height 0.5s ease-in-out;
}

.reply-list::-webkit-scrollbar {
  width: 6px;
}

.reply-list::-webkit-scrollbar-thumb {
  background-color: #007bff;
  border-radius: 10px;
}

/* Поля ввода */
.textarea, .input {
  width: 100%;
  margin-bottom: 10px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* Кнопки */
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

.info-button {
  margin: 5px;
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.info-button:hover {
  transform: scale(1.05);
}

.home-page-link, .email-info, .homepage-info {
  margin-top: 10px;
  padding: 10px;
  background-color: #e9ecef;
  border-radius: 4px;
  transition: opacity 0.5s ease-in-out;
}

/* Аватар */
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
  margin-right: 10px;
  float: left;
}

/* Кнопки "Ответить" и показать/скрыть комментарии */
.reply-button, .view-replies-button, .hide-replies-button {
  background-color: transparent;
  border: none;
  color: #007bff;
  cursor: pointer;
  margin-top: 10px;
}

.reply-button:hover, .view-replies-button:hover, .hide-replies-button:hover {
  text-decoration: underline;
}
</style>

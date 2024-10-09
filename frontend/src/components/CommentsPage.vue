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
                <button @click="toggleEmailModal(comment)" class="info-button">Email</button>
                <button @click="handleHomepage(comment)" class="info-button">Homepage</button>
                <button @click="setReply(comment.id, comment.username, comment.text)" class="reply-button">Reply
                </button>
              </div>
            </div>

            <p class="comment-text">{{ comment.text }}</p>

            <button v-if="!comment.showReplies && comment.replies && comment.replies.length > 0"
                    @click="toggleReplies(comment)" class="view-replies-button">
              View comments ({{ comment.replies.length }})
            </button>

            <button v-if="comment.showReplies && comment.replies && comment.replies.length > 0"
                    @click="toggleReplies(comment)" class="hide-replies-button">
              Hide comments
            </button>
            <ul v-if="comment.replies && comment.replies.length > 0" class="reply-list">
              <li v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                <div class="reply-box">
                  <strong>{{ reply.username }}</strong>
                  <span class="comment-date">{{ formatDate(reply.created_at) }}</span>:
                  <p>{{ reply.text }}</p>
                  <a v-if="reply.home_page" :href="reply.home_page" target="_blank">{{ reply.home_page }}</a>
                  <!-- Рекурсивный вызов для рендеринга вложенных ответов -->
                  <ul v-if="reply.replies && reply.replies.length > 0">
                    <li v-for="nestedReply in reply.replies" :key="nestedReply.id" class="nested-reply-item">
                      <div class="nested-reply-box">
                        <strong>{{ nestedReply.username }}</strong>
                        <span class="comment-date">{{ formatDate(nestedReply.created_at) }}</span>:
                        <p>{{ nestedReply.text }}</p>
                      </div>
                    </li>
                  </ul>
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

    <div v-if="showEmailModal" class="modal">
      <div class="modal-content">
        <h3>Email</h3>
        <p>{{ selectedComment.email }}</p>
        <button @click="closeModal" class="close-button">Close</button>
      </div>
    </div>

    <div v-if="showHomepageModal" class="modal">
      <div class="modal-content">
        <h3>Homepage</h3>
        <p v-if="selectedComment.home_page">
          <a :href="selectedComment.home_page" target="_blank">{{ selectedComment.home_page }}</a>
        </p>
        <p v-else>The user did not specify homepage</p>
        <button @click="closeModal" class="close-button">Close</button>
      </div>
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
      showEmailModal: false,
      showHomepageModal: false,
      selectedComment: null
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

    toggleReplies(comment) {
      comment.showReplies = !comment.showReplies;
    },

    toggleEmailModal(comment) {
      this.selectedComment = comment;
      this.showEmailModal = true;
    },

    handleHomepage(comment) {
      if (comment.home_page) {
        window.open(comment.home_page, "_blank");
      } else {
        this.selectedComment = comment;
        this.showHomepageModal = true;
      }
    },

    closeModal() {
      this.showEmailModal = false;
      this.showHomepageModal = false;
      this.selectedComment = null;
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
  animation: fadeIn 0.6s ease-in-out;
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

.info-button, .reply-button, .view-replies-button, .hide-replies-button {
  background-color: #764ba2;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.info-button:hover, .reply-button:hover, .view-replies-button:hover, .hide-replies-button:hover {
  background-color: #5e3c96;
}

.reply-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f0f0f0;
  padding: 10px 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  word-wrap: break-word;
}

.replying-text {
  font-size: 1.1rem;
  color: #444;
}

.cancel-reply {
  background-color: #ff4d4d;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.cancel-reply:hover {
  background-color: #ff1a1a;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 40px;
  border-radius: 8px;
  text-align: center;
  animation: fadeIn 0.5s ease-in-out;
}

.close-button {
  background-color: #ff4d4d;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 10px;
}

.close-button:hover {
  background-color: #ff1a1a;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.reply-list {
  max-height: 150px;
  overflow-y: auto;
  padding-left: 0;
  margin-top: 15px;
}

.reply-box {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 10px;
}

.reply-list::-webkit-scrollbar {
  width: 6px;
}

.reply-list::-webkit-scrollbar-thumb {
  background-color: #764ba2;
  border-radius: 10px;
}

.home-page-link {
  color: #764ba2;
  text-decoration: none;
  font-weight: bold;
}

.home-page-link:hover {
  text-decoration: underline;
}
</style>

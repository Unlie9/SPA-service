<template>
  <div class="comments-container">
    <div class="comments-section">
      <ul class="comments-list">
        <comment-item
          v-for="comment in comments"
          :key="comment.id"
          :comment="comment"
          @reply="setReply"
        />
      </ul>
    </div>

    <form @submit.prevent="sendCommentOrReply" class="fixed-comment-form">
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
</template>

<script>
import CommentItem from './CommentItem.vue';

export default {
  components: {
    CommentItem
  },
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
        const payload = {
          action: "create_comment",
          text: this.newComment,
          home_page: this.homePage
        };

        if (this.replyTo) {
          payload.reply_id = this.replyTo;
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
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
}

.comments-section {
  flex: 1;
  background-color: #fff;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  overflow-y: auto;
}

.fixed-comment-form {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #fff;
  padding: 10px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.textarea, .input {
  width: 100%;
  margin-bottom: 10px;
  padding: 16px;
  border-radius: 5px;
  border: 1px solid #ddd;
  font-size: 1.1rem;
  word-wrap: break-word;
  resize: none;
  max-height: 100px;
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

.reply-indicator {
  margin-bottom: 10px;
}
</style>

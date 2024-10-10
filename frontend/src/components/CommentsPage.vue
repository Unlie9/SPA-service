<template>
  <div class="comments-container">
    <div class="comments-section" ref="commentsSection">
      <ul class="comments-list">
        <comment-item
          v-for="comment in comments"
          :key="comment.id"
          :comment="comment"
          @reply="setReply"
          @showEmail="openEmailModal"
          @showHomepage="openHomepageModal"
        />
      </ul>
    </div>

    <form @submit.prevent="sendCommentOrReply" class="comment-form">
      <div v-if="replyTo" class="reply-indicator">
        <span class="replying-text">
          Replying to "{{ replyToUsername }}" comment:
          <br />
          "{{ replyToText }}"
        </span>
        <button @click="cancelReply" class="cancel-reply">Cancel</button>
      </div>

      <textarea v-model="newComment" placeholder="Write a message..." class="textarea"></textarea>

      <input
        v-model="homePage"
        type="url"
        placeholder="Your home page (optional)"
        class="input"
      />

      <button type="submit" class="submit-button">
        {{ replyTo ? 'Reply' : 'Post Comment' }}
      </button>
    </form>

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
import CommentItem from './CommentItem.vue';

export default {
  components: {
    CommentItem,
  },
  data() {
    return {
      newComment: '',
      homePage: '',
      replyTo: null,
      replyToUsername: null,
      replyToText: null,
      socket: null,
      comments: [],
      selectedComment: null,
      showEmailModal: false,
      showHomepageModal: false,
    };
  },
  methods: {
    connectWebSocket() {
      const token = localStorage.getItem('jwt');
      console.log('Attempting to connect to WebSocket with token:', token);

      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.socket.send(JSON.stringify({ action: 'list_comments' }));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received message from WebSocket:', data);

        if (data.action === 'list_comments') {
          this.comments = data.comments;
          console.log('Comments updated:', this.comments);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
      };
    },

    sendCommentOrReply() {
      if (this.newComment.trim()) {
        const payload = {
          action: 'create_comment',
          text: this.newComment,
          home_page: this.homePage || null,
        };

        if (this.replyTo) {
          payload.reply_id = this.replyTo;
        }

        console.log('Sending comment payload:', payload);
        this.socket.send(JSON.stringify(payload));

        this.newComment = '';
        this.homePage = '';
        this.replyTo = null;
        this.replyToUsername = null;
        this.replyToText = null;

        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },

    setReply(commentId, username, text) {
      this.replyTo = commentId;
      this.replyToUsername = username;
      this.replyToText = text.slice(0, 50) + (text.length > 50 ? '...' : '');
      console.log('Replying to comment:', this.replyTo, this.replyToUsername);
    },

    cancelReply() {
      this.replyTo = null;
      this.replyToUsername = null;
      this.replyToText = null;
      console.log('Reply cancelled');
    },

    scrollToBottom() {
      const commentsSection = this.$refs.commentsSection;
      commentsSection.scrollTop = commentsSection.scrollHeight;
      console.log('Scrolled to bottom');
    },

    openEmailModal(comment) {
      this.selectedComment = comment;
      this.showEmailModal = true;
      console.log('Email modal opened for comment:', comment);
    },

    openHomepageModal(comment) {
      this.selectedComment = comment;
      if (!comment.home_page) {
        this.showHomepageModal = true;
        console.log('Homepage modal opened for comment without homepage:', comment);
      } else {
        window.open(comment.home_page, "_blank");
        console.log('Opening homepage in new tab:', comment.home_page);
      }
    },

    closeModal() {
      this.showEmailModal = false;
      this.showHomepageModal = false;
      this.selectedComment = null;
      console.log('Modals closed');
    },
  },
  mounted() {
    this.connectWebSocket();
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
      console.log('WebSocket closed');
    }
  },
};
</script>

<style scoped>
.comments-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  height: 100vh;
}

.comments-section {
  width: 100%;
  max-width: 80%;
  height: 100%;
  overflow-y: auto;
  margin-bottom: 20px;
  padding-right: 10px;
}

.comments-list {
  padding: 0;
  list-style: none;
  margin: 0;
}

.comment-form {
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 47%;
  position: sticky;
  bottom: 0;
}

.textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  min-height: 80px;
  margin-bottom: 15px;
  font-size: 1rem;
}

.input {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 15px;
}

.submit-button {
  background-color: #5e60ce;
  color: white;
  font-size: 1rem;
  padding: 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #4a47a3;
}

.reply-indicator {
  background-color: #f0f0f0;
  padding: 10px;
  border-left: 4px solid #5e60ce;
  margin-bottom: 15px;
}

.cancel-reply {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
  margin-left: 10px;
  font-size: 0.9rem;
  font-weight: bold;
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
</style>
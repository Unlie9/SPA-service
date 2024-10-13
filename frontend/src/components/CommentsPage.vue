<template>
  <div class="comments-container">
    <div class="sort-controls">
      <label for="sort-by">Sort by:</label>
      <select id="sort-by" v-model="sortBy" @change="requestComments(1)">
        <option value="username">User Name</option>
        <option value="email">E-mail</option>
        <option value="date">Date</option>
      </select>

      <label for="sort-order">Order:</label>
      <select id="sort-order" v-model="sortOrder" @change="requestComments(1)">
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>
    </div>

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

    <div class="pagination-controls">
      <button @click="previousPage" :disabled="currentPage === 1" class="pagination-button">Previous</button>
      <span class="pagination-text">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="pagination-button">Next</button>
      <button @click="goToLastPage" :disabled="currentPage === totalPages" class="pagination-button">Last Page</button>
    </div>

    <form @submit.prevent="sendCommentOrReply" class="comment-form">
      <textarea v-model="newComment" placeholder="Write a message..." class="textarea"></textarea>
      <input v-model="homePage" type="url" placeholder="Your home page (optional)" class="input"/>
      <input type="file" @change="onImageSelected" class="input"/>
      <button type="submit" class="submit-button">{{ replyTo ? 'Reply' : 'Post Comment' }}</button>
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
      currentPage: 1,
      totalPages: 1,
      pageSize: 25,
      sortBy: 'date',
      sortOrder: 'desc',
      selectedComment: null,
      showEmailModal: false,
      showHomepageModal: false,
      imageFile: null,
      imageBase64: null,
    };
  },
  methods: {
    connectWebSocket() {
      const token = localStorage.getItem('jwt');
      console.log('Attempting to connect to WebSocket with token:', token);

      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.requestComments(this.currentPage);
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received message from WebSocket:', data);

        if (data.action === 'list_comments') {
          this.comments = data.comments;
          this.currentPage = data.current_page;
          this.totalPages = data.count_pages;
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

    requestComments(page) {
      this.socket.send(JSON.stringify({
        action: 'list_comments',
        page: page,
        page_size: this.pageSize,
        sort_by: this.sortBy,
        sort_order: this.sortOrder
      }));
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.requestComments(this.currentPage);
      }
    },

    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.requestComments(this.currentPage);
      }
    },

    goToLastPage() {
      this.requestComments(this.totalPages);
      this.currentPage = this.totalPages;
    },

    onImageSelected(event) {
      const file = event.target.files[0];
      if (file) {
        this.convertToBase64(file);
      }
    },

    convertToBase64(file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageBase64 = e.target.result;
      };
      reader.readAsDataURL(file);
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

        if (this.imageBase64) {
          payload.image = this.imageBase64;
        }

        console.log('Sending comment payload:', payload);
        this.socket.send(JSON.stringify(payload));

        this.newComment = '';
        this.homePage = '';
        this.imageBase64 = null; 
        this.replyTo = null;
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
  padding-top: 20px;
  animation: fadeInPage 1s ease-in-out;
}

@keyframes fadeInPage {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.comments-section {
  width: 100%;
  max-width: 80%;
  height: 100%;
  overflow-y: auto;
  margin-bottom: 20px;
  padding-right: 10px;
  animation: slideInSection 0.8s ease-in-out;
}

@keyframes slideInSection {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
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
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 47%;
  position: sticky;
  display: flex;
  flex-direction: column;
  align-items: center;
  bottom: 0;
  transition: box-shadow 0.3s ease-in-out, transform 0.3s;
}

.comment-form:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  transform: translateY(-5px);
}

.textarea {
  width: 98%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 10px;
  resize: vertical;
  min-height: 68px;
  margin-bottom: 5px;
  font-size: 1.1rem;
  transition: border-color 0.3s ease-in-out, background-color 0.3s ease-in-out;
}


.textarea, .input {
  transition: border-color 0.3s ease-in-out, background-color 0.3s ease-in-out;
}

.textarea:focus, .input:focus {
  border-color: #5e60ce;
  background-color: #f0f0ff;
  box-shadow: 0 0 10px rgba(118, 75, 162, 0.2);
  outline: none;
}

.input {
  width: 98%;
  padding: 15px;
  font-size: 1.1rem;
  border: 2px solid #ddd;
  border-radius: 10px;
  margin-bottom: 20px;
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
  transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
}

.submit-button:hover {
  background-color: #4a47a3;
  box-shadow: 0 4px 15px rgba(74, 71, 163, 0.5);
  transform: translateY(-5px);
}

.submit-button:active {
  transform: scale(0.98);
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.pagination-button {
  background-color: #5e60ce;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
}

.pagination-button:hover:not(:disabled) {
  background-color: #4a47a3;
  transform: translateY(-5px);
  box-shadow: 0 4px 15px rgba(74, 71, 163, 0.5);
}

.pagination-button:active:not(:disabled) {
  transform: scale(0.98);
}

.pagination-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.pagination-text {
  font-size: 1rem;
  transition: color 0.3s ease;
  color: #fff;
}

.sort-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.sort-controls:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: scale(1.02);
}

label {
  font-size: 0.9rem;
  color: #f0f0f0;
  font-weight: 500;
}

select {
  padding: 8px 12px;
  font-size: 0.9rem;
  color: #333;
  background-color: #fff;
  border: 1px solid #764ba2;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

select:hover {
  border-color: #5e60ce;
  box-shadow: 0 2px 8px rgba(94, 96, 206, 0.3);
  transform: translateY(-1px);
}

select:focus {
  outline: none;
  border-color: #5e60ce;
  box-shadow: 0 0 6px rgba(94, 96, 206, 0.4);
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
  animation: modalFadeIn 0.5s ease-in-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-content {
  background-color: #fff;
  padding: 40px;
  border-radius: 8px;
  text-align: center;
  transition: box-shadow 0.3s ease-in-out;
}

.modal-content:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.close-button {
  background-color: #ff4d4d;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 10px;
  transition: background-color 0.3s;
}

.close-button:hover {
  background-color: #ff1a1a;
}

</style>

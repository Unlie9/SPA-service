<template>
  <div class="comment-section">
    <h2>Comments</h2>
    <ul class="comments-list">
      <li v-for="comment in comments" :key="comment.id">
        <div class="comment-item">
          <strong>{{ comment.username }}</strong>: {{ comment.text }}
          <div class="comment-date">{{ formatDate(comment.created_at) }}</div>
        </div>
      </li>
    </ul>
    <form @submit.prevent="sendComment">
      <textarea v-model="newCommentText" placeholder="Write a comment..."></textarea>
      <input v-model="newCommentHomepage" placeholder="Your homepage (optional)"/>
      <button type="submit">Post Comment</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      socket: null,
      comments: [],
      newCommentText: '',
      newCommentHomepage: '',
    };
  },
  methods: {
    connectWebSocket() {
      const token = localStorage.getItem('jwt');
      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        console.log('WebSocket connection opened.');
        this.socket.send(JSON.stringify({action: 'list_comments'}));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === 'list_comments') {
          this.comments = data.comments;
        } else if (data.error) {
          console.error('WebSocket error:', data.error);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.socket.onclose = () => {
        console.log('WebSocket connection closed.');
      };
    },

    sendComment() {
      const payload = {
        action: 'create_comment',
        text: this.newCommentText,
        home_page: this.newCommentHomepage || null,
      };
      this.socket.send(JSON.stringify(payload));
      this.newCommentText = '';
      this.newCommentHomepage = '';
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}`;
    },
  },
  mounted() {
    this.connectWebSocket();
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  },
};
</script>

<style scoped>
.comment-section {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.comments-list {
  list-style: none;
  padding: 0;
}

.comment-item {
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

textarea {
  width: 100%;
  height: 80px;
  margin-bottom: 10px;
}

input {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
}

button {
  display: block;
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: #fff;
  border: none;
  cursor: pointer;
}
</style>

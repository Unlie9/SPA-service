<template>
  <div class="comments-page">
    <ul class="comments-list" ref="commentsList">
      <li v-for="comment in comments" :key="comment.id" class="comment-card" :class="{ 'new-comment': comment.isNew }">
        <div class="comment-header">
          <div class="avatar-placeholder">{{ comment.username.charAt(0).toUpperCase() }}</div>
          <strong class="username">{{ comment.username }}</strong>
          <span class="time-text">{{ formatDate(comment.created_at) }}</span>
        </div>
        <div class="comment-body">
          <strong class="comment-text">{{ comment.text }}</strong>
        </div>
      </li>
      <form @submit.prevent="sendComment" class="comment-form">
        <textarea v-model="newComment" placeholder="Write a message..." class="comment-input"></textarea>
        <button type="submit" class="submit-button">Send</button>
      </form>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      comments: [],
      newComment: "",
      socket: null
    };
  },
  methods: {
    connectWebSocket() {
      const token = localStorage.getItem('jwt');
      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        console.log("WebSocket connected");
        this.socket.send(JSON.stringify({ action: "list_comments" }));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === "list_comments") {
          this.comments = data.comments.map(comment => ({
            ...comment,
            isNew: false
          }));
          this.scrollToBottom();
        }
      };

      this.socket.onerror = (error) => {
        console.error("Error WebSocket:", error);
      };

      this.socket.onclose = () => {
        console.log("WebSocket disconnected");
      };
    },

    sendComment() {
      if (this.newComment.trim()) {
        this.socket.send(JSON.stringify({
          action: "create_comment",
          text: this.newComment
        }));
        const newCommentObj = {
          id: Date.now(),
          username: 'CurrentUser',
          text: this.newComment,
          isNew: true
        };
        this.comments.push(newCommentObj);
        this.newComment = "";
        this.$nextTick(() => {
          this.scrollToBottom();
        });

        setTimeout(() => {
          newCommentObj.isNew = false;
        }, 1000);
      }
    },

    formatDate(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = String(date.getFullYear()).slice(-2);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${day}.${month}.${year} в ${hours}:${minutes}`;
  },

    scrollToBottom() {
      const commentsList = this.$refs.commentsList;
      commentsList.scrollTop = commentsList.scrollHeight;
    }
  },
  mounted() {
    this.connectWebSocket();
  },
  updated() {
    this.$nextTick(() => {
      this.scrollToBottom();
    });
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  }
};
</script>

<style scoped>
body {
  margin: 0;
  padding: 0;
  font-family: 'Arial', sans-serif;
  background-color: #f0f4f8;
  display: none;
  overflow: hidden;
}

.comments-page {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 150px;
  background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  font-size: 2.2em;
  color: #333;
  margin-bottom: 20px;
}

.comments-list {
  list-style: none;
  padding: 0;
  margin: 0 auto;
  max-width: 100%;
  max-height: 40%;
  overflow-y: auto;
}

.comment-card {
  background-color: #f7f7f7;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.comment-header {
  display: flex;
  align-items: center;
  background-color: #e0e0e0;
  padding: 10px;
  border-radius: 8px;
  width: 100%;
}

.avatar-placeholder {
  width: 50px;
  height: 50px;
  background-color: #3498db;
  color: #fff;
  font-size: 24px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 10px;
}

.username {
  font-size: 1.2em;
  color: #34495e;
}

.comment-body {
  margin-top: 10px;
  text-align: left;
  word-wrap: break-word;
  width: 100%;
}

.comment-text {
  color: #555;
  line-height: 1.5;
  font-size: 1.1em;
  padding-left: 20px;
}

.time-text {
  color: black;
  line-height: 1.5;
  font-size: 1.1em;
  padding-left: 5px;
}

.comment-form {
  position: fixed;
  bottom: 1px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
  padding: 20px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 700px;
}

.comment-input {
  flex-grow: 1;
  border: 1px solid #ccc;
  border-radius: 20px;
  padding: 14px 20px;
  font-size: 16px;
  resize: none;
  outline: none;
  transition: border-color 0.3s;
}

.comment-input:focus {
  border-color: #3498db;
}

.submit-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 20px;
  margin-left: 15px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s, box-shadow 0.3s;
}

.submit-button:hover {
  background-color: #2980b9;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.submit-button:active {
  background-color: #1f669d;
}

.comment-input::placeholder {
  color: #ccc;
}
</style>

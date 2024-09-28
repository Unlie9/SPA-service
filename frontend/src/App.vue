<template>
  <div id="app">
    <div class="comments-view">
      <h1>Comments</h1>

      <div class="comment-list">
        <div
          class="comment-item"
          v-for="comment in comments"
          :key="comment.id"
        >
          <div class="comment-avatar">
            <img :src="comment.avatar" alt="User avatar" />
          </div>
          <div class="comment-content">
            <div class="comment-header">
              <strong v-if="comment.username">{{ comment.username }}</strong>
              <span v-if="comment.created_at">
                {{ formatDate(comment.created_at) }}
              </span>
            </div>
            <div class="comment-text">{{ comment.text }}</div>

            <button class="reply-button" @click="toggleReplyForm(comment)">
              <i class="fas fa-reply"></i> Reply
            </button>

            <div v-if="activeComment === comment.id">
              <div class="reply-form">
                <input v-model="replyText" placeholder="Your reply..." />
                <button @click="submitReply(comment.id)">
                  <i class="fas fa-paper-plane"></i> Send
                </button>
              </div>
            </div>

            <div v-if="comment.replies && comment.replies.length" class="replies-list">
              <div
                class="comment-item"
                v-for="reply in comment.replies"
                :key="reply.id"
              >
                <div class="comment-header">
                  <strong v-if="reply.username">{{ reply.username }}</strong>
                  <span v-if="reply.created_at">
                    {{ formatDate(reply.created_at) }}
                  </span>
                </div>
                <div class="comment-text">{{ reply.text }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <form @submit.prevent="addComment" class="new-comment-form">
        <input v-model="newComment" placeholder="Write a comment..." />
        <button type="submit">
          <i class="fas fa-paper-plane"></i> Send Comment
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      comments: [],
      newComment: '',
      replyText: '',
      activeComment: null,
    };
  },
  created() {
    this.fetchComments();
  },
  methods: {
    fetchComments() {
      axios
        .get(`${process.env.VUE_APP_API_URL}/spa/comments/`)
        .then((response) => {
          this.comments = response.data.results;
        })
        .catch((error) => {
          console.error("Error fetching comments:", error);
        });
    },

    addComment() {
      if (this.newComment.trim() === '') return;
      axios
        .post(`${process.env.VUE_APP_API_URL}/spa/comments/`, {
          text: this.newComment,
        })
        .then((response) => {
          this.comments.push(response.data);
          this.newComment = '';
        })
        .catch((error) => {
          console.error("Error adding comment:", error);
        });
    },

    submitReply(commentId) {
      if (this.replyText.trim() === '') return;

      const reply = {
        text: this.replyText,
        reply: commentId,
      };

      axios
        .post(`${process.env.VUE_APP_API_URL}/spa/comments/`, reply)
        .then((response) => {
          const savedReply = response.data;

          const comment = this.comments.find((c) => c.id === commentId);

          if (!comment.replies) {
            comment.replies = [];
          }

          comment.replies.push(savedReply);

          this.replyText = '';
          this.activeComment = null;
        })
        .catch((error) => {
          console.error('Error adding reply:', error);
        });
    },
    toggleReplyForm(comment) {
      this.activeComment = this.activeComment === comment.id ? null : comment.id;
    },
    formatDate(date) {
      const d = new Date(date);
      const day = String(d.getDate()).padStart(2, '0');
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const year = String(d.getFullYear()).slice(-2);
      const hours = String(d.getHours()).padStart(2, '0');
      const minutes = String(d.getMinutes()).padStart(2, '0');

      return `${day}.${month}.${year} в ${hours}:${minutes}`;
    },
  },
};
</script>

<style scoped>
body {
  font-family: Arial, sans-serif;
  background-color: #f9f9f9;
  color: #333;
}

.comments-view {
  max-width: 700px;
  margin: 40px auto;
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.comment-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comment-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-avatar img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 15px;
}

.comment-content {
  flex-grow: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-header strong {
  font-size: 16px;
  font-weight: bold;
}

.comment-date {
  color: #888;
  font-size: 0.9em;
}

.comment-text {
  margin-top: 8px;
  line-height: 1.5;
}

.reply-button {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.9em;
  margin-top: 10px;
}

.reply-button:hover {
  text-decoration: underline;
}

.replies-list {
  padding-left: 40px;
  margin-top: 15px;
  border-left: 2px solid #ddd;
}

.new-comment-form {
  display: flex;
  margin-top: 20px;
}

.new-comment-form input {
  flex-grow: 1;
  padding: 10px;
  font-size: 16px;
  border-radius: 5px;
  border: 1px solid #ddd;
  margin-right: 10px;
}

.new-comment-form button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.new-comment-form button:hover {
  background-color: #0056b3;
}

.reply-form {
  margin-top: 10px;
}

.reply-form input {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  border-radius: 5px;
  border: 1px solid #ddd;
}

.reply-form button {
  margin-top: 10px;
  padding: 8px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.reply-form button:hover {
  background-color: #0056b3;
}

.comment-item:hover {
  background-color: #f7f7f7;
}

.comment-avatar {
  display: flex;
  align-items: center;
}

.comment-header .icons {
  display: flex;
  align-items: center;
}

.icons span {
  margin-left: 10px;
  font-size: 12px;
  color: #888;
}

@media screen and (max-width: 768px) {
  .comment-avatar img {
    width: 40px;
    height: 40px;
  }

  .new-comment-form input {
    font-size: 14px;
  }

  .comment-header strong {
    font-size: 14px;
  }

  .comment-text {
    font-size: 14px;
  }
}
</style>
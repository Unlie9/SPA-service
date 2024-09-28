<template>
  <div id="app">
    <div class="comments-view">

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
/* Google Font for modern, clean typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background-color: #f8fafc;
  color: #333;
}

.comments-view {
  max-width: 800px;
  margin: 40px auto;
  background-color: #ffffff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
}

.comment-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comment-item {
  display: flex;
  padding: 20px 0;
  border-bottom: 1px solid #e0e6ed;
  transition: background-color 0.2s ease;
}

.comment-item:hover {
  background-color: #f0f4f8;
}

.comment-avatar img {
  width: 45px;
  height: 45px;
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
  margin-bottom: 5px;
}

.comment-header strong {
  font-size: 1.1rem;
  font-weight: 600;
  color: #222;
}

.comment-header .comment-date {
  font-size: 0.85rem;
  color: #888;
  margin-left: 10px;
}

.comment-text {
  margin-top: 5px;
  line-height: 1.6;
  font-size: 0.95rem;
  color: #555;
}

.reply-button,
.upvote-button,
.downvote-button {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.85rem;
  margin-right: 10px;
  transition: color 0.2s;
}

.reply-button:hover,
.upvote-button:hover,
.downvote-button:hover {
  color: #0056b3;
  text-decoration: underline;
}

.icon {
  margin-right: 5px;
  font-size: 1.1rem;
  color: #007bff;
}

.replies-list {
  padding-left: 40px;
  margin-top: 15px;
  border-left: 2px solid #e0e6ed;
}

.new-comment-form {
  display: flex;
  margin-top: 30px;
  border-top: 1px solid #e0e6ed;
  padding-top: 20px;
}

.new-comment-form input {
  flex-grow: 1;
  padding: 12px;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid #ced4da;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-right: 10px;
  transition: border 0.2s;
}

.new-comment-form input:focus {
  border-color: #007bff;
  outline: none;
}

.new-comment-form button {
  padding: 12px 20px;
  background-color: #007bff;
  color: white;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.new-comment-form button:hover {
  background-color: #0056b3;
}

.reply-form {
  margin-top: 10px;
}

.reply-form input {
  width: 100%;
  padding: 10px;
  font-size: 0.9rem;
  border-radius: 8px;
  border: 1px solid #ced4da;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.reply-form button {
  margin-top: 10px;
  padding: 10px 18px;
  background-color: #007bff;
  color: white;
  font-size: 0.9rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reply-form button:hover {
  background-color: #0056b3;
}

.comment-header .actions {
  display: flex;
  align-items: center;
}

.actions .action-icon {
  margin-left: 10px;
  color: #888;
  font-size: 1rem;
}

.actions .action-icon:hover {
  color: #333;
}

.comment-item:hover .action-icon {
  color: #007bff;
}

/* Responsive Design */
@media screen and (max-width: 768px) {
  .comment-avatar img {
    width: 40px;
    height: 40px;
  }

  .comment-header strong {
    font-size: 1rem;
  }

  .comment-text {
    font-size: 0.9rem;
  }

  .new-comment-form input {
    font-size: 0.9rem;
  }

  .new-comment-form button {
    font-size: 0.9rem;
  }
}
</style>

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
              Reply
            </button>

            <div v-if="activeComment === comment.id">
              <div class="reply-form">
                <input v-model="replyText" placeholder="Your reply..." />
                <button @click="submitReply(comment.id)">Send</button>
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
        <button type="submit">Send Comment</button>
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
.comments-view {
  max-width: 600px;
  margin: 0 auto;
}

.comment-list {
  list-style: none;
  padding: 0;
}

.comment-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #e0e0e0;
}

.comment-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.comment-content {
  margin-left: 10px;
  flex-grow: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
}

.comment-date {
  color: #aaa;
  font-size: 0.9em;
}

.reply-button {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
}

.reply-button:hover {
  text-decoration: underline;
}

.replies-list {
  padding-left: 20px;
}

.new-comment-form input {
  width: 80%;
  padding: 10px;
  margin-right: 10px;
}

.new-comment-form button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

.reply-form {
  margin-top: 10px;
}

.reply-form input {
  width: 70%;
  padding: 5px;
}

.reply-form button {
  margin-left: 10px;
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}
</style>

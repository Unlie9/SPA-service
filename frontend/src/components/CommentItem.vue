<template>
  <li class="comment-item">
    <div class="comment-box">
      <div style="background: lightgray; border-radius: 8px; padding: 2px">

        <div v-if="comment.replyTo" class="reply-preview">
          <div class="reply-info">
            <strong>{{ comment.replyTo.username }}</strong>
            <span class="reply-text">{{ truncateText(comment.replyTo.text, 10) }}</span>
          </div>
        </div>

        <div class="comment-header">
          <div class="avatar">{{ comment.username.charAt(0).toUpperCase() }}</div>
          <div class="header-info">
            <strong class="comment-username">{{ comment.username }}</strong>
            <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
            <button @click="showEmail" class="meta-button">Email</button>
            <button @click="showHomepage" class="meta-button">Homepage</button>
            <button @click="setReply(comment.id, comment.username, comment.text)" class="meta-button">Reply</button>
          </div>
        </div>
      </div>

      <p class="comment-text">{{ comment.text }}</p>
      <div v-if="comment.image" class="comment-image">
        <img :src="comment.image" alt="comment image" class="comment-img" />
      </div>



      <ul v-if="comment.replies && comment.replies.length && showReplies" class="reply-list">
        <comment-item
          v-for="reply in comment.replies"
          :key="reply.id"
          :comment="reply"
          @reply="setReply"
          @showEmail="showEmail"
          @showHomepage="showHomepage"
        />
      </ul>

      <button v-if="comment.replies && comment.replies.length && !showReplies" @click="toggleReplies" class="view-replies-button">
        View replies ({{ comment.replies.length }})
      </button>

      <button v-if="showReplies" @click="toggleReplies" class="view-replies-button">Hide replies</button>
    </div>
  </li>
</template>

<script>
export default {
  props: {
    comment: Object,
  },
  data() {
    return {
      showReplies: false,
    };
  },
  methods: {
    setReply(commentId, username, text) {
      this.$emit('reply', commentId, username, text);
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = String(date.getFullYear()).slice(2);
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${day}.${month}.${year} at ${hours}:${minutes}`;
    },
    truncateText(text, maxLength) {
      return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
    },
    showEmail() {
      this.$emit('showEmail', this.comment);
    },
    showHomepage() {
      this.$emit('showHomepage', this.comment);
    },
    toggleReplies() {
      this.showReplies = !this.showReplies;
    },
  },
};
</script>

<style scoped>
.comment-item {
  margin-bottom: 20px;
  list-style: none;
  animation: fadeInComment 0.5s ease-in-out;
}

.header-info {
  padding-left: 5px;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

@keyframes fadeInComment {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.comment-box {
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
  word-wrap: break-word;
  transition: box-shadow 0.3s ease-in-out, transform 0.3s;
}

.comment-box:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  transform: translateY(-5px);
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.avatar {
  background-color: #5e60ce;
  color: #fff;
  font-size: 1.2rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.3s;
}

.avatar:hover {
  transform: rotate(360deg);
}

.meta-button {
  background-color: #5e60ce;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
}

.meta-button:hover {
  background-color: #4a47a3;
  box-shadow: 0 4px 15px rgba(74, 71, 163, 0.5);
  transform: translateY(-5px);
}

.meta-button:active {
  transform: scale(0.98);
}

.comment-text {
  font-size: 1rem;
  margin-top: 10px;
}

.reply-list {
  margin-top: 15px;
  padding-left: 20px;
  border-left: 2px solid #ddd;
  background-color: #f8f9fa;
  border-radius: 6px;
  animation: fadeInReply 0.5s ease-in-out;
}

@keyframes fadeInReply {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.view-replies-button {
  background-color: #5e60ce;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-top: 10px;
  transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
}

.view-replies-button:hover {
  background-color: #4a47a3;
  transform: translateY(-5px);
  box-shadow: 0 4px 15px rgba(74, 71, 163, 0.5);
}

.view-replies-button:active {
  transform: scale(0.98);
}

.comment-image {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

.comment-img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

</style>

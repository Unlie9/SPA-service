<template>
  <div class="comments-container">
    <h1>Комментарии</h1>
    <ul class="comments-list">
      <li v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-content">
          <strong>{{ comment.username }}</strong>: {{ comment.text }}
        </div>
        
        <!-- Кнопка для ответа -->
        <button class="reply-button" @click="toggleReplyForm(comment.id)">
          Ответить
        </button>

        <!-- Форма для ответа на комментарий -->
        <div v-if="activeReply === comment.id" class="reply-form">
          <input v-model="newReply" placeholder="Напишите ответ" />
          <button @click="submitReply(comment.id)">Отправить ответ</button>
        </div>

        <!-- Если у комментария есть ответы -->
        <ul v-if="comment.replies && comment.replies.length > 0" class="replies-list">
          <li v-for="reply in comment.replies" :key="reply.id" class="reply-item">
            <div class="reply-content">
              <strong>{{ reply.username }}</strong>: {{ reply.text }}
            </div>
          </li>
        </ul>
      </li>
    </ul>

    <!-- Форма для добавления нового комментария -->
    <form @submit.prevent="addComment" class="new-comment-form">
      <input v-model="newComment" placeholder="Напишите комментарий" />
      <button type="submit">Отправить комментарий</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      comments: [],  // Сюда сохраняем комментарии с бэкенда
      newComment: '',  // Поле для нового комментария
      newReply: '',  // Поле для нового ответа
      activeReply: null,  // ID комментария, к которому пишется ответ
    };
  },
  created() {
    this.fetchComments();
  },
  methods: {
    fetchComments() {
      axios.get(`${process.env.VUE_APP_API_URL}/spa/comments/`)
        .then(response => {
          this.comments = response.data.results;
        })
        .catch(error => {
          console.error('Error fetching comments:', error);
        });
    },
    addComment() {
      axios.post(`${process.env.VUE_APP_API_URL}/spa/comments/`, {
        text: this.newComment,
      })
      .then(response => {
        this.comments.push(response.data);
        this.newComment = '';
      })
      .catch(error => {
        console.error('Error adding comment:', error);
      });
    },
    toggleReplyForm(commentId) {
      this.activeReply = this.activeReply === commentId ? null : commentId;  // Открытие/закрытие формы ответа
    },
    submitReply(commentId) {
      axios.post(`${process.env.VUE_APP_API_URL}/spa/comments/`, {
        text: this.newReply,
        reply: commentId,  // Связь ответа с исходным комментарием
      })
      .then(response => {
        // Найдем комментарий, к которому добавлен ответ, и добавим ответ в его список replies
        const parentComment = this.comments.find(comment => comment.id === commentId);
        parentComment.replies.push(response.data);
        this.newReply = '';  // Очистим поле ввода ответа
        this.activeReply = null;  // Закроем форму ответа
      })
      .catch(error => {
        console.error('Error submitting reply:', error);
      });
    },
  },
};
</script>

<!-- Добавляем простые стили для красивого дизайна -->
<style>
.comments-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.comments-list,
.replies-list {
  list-style-type: none;
  padding-left: 0;
}

.comment-item,
.reply-item {
  padding: 10px;
  border-bottom: 1px solid #ccc;
}

.comment-content,
.reply-content {
  padding: 5px 0;
}

.reply-button {
  background-color: #f0f0f0;
  border: none;
  color: #007bff;
  cursor: pointer;
  padding: 5px 10px;
}

.reply-button:hover {
  text-decoration: underline;
}

.reply-form input {
  width: 80%;
  padding: 5px;
  margin-right: 10px;
}

.reply-form button {
  background-color: #007bff;
  color: white;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
}

.new-comment-form {
  margin-top: 20px;
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

.new-comment-form button:hover {
  background-color: #0056b3;
}
</style>
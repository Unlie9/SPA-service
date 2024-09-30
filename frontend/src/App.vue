<template>
  <div id="app">
    <h1>Comments</h1>
    <ul>
      <li v-for="comment in comments" :key="comment.id">
        <strong>{{ comment.username }}:</strong> {{ comment.text }}
        <ul v-if="comment.replies && comment.replies.length">
          <li v-for="reply in comment.replies" :key="reply.id">
            <strong>{{ reply.username }}:</strong> {{ reply.text }}
          </li>
        </ul>
      </li>
    </ul>
    <input v-model="newComment" placeholder="Write a comment" />
    <button @click="sendComment">Send</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      newComment: '',
      comments: [], // Массив комментариев
      socket: null, // WebSocket соединение
    };
  },
  mounted() {
    this.connectWebSocketForComments();
  },
  methods: {
    // Соединение с WebSocket для комментариев
    connectWebSocketForComments() {
      this.socket = new WebSocket('ws://localhost:8003/ws/comments/');

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Received data:", data); // Логируем полученные данные

        if (data.action === 'list_comments') {
          this.comments = data.comments; // Получаем и отображаем комментарии
        }
      };

      this.socket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      this.socket.onclose = () => {
        console.log("WebSocket connection closed");
      };
    },

    // Отправка нового комментария
    sendComment() {
      if (this.newComment.trim() !== '') {
        this.socket.send(JSON.stringify({
          action: 'create_comment',
          text: this.newComment,
        }));
        this.newComment = ''; // Очищаем поле ввода
      }
    },
  },
};
</script>

<style scoped>
#app {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
}

input {
  display: block;
  width: 100%;
  margin-bottom: 10px;
  padding: 8px;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
}
</style>

<template>
  <div class="comments-page">
    <h1>Комментарии</h1>
    <ul>
      <li v-for="comment in comments" :key="comment.id">
        <strong>{{ comment.username }}:</strong> {{ comment.text }}
      </li>
    </ul>
    <form @submit.prevent="sendComment">
      <textarea v-model="newComment" placeholder="Введите комментарий"></textarea>
      <button type="submit">Отправить</button>
    </form>
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
      // Получаем токен из localStorage
      const token = localStorage.getItem('jwt');

      // Открываем WebSocket-соединение, добавив токен в параметры URL
      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        console.log("WebSocket соединение установлено");
        this.socket.send(JSON.stringify({
          action: "list_comments"
        }));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === "list_comments") {
          this.comments = data.comments;
        }
      };

      this.socket.onerror = (error) => {
        console.error("Ошибка WebSocket:", error);
      };

      this.socket.onclose = () => {
        console.log("WebSocket соединение закрыто");
      };
    },

    sendComment() {
      if (this.newComment.trim()) {
        this.socket.send(JSON.stringify({
          action: "create_comment",
          text: this.newComment
        }));
        this.newComment = "";
      }
    }
  },
  mounted() {
    // Устанавливаем WebSocket-соединение при монтировании компонента
    this.connectWebSocket();
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  }
};
</script>

<style scoped>
.comments-page {
  padding: 20px;
}

textarea {
  width: 100%;
  height: 100px;
  margin-bottom: 10px;
}

button {
  padding: 10px 20px;
}
</style>

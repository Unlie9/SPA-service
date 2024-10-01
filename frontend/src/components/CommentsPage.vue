<template>
  <div>
    <ul style="text-align: center">
      <li v-for="comment in comments" :key="comment.id">
        <ul>
          <li>{{ comment.username }}</li>
          <li>{{ formatDate(comment.created_at) }}</li>
          <li>{{ comment.text }}</li>
          <li>{{ comment.home_page ? comment.home_page : 'Empty' }}</li>
        </ul>
      </li>
    </ul>

    <form @submit.prevent="sendComment" style="text-align: center">
      <textarea v-model="newComment" placeholder="Write a message..."></textarea>
      <input v-model="homePage" placeholder="Your homepage (optional)" type="url"/>
      <button type="submit">Send</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      comments: [],
      newComment: "",
      homePage: "",
      socket: null
    };
  },
  methods: {
    connectWebSocket() {
      const token = localStorage.getItem('jwt');
      this.socket = new WebSocket(`${process.env.VUE_APP_WS_URL}/ws/comments/?token=${token}`);

      this.socket.onopen = () => {
        this.socket.send(JSON.stringify({ action: "list_comments" }));
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === "list_comments") {
          this.comments = data.comments;
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
          text: this.newComment,
          home_page: this.homePage
        }));

        const newCommentObj = {
          id: Date.now(),
          username: 'CurrentUser',
          text: this.newComment,
          home_page: this.homePage,
          created_at: new Date().toISOString()
        };

        this.comments.push(newCommentObj);
        this.newComment = "";
        this.homePage = "";
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}`;
    }
  },
  mounted() {
    this.connectWebSocket();
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  }
};
</script>

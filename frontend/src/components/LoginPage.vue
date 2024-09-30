<template>
  <div>
    <h1>Login</h1>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="Username" />
      <input type="password" v-model="password" placeholder="Password" />
      <button type="submit" :disabled="loading">Login</button>
    </form>
    <p v-if="error">{{ error }}</p>
    <p v-if="loading">Logging in...</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      error: null,
      loading: false,  // Добавляем индикатор загрузки
    };
  },
  methods: {
    async login() {
      this.loading = true;  // Запуск индикатора загрузки
      this.error = null;    // Очищаем предыдущие ошибки
      try {
        const response = await axios.post(`${process.env.VUE_APP_API_URL}/user/token/`, {
          username: this.username,
          password: this.password,
        });
        // Сохраняем токен в localStorage
        localStorage.setItem('jwt', response.data.access);
        this.$router.push('/comments');  // Перенаправляем на страницу комментариев
      } catch (error) {
        this.error = 'Login failed. Please check your credentials.';
      } finally {
        this.loading = false;  // Останавливаем индикатор загрузки
      }
    },
  },
};
</script>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  width: 300px;
  margin: 0 auto;
}

input {
  margin-bottom: 10px;
  padding: 8px;
  font-size: 16px;
}

button {
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
}

p {
  color: red;
}
</style>

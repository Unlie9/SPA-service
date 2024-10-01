<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Login</h1>
      <form @submit.prevent="login">
        <div class="input-group">
          <input v-model="username" placeholder="Username" />
        </div>
        <div class="input-group">
          <input type="password" v-model="password" placeholder="Password" />
        </div>
        <button type="submit" :disabled="loading">Login</button>
      </form>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <p v-if="loading" class="loading-msg">Logging in...</p>
    </div>
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
      loading: false,
    };
  },
  methods: {
    async login() {
      this.loading = true;  // Старт индикатора загрузки
      this.error = null;    // Очистка ошибок
      try {
        const response = await axios.post(`${process.env.VUE_APP_API_URL}/user/token/`, {
          username: this.username,
          password: this.password,
        });
        localStorage.setItem('jwt', response.data.access);  // Сохранение токена
        this.$router.push('/comments');  // Перенаправление
      } catch (error) {
        this.error = 'Login failed. Please check your credentials.';
      } finally {
        this.loading = false;  // Остановка индикатора загрузки
      }
    },
  },
};
</script>

<style scoped>
/* Убираем скролл и заставляем фон занимать всю высоту */
html, body {
  overflow: hidden; /* Полностью убираем скролл */
  display: none;
}

/* Контейнер для всей страницы */
.login-container {
  min-height: 100vh; /* Занимаем 100% высоты экрана */
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
  font-family: 'Roboto', sans-serif;
  overflow: hidden;
}

.login-box {
  background-color: white;
  padding: 5%;
  border-radius: 10px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  max-width: 30%;
  width: 100%;
  text-align: center;
}

/* Заголовок */
h1 {
  font-size: 2rem;
  color: #333;
}

/* Оформление полей формы */
.input-group {
  width: 94%;
  margin-bottom: 5%;
}

input {
  width: 100%; /* Занимаем всю ширину родителя */
  padding: 3%; /* Используем проценты для отступов */
  font-size: 1.1rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  transition: all 0.3s ease;
}

input:focus {
  border-color: #007bff;
  box-shadow: 0 0 8px rgba(0, 123, 255, 0.3);
  outline: none;
}

/* Кнопка */
button {
  width: 100%; /* Ширина кнопки равна ширине инпутов */
  padding: 3%; /* Используем проценты для отступов */
  background-color: #007bff;
  color: white;
  font-size: 1.1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #0056b3;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* Сообщения об ошибке и загрузке */
.error-msg {
  color: red;
  margin-top: 5%;
}

.loading-msg {
  color: #007bff;
  margin-top: 5%;
}

/* Плавные переходы для полей ввода */
input {
  transition: border-color 0.3s, box-shadow 0.3s;
}
</style>

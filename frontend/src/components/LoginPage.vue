<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Login</h1>
      <form @submit.prevent="login">
        <div class="input-group">
          <input v-model="username" placeholder="Username"/>
        </div>
        <div class="input-group">
          <input type="password" v-model="password" placeholder="Password"/>
        </div>
        <button type="submit" :disabled="loading">Login</button>
      </form>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <p v-if="loading" class="loading-msg">Logging in...</p>
      <div class="register-section">
        <p>Not registered?</p>
        <button @click="goToRegister" class="register-button">Register here</button>
      </div>
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
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(`${process.env.VUE_APP_API_URL}/user/token/`, {
          username: this.username,
          password: this.password,
        });
        localStorage.setItem('jwt', response.data.access);
        localStorage.setItem('refresh', response.data.refresh);
        this.$router.push('/comments');
        this.setupTokenRefresh();
      } catch (error) {
        this.error = 'Login failed. Please check your credentials.';
      } finally {
        this.loading = false;
      }
    },
    setupTokenRefresh() {
      setInterval(async () => {
        try {
          const refreshToken = localStorage.getItem('refresh');
          if (refreshToken) {
            const response = await axios.post(`${process.env.VUE_APP_API_URL}/user/token/refresh/`, {
              refresh: refreshToken,
            });
            localStorage.setItem('jwt', response.data.access);
          }
        } catch (error) {
          console.error('Token refresh failed:', error);
        }
      }, 4 * 60 * 1000);
    },
    goToRegister() {
      this.$router.push('/register');
    }
  },
  mounted() {
    this.setupTokenRefresh();
  },
};
</script>

<style scoped>
html, body {
  margin: 0 !important;
  padding: 0 !important;
  height: 100%;
  overflow: hidden;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
}

.login-box {
  background-color: #fff;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
  position: relative;
  animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 20px;
  font-family: 'Poppins', sans-serif;
}

.input-group {
  margin-bottom: 20px;
}

input {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  transition: all 0.3s ease;
  font-family: 'Roboto', sans-serif;
}

input:focus {
  border-color: #764ba2;
  box-shadow: 0 0 10px rgba(118, 75, 162, 0.2);
  outline: none;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #764ba2;
  color: #fff;
  font-size: 1.1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #5e3c96;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-msg {
  color: red;
  margin-top: 15px;
  font-size: 0.9rem;
}

.loading-msg {
  color: #007bff;
  margin-top: 15px;
  font-size: 0.9rem;
}

.register-section {
  margin-top: 20px;
  font-size: 0.9rem;
  color: #555;
}

.register-button {
  margin-top: 10px;
  background-color: transparent;
  border: 2px solid #764ba2;
  color: #764ba2;
  padding: 10px 20px;
  font-size: 1rem;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.register-button:hover {
  background-color: #764ba2;
  color: #fff;
}

@media (max-width: 768px) {
  .login-box {
    padding: 20px;
  }

  h1 {
    font-size: 1.8rem;
  }

  input, button {
    padding: 10px;
    font-size: 0.9rem;
  }
}
</style>

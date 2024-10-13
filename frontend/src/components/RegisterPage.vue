<template>
  <div class="register-container">
    <div class="register-box">
      <h1>Register</h1>
      <form @submit.prevent="register">
        <div class="input-group">
          <input v-model="username" placeholder="Username" />
          <p v-if="usernameError" class="error-msg">{{ usernameError }}</p>
        </div>
        <div class="input-group">
          <input v-model="email" placeholder="Email" />
          <p v-if="emailError" class="error-msg">{{ emailError }}</p>
        </div>
        <div class="input-group">
          <input type="password" v-model="password" placeholder="Password" />
          <p v-if="passwordError" class="error-msg">{{ passwordError }}</p>
        </div>
        <button type="submit">Register</button>
      </form>

      <div class="login-section">
        <p>Already have an account?</p>
        <button @click="goToLogin" class="login-button">Login here</button>
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
      email: '',
      password: '',
      usernameError: '',
      emailError: '',
      passwordError: '',
    };
  },
  methods: {
    register() {
      axios
        .post(`${process.env.VUE_APP_API_URL}/user/register/`, {
          username: this.username,
          email: this.email,
          password: this.password,
        })
        .then(() => {
          this.$router.push('/login');
        })
        .catch((error) => {
          // Сбрасываем предыдущие ошибки перед новой попыткой
          this.usernameError = '';
          this.emailError = '';
          this.passwordError = '';

          // Проверка и назначение ошибок для соответствующих полей
          if (error.response && error.response.data) {
            if (error.response.data.username) {
              this.usernameError = error.response.data.username.join(' ');
            }
            if (error.response.data.email) {
              this.emailError = error.response.data.email.join(' ');
            }
            if (error.response.data.password) {
              this.passwordError = error.response.data.password.join(' ');
            }
          } else {
            this.usernameError = 'An error occurred. Please try again later.';
          }
        });
    },
    goToLogin() {
      this.$router.push('/login');
    },
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

.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
}

.register-box {
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

.login-section {
  margin-top: 20px;
  font-size: 0.9rem;
  color: #555;
}

.login-button {
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

.login-button:hover {
  background-color: #764ba2;
  color: #fff;
}

@media (max-width: 768px) {
  .register-box {
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

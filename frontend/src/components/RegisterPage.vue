<template>
  <div class="register-container">
    <div class="register-box">
      <h1>Register</h1>
      <form @submit.prevent="register">
        <div class="input-group">
          <input v-model="username" placeholder="Username" />
        </div>
        <div class="input-group">
          <input v-model="email" placeholder="Email" />
        </div>
        <div class="input-group">
          <input type="password" v-model="password" placeholder="Password" />
        </div>
        <button type="submit">Register</button>
      </form>
      <p v-if="error" class="error-msg">{{ error }}</p>
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
      error: null,
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
          .catch(() => {
            this.error = 'Registration failed. Please check your inputs.';
          });
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

/* Кнопка */
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

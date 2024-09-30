<template>
  <div>
    <h1>Register</h1>
    <form @submit.prevent="register">
      <input v-model="username" placeholder="Username" />
      <input v-model="email" placeholder="Email" />
      <input type="password" v-model="password" placeholder="Password" />
      <button type="submit">Register</button>
    </form>
    <p v-if="error">{{ error }}</p>
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
      console.log('Registering user with data:', {
        username: this.username,
        email: this.email,
        password: this.password,
      });

      axios
        .post(`${process.env.VUE_APP_API_URL}/user/register/`, {
          username: this.username,
          email: this.email,
          password: this.password,
        })
        .then((response) => {
          console.log('Registration successful:', response.data);
          this.$router.push('/login');
        })
        .catch((error) => {
          console.error('Registration failed:', error.response.data);
          this.error = 'Registration failed. Please check your inputs.';
        });
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
p {
  color: red;
}
</style>

import { createRouter, createWebHistory } from 'vue-router';
import RegisterPage from './components/RegisterPage.vue';
import LoginPage from './components/LoginPage.vue';
import CommentsPage from './components/CommentsPage.vue'; // Добавим позже

const routes = [
  { path: '/register', component: RegisterPage },
  { path: '/login', component: LoginPage },
  { path: '/comments', component: CommentsPage }, // Страница комментариев, будет позже
  { path: '/', redirect: '/register' }, // Редирект на регистрацию
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

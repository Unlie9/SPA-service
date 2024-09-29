import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Создание и монтирование приложения
createApp(App).use(router).mount('#app');
